serpextract
===========

.. image:: https://travis-ci.org/Parsely/serpextract.png?branch=master
   :target: https://travis-ci.org/Parsely/serpextract

``serpextract`` provides easy extraction of keywords from search engine results pages (SERPs).

This module is possible in large part to the very hard work of the `Piwik <http://piwik.org/>`_ team.
Specifically, we make extensive use of their `list of search engines <https://github.com/piwik/piwik/blob/master/core/DataFiles/SearchEngines.php>`_.


Installation
------------
Latest release on PyPI::

    $ pip install serpextract

Or the latest development version::

    $ pip install -e git://github.com/Parsely/serpextract.git#egg=serpextract

Usage
-----

Command Line
^^^^^^^^^^^^

Command-line usage, returns the engine name and keyword components separated by a
comma and enclosed in quotes::

    $ serpextract "http://www.google.ca/url?sa=t&rct=j&q=ars%20technica"
    "Google","ars technica"

You can also print out a list of all the SearchEngineParsers currently available in
your local cache via::

    $ serpextract -l

Python
^^^^^^

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

Tests
-----

There are some basic tests for popular search engines, but more are required::

    $ pip install -r requirements.txt
    $ nosetests

Caching
-------

Internally, this module caches an OrderedDict representation of 
`Piwik's list of search engines <https://github.com/piwik/piwik/blob/master/core/DataFiles/SearchEngines.php>`_
which is stored in ``serpextract/search_engines.pickle``.  This isn't intended to change that often and so this
module ships with a cached version.
