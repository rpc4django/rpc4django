import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.util import convert_path

# Get __version__ without loading rpc4django module
main_ns = {}
version_path = convert_path('rpc4django/version.py')
with open(version_path) as version_file:
    exec(version_file.read(), main_ns)


# setup.py should run from the directory where it is
package_dir = os.path.dirname(__file__)
if package_dir != '':
    os.chdir(package_dir)

long_description = """========================
RPC4Django Documentation
========================

""" + open('docs/setup.txt').read()

setup(
    name='rpc4django',
    version=main_ns['__version__'],
    description='Handles JSONRPC and XMLRPC requests easily with Django',
    long_description=long_description,
    author='David Fischer',
    author_email='djfische@gmail.com',
    url='https://github.com/rpc4django/rpc4django',
    license='BSD',
    platforms=['OS Independent'],
    packages=[
        'rpc4django',
        'rpc4django.templatetags',
    ],
    package_data={
        'rpc4django': [
            'templates/rpc4django/rpcmethod_summary.html',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires=['Django>=1.9', 'defusedxml'],
    extras_require={
        "reST": ['docutils >= 0.4'],
    },

    # templates packaged into eggs cannot be loaded unless TEMPLATE_LOADER
    # django.template.loaders.eggs.load_template_source
    # is specifically enabled.
    # By setting zip_safe=False, setuptools will unpack the egg
    zip_safe=False,

    test_suite='tests',
)
