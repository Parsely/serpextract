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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

