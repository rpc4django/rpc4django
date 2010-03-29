from rpc4django import rpcmethod

@rpcmethod(signature=['int', 'int', 'int'])
def power(a, b):
    return a ** b
