"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from __future__ import absolute_import, division, print_function
import argparse
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
def array(*args, **kwargs):
    if args:
        return list(args)
    if kwargs:
        return OrderedDict(kwargs)

GLOBALS = {}
null = None

def parse_php(php_script):
    if_index = php_script.find('if ')
    start_index = php_script.find('{', if_index)+1

    end_index = php_script.rfind('}')
    json_body = php_script[start_index:end_index]

    # replace "$GLOBALS" to "GLOBALS"
    json_body = json_body.replace("$GLOBALS", "GLOBALS")

    # replace "=>" to ":", id dict
    json_body = json_body.replace("=>", ":")

    # replace "//" => "#"
    json_body = json_body.replace("//", "#")

    # replace "/*" => " ''' "
    # replace "*/" => " ''' "
    json_body = json_body.replace("/*", "'''")
    json_body = json_body.replace("*/", "'''")

    # first array is dict
    json_body = json_body.replace('array(', "OrderedDict(**{", 1)
    json_body = '})'.join(json_body.rsplit(')', 1))

    # indent
    json_body = 'if 1:\n' + json_body
    exec(json_body)

    return GLOBALS["Piwik_SearchEngines"]

def main():
    parser = argparse.ArgumentParser(description="SearchEngines.php file path")
    parser.add_argument("--file",
                        dest="file",
                        type=str,
                        default="https://raw.githubusercontent.com/piwik/piwik/2.14.3/core/DataFiles/SearchEngines.php",
                        help="SearchEngines.php")
    args = parser.parse_args()

    py_version = sys.version_info[0]
    filename = _here('serpextract', 'search_engines.py{}.pickle'.format(py_version))
    print('Updating search engine parser definitions (requires PHP).')

    # from piwik
    if args.file.startswith('http'):
        url = urlopen(args.file)
        php_script = url.read()
    # from local
    else:
        with open(args.file) as f:
            php_script = f.read()

    piwik_engines = parse_php(php_script)
    with open(filename, 'wb') as pickle_file:
        pickle.dump(piwik_engines, pickle_file)

    print('Saved {} search engine parser definitions to {}.'
          .format(len(piwik_engines), filename))


if __name__ == '__main__':
    main()
