'''
Contains methods that are protected by the permission system
'''

from rpc4django import rpcmethod

@rpcmethod(name='rpc4django.secret', signature=['string'], permission='auth.add_group')
def secret():
    '''
    This method is protected by the Django `auth <http://docs.djangoproject.com/en/dev/topics/auth/>`_ system
    
    Calling this method via RPC will return a 403 Forbidden unless the user 
    is logged in and has the correct permissions
    
    Try the following to see that the method is protected:

    ::

        >>> from xmlrpclib import ServerProxy
        >>> s = ServerProxy('https://rpcnoauth:rpcnoauth@rpcauth.davidfischer.name/')
        >>> s.rpc4django.secret()


    '''
    
    return "Successfully called a protected method"