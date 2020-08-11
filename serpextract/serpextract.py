"""Utilities for extracting keyword information from search engine
referrers."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import re
import sys
from collections import defaultdict
from io import TextIOWrapper

import pylru
import tldextract
from iso3166 import countries
from six import iteritems, itervalues, PY3, string_types, text_type
from six.moves.urllib.parse import urlparse, parse_qs, ParseResult

# import pkg_resources
# with fallback for environments that lack it
try:
    import pkg_resources
except ImportError:
    import os

    class pkg_resources(object):
        """Fake pkg_resources interface which falls back to getting resources
        inside `serpextract`'s directory. (thank you tldextract!)
        """
        @classmethod
        def resource_stream(cls, package, resource_name):
            moddir = os.path.dirname(__file__)
            f = os.path.join(moddir, resource_name)
            return open(f)

# import ujson for performance with a fallback on default json
try:
    import ujson as json
except ImportError:
    import json


__all__ = ('get_parser', 'is_serp', 'extract', 'get_all_query_params',
           'get_all_query_params_by_domain', 'add_custom_parser',
           'SearchEngineParser')

log = logging.getLogger('serpextract')

_country_codes = [country.alpha2.lower()
                  for country in countries]
# uk is not an official ISO-3166 country code, but it's used in top-level
# domains so we add it to our list see
# http://en.wikipedia.org/wiki/ISO_3166-1 for more information
_country_codes += ['uk']

# For generating possible variations of domains based
_second_level_domains = ['co', 'com']

# Cache for querystring params returned by get_all_query_params_by_domain
_qs_params = None

# A LRUCache of domains to save us from having to do lots of regex matches
_domain_cache = pylru.lrucache(500)

# Naive search engine detection.  Look for \.?search\. in the netloc and then
# try to extract using common query params
_naive_re = re.compile(r'\.?search\.')
_naive_params = ('q', 'query', 'k', 'keyword', 'term',)


def _unicode_parse_qs(qs, **kwargs):
    """
    A wrapper around ``urlparse.parse_qs`` that converts unicode strings to
    UTF-8 to prevent ``urlparse.unquote`` from performing it's default decoding
    to latin-1 see http://hg.python.org/cpython/file/2.7/Lib/urlparse.py

    :param qs:       Percent-encoded query string to be parsed.
    :type qs:        ``str``

    :param kwargs:   Other keyword args passed onto ``parse_qs``.
    """
    if PY3 or isinstance(qs, bytes):
        # Nothing to do
        return parse_qs(qs, **kwargs)

    qs = qs.encode('utf-8', 'ignore')
    query = parse_qs(qs, **kwargs)
    unicode_query = {}
    for key in query:
        uni_key = key.decode('utf-8', 'ignore')
        if uni_key == '':
            # because we ignore decode errors and only support utf-8 right now,
            # we could end up with a blank string which we ignore
            continue
        unicode_query[uni_key] = [p.decode('utf-8', 'ignore') for p in query[key]]
    return unicode_query


def _unicode_urlparse(url, encoding='utf-8', errors='ignore'):
    """
    Safely parse a URL into a :class:`urlparse.ParseResult` ensuring that
    all elements of the parse result are unicode.

    :param url:      A URL.
    :type url:       ``bytes``, ``unicode`` or :class:`urlparse.ParseResult`

    :param encoding: The string encoding assumed in the underlying ``str`` or
                     :class:`urlparse.ParseResult` (default is utf-8).
    :type encoding:  ``bytes``

    :param errors:   response from ``decode`` if string cannot be converted to
                     unicode given encoding (default is ignore).
    :type errors:    ``bytes``
    """
    if isinstance(url, bytes):
        url = url.decode(encoding, errors)
    elif isinstance(url, ParseResult):
        # Ensure every part is unicode because we can't rely on clients to do so
        parts = list(url)
        for i in range(len(parts)):
            if isinstance(parts[i], bytes):
                parts[i] = parts[i].decode(encoding, errors)
        return ParseResult(*parts)

    try:
        return urlparse(url)
    except ValueError:
        msg = 'Malformed URL "{}" could not parse'.format(url)
        log.debug(msg, exc_info=True)
        return None


def _serp_query_string(parse_result):
    """
    Some search engines contain the search keyword in the fragment so we
    build a version of a query string that contains the query string and
    the fragment.

    :param parse_result: A URL.
    :type parse_result:  :class:`urlparse.ParseResult`
    """
    query = parse_result.query
    if parse_result.fragment != '':
        query = '{}&{}'.format(query, parse_result.fragment)

    return query


def _is_url_without_path_query_or_fragment(url_parts):
    """
    Determines if a URL has a blank path, query string and fragment.

    :param url_parts: A URL.
    :type url_parts:  :class:`urlparse.ParseResult`
    """
    return url_parts.path.strip('/') in ['', 'search'] and url_parts.query == '' \
           and url_parts.fragment == ''

_engines = None
def _get_search_engines():
    """
    Convert the OrderedDict of search engine parsers that we get from Matomo
    to a dictionary of SearchEngineParser objects.

    Cache this thing by storing in the global ``_engines``.
    """
    global _engines
    if _engines:
        return _engines

    matomo_engines = _get_matomo_engines()
    # Engine names are the first param of each of the search engine arrays
    # so we group by those guys, and create our new dictionary with that
    # order
    _engines = {}

    for engine_name, rule_group in iteritems(matomo_engines):
        defaults = {
            'extractor': None,
            'link_macro': None,
            'charsets': ['utf-8'],
            'hiddenkeyword': None
        }

        for rule in rule_group:
            if any(url for url in rule['urls'] if '{}' in url):
                rule['urls'] = _expand_country_codes(rule['urls'])
            for i, domain in enumerate(rule['urls']):
                if i == 0:
                    defaults['extractor'] = rule['params']
                    if 'backlink' in rule:
                        defaults['link_macro'] = rule['backlink']
                    if 'charsets' in rule:
                        defaults['charsets'] = rule['charsets']
                    if 'hiddenkeyword' in rule:
                        defaults['hiddenkeyword'] = rule['hiddenkeyword']

                _engines[domain] = SearchEngineParser(engine_name,
                                                      defaults['extractor'],
                                                      defaults['link_macro'],
                                                      defaults['charsets'],
                                                      defaults['hiddenkeyword'])

    return _engines


def _expand_country_codes(urls):
    urls = set(urls) if isinstance(urls, list) else {urls}
    expanded_urls = {url.format(country_code) for url in urls
                     for country_code in _country_codes}
    expanded_urls.update({url.format(second_level_domain + '.' + cc_sub_domain)
                          for url in urls
                          for cc_sub_domain in _country_codes
                          for second_level_domain in _second_level_domains
                          if not url[-1].isalnum()})
    return expanded_urls


def _get_matomo_engines():
    """
    Return the search engine parser definitions stored in this module. We don't
    cache this result since it's only supposed to be called once.
    """
    stream = pkg_resources.resource_stream
    with stream(__name__, 'search_engines.json') as json_stream:
        if PY3:
            if hasattr(json_stream, 'buffer'):
                json_stream = TextIOWrapper(json_stream.buffer, encoding='utf-8')
            else:
                json_stream = TextIOWrapper(json_stream, encoding='utf-8')
        _matomo_engines = json.load(json_stream)
    return _matomo_engines


class ExtractResult(object):
    __slots__ = ('engine_name', 'keyword', 'parser')

    def __init__(self, engine_name, keyword, parser):
        self.engine_name = engine_name
        self.keyword = keyword
        self.parser = parser

    def __repr__(self):
        repr_fmt = 'ExtractResult(engine_name={!r}, keyword={!r}, parser={!r})'
        return repr_fmt.format(self.engine_name, self.keyword, self.parser)


class SearchEngineParser(object):
    """Handles persing logic for a single line in Matomo's list of search
    engines.

    Matomo's list for reference:

    https://raw.githubusercontent.com/matomo-org/searchengine-and-social-list/master/SearchEngines.yml

    This class is not used directly since it already assumes you know the
    exact search engine you want to use to parse a URL. The main interface
    for users of this module is the :func:`extract` method.
    """
    __slots__ = ('engine_name', 'keyword_extractor', 'link_macro', 'charsets',
                 'hidden_keyword_paths')

    def __init__(self, engine_name, keyword_extractor, link_macro, charsets,
                 hidden_keyword_paths=None):
        """New instance of a :class:`SearchEngineParser`.

        :param engine_name:         the friendly name of the engine (e.g.
                                    'Google')

        :param keyword_extractor:   a string or list of keyword extraction
                                    methods for this search engine.  If a
                                    single string, we assume we're extracting a
                                    query string param, if it's a string that
                                    starts with '/' then we extract from the
                                    path instead of query string

        :param link_macro:          a string indicating how to build a link to
                                    the search engine results page for a given
                                    keyword

        :param charsets:            a string or list of charsets to use to
                                    decode the keyword

        :param hidden_keywords_paths: an optional list of strings (that may
                                      contain regular expressions) describing
                                      valid paths for the search engine that may
                                      not contain any keywords. Regular
                                      expressions are expected to be surround by
                                      `/` characters.
        """
        self.engine_name = engine_name
        if isinstance(keyword_extractor, string_types):
            keyword_extractor = [keyword_extractor]
        self.keyword_extractor = keyword_extractor[:]
        for i, extractor in enumerate(self.keyword_extractor):
            # Pre-compile all the regular expressions
            if extractor.startswith('/'):
                extractor = extractor.strip('/')
                extractor = re.compile(extractor)
                self.keyword_extractor[i] = extractor

        self.link_macro = link_macro
        if isinstance(charsets, string_types):
            charsets = [charsets]
        self.charsets = [c.lower() for c in charsets]
        if hidden_keyword_paths:
            self.hidden_keyword_paths = hidden_keyword_paths[:]
        else:
            self.hidden_keyword_paths = []
        for i, path in enumerate(self.hidden_keyword_paths):
            # Pre-compile all the regular expressions
            if len(path) > 1 and path.startswith('/') and path.endswith('/'):
                path = path[1:-1]
                path = re.compile(path)
                self.hidden_keyword_paths[i] = path

    def get_serp_url(self, base_url, keyword):
        """
        Get a URL to a SERP for a given keyword.

        :param base_url: String of format ``'<scheme>://<netloc>'``.
        :type base_url:  ``str``

        :param keyword:  Search engine keyword.
        :type keyword:   ``str``

        :returns: a URL that links directly to a SERP for the given keyword.
        """
        if self.link_macro is None:
            return None

        link = '{}/{}'.format(base_url, self.link_macro.format(k=keyword))
        return link

    def parse(self, url_parts):
        """
        Parse a SERP URL to extract the search keyword.

        :param serp_url: The SERP URL
        :type serp_url:  A :class:`urlparse.ParseResult` with all elements
                         as unicode

        :returns: An :class:`ExtractResult` instance.
        """
        original_query = _serp_query_string(url_parts)
        query = _unicode_parse_qs(original_query, keep_blank_values=True)

        keyword = None
        engine_name = self.engine_name

        if engine_name == 'Google Images' or \
           (engine_name == 'Google' and '/imgres' in original_query):
            # When using Google's image preview mode, it hides the keyword
            # within the prev query string param which itself contains a
            # path and query string
            # e.g. &prev=/search%3Fq%3Dimages%26sa%3DX%26biw%3D320%26bih%3D416%26tbm%3Disch
            engine_name = 'Google Images'
            if 'prev' in query:
                query = _unicode_parse_qs(_unicode_urlparse(query['prev'][0]).query)
        elif engine_name == 'Google' and 'as_' in original_query:
            # Google has many different ways to filter results.  When some of
            # these filters are applied, we can no longer just look for the q
            # parameter so we look at additional query string arguments and
            # construct a keyword manually
            keys = []

            # Results should contain all of the words entered
            # Search Operator: None (same as normal search)
            key = query.get('as_q')
            if key:
                keys.append(key[0])
            # Results should contain any of these words
            # Search Operator: <keyword> [OR <keyword>]+
            key = query.get('as_oq')
            if key:
                key = key[0].replace('+', ' OR ')
                keys.append(key)
            # Results should match the exact phrase
            # Search Operator: "<keyword>"
            key = query.get('as_epq')
            if key:
                keys.append('"{}"'.format(key[0]))
            # Results should contain none of these words
            # Search Operator: -<keyword>
            key = query.get('as_eq')
            if key:
                keys.append('-{}'.format(key[0]))

            keyword = ' '.join(keys).strip()

        if engine_name == 'Google':
            # Check for usage of Google's top bar menu
            tbm = query.get('tbm', [None])[0]
            if tbm == 'isch':
                engine_name = 'Google Images'
            elif tbm == 'vid':
                engine_name = 'Google Video'
            elif tbm == 'shop':
                engine_name = 'Google Shopping'

        if keyword is not None:
            # Edge case found a keyword, exit quickly
            return ExtractResult(engine_name, keyword, self)

        # Otherwise we keep looking through the defined extractors
        for extractor in self.keyword_extractor:
            if not isinstance(extractor, string_types):
                # Regular expression extractor
                match = extractor.search(url_parts.path)
                if match:
                    keyword = match.group(1)
                    break
            else:
                # Search for keywords in query string
                if extractor in query:
                    # Take the last param in the qs because it should be the
                    # most recent
                    keyword = query[extractor][-1]

                # Now we have to check for a tricky case where it is a SERP but
                # there are no keywords
                if keyword == '':
                    keyword = False

                if keyword is not None:
                    break

        # if no keyword found, but empty/hidden keywords are allowed
        if self.hidden_keyword_paths and (keyword is None or keyword is False):
            path_with_query_and_frag = url_parts.path
            if url_parts.query:
                path_with_query_and_frag += '?{}'.format(url_parts.query)
            if url_parts.fragment:
                path_with_query_and_frag += '#{}'.format(url_parts.fragment)
            for path in self.hidden_keyword_paths:
                if not isinstance(path, string_types):
                    if path.search(path_with_query_and_frag):
                        keyword = False
                        break
                elif path == path_with_query_and_frag:
                    keyword = False
                    break

        if keyword is not None:
            # Replace special placeholder with blank string
            if keyword is False:
                keyword = ''
            return ExtractResult(engine_name, keyword, self)

    def __repr__(self):
        repr_fmt = ("SearchEngineParser(engine_name={!r}, "
                    "keyword_extractor={!r}, link_macro={!r}, charsets={!r}, "
                    "hidden_keywords={!r})")
        return repr_fmt.format(self.engine_name,
                               self.keyword_extractor,
                               self.link_macro,
                               self.charsets,
                               self.hidden_keyword_paths)


def add_custom_parser(match_rule, parser):
    """
    Add a custom search engine parser to the cached ``_engines`` list.

    :param match_rule: A match rule which is used by :func:`get_parser` to look
                       up a parser for a given domain/path.
    :type match_rule:  ``unicode``

    :param parser:     A custom parser.
    :type parser:      :class:`SearchEngineParser`
    """
    assert isinstance(match_rule, text_type)
    assert isinstance(parser, SearchEngineParser)

    global _engines
    _get_search_engines()  # Ensure that the default engine list is loaded

    _engines[match_rule] = parser


def get_all_query_params():
    """
    Return all the possible query string params for all search engines.

    :returns: a ``list`` of all the unique query string parameters that are
              used across the search engine definitions.
    """
    engines = _get_search_engines()
    all_params = set()
    for parser in itervalues(engines):
        # Find non-regex params
        params = {param for param in parser.keyword_extractor
                  if isinstance(param, string_types)}
        all_params |= params

    return list(all_params)


def get_all_query_params_by_domain():
    """
    Return all the possible query string params for all search engines.

    :returns: a ``list`` of all the unique query string parameters that are
              used across the search engine definitions.
    """
    global _qs_params
    if _qs_params:
        return _qs_params
    engines = _get_search_engines()
    param_dict = defaultdict(list)
    for domain, parser in iteritems(engines):
        # Find non-regex params
        params = {param for param in parser.keyword_extractor
                  if isinstance(param, string_types)}
        tld_res = tldextract.extract(domain)
        domain = tld_res.registered_domain
        param_dict[domain] = sorted(set(param_dict[domain]) | params)
    _qs_params = param_dict
    return param_dict


def get_parser(referring_url):
    """
    Utility function to find a parser for a referring URL if it is a SERP.

    :param referring_url: Suspected SERP URL.
    :type referring_url:  ``str`` or :class:`urlparse.ParseResult`

    :returns: :class:`SearchEngineParser` object if one exists for URL,
              ``None`` otherwise.
    """
    engines = _get_search_engines()
    url_parts = _unicode_urlparse(referring_url)
    if url_parts is None:
        return None

    query = _serp_query_string(url_parts)

    domain = url_parts.netloc
    path = url_parts.path
    engine_key = url_parts.netloc
    stripped_domain = domain[4:] if domain.startswith('www.') else None
    # Try to find a parser in the engines list.  We go from most specific to
    # least specific order:
    # 1. <domain><path>
    # 2. <custom search engines>
    # 3. <domain>
    # 4. <stripped_domain>
    # The second step has some special exceptions for things like Google custom
    # search engines, yahoo and yahoo images
    if '{}{}'.format(domain, path) in engines:
        engine_key = '{}{}'.format(domain, path)
    elif domain not in engines and stripped_domain not in engines:
        if query[:14] == 'cx=partner-pub':
            # Google custom search engine
            engine_key = 'google.com/cse'
        elif url_parts.path[:28] == '/pemonitorhosted/ws/results/':
            # private-label search powered by InfoSpace Metasearch
            engine_key = 'wsdsold.infospace.com'
        elif '.images.search.yahoo.com' in url_parts.netloc:
            # Yahoo! Images
            engine_key = 'images.search.yahoo.com'
        elif '.search.yahoo.com' in url_parts.netloc:
            # Yahoo!
            engine_key = 'search.yahoo.com'
        else:
            return None

    return engines.get(engine_key) or engines.get(stripped_domain)


def is_serp(referring_url, parser=None, use_naive_method=False):
    """
    Utility function to determine if a referring URL is a SERP.

    :param referring_url:    Suspected SERP URL.
    :type referring_url:     str or urlparse.ParseResult

    :param parser:           A search engine parser.
    :type parser:            :class:`SearchEngineParser` instance or
                             ``None``.

    :param use_naive_method: Whether or not to use a naive method of search
                             engine detection in the event that a parser does
                             not exist for the given ``referring_url``.  See
                             :func:`extract` for more information.
    :type use_naive_method:  ``True`` or ``False``

    :returns: ``True`` if SERP, ``False`` otherwise.
    """
    res = extract(referring_url, parser=parser,
                  use_naive_method=use_naive_method)
    return res is not None


def extract(serp_url, parser=None, lower_case=True, trimmed=True,
            collapse_whitespace=True, use_naive_method=False):
    """
    Parse a SERP URL and return information regarding the engine name,
    keyword and :class:`SearchEngineParser`.

    :param serp_url:            Suspected SERP URL to extract a keyword from.
    :type serp_url:             ``str`` or :class:`urlparse.ParseResult`

    :param parser:              Optionally pass in a parser if already
                                determined via call to get_parser.
    :type parser:               :class:`SearchEngineParser`

    :param lower_case:          Lower case the keyword.
    :type lower_case:           ``True`` or ``False``

    :param trimmed:             Trim keyword leading and trailing whitespace.
    :type trimmed:              ``True`` or ``False``

    :param collapse_whitespace: Collapse 2 or more ``\s`` characters into one
                                space ``' '``.
    :type collapse_whitespace:  ``True`` or ``False``

    :param use_naive_method:    In the event that a parser doesn't exist for
                                the given ``serp_url``, attempt to find an
                                instance of ``_naive_re_pattern`` in the netloc
                                of the ``serp_url``.  If found, try to extract
                                a keyword using ``_naive_params``.
    :type use_naive_method:     ``True`` or ``False``

    :returns: an :class:`ExtractResult` instance if ``serp_url`` is valid,
              ``None`` otherwise
    """
    # Software should only work with Unicode strings internally, converting
    # to a particular encoding on output.
    url_parts = _unicode_urlparse(serp_url)
    if url_parts is None:
        return None

    result = None
    if parser is None:
        parser = get_parser(url_parts)

    if parser is None:
        if not use_naive_method:
            return None  # Tried to get keyword from non SERP URL

        # Try to use naive method of detection
        if _naive_re.search(url_parts.netloc):
            query = _unicode_parse_qs(url_parts.query, keep_blank_values=True)
            for param in _naive_params:
                if param in query:
                    tld_res = tldextract.extract(url_parts.netloc)
                    return ExtractResult(tld_res.domain,
                                         query[param][0],
                                         None)

        return None  # Naive method could not detect a keyword either

    result = parser.parse(url_parts)

    if result is None:
        return None

    if lower_case:
        result.keyword = result.keyword.lower()
    if trimmed:
        result.keyword = result.keyword.strip()
    if collapse_whitespace:
        result.keyword = re.sub(r'\s+', ' ', result.keyword, re.UNICODE)

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Parse a SERP URL to extract engine name and keyword.')

    parser.add_argument('input', metavar='url', type=text_type, nargs='*',
                        help='A potential SERP URL')
    parser.add_argument('-l', '--list', default=False, action='store_true',
                        help='Print a list of all the SearchEngineParsers.')

    args = parser.parse_args()

    if args.list:
        engines = _get_search_engines()
        engines = sorted(iteritems(engines), key=lambda x: x[1].engine_name)
        print('{:<30}{}'.format('Fuzzy Domain', 'Parser'))
        for fuzzy_domain, parser in engines:
            print('{:<30}{}'.format(fuzzy_domain, parser))
        print('{} parsers.'.format(len(engines)))
        sys.exit(0)

    if len(args.input) == 0:
        parser.print_usage()
        sys.exit(1)

    escape_quotes = lambda s: re.sub(r'"', '\\"', s)

    for url in args.input:
        res = extract(url)
        if res is None:
            res = ['""', '""']
        else:
            res = [escape_quotes(res.engine_name), escape_quotes(res.keyword)]
            res = ['"{}"'.format(r) for r in res]
        print(','.join(res))

if __name__ == '__main__':
    main()
