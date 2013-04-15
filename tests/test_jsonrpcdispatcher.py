# -*- coding: utf-8 -*-

'''
JSON RPC Dispatcher Tests
-------------------------

'''

import unittest
from datetime import datetime
from rpc4django.jsonrpcdispatcher import *

class TestJSONRPCDispatcher(unittest.TestCase):

    def setUp(self):
        def add(a,b):
            return a+b

        def factorial(num):
            if num > 1:
                return num * factorial(num-1)
            else:
                return 1

        def unicode_ret():
            return u'はじめまして'

        def kwargstest(a, b, **kwargs):
            if kwargs.get('c', None) is not None:
                return True
            return False

        self.dispatcher = JSONRPCDispatcher()
        self.dispatcher.register_function(add, 'add')
        self.dispatcher.register_function(factorial, 'fact')
        self.dispatcher.register_function(unicode_ret, 'unicode_ret')
        self.dispatcher.register_function(kwargstest, 'kwargstest')
        self.dispatcher.register_function(lambda: datetime.now(), 'datetest')

    def test_dates(self):
        jsontxt = json.dumps({"method": "datetest", "id": 1, "params": []})
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is not None)

        class MyEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    return super(MyEncoder, self).default(o)
        dispatcher = JSONRPCDispatcher(MyEncoder)
        dispatcher.register_function(lambda: datetime.now(), 'datetest')
        resp = dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(type(jsondict['result']), unicode)
        self.assertEqual(type(datetime.strptime(jsondict['result'], "%Y-%m-%d %H:%M:%S")), datetime)

    def test_jsonrpc_member(self):
        # Demonstrate that the jsondict contains "jsonrpc"
        d = dict()
        d['params'] = [1,2]
        d['method'] = 'kwargstest'
        d['id'] = 1

        jsontxt = json.dumps(d)
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertEqual(jsondict['jsonrpc'], '2.0')

    def test_kwargs(self):
        d = dict()
        d['params'] = [1,2]
        d['method'] = 'kwargstest'
        d['id'] = 1

        jsontxt = json.dumps(d)
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertFalse(jsondict['result'])

        resp = self.dispatcher.dispatch(jsontxt, c=1)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'])

    def test_unicode(self):
        jsontxt = '{"params":[],"method":"unicode_ret","id":1}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 1)
        self.assertEqual(jsondict['result'], u'はじめまして')

        jsontxt = '{"params":["\u306f\u3058\u3081","\u307e\u3057\u3066"],"method":"add","id":2}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 2)
        self.assertEqual(jsondict['result'], u'はじめまして')

    def test_dispatch_success(self):
        jsontxt = '{"params":[1,2],"method":"add","id":1}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 1)
        self.assertEqual(jsondict['result'], 3)

        jsontxt = '{"params":[5],"method":"fact","id":"hello"}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 'hello')
        self.assertEqual(jsondict['result'], 120)

    def test_method_error(self):
        jsontxt = '{"params":["a"],"method":"fact","id":"hello"}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertTrue(jsondict['error'] is not None)

    def test_dispatch_paramserror(self):
        jsontxt = '{"params":[1],"method":"add","id":"4"}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertTrue(jsondict['error'] is not None)

    def test_dispatch_nomethod(self):
        jsontxt = '{"params":[],"method":"add123","id":123}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], 123)
        self.assertTrue(isinstance(jsondict['error'], dict))
        self.assertEqual(jsondict['error'] ['code'], 105)
        self.assertEqual(jsondict['error'] ['message'], 'method "add123" is not supported')

    def test_dispatch_badrequest(self):
        jsontxt = '"params":asdf[14]","method":"add","id":0}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], '')
        self.assertTrue(isinstance(jsondict['error'], dict))
        self.assertEqual(jsondict['error'] ['code'], 101)
        self.assertEqual(jsondict['error'] ['message'], 'JSON decoding error')

        jsontxt = '["should", "be", "a", "Object"]'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], '')
        self.assertTrue(isinstance(jsondict['error'], dict))
        self.assertEqual(jsondict['error'] ['code'], 102)
        self.assertEqual(jsondict['error'] ['message'], 'Cannot decode to a javascript Object')

        jsontxt = '{"params":"shouldbelist","method":"add","id":0}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], 0)
        self.assertTrue(isinstance(jsondict['error'], dict))
        self.assertEqual(jsondict['error'] ['code'], 102)
        self.assertEqual(jsondict['error'] ['message'], 'params must be a javascript Array')

        jsontxt = '{"params":"[]","method":123,"id":42}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], 42)
        self.assertTrue(isinstance(jsondict['error'], dict))
        self.assertEqual(jsondict['error'] ['code'], 102)
        self.assertEqual(jsondict['error'] ['message'], 'method must be a javascript String')

if __name__ == '__main__':
    unittest.main()
