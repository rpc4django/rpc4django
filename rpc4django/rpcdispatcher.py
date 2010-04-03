'''
RPC Dispatcher
--------------

This module contains the classes necessary to handle both
`jsonrpc <http://json-rpc.org/>`_ and 
`xmlrpc <http://www.xmlrpc.com/>`_ requests. 
It also contains a decorator to mark methods as rpc methods.
'''

import inspect
import platform
import pydoc
import types
import xmlrpclib
from xmlrpclib import Fault
from jsonrpcdispatcher import JSONRPCDispatcher, json
from xmlrpcdispatcher import XMLRPCDispatcher

# this error code is taken from xmlrpc-epi
# http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php
APPLICATION_ERROR = -32500

def rpcmethod(**kwargs):
    '''
    Accepts keyword based arguments that describe the method's rpc aspects

    EXAMPLES:
    @rpcmethod()
    @rpcmethod(name='myns.myFuncName', signature=['int','int'])
    @rpcmethod(permission='add_group')
    '''
    
    def set_rpcmethod_info(method):
        method.is_rpcmethod = True
        method.signature = []
        method.permission = None
        method.external_name = getattr(method, '__name__')

        if 'name' in kwargs:
            method.external_name = kwargs['name']

        if 'signature' in kwargs:
            method.signature = kwargs['signature']
            
        if 'permission' in kwargs:
            method.permission = kwargs['permission']

        return method
    return set_rpcmethod_info

class RPCMethod:
    '''
    A method available via the rpc dispatcher
    '''
    
    def __init__(self, method, name=None, signature=None, docstring=None):
        self.method = method
        self.help = ''
        self.signature = []
        self.name = ''
        self.permission = None
        self.args = []
        
        # set the method name based on @rpcmethod or the passed value
        # default to the actual method name
        if hasattr(method, 'external_name'):
            self.name = method.external_name
        elif name is not None:
            self.name = name
        else:
            self.name = method.func_name
            
        # get the help string for each method
        if docstring is not None:
            self.help = docstring
        else:
            self.help = pydoc.getdoc(method)
            
        # set the permissions based on the decorator
        self.permission = getattr(method, 'permission', None)
            
        # use inspection (reflection) to get the arguments
        args, varargs, keywords, defaults = inspect.getargspec(method)
        self.args = [arg for arg in args if arg != 'self']
        self.signature = ['object' for arg in self.args]
        self.signature.insert(0, 'object')
        
        if hasattr(method, 'signature') and \
             len(method.signature) == len(self.args) + 1:
            # use the @rpcmethod signature if it has the correct
            # number of args
            self.signature = method.signature
        elif signature is not None and len(self.args) + 1 == len(signature):
            # use the passed signature if it has the correct number
            # of arguments
            self.signature = signature
           
    def get_stub(self):
        '''
        Returns a stub json for an jsonrpc request for this method
        '''
        
        params = self.get_params()
        plist = ['"' + param['name'] + '"' for param in params]
            
        jsonlist = [
                   '{',
                   '"id": "djangorpc",',
                   '"method": "' + self.name + '",',
                   '"params": [',
                   '   ' + ','.join(plist),
                   ']',
                   '}',
        ]
        
        return '\n'.join(jsonlist)
                
    def get_returnvalue(self):
        '''
        Returns the return value which is the first element of the signature
        '''
        if len(self.signature) > 0:
            return self.signature[0]
        return None
        
    def get_params(self):
        '''
        Returns a list of dictionaries containing name and type of the params
        
        eg. [{'name': 'arg1', 'rpctype': 'int'}, 
             {'name': 'arg2', 'rpctype': 'int'}]
        '''
        if len(self.signature) > 0:
            arglist = []
            if len(self.signature) == len(self.args) + 1:
                for argnum in range(len(self.args)):
                    arglist.append({'name': self.args[argnum], \
                                    'rpctype': self.signature[argnum+1]})
                return arglist
            else:
                # this should not happen under normal usage
                for argnum in range(len(self.args)):
                    arglist.append({'name': self.args[argnum], \
                                    'rpctype': 'object'})
                return arglist
        return []


class RPCDispatcher:
    '''
    Dispatches method calls to either the xmlrpc or jsonrpc dispatcher
    '''
    
    def __init__(self, url='', apps=[], restrict_introspection=False):
        version = platform.python_version_tuple()
        self.url = url
        self.rpcmethods = []        # a list of RPCMethod objects
        self.jsonrpcdispatcher = JSONRPCDispatcher()
        self.xmlrpcdispatcher = XMLRPCDispatcher()
            
        if not restrict_introspection:
            self.register_method(self.system_listmethods)
            self.register_method(self.system_methodhelp)
            self.register_method(self.system_methodsignature)
            self.register_method(self.system_describe)
            
        self.register_rpcmethods(apps)
        
    @rpcmethod(name='system.describe', signature=['struct'])
    def system_describe(self):
        '''
        Returns a simple method description of the methods supported
        '''
        
        description = {}
        description['serviceType'] = 'RPC4Django JSONRPC+XMLRPC'
        description['serviceURL'] = self.url,
        description['methods'] = [{'name': method.name, 
                                   'summary': method.help, 
                                   'params': method.get_params(),
                                   'return': method.get_returnvalue()} \
                                  for method in self.rpcmethods]
        
        return description
    
    @rpcmethod(name='system.listMethods', signature=['array'])
    def system_listmethods(self):
        '''
        Returns a list of supported methods
        '''
        
        methods = [method.name for method in self.rpcmethods]
        methods.sort()
        return methods
    
    @rpcmethod(name='system.methodHelp', signature=['string', 'string'])
    def system_methodhelp(self, method_name):
        '''
        Returns documentation for a specified method
        '''
        
        for method in self.rpcmethods:
            if method.name == method_name:
                return method.help
            
        # this differs from what implementation in SimpleXMLRPCServer does
        # this will report via a fault or error while SimpleXMLRPCServer
        # just returns an empty string
        raise Fault(APPLICATION_ERROR, 'No method found with name: ' + \
                    str(method_name))
          
    @rpcmethod(name='system.methodSignature', signature=['array', 'string'])
    def system_methodsignature(self, method_name):
        '''
        Returns the signature for a specified method 
        '''
        
        for method in self.rpcmethods:
            if method.name == method_name:
                return method.signature
        raise Fault(APPLICATION_ERROR, 'No method found with name: ' + \
                    str(method_name))
               
    def register_rpcmethods(self, apps):
        '''
        Scans the installed apps for methods with the rpcmethod decorator
        Adds these methods to the list of methods callable via RPC
        '''    
        
        for appname in apps:
            # check each app for any rpcmethods
            app = __import__(appname, globals(), locals(), ['*'])
            for obj in dir(app):
                method = getattr(app, obj)
                if callable(method) and \
                   hasattr(method, 'is_rpcmethod'):
                    # if this method is callable and it has the rpcmethod
                    # decorator, add it to the dispatcher
                    self.register_method(method, method.external_name)
                elif isinstance(method, types.ModuleType):
                    # if this is not a method and instead a sub-module,
                    # scan the module for methods with @rpcmethod
                    try:
                        self.register_rpcmethods(["%s.%s" % (appname, obj)])
                    except ImportError:
                        pass

    
    def jsondispatch(self, raw_post_data, **kwargs):
        '''
        Sends the post data to a jsonrpc processor
        '''
        
        return self.jsonrpcdispatcher.dispatch(raw_post_data, **kwargs)
    
    def xmldispatch(self, raw_post_data, **kwargs):
        '''
        Sends the post data to an xmlrpc processor
        '''
        
        return self.xmlrpcdispatcher.dispatch(raw_post_data, **kwargs)
        
    def get_method_name(self, raw_post_data, request_format='xml'):
        '''
        Gets the name of the method to be called given the post data
        and the format of the data
        '''
        
        if request_format == 'xml':
            # xmlrpclib.loads could throw an exception, but this is fine
            # since _marshaled_dispatch would throw the same thing
            try:
                params, method = xmlrpclib.loads(raw_post_data)
                return method
            except Fault:
                return None
        else:
            try:
                # attempt to do a json decode on the data
                jsondict = json.loads(raw_post_data)
                if not isinstance(jsondict, dict) or 'method' not in jsondict:
                    return None
                else:
                    return jsondict['method']
            except ValueError:
                return None
        
    def list_methods(self):
        '''
        Returns a list of RPCMethod objects supported by the server
        '''
        
        return self.rpcmethods
    
    def register_method(self, method, name=None, signature=None, helpmsg=None):
        '''
        Registers a method with the rpc server
        '''

        meth = RPCMethod(method, name, signature, helpmsg)
        
        if meth.name not in self.system_listmethods():
            self.xmlrpcdispatcher.register_function(method, meth.name)
            self.jsonrpcdispatcher.register_function(method, meth.name)
            self.rpcmethods.append(meth)
    
