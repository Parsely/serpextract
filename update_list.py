"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""

from __future__ import absolute_import, division, print_function

import os

try:
    import ujson as json
except ImportError:
    import json
from ruamel.yaml import YAML
from six.moves.urllib.request import urlopen


_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *paths)


def main():
    filename = _here('serpextract', 'search_engines.json')
    print('Updating search engine parser definitions.')

    url = urlopen('https://raw.githubusercontent.com/matomo-org/searchengine-and-social-list/master/SearchEngines.yml')
    yaml = YAML(typ='safe', pure=True)
    matomo_engines = yaml.load(url)

    # Hard-code Mojeek entries in expected format
    # see: https://github.com/Parsely/serpextract/pull/23
    matomo_engines["Mojeek"] = [
        {
            "backlink": "search?q={k}",
            "hiddenkeyword": ["/^$/", "/", "/\\/search(\\?.*)?/", "/\\/url\\?.*/"],
            "params": ["q"],
            "urls": ["mojeek.com", "www.mojeek.com"],
        }
    ]

    with open(filename, "w") as json_file:
        json.dump(matomo_engines, json_file, indent=2, sort_keys=True)

    print('Saved {} search engine parser definitions to {}.'
          .format(len(matomo_engines), filename))


if __name__ == '__main__':
    main()
