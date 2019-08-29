#!/usr/bin/env python

import os
import subprocess
import sys

# Handle incompatible versions of Python & Django
# https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django
SUPPORTED_VERSIONS = {
    '2.7': ('Django<1.9', 'Django<1.10', 'Django<1.11', 'Django<1.12', 'Django<2'),
    '3.4': ('Django<1.9', 'Django<1.10', 'Django<1.11', 'Django<1.12', 'Django<2.1'),
    '3.5': ('Django<1.9', 'Django<1.10', 'Django<1.11', 'Django<1.12', 'Django<2.3'),
    '3.6': ('Django<2.3'),
    '3.7': ('Django<2.3'),
}

python_version = os.environ.get('TRAVIS_PYTHON_VERSION')
django_version = os.environ.get('DJANGO_VERSION')

if not python_version:
    sys.exit(u'Unknown python version: {}'.format(python_version))
if not django_version:
    sys.exit(u'Unknown django version: {}'.format(django_version))

if python_version in SUPPORTED_VERSIONS:
    # If the version of Django is not supported with this version of
    # Python simply exit the tests with a success
    if django_version not in SUPPORTED_VERSIONS[python_version]:
        print(u'Incompatible Python/Django versions - ignoring')
    else:
        p = subprocess.Popen(['python', 'setup.py', 'test'])
        p.communicate()
        sys.exit(p.returncode)
else:
    sys.exit(u'Unsupported python version: {}'.format(python_version))
