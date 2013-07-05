"""Utilities for extracting keyword information from search engine
referrers."""
import re
import logging

from itertools import groupby
from urlparse import urlparse, parse_qs, ParseResult
from iso3166 import countries

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

# import cPickle
# for performance with a fallback on Python pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle

__all__ = ('get_parser', 'is_serp', 'extract', 'get_all_query_params')

log = logging.getLogger('serpextract')

_country_codes = [country.alpha2.lower()
                  for country in countries]
# uk is not an official ISO-3166 country code, but it's used in top-level
# domains so we add it to our list see
# http://en.wikipedia.org/wiki/ISO_3166-1 for more information
_country_codes += ['uk']


def _to_unicode(s):
    """safely decodes a string into unicode if it's not already unicode"""
    return s if isinstance(s, unicode) else s.decode("utf-8", "ignore")


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
    """Handles persing logic for a single line in Piwik's list of search
    engines.

    Piwik's list for reference:

    https://raw.github.com/piwik/piwik/master/core/DataFiles/SearchEngines.php

    This class is not used directly since it already assumes you know the
    exact search engine you want to use to parse a URL. The main interface
    for users of this module is the `get_keyword` method.
    """
    __slots__ = ('engine_name', 'keyword_extractor', 'link_macro', 'charsets')

    def __init__(self, engine_name, keyword_extractor, link_macro, charsets):
        """New instance of a `SearchEngineParser`.

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
        """
        self.engine_name = engine_name
        if isinstance(keyword_extractor, basestring):
            keyword_extractor = [keyword_extractor]
        self.keyword_extractor = keyword_extractor
        self.link_macro = link_macro
        if isinstance(charsets, basestring):
            charsets = [charsets]
        self.charsets = [c.lower() for c in charsets]

    def get_serp_url(self, base_url, keyword):
        """Get a URL to the search engine results page (SERP) for a given
        keyword.

        :param base_url: string of format '<scheme>://<netloc>'

        :param keyword: search keyword string

        :returns: string URL of SERP
        """
        if self.link_macro is None:
            return None

        link = u'{}/{}'.format(base_url, self.link_macro.format(k=keyword))
        #link = self.decode_string(link)
        return link

    def parse(self, serp_url):
        """Parse a SERP URL to extract the search keyword.

        :param serp_url: either a string or a `ParseResult`

        :returns: An `ExtractResult` instance
        """
        if isinstance(serp_url, basestring):
            try:
                url_parts = urlparse(serp_url)
            except ValueError:
                msg = "Malformed URL '{}' could not parse".format(serp_url)
                log.debug(msg, exc_info=True)
                return
        else:
            url_parts = serp_url
        query = parse_qs(url_parts.query, keep_blank_values=True)

        keyword = None
        for extractor in self.keyword_extractor:
            if extractor.startswith('/'):
                # Regular expression extractor
                extractor = extractor.strip('/')
                regex = re.compile(extractor)
                match = regex.search(url_parts.path)
                if match:
                    keyword = match.group(1)
                    break
            else:
                if extractor in query:
                    keyword = query[extractor][0]
                    break

        if keyword is None:
            return

        keyword = _to_unicode(keyword)

        return ExtractResult(self.engine_name, keyword, self)

    def __repr__(self):
        repr_fmt = ("SearchEngineParser(engine_name={!r}, "
                    "keyword_extractor={!r}, link_macro={!r}, charsets={!r})")
        return repr_fmt.format(
                        self.engine_name, 
                        self.keyword_extractor, 
                        self.link_macro,
                        self.charsets)


_piwik_engines = None
def _get_piwik_engines():
    """Return the search engine parser definitions stored in this module"""
    global _piwik_engines
    if _piwik_engines is None:
        stream = pkg_resources.resource_stream
        with stream(__name__, 'search_engines.pickle') as picklestream:
            _piwik_engines = pickle.load(picklestream)

    return _piwik_engines


def _get_lossy_domain(domain):
    """A lossy version of a domain/host to use as lookup in the
    `_engines` dict."""
    domain = unicode(domain)
    codes = '|'.join(_country_codes)
    domain = re.sub(r'^(\w+[0-9]*|search)\.',
                    '',
                    domain)
    domain = re.sub(r'(^|\.)m\.',
                    r'\1',
                    domain)
    domain = re.sub(r'(\.(com|org|net|co|it|edu))?\.({})(\/|$)'.format(codes),
                    r'.{}\4',
                    domain)
    domain = re.sub(r'(^|\.)({})\.'.format(codes),
                    r'\1{}.',
                    domain)
    return domain


_engines = None
def _get_search_engines():
    """Convert the OrderedDict of search engine parsers that we get from Piwik
    to a dictionary of SearchEngineParser objects.

    Cache this thing by storing in the global ``_engines``.
    """
    global _engines
    if _engines:
        return _engines

    piwik_engines = _get_piwik_engines()
    # Engine names are the first param of each of the search engine arrays
    # so we group by those guys, and create our new dictionary with that
    # order
    get_engine_name = lambda x: x[1][0]
    definitions_by_engine = groupby(piwik_engines.iteritems(), get_engine_name)
    _engines = {}

    for engine_name, rule_group in definitions_by_engine:
        defaults = {
            'extractor': None,
            'link_macro': None,
            'charsets': ['utf-8']
        }

        for i, rule in enumerate(rule_group):
            domain = rule[0]
            rule = rule[1][1:]
            if i == 0:
                defaults['extractor'] = rule[0]
                if len(rule) >= 2:
                    defaults['link_macro'] = rule[1]
                if len(rule) >= 3:
                    defaults['charsets'] = rule[2]

                _engines[domain] = SearchEngineParser(engine_name,
                                                      defaults['extractor'],
                                                      defaults['link_macro'],
                                                      defaults['charsets'])
                continue

            # Default args for SearchEngineParser
            args = [engine_name, defaults['extractor'],
                    defaults['link_macro'], defaults['charsets']]
            if len(rule) >= 1:
                args[1] = rule[0]

            if len(rule) >= 2:
                args[2] = rule[1]

            if len(rule) == 3:
                args[3] = rule[2]

            _engines[domain] = SearchEngineParser(*args)

    return _engines


def _not_regex(value):
    return not value.startswith('/') and not value.strip() == ''


def get_all_query_params():
    """Return all the possible query string params for all search engines."""
    engines = _get_search_engines()
    all_params = set()
    for _, parser in engines.iteritems():
        # Find non-regex params
        params = set(filter(_not_regex, parser.keyword_extractor))
        all_params |= params

    return list(all_params)


def get_parser(referring_url):
    """Utility function to find a parser for a referring URL
    if it is a SERP.

    :param referring_url: either the referring URL as a string or ParseResult
    :returns: SearchEngineParser object if one exists for URL, None otherwise
    """
    engines = _get_search_engines()
    try:
        if isinstance(referring_url, ParseResult):
            url_parts = referring_url
        else:
            url_parts = urlparse(referring_url)
    except ValueError:
        msg = "Malformed URL '{}' could not parse".format(referring_url)
        log.debug(msg, exc_info=True)
        # Malformed URLs
        return

    # First try to look up a search engine by the host name incase we have
    # a direct entry for it
    parser = engines.get(url_parts.netloc, 'nothing')
    if parser == 'nothing':
        # Now we'll try searching by lossy domain which converts
        # things like country codes for us
        parser = engines.get(_get_lossy_domain(url_parts.netloc),
                             'nothing')

    if parser == 'nothing':
        # no parser found
        return None

    return parser


def is_serp(referring_url):
    """Utility function to determine if a referring URL is a SERP URL.

    :returns: True if SERP, False otherwise.
    """
    parser = get_parser(referring_url)
    if parser is None:
        return False
    result = parser.parse(referring_url)

    return result is not None


def extract(serp_url, parser=None, lower_case=True, trimmed=True,
            collapse_whitespace=True):
    """Parse a SERP URL and return information regarding the engine, keyword
    and serp_link.

    This is a far more basic implementation than what Piwik has done in their
    source, but right now, we don't care about all the crazy edge cases.

    :param serp_url: the suspected SERP URL to extract a keyword from
    :param parser: optionally pass in a parser if already looked up via
                   call to get_parser
    :param lower_case: lower case the keyword
    :param trimmed: trim extra spaces before and after keyword
    :param collapse_whitespace: collapse 2 or more \s characters into
                                one space ' '
    :returns: an `ExtractResult` instance
    """
    if parser is None:
        parser = get_parser(serp_url)
    if not parser:
        # Tried to get keyword from non SERP URL
        return None

    result = parser.parse(serp_url)
    if result is None:
        msg = ('Found search engine parser for {} but was '
               'unable to extract keyword.')
        log.debug(msg.format(serp_url))
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
    import sys
    import re

    parser = argparse.ArgumentParser(
        description='Parse a SERP URL to extract engine name and keyword.')

    parser.add_argument('input', metavar='url', type=unicode, nargs='*',
                        help='A potential SERP URL')
    parser.add_argument('-l', '--list', default=False, action='store_true',
                        help='Print a list of all the SearchEngineParsers.')

    args = parser.parse_args()

    if args.list:
        engines = _get_search_engines()
        engines = sorted(engines.iteritems(), key=lambda x: x[1].engine_name)
        print '{:<30}{}'.format('Fuzzy Domain', 'Parser')
        for fuzzy_domain, parser in engines:
            print '{:<30}{}'.format(fuzzy_domain, parser)
        print '{} parsers.'.format(len(engines))
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
            res = [u'"{}"'.format(r) for r in res]
        print u','.join(res)

if __name__ == '__main__':
    main()
