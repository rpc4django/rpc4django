'''
RPC4Django
----------

An XMLRPC and JSONRPC server packaged as a Django application

Copyright (c) 2009 - 2010, David Fischer

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, 
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation 
  and/or other materials provided with the distribution.
- Neither the name of rpc4django nor the names of its contributors may be 
  used to endorse or promote products derived from this software without 
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY David Fischer ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL David Fischer BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from rpcdispatcher import RPCDispatcher, rpcmethod

_MAJOR = 0
_MINOR = 1
_PATCH = 7

__author__ = 'David Fischer'
__author_email__ = 'rpc4django@davidfischer.name'
__modulename__ = 'rpc4django'
__description__ = 'Handles JSONRPC and XMLRPC requests easily with Django'
__url__ = 'http://www.davidfischer.name/rpc4django'
__version__ = str(_MAJOR) + '.' + str(_MINOR) + '.' + str(_PATCH)


def version():
    '''
    Returns a string representation of the version
    '''
    return __version__


def version_tuple():
    '''
    Returns a 3-tuple of ints that represent the version
    '''
    return (_MAJOR, _MINOR, _PATCH)
