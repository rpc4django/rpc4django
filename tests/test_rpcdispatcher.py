# -*- coding: utf-8 -*-

'''
RPC Dispatcher Tests
--------------------

'''

import base64
import json
import unittest
from xml.dom.minidom import parseString
from rpc4django.rpcdispatcher import rpcmethod, RPCMethod, RPCDispatcher

try:
    from xmlrpclib import Fault, Binary
except ImportError:
    from xmlrpc.client import Fault, Binary

BINARY_STRING = b'\x97\xd2\xab\xc8\xfc\x98\xad'


# tests both the class and the decorator
class TestRPCMethod(unittest.TestCase):
    def setUp(self):
        @rpcmethod(name='my.add', signature=['int', 'int', 'int'])
        def add(a, b):
            return a + b
        self.add = RPCMethod(add)

        @rpcmethod()
        def test1(arg1):
            return 4
        self.test1 = RPCMethod(test1)

    def test_verify_creation(self):
        self.assertEqual(self.add.name, 'my.add')
        self.assertEqual(self.add.signature, ['int', 'int', 'int'])
        self.assertEqual(self.add.args, ['a', 'b'])

        self.assertEqual(self.test1.name, 'test1')
        self.assertEqual(self.test1.signature, ['object', 'object'])
        self.assertEqual(self.test1.args, ['arg1'])

    def test_get_retrunvalue(self):
        self.assertEqual(self.add.get_returnvalue(), 'int')
        self.assertEqual(self.test1.get_returnvalue(), 'object')

    def test_get_params(self):
        self.assertEqual(self.add.get_params(), [{'name': 'a', 'rpctype': 'int'}, {'name': 'b', 'rpctype': 'int'}])
        self.assertEqual(self.test1.get_params(), [{'name': 'arg1', 'rpctype': 'object'}])


class TestRPCDispatcher(unittest.TestCase):
    def setUp(self):
        self.d = RPCDispatcher()

        def add(a, b):
            return a + b

        self.add = add

        def kwargstest(a, b, **kwargs):
            if kwargs.get('c', None) is not None:
                return True
            return False

        self.kwargstest = kwargstest

        def testBin():
            return Binary(BINARY_STRING)
        self.testBin = testBin

    def test_rpcfault(self):
        try:
            self.d.system_methodhelp('method.DoesNotExist.AtAll')
            self.fail('method not exists fault expected!')
        except Fault:
            pass

        try:
            self.d.system_methodsignature('method.DoesNotExist.AtAll')
            self.fail('method not exists fault expected!')
        except Fault:
            pass

    def test_listmethods(self):
        resp = self.d.system_listmethods()
        self.assertEqual(resp, ['system.describe', 'system.listMethods', 'system.methodHelp', 'system.methodSignature'])

        self.d.register_method(self.add)
        resp = self.d.system_listmethods()
        self.assertEqual(resp, ['add', 'system.describe', 'system.listMethods', 'system.methodHelp', 'system.methodSignature'])

    def test_methodhelp(self):
        resp = self.d.system_methodhelp('system.methodHelp')
        self.assertEqual(resp, 'Returns documentation for a specified method')

    def test_methodsignature(self):
        resp = self.d.system_methodsignature('system.listMethods')
        self.assertEqual(resp, ['array'])

        resp = self.d.system_methodsignature('system.methodSignature')
        self.assertEqual(resp, ['array', 'string'])

    def test_xmlrpc_call(self):
        xml = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        expresp = "<?xml version='1.0'?><methodResponse><params><param><value><array><data><value><string>system.describe</string></value><value><string>system.listMethods</string></value><value><string>system.methodHelp</string></value><value><string>system.methodSignature</string></value></data></array></value></param></params></methodResponse>"
        resp = self.d.xmldispatch(xml.encode('utf-8'))
        self.assertEqual(resp.replace('\n', ''), expresp)

    def test_unicode_call(self):
        self.d.register_method(self.add)
        s1 = u'は'
        s2 = u'じめまして'
        xml = u'<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><string>%s</string></value></param><param><value><string>%s</string></value></param></params></methodCall>' % (s1, s2)
        resp = self.d.xmldispatch(xml.encode('utf-8'))
        dom = parseString(resp)
        retval = dom.getElementsByTagName('string')[0].firstChild.data
        self.assertEqual(retval, u'はじめまして')

    def test_base64_call(self):
        self.d.register_method(self.testBin)

        xml = '<?xml version="1.0"?><methodCall><methodName>testBin</methodName><params></params></methodCall>'
        resp = self.d.xmldispatch(xml.encode('utf-8'))
        dom = parseString(resp)
        retval = dom.getElementsByTagName('base64')[0].firstChild.data
        self.assertEqual(base64.b64decode(retval), BINARY_STRING)

    def test_jsonrpc_call(self):
        jsontxt = '{"params":[],"method":"system.listMethods","id":1}'
        resp = self.d.jsondispatch(jsontxt.encode('utf-8'))
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 1)
        self.assertTrue(isinstance(jsondict['result'], list))

    def test_register_method(self):
        self.d.register_method(self.add)

        jsontxt = '{"params":[1,2],"method":"add","id":1}'
        resp = self.d.jsondispatch(jsontxt.encode('utf-8'))
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 1)
        self.assertEqual(jsondict['result'], 3)

    def test_kwargs(self):
        self.d.register_method(self.kwargstest)

        jsontxt = '{"params":[1,2],"method":"kwargstest","id":1}'
        resp = self.d.jsondispatch(jsontxt.encode('utf-8'))
        jsondict = json.loads(resp)
        self.assertFalse(jsondict['result'])

        resp = self.d.jsondispatch(jsontxt.encode('utf-8'), c=1)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'])

if __name__ == '__main__':
    unittest.main()
