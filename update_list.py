"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from collections import OrderedDict
import os
from urllib2 import urlopen
from subprocess import Popen, PIPE, STDOUT
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except ImportError:
    import json



_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)), *paths)
def main():
    filename = _here('serpextract', 'search_engines.pickle')
    print 'Updating search engine parser definitions (requires PHP).'

    url = urlopen('https://raw.github.com/piwik/piwik/master/core/DataFiles/SearchEngines.php')
    php_script = url.readlines()
    php_script.append('echo(json_encode($GLOBALS["Piwik_SearchEngines"]));\n')
    php_script = ''.join(php_script)
    process = Popen(['php'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    json_string = process.communicate(input=php_script)[0]
    # Ordering of the dictionary from PHP matters so we keep it in an
    # OrderedDict
    piwik_engines = json.loads(json_string, object_pairs_hook=OrderedDict)
    with open(filename, 'w') as file_:
        pickle.dump(piwik_engines, file_)

    print 'Saved {} search engine parser definitions to {}.'.format(len(piwik_engines), filename)


if __name__ == '__main__':
    main()