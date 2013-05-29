'''
XML RPC Dispatcher Tests
-------------------------

'''

import unittest
from rpc4django.xmlrpcdispatcher import *

try:
    from xmlrpclib import loads, dumps
except ImportError:
    from xmlrpc.client import loads, dumps


class TestXMLRPCDispatcher(unittest.TestCase):

    def setUp(self):
        def kwargstest(a, b, **kwargs):
            if kwargs.get('c', None) is not None:
                return True
            return False

        self.dispatcher = XMLRPCDispatcher()
        self.dispatcher.register_function(kwargstest, 'kwargstest')

    def test_kwargs(self):
        xml = dumps((1,2), 'kwargstest')
        ret = self.dispatcher.dispatch(xml)
        out, name = loads(ret)
        self.assertFalse(out[0])

        ret = self.dispatcher.dispatch(xml, c=1)
        out, name = loads(ret)
        self.assertTrue(out[0])


if __name__ == '__main__':
    unittest.main()
