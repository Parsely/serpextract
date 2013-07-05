#!/bin/sh

set -e

# Deploy the module to PyPI
VERSION=`python -c "import serpextract; print serpextract.__version__"`
echo "Deploying serpextract" $VERSION "to PyPI."
echo
python update_list.py
nosetests
TEST_SUCCESSFUL=$?

if [ $TEST_SUCCESSFUL -eq 0 ];then
    echo "Tests succeeded, deploying to PyPI"
    python setup.py sdist upload
else
    echo "Tests failed, fix before deploying."
fi

