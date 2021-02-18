Contributing to serpextract
===========================

Updating the search engine list
-------------------------------

Internally, this module caches an OrderedDict representation of
`Matomo's list of search engines <https://raw.githubusercontent.com/matomo-org/searchengine-and-social-list/master/SearchEngines.yml>`_
which is stored in ``serpextract/search_engines.json``.  This isn't intended to change that often and so this
module ships with a cached version.

When developing on serpextract, you can update the list by running `python update_list.py` and committing the resulting changes.

Releasing a new version
-----------------------

Assuming master contains the changes you want to include in the new version:

1. Increment the version string in `serpextract/__init__.py` according to semantic versioning. Commit this change.
2. Tag the commit with the version string prefixed by a `v` (ex `v0.7.1`) `git tag v0.7.1`
3. `rm -rf dist && python setup.py sdist bdist_wheel && twine upload dist/*`
4. Add an entry to `CHANGES.txt` for the new version. Commit this change.
5. `git push origin master --tags`
