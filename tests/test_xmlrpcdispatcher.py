'''
XML RPC Dispatcher Tests
-------------------------

'''

import unittest
from django.core.exceptions import ImproperlyConfigured
from decimal import Decimal


try:
    from rpc4django.xmlrpcdispatcher import XMLRPCDispatcher
except ImproperlyConfigured:
    # Configure Django settings if not already configured
    from django.conf import settings
    settings.configure(DEBUG=True)
    from rpc4django.xmlrpcdispatcher import XMLRPCDispatcher

try:
    from xmlrpclib import loads, dumps, Fault
except ImportError:
    from xmlrpc.client import loads, dumps, Fault


class TestXMLRPCDispatcher(unittest.TestCase):

    def setUp(self):
        def echotest(a):
            return a

        def kwargstest(a, b, **kwargs):
            if kwargs.get('c', None) is not None:
                return True
            return False
        
        def withoutargstest():
            return True
        
        def requestargtest(request,a):
            return request

        self.dispatcher = XMLRPCDispatcher()
        self.dispatcher.register_function(echotest, 'echotest')
        self.dispatcher.register_function(kwargstest, 'kwargstest')
        self.dispatcher.register_function(requestargtest, 'requestargtest')
        self.dispatcher.register_function(withoutargstest, 'withoutargstest')
        self.dispatcher.register_multicall_functions()
        
    def test_kwargs(self):
        xml = dumps((1, 2), 'kwargstest')
        ret = self.dispatcher.dispatch(xml)
        out, name = loads(ret)
        self.assertFalse(out[0])

        ret = self.dispatcher.dispatch(xml, c=1)
        out, name = loads(ret)
        self.assertTrue(out[0])
        
        xml = dumps((1,),'requestargtest')
        ret = self.dispatcher.dispatch(xml, request=True)
        out, name = loads(ret)
        self.assertTrue(out[0])
        
        xml = """<?xml version='1.0'?>
<methodCall>
<methodName>withoutargstest</methodName>
<params>
</params>
</methodCall>
        """
        ret = self.dispatcher.dispatch(xml, request='fakerequest')
        out, name = loads(ret)
        self.assertTrue(out[0])
        

    def test_billion_laughs(self):
        payload = """<?xml version="1.0"?>
<!DOCTYPE lolz [
<!ENTITY lol "lol">
<!ELEMENT lolz (#PCDATA)>
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
<!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
<!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
<!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
<!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
<!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>"""

        ret = self.dispatcher.dispatch(payload)
        self.assertRaises(Fault, loads, ret)

    def test_decimal(self):
        d = Decimal('1.23456')
        xml = dumps((d,), 'echotest')
        ret = self.dispatcher.dispatch(xml)
        out, name = loads(ret)
        self.assertEqual(d, out[0])
        self.assertTrue(isinstance(out[0], Decimal))
    
                                        
if __name__ == '__main__':
    unittest.main()
