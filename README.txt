.. Please see the full HTML documentation in the docs/ directory.
..
.. This documentation is used to generate the HTML documentation using docutils:
.. rst2html.py --title="RPC4Django Documentation" --initial-header-level=2 --stylesheet=docs/voidspace.css README.txt > docs/index.html

========================
RPC4Django Documentation
========================

Version: 0.1.7

19 January 2010

.. contents:: **Table of Contents**

Overview
========

RPC4Django is an XMLRPC and JSONRPC server for Django powered projects. Simply plug it into any existing Django project and you can make your methods available via XMLRPC and JSONRPC. In addition, it can display nice documentation about the methods it makes available in a more customizable way than DocXMLRPCServer. 
RPC4Django is not affiliated with the `Django Project <http://djangoproject.com>`_.

Features
--------

- Detects request type (JSONRPC or XMLRPC) based on content
- Easy identification of RPC methods via a decorator
- Pure python and requires no external modules except Django
- Customizable RPC method documentation including `reST <http://docutils.sourceforge.net/rst.html>`_
- Supports XMLRPC and JSONRPC introspection
- Supports method signatures (unlike SimpleXMLRPCServer)
- Easy installation and integration with existing Django projects
- Licensed for inclusion in open source and commercial software
- Ties in with Django's `authentication and authorization <http://docs.djangoproject.com/en/dev/topics/auth>`_


Project Website & More
----------------------

Project Site
%%%%%%%%%%%%

- http://www.davidfischer.name/rpc4django

Demo Sites
%%%%%%%%%%
- http://rpc4django.davidfischer.name
- https://rpcauth.davidfischer.name (user = pass = rpc4django, self signed certificate)

Subversion Repository
%%%%%%%%%%%%%%%%%%%%%

- https://svn.davidfischer.name/rpc4django/trunk (user = pass = rpc4django, self signed certificate)

Contributors
------------
- `David Fischer <mailto:rpc4django@davidfischer.name>`_ (`wish list <http://amzn.com/w/1Z1GLQYQPFBT1>`_)

----

.. include:: LICENSE.txt

----

.. include:: INSTALL.txt

----

.. include:: CONFIGURATION.txt

----

Additional Information and Settings
===================================

Running the Unit Tests
----------------------

All unit tests can be `run <http://docs.djangoproject.com/en/dev/topics/testing/#id1>`_ using ``manage.py``

::

	$> python manage.py test rpc4django
	
Some tests require ``DJANGO_SETTINGS_MODULE`` to be set. The test cases that do not require
the Django environment can be run using the following:

::

	$> python setup.py test

How RPC4Django Handles Requests
-------------------------------

- If the request is a GET request, return an HTML method summary
- A POST request with content-type header set to ``text/xml`` or ``application/xml`` will be processed as XMLRPC
- A POST request with content-type header containing ``json`` or ``javascript`` will be processed as JSONRPC
- Try to parse the POST data as xml. If it parses successfully, process it as XMLRPC
- Process it as JSONRPC


Method Summary
------------------------------

- The method summary displays docstrings, signatures, and names from methods marked with the ``@rpcmethod`` decorator.
- The method summary allows testing of methods via JSONRPC (unless it is disabled)
- The summary is served (unless it is disabled) from a template ``rpc4django/rpcmethod_summary.html`` and can be customized in a similar way to the `django admin <http://docs.djangoproject.com/en/dev/intro/tutorial02/#customize-the-admin-look-and-feel>`_. 
- The method summary supports `reST <http://docutils.sourceforge.net/rst.html>`_ in docstrings if the docutils library is installed. Plain text is used otherwise. ReST warnings and errors are not reported in the output.

Optional Settings
-----------------

These are settings that can go in your project's ``settings.py``:

``RPC4DJANGO_LOG_REQUESTS_RESPONSES=True|False`` (default True)
    By default RPC4Django will log (using the python logging module) all requests and responses. This can be disabled by setting ``RPC4DJANGO_LOG_REQUESTS_RESPONSES=False``.
``RPC4DJANGO_RESTRICT_INTROSPECTION=True|False`` (default False)
    By default RPC4Django registers the standard XMLRPC and JSONRPC introspection functions. This can be disabled by setting ``RPC4DJANGO_RESTRICT_INTROSPECTION=True``.
``RPC4DJANGO_RESTRICT_JSONRPC=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_JSONRPC=True``, RPC4Django will never serve a JSONRPC request. Instead, either XMLRPC will be tried or status code 404 will be returned.
``RPC4DJANGO_RESTRICT_XMLRPC=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_XMLRPC=True``, RPC4Django will never serve an XMLRPC request. Instead, either JSONRPC will be tried or status code 404 will be returned.
``RPC4DJANGO_RESTRICT_METHOD_SUMMARY=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_METHOD_SUMMARY=True``, status code 404 will be returned instead of serving the method summary as a response to a GET request.
``RPC4DJANGO_RESTRICT_RPCTEST=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_RPCTEST=True``, the method summary will not allow testing via JSONRPC.
``RPC4DJANGO_RESTRICT_REST=True|False`` (default False) **[new in 0.1.4]**
    If ``RPC4DJANGO_RESTRICT_REST=True``, RPC4Django does not attempt to convert any of the method summary docstrings to restructured text.
``RPC4DJANGO_HTTP_ACCESS_CREDENTIALS=True|False`` (default False) **[new in 0.1.6]**
    RPC4Django will respond to OPTIONS requests with the HTTP header ``Access-Control-Allow-Credentials`` set to the given value. This pertains to allowing cross site requests with cookies. See the Mozilla documentation on `requests with credentials <https://developer.mozilla.org/en/HTTP_access_control#Requests_with_credentials>`_ for more details.
``RPC4DJANGO_HTTP_ACCESS_ALLOW_ORIGIN=URL|*`` (default empty string) **[new in 0.1.6]**
    RPC4Django will respond to OPTIONS requests with the HTTP header ``Access-Control-Allow-Origin`` set to the given value. This pertains to allowing cross site requests. See the Mozilla documentation on `preflighted requests <https://developer.mozilla.org/en/HTTP_access_control#Preflighted_requests>`_ for more details.


Authentication
--------------

RPC4Django can be used with authenticated HTTP(s) requests and Django's `authentication and authorization <http://docs.djangoproject.com/en/dev/topics/auth>`_. **[new in 0.1.5, requires Django 1.1+]**
It uses `RemoteUserMiddleware <http://docs.djangoproject.com/en/1.1/howto/auth-remote-user/>`_ or another derived middleware which is only built-in to Django 1.1 and higher. It is possible to use it
with Django versions prior to 1.1, but it would require the ``RemoteUserMiddleware`` and the ``RemoteUserBackend`` to be added manually.

Setup
%%%%%

Firstly, the webserver should be configured to use basic HTTP authentication or some sort of single sign on (SSO) solution.

In settings.py, the following changes need to be made:

::

	MIDDLEWARE_CLASSES = (
	    # ...
	    # Must be enabled for RPC4Django authenticated method calls
	    'django.contrib.auth.middleware.AuthenticationMiddleware',
	    
	    # Required for RPC4Django authenticated method calls
	    # Requires Django 1.1+
	    'django.contrib.auth.middleware.RemoteUserMiddleware',
	)
	
	# Required for RPC4Django authenticated method calls
	# Requires Django 1.1+
	AUTHENTICATION_BACKENDS = (
	    'django.contrib.auth.backends.RemoteUserBackend',
	)

Usage
%%%%%

To protect a method, it needs to be defined with the ``@rpcmethod`` decorator and the ``permission`` parameter.

::

	from rpc4django import rpcmethod
	
	@rpcmethod(name='rpc4django.secret', signature=['string'], permission='auth.add_group')
	def secret():
	    return "Successfully called a protected method"

To call an authenticated method from the Python command prompt, use the following:

::

	from xmlrpclib import ServerProxy
	s = ServerProxy('https://username:password@example.com')
	s.rpc4django.secret()

Access to the Request Object
----------------------------

RPC4Django allows RPC methods to be written in such a way that they have
access to Django's HttpRequest_ object. **[new in 0.1.6]** This can be used
to see the type of request, the user making the request or any specific
headers in the request object. To use this, methods must be written such that they can accept arbitrary
keyword arguments. Although currently only the HttpRequest object is sent,
additional keyword arguments may be sent in the future.

.. _HttpRequest: http://docs.djangoproject.com/en/dev/ref/request-response/

::

 @rpcmethod(name='rpc4django.httprequest',signature=['string'])
 def request(**kwargs):
     '''
     Illustrates access to the HttpRequest object
     '''
     
     return str(kwargs.get('request', None))

----

.. include:: TODO.txt

----

.. include:: BUGS.txt

----

.. include:: CHANGELOG.txt
