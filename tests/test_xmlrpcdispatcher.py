'''
XML RPC Dispatcher Tests
-------------------------

'''

import unittest
from django.core.exceptions import ImproperlyConfigured


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
        def kwargstest(a, b, **kwargs):
            if kwargs.get('c', None) is not None:
                return True
            return False

        self.dispatcher = XMLRPCDispatcher()
        self.dispatcher.register_function(kwargstest, 'kwargstest')

    def test_kwargs(self):
        xml = dumps((1, 2), 'kwargstest')
        ret = self.dispatcher.dispatch(xml)
        out, name = loads(ret)
        self.assertFalse(out[0])

        ret = self.dispatcher.dispatch(xml, c=1)
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


if __name__ == '__main__':
    unittest.main()
