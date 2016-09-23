"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from __future__ import absolute_import, division, print_function

import os

try:
    import ujson as json
except ImportError:
    import json
import ruamel.yaml as yaml
from six.moves.urllib.request import urlopen


_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *paths)


def main():
    filename = _here('serpextract', 'search_engines.json')
    print('Updating search engine parser definitions.')

    # TODO: Change this back once PR is merged
    # url = urlopen('https://raw.githubusercontent.com/piwik/searchengine-and-social-list/master/SearchEngines.yml')
    url = urlopen('https://raw.githubusercontent.com/dan-blanchard/searchengine-and-social-list/patch-1/SearchEngines.yml')
    piwik_engines = yaml.load(url)
    with open(filename, 'w') as json_file:
        json.dump(piwik_engines, json_file, indent=2)

    print('Saved {} search engine parser definitions to {}.'
          .format(len(piwik_engines), filename))


if __name__ == '__main__':
    main()
