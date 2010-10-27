import os
import shutil
import sys
import zipfile
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
from distutils.core import Command
from subprocess import Popen, PIPE
from unittest import TextTestRunner, TestLoader

try:
    from setuptools import setup
except:
    from distutils.core import setup

import rpc4django
import rpc4django.tests

cmdclasses = dict()

loader = TestLoader()
tests = loader.loadTestsFromModule(rpc4django.tests)

class EasyCommand(Command):
    """
    Other commands extend this one
    """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass

class TestCommand(EasyCommand):
    """
    Runs the unit tests for rpc4django
    """
    
    def run(self):
        '''
        Runs tests from rpc4django.tests
        '''

        t = TextTestRunner()
        t.run(tests)

cmdclasses['test'] = TestCommand

class CleanCommand(EasyCommand):
    """
    Cleans all intermediate files from the build directory
    """

    def remove(self, path):
        """
        Removes 'path' and prints a message if it exists
        """

        if os.path.isfile(path):
            print 'Removing file %s' %path
            os.remove(path)
        elif os.path.isdir(path):
            print 'Removing directory %s' %path
            shutil.rmtree(path)

    def run(self):
        '''
        Removes intermediate files
        '''

        self.remove('docs/_build/html')
        self.remove('dist')
        self.remove('build')
        self.remove('rpc4django.egg-info')
        self.remove('rpc4django.diff')

cmdclasses['clean'] = CleanCommand


## BEGIN DJANGO CODE ##
# This code below is directly stolen from the Django setup.py:
#
#     Copyright (c) Django Software Foundation and individual contributors.
#     All rights reserved.
#     
#     Redistribution and use in source and binary forms, with or without modification,
#     are permitted provided that the following conditions are met:
#     
#         1. Redistributions of source code must retain the above copyright notice,
#            this list of conditions and the following disclaimer.
#        
#         2. Redistributions in binary form must reproduce the above copyright
#            notice, this list of conditions and the following disclaimer in the
#            documentation and/or other materials provided with the distribution.
#     
#         3. Neither the name of Django nor the names of its contributors may be used
#            to endorse or promote products derived from this software without
#            specific prior written permission.
#     
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#     ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#     WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#     ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#     (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#     LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#     ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#     (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#     SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific fix
    # for this in distutils.command.install_data#306. It fixes install_lib but not
    # install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to the
        # fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses['install_data'] = osx_install_data
else:
    cmdclasses['install_data'] = install_data 
    
# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

## END DJANGO CODE ##

# setup.py should run from the directory where it is
package_dir = os.path.dirname(__file__)
if package_dir != '':
    os.chdir(package_dir)
    
long_description = """========================
RPC4Django Documentation
========================

""" + open('docs/setup.txt').read()

setup(
      name = rpc4django.__modulename__,
      version = rpc4django.version(),
      description = rpc4django.__description__,
      long_description = long_description,
      author = rpc4django.__author__,
      author_email = rpc4django.__author_email__,
      url = rpc4django.__url__,
      download_url = rpc4django.__url__,
      license = 'BSD',
      platforms = ['OS Independent'],
      packages = ['rpc4django', 
                  'rpc4django.tests', 
                  'rpc4django.tests.testmod', 
                  'rpc4django.tests.testmod.testsubmod', 
                  'rpc4django.templatetags',
                 ],
      data_files = [('rpc4django/templates/rpc4django', 
                     ['rpc4django/templates/rpc4django/rpcmethod_summary.html'])],
      cmdclass = cmdclasses,
      classifiers = [
                     'Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     
      ],
      
      # templates packaged into eggs cannot be loaded unless TEMPLATE_LOADER
      # django.template.loaders.eggs.load_template_source
      # is specifically enabled.
      # By setting zip_safe=False, setuptools will unpack the egg
      zip_safe = False,
)
