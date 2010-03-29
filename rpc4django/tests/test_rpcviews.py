'''
Views Tests
-------------------------

'''

import unittest
import xmlrpclib
from django.test.client import Client
from rpc4django.jsonrpcdispatcher import json, JSONRPC_SERVICE_ERROR

RPCPATH = '/RPC2'

class TestRPCViews(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_methodsummary(self):
        response = self.client.get(RPCPATH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'rpc4django/rpcmethod_summary.html')
    
    def test_xmlrequests(self):
        data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        response = self.client.post(RPCPATH, data, 'text/xml')
        self.assertEqual(response.status_code, 200)
        xmlrpclib.loads(response.content)       # this will throw an exception with bad data
        
    def test_jsonrequests(self):
        data = '{"params":[],"method":"system.listMethods","id":123}'
        response = self.client.post(RPCPATH, data, 'application/json')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 123)
        self.assertTrue(isinstance(jsondict['result'], list))
        
        data = '{"params":[],"method":"system.describe","id":456}'
        response = self.client.post(RPCPATH, data, 'text/javascript')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 456)
        self.assertTrue(isinstance(jsondict['result'], dict))
        
    def test_typedetection(self):
        data = '{"params":[],"method":"system.listMethods","id":123}'
        response = self.client.post(RPCPATH, data, 'text/plain')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is None)
        self.assertEqual(jsondict['id'], 123)
        self.assertTrue(isinstance(jsondict['result'], list))
        
        data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        response = self.client.post(RPCPATH, data, 'text/plain')
        self.assertEqual(response.status_code, 200)
        xmlrpclib.loads(response.content)       # this will throw an exception with bad data
        
        # jsonrpc request with xmlrpc data (should be error)
        data = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        response = self.client.post(RPCPATH, data, 'application/json')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['id'], '')
        self.assertTrue(isinstance(jsondict['error'], dict))
        
        data = '{"params":[],"method":"system.listMethods","id":123}'
        try:
            response = self.client.post(RPCPATH, data, 'text/xml')
        except:
            # for some reason, this throws an expat error
            # but only in python 2.4
            return
        self.assertEqual(response.status_code, 200)
        try:
            xmlrpclib.loads(response.content)
            self.fail('parse error expected')
        except xmlrpclib.Fault:
            pass
        
    def test_badrequests(self):
        data = '{"params":[],"method":"system.methodHelp","id":456}'
        response = self.client.post(RPCPATH, data, 'application/json')
        self.assertEqual(response.status_code, 200)
        jsondict = json.loads(response.content)
        self.assertTrue(jsondict['error'] is not None)
        self.assertEqual(jsondict['id'], 456)
        self.assertTrue(jsondict['result'] is None)
        self.assertEqual(jsondict['error']['code'], JSONRPC_SERVICE_ERROR)
        
        data = '<?xml version="1.0"?><methodCall><methodName>method.N0t.Exists</methodName><params></params></methodCall>'
        response = self.client.post(RPCPATH, data, 'text/xml')
        self.assertEqual(response.status_code, 200)
        try:
            xmlrpclib.loads(response.content)
            self.fail('parse error expected')
        except xmlrpclib.Fault, fault:
            self.assertEqual(fault.faultCode, 1)
        
    def test_httpaccesscontrol(self):
        import django
        t = django.VERSION
        
        if t[0] < 1 or (t[0] == 1 and t[1] < 1):
            # options requests can only be tested by django 1.1+
            self.fail('This version of django "%s" does not support http access control' %str(t))
        
        response = self.client.options(RPCPATH, '', 'text/plain')
        self.assertEqual(response['Access-Control-Allow-Methods'], 'POST, GET, OPTIONS')
        self.assertEqual(response['Access-Control-Max-Age'], '0')
        
if __name__ == '__main__':
    unittest.main()