#!/bin/bash
set -ev

# Handle incompatible versions of Python & Django
if ([ $TRAVIS_PYTHON_VERSION == '3.3' ] && [ $DJANGO == 'Django<1.10' ])
then
    exit 0
else
    python setup.py test
fi
