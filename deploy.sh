#!/bin/sh

set -e

# Deploy the module to PyPI
VERSION=`python -c "import serpextract; print(serpextract.__version__)"`
echo "Deploying serpextract" $VERSION "to PyPI."
echo
read -p "Did you update the pickles for Python 2 and 3? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    nosetests
    TEST_SUCCESSFUL=$?

    if [ $TEST_SUCCESSFUL -eq 0 ];then
        echo "Tests succeeded, deploying to PyPI"
        python setup.py sdist upload
    else
        echo "Tests failed, fix before deploying."
    fi
else
    echo "You must update the pickles before deploying. "
    echo "You'll need a Python 2 and a Python 3 virtualenv setup to do this."
fi
