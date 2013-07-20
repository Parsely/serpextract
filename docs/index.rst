.. serpextract documentation master file, created by
   sphinx-quickstart on Wed Jul  3 18:25:18 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

serpextract |release| Documentation
===================================

Overview
--------
**serpextract** provides easy extraction of keywords from search engine results pages (SERPs).

Contents:

.. toctree::
   :maxdepth: 4

   serpextract

Examples
--------

**Python**

.. code-block:: python

    from serpextract import get_parser, extract, is_serp, get_all_query_params

    non_serp_url = 'http://arstechnica.com/'
    serp_url = ('http://www.google.ca/url?sa=t&rct=j&q=ars%20technica&source=web&cd=1&ved=0CCsQFjAA'
                '&url=http%3A%2F%2Farstechnica.com%2F&ei=pf7RUYvhO4LdyAHf9oGAAw&usg=AFQjCNHA7qjcMXh'
                'j-UX9EqSy26wZNlL9LQ&bvm=bv.48572450,d.aWc')

    get_all_query_params()
    # ['key', 'text', 'search_for', 'searchTerm', 'qrs', 'keyword', ...]

    is_serp(serp_url)
    # True
    is_serp(non_serp_url)
    # False

    get_parser(serp_url)
    # SearchEngineParser(engine_name='Google', keyword_extractor=['q'], link_macro='search?q={k}', charsets=['utf-8'])
    get_parser(non_serp_url)
    # None

    extract(serp_url)
    # ExtractResult(engine_name='Google', keyword=u'ars technica', parser=SearchEngineParser(...))
    extract(non_serp_url)
    # None

**Command Line**

Command-line usage, returns the engine name and keyword components separated by a
comma and enclosed in quotes::

    $ serpextract "http://www.google.ca/url?sa=t&rct=j&q=ars%20technica"
    "Google","ars technica"

You can also print out a list of all the SearchEngineParsers currently available in
your local cache via::

    $ serpextract -l

Naive Detection
---------------

The list of search engine parsers that Piwik and therefore :mod:`serpextract.serpextract` uses is far from
exhaustive.  If you want :mod:`serpextract.serpextract` to attempt to guess if a given referring URL is a SERP,
you can specify ``use_naive_method=True`` to :func:`serpextract.serpextract.is_serp` or :func:`serpextract.serpextract.extract`.
By default, the naive method is disabled.

Naive search engine detection tries to find an instance of ``r'\.?search\.'`` in the ``netloc``
of a URL.  If found, :mod:`serpextract.serpextract` will then try to find a keyword in the ``query`` portion of
the URL by looking for the following params in order::

    _naive_params = ('q', 'query', 'k', 'keyword', 'term',)

If one of these are found, a keyword is extracted and an ``ExtractResult`` is constructed as::

    ExtractResult(domain, keyword, None)  # No parser, but engine name and keyword

.. code-block:: python

    # Not a recognized search engine by serpextract
    serp_url = 'http://search.piccshare.com/search.php?cat=web&channel=main&hl=en&q=test'

    is_serp(serp_url)
    # False

    extract(serp_url)
    # None

    is_serp(serp_url, use_naive_method=True)
    # True

    extract(serp_url, use_naive_method=True)
    # ExtractResult(engine_name=u'piccshare', keyword=u'test', parser=None)

Custom Parsers
--------------

In the event that you have a custom search engine that you'd like to track which is not currently
supported by Piwik/:mod:`serpextract.serpextract`, you can create your own instance of
:class:`serpextract.serpextract.SearchEngineParser` and either pass it explicitly to either
:func:`serpextract.serpextract.is_serp` or :func:`serpextract.serpextract.extract` or add it
to the internal list of parsers.

.. code-block:: python

    # Create a parser for PiccShare
    from serpextract import SearchEngineParser, is_serp, extract

    my_parser = SearchEngineParser(u'PiccShare',          # Engine name
                                   u'q',                  # Keyword extractor
                                   u'/search.php?q={k}',  # Link macro
                                   u'utf-8')              # Charset
    serp_url = 'http://search.piccshare.com/search.php?cat=web&channel=main&hl=en&q=test'

    is_serp(serp_url)
    # False

    extract(serp_url)
    # None

    is_serp(serp_url, parser=my_parser)
    # True

    extract(serp_url, parser=my_parser)
    # ExtractResult(engine_name=u'PiccShare', keyword=u'test', parser=SearchEngineParser(engine_name=u'PiccShare', keyword_extractor=[u'q'], link_macro=u'/search.php?q={k}', charsets=[u'utf-8']))

You can also permanently add a custom parser to the internal list of parsers that
:mod:`serpextract.serpextract` maintains so that you no longer have to explicitly pass a parser
object to :func:`serpextract.serpextract.is_serp` or :func:`serpextract.serpextract.extract`.

.. code-block:: python

    from serpextract import SearchEngineParser, add_custom_parser, is_serp, extract

    my_parser = SearchEngineParser(u'PiccShare',          # Engine name
                                   u'q',                  # Keyword extractor
                                   u'/search.php?q={k}',  # Link macro
                                   u'utf-8')              # Charset
    add_custom_parser(u'search.piccshare.com', my_parser)

    serp_url = 'http://search.piccshare.com/search.php?cat=web&channel=main&hl=en&q=test'
    is_serp(serp_url)
    # True

    extract(serp_url)
    # ExtractResult(engine_name=u'PiccShare', keyword=u'test', parser=SearchEngineParser(engine_name=u'PiccShare', keyword_extractor=[u'q'], link_macro=u'/search.php?q={k}', charsets=[u'utf-8']))

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

