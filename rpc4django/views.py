'''
Views

This module contains the method serve_rpc_request which is intended to
be called from the urls.py module of a 
`django <http://www.djangoproject.com/>`_ project.

It should be called like this from urls.py:

    (r'^RPC2$', 'rpc4django.views.serve_rpc_request'),

'''

import logging
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from rpcdispatcher import RPCDispatcher
from __init__ import version

# these restrictions can change the functionality of rpc4django
# but they are completely optional
# see the rpc4django documentation for more details
LOG_REQUESTS_RESPONSES = getattr(settings,
                                 'RPC4DJANGO_LOG_REQUESTS_RESPONSES', True)
RESTRICT_INTROSPECTION = getattr(settings,
                                 'RPC4DJANGO_RESTRICT_INTROSPECTION', False)
RESTRICT_JSON = getattr(settings, 'RPC4DJANGO_RESTRICT_JSONRPC', False)
RESTRICT_XML = getattr(settings, 'RPC4DJANGO_RESTRICT_XMLRPC', False)
RESTRICT_METHOD_SUMMARY = getattr(settings, 
                                  'RPC4DJANGO_RESTRICT_METHOD_SUMMARY', False)
RESTRICT_RPCTEST = getattr(settings, 'RPC4DJANGO_RESTRICT_RPCTEST', False)
RESTRICT_RPCTEST = getattr(settings, 'RPC4DJANGO_RESTRICT_RPCTEST', False)
HTTP_ACCESS_CREDENTIALS = getattr(settings, 
                                  'RPC4DJANGO_HTTP_ACCESS_CREDENTIALS', False)
HTTP_ACCESS_ALLOW_ORIGIN = getattr(settings, 
                                  'RPC4DJANGO_HTTP_ACCESS_ALLOW_ORIGIN', '')

# get a list of the installed django applications
# these will be scanned for @rpcmethod decorators
APPS = getattr(settings, 'INSTALLED_APPS', [])

def _check_request_permission(request, request_format='xml'):
    '''
    Checks whether this user has permission to perform the specified action
    This method does not check method call validity. That is done later
    
    PARAMETERS
    
    - ``request`` - a django HttpRequest object
    - ``request_format`` - the request type: 'json' or 'xml' 
    
    RETURNS 
    
    True if the request is valid and False if permission is denied
    '''
    
    user = getattr(request, 'user', None)
    methods = dispatcher.list_methods()
    method_name = dispatcher.get_method_name(request.raw_post_data, \
                                             request_format)
    response = True
    
    for method in methods:
        if method.name == method_name:
            # this is the method the user is calling
            # time to check the permissions
            if method.permission is not None:
                logging.debug('Method "%s" is protected by permission "%s"' \
                              %(method.name, method.permission))
                if user is None:
                    # user is only none if not using AuthenticationMiddleware
                    logging.warn('AuthenticationMiddleware is not enabled')
                    response = False
                elif not user.has_perm(method.permission):
                    # check the permission against the permission database
                    logging.info('User "%s" is NOT authorized' %(str(user)))
                    response = False
                else:
                    logging.debug('User "%s" is authorized' %(str(user)))
            else:
                logging.debug('Method "%s" is unprotected' %(method.name))
                
            break
    
    return response
    
def _is_xmlrpc_request(request):
    '''
    Determines whether this request should be served by XMLRPC or JSONRPC
    
    Returns true if this is an XML request and false for JSON
    
    It is based on the following rules:
    
    # If there is no post data, display documentation
    # content-type = text/xml or application/xml => XMLRPC
    # content-type contains json or javascript => JSONRPC
    # Try to parse as xml. Successful parse => XMLRPC
    # JSONRPC
    '''
    
    conttype = request.META.get('CONTENT_TYPE', 'unknown type')
    
    # check content type for obvious clues
    if conttype == 'text/xml' or conttype == 'application/xml':
        return True
    elif conttype.find('json') >= 0 or conttype.find('javascript') >= 0:
        return False
    
    if LOG_REQUESTS_RESPONSES:
        logging.info('Unrecognized content-type "%s"' %conttype)
        logging.info('Analyzing rpc request data to get content type')
    
    # analyze post data to see whether it is xml or json
    # this is slower than if the content-type was set properly
    try:
        parseString(request.raw_post_data)
        return True
    except ExpatError:
        pass
    
    return False

def serve_rpc_request(request):
    '''
    This method handles rpc calls based on the content type of the request
    '''

    if request.method == "POST" and len(request.POST) > 0:
        # Handle POST request with RPC payload
        
        if LOG_REQUESTS_RESPONSES:
            logging.debug('Incoming request: %s' %str(request.raw_post_data))
            
        if _is_xmlrpc_request(request):
            if RESTRICT_XML:
                raise Http404
            
            if not _check_request_permission(request, 'xml'):
                return HttpResponseForbidden()
            
            resp = dispatcher.xmldispatch(request.raw_post_data, \
                                          request=request)
            response_type = 'text/xml'
        else:
            if RESTRICT_JSON:
                raise Http404
            
            if not _check_request_permission(request, 'json'):
                return HttpResponseForbidden()
            
            resp = dispatcher.jsondispatch(request.raw_post_data, \
                                           request=request)
            response_type = 'application/json'
            
        if LOG_REQUESTS_RESPONSES:
            logging.debug('Outgoing %s response: %s' %(response_type, resp))
        
        return HttpResponse(resp, response_type)
    elif request.method == 'OPTIONS':
        # Handle OPTIONS request for "preflighted" requests
        # see https://developer.mozilla.org/en/HTTP_access_control
        
        response = HttpResponse('', 'text/plain')
        
        origin = request.META.get('HTTP_ORIGIN', 'unknown origin')
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response['Access-Control-Max-Age'] = 0
        response['Access-Control-Allow-Credentials'] = \
                        str(HTTP_ACCESS_CREDENTIALS).lower()
        response['Access-Control-Allow-Origin']= HTTP_ACCESS_ALLOW_ORIGIN
        
        response['Access-Control-Allow-Headers'] = \
                    request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', '')
                    
        if LOG_REQUESTS_RESPONSES:
            logging.debug('Outgoing HTTP access response to: %s' %(origin))
                    
        return response
    else:
        # Handle GET request
        
        if RESTRICT_METHOD_SUMMARY:
            # hide the documentation by raising 404
            raise Http404
        
        # show documentation
        methods = dispatcher.list_methods()
        template_data = {
            'methods': methods,
            'url': URL,
            
            # rpc4django version
            'version': version(),
            
            # restricts the ability to test the rpc server from the docs
            'restrict_rpctest': RESTRICT_RPCTEST,
        }
        return render_to_response('rpc4django/rpcmethod_summary.html', \
                                  template_data)

# reverse the method for use with system.describe and ajax
try:
    URL = reverse(serve_rpc_request)
except NoReverseMatch:
    URL = ''
    
# exclude from the CSRF framework because RPC is intended to be used cross site
try:
    # Django 1.2
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    try:
        # Django 1.1
        from django.contrib.csrf.middleware import csrf_exempt
    except ImportError:
        # Django 1.0
        csrf_exempt = None

if csrf_exempt is not None:
    serve_rpc_request = csrf_exempt(serve_rpc_request)

    
# instantiate the rpcdispatcher -- this examines the INSTALLED_APPS
# for any @rpcmethod decorators and adds them to the callable methods
dispatcher = RPCDispatcher(URL, APPS, RESTRICT_INTROSPECTION) 
