# -*- coding: utf-8 -*-

'''
This other module shows how to import a remote method for the rpc server
'''

from rpc4django import rpcmethod

@rpcmethod(name='rpc4django.introduction', signature=['string'])
def intro():
    '''
    `RPC4Django <http://www.davidfischer.name/rpc4django>`_  
    automatically generated this XMLRPC and JSONRPC method summary.
    
    These methods can be tested using JSONRPC by clicking the method name.
    
    Alternatively, they can be tested using python's xmlrpclib as follows
    
    ::
    
        >>> from xmlrpclib import ServerProxy
        >>> s = ServerProxy('http://rpc4django.davidfischer.name/')
        >>> s.system.listMethods()
    
    Features
    
    - Detects request type (JSONRPC or XMLRPC) based on content
    - Easy identification of RPC methods via a decorator
    - Pure python and requires no external modules except Django
    - Customizable RPC method documentation including `reST <http://docutils.sourceforge.net/rst.html>`_
    - Supports XMLRPC and JSONRPC introspection
    - Supports method signatures (unlike SimpleXMLRPCServer)
    - Easy installation and integration with existing Django projects
    - Licensed for inclusion in open source and commercial software
    - Ties in with Django's `authentication and authorization <http://docs.djangoproject.com/en/dev/topics/auth>`_
    
    This method returns a unicode introduction
    '''
    
    return u'はじめまして'

@rpcmethod(name='view.request')
def request(**kwargs):
    '''
    Illustrates access to the HttpRequest object
    '''
    
    request = kwargs.get('request', None)
    
    if request is not None:
        return str(request)
    else:
        return "No Access"
    