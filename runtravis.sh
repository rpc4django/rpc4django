#!/bin/bash
set -ev
if [ $TRAVIS_PYTHON_VERSION == '2.6' ] && ([ $DJANGO == 'Django<1.8' ] || [ $DJANGO == 'Django<1.9' ])
then 
   exit 0 
elif ([ $TRAVIS_PYTHON_VERSION == '3.3'] || [ $TRAVIS_PYTHON_VERSION == '3.4' ]) && \ 
    ([ $DJANGO == 'Django<1.4' ] || [ $DJANGO == 'Django<1.5' ])
then
    exit 0
else
    python setup.py test
fi
