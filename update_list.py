"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from __future__ import absolute_import, division, print_function

import os
import sys
from collections import OrderedDict
from subprocess import Popen, PIPE

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except ImportError:
    import json
from six.moves.urllib.request import urlopen


_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *paths)


def main():
    py_version = sys.version_info[0]
    filename = _here('serpextract', 'search_engines.py{}.pickle'.format(py_version))
    print('Updating search engine parser definitions (requires PHP).')

    url = urlopen('https://raw.githubusercontent.com/piwik/piwik/2.14.3/core/DataFiles/SearchEngines.php')
    php_script = url.readlines()
    php_script.append(b'echo(json_encode($GLOBALS["Piwik_SearchEngines"]));\n')
    php_script = b''.join(php_script)
    process = Popen(['php'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    json_string = process.communicate(input=php_script)[0]
    # Ordering of the dictionary from PHP matters so we keep it in an
    # OrderedDict
    piwik_engines = json.loads(json_string, object_pairs_hook=OrderedDict)
    with open(filename, 'wb') as pickle_file:
        pickle.dump(piwik_engines, pickle_file)

    print('Saved {} search engine parser definitions to {}.'
          .format(len(piwik_engines), filename))


if __name__ == '__main__':
    main()
