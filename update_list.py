"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from __future__ import absolute_import, division, print_function

import os
import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except ImportError:
    import json
import ruamel.yaml as yaml
from six.moves.urllib.request import urlopen


_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *paths)


def main():
    py_version = sys.version_info[0]
    filename = _here('serpextract', 'search_engines.py{}.pickle'.format(py_version))
    print('Updating search engine parser definitions.')

    url = urlopen('https://raw.githubusercontent.com/piwik/searchengine-and-social-list/master/SearchEngines.yml')
    piwik_engines = yaml.load(url)
    with open(filename, 'wb') as pickle_file:
        pickle.dump(piwik_engines, pickle_file)

    print('Saved {} search engine parser definitions to {}.'
          .format(len(piwik_engines), filename))


if __name__ == '__main__':
    main()
