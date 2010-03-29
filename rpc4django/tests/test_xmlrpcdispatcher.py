'''
XML RPC Dispatcher Tests
-------------------------

'''

import unittest
import xmlrpclib
from rpc4django.xmlrpcdispatcher import *

class TestXMLRPCDispatcher(unittest.TestCase):

    def setUp(self):
        def kwargstest(a, b, **kwargs):
            if kwargs.get('c', None) is not None:
                return True
            return False
        
        self.dispatcher = XMLRPCDispatcher()
        self.dispatcher.register_function(kwargstest, 'kwargstest')

    def test_kwargs(self):
        xml = xmlrpclib.dumps((1,2), 'kwargstest')
        ret = self.dispatcher.dispatch(xml)
        out, name = xmlrpclib.loads(ret)
        self.assertFalse(out[0])
        
        ret = self.dispatcher.dispatch(xml, c=1)
        out, name = xmlrpclib.loads(ret)
        self.assertTrue(out[0])
        
if __name__ == '__main__':
    unittest.main()
