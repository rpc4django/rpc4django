RPC4Django
==========

.. image:: https://travis-ci.org/rpc4django/rpc4django.svg
    :target: https://travis-ci.org/rpc4django/rpc4django


Prerequisites
-------------

- Python_ 2.7, 3.3+
- Django_ 1.8+
- DefusedXML_
- Docutils_ (optional)

.. _Python: http://www.python.org
.. _Django: http://www.djangoproject.com
.. _DefusedXML: https://pypi.python.org/pypi/defusedxml
.. _Docutils: http://docutils.sourceforge.net


Installation
------------

::

    pip install rpc4django[reST]


Configuration
-------------

1. First, you need to add new url pattern to your root ``urls.py`` file.
   You can replace ``r'^RPC2$'`` with anything you like.

    ::
    
        # urls.py
        from rpc4django.views import serve_rpc_request

        urlpatterns = patterns('',
            # rpc4django will need to be in your Python path
            (r'^RPC2$', serve_rpc_request),
        )

2. Second, add RPC4Django to the list of installed applications in your
   ``settings.py``.

    ::
    
        # settings.py

        INSTALLED_APPS = (
            'rpc4django',
        )

3. Lastly, you need to let RPC4Django know which methods to make available.
   RPC4Django recursively imports all the apps in ``INSTALLED_APPS``
   and makes any methods importable via ``__init__.py`` with the
   `@rpcmethod` decorator available as RPC methods. You can always write
   your RPC methods in another module and simply import it in ``__init__.py``.

    ::
    
        # testapp/__init__.py

        from rpc4django import rpcmethod

        # The doc string supports reST if docutils is installed
        @rpcmethod(name='mynamespace.add', signature=['int', 'int', 'int'])
        def add(a, b):
            '''Adds two numbers together
            >>> add(1, 2)
            3
            '''

            return a+b

4. For additional information, `read the docs`_

.. _read the docs: https://rpc4django.readthedocs.org

