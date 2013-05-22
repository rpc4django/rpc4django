# -*- coding: utf-8 -*-

from rpc4django import rpcmethod
from othermodule import intro, request
from secretmodule import * # imports protected method

@rpcmethod(name='rpc4django.mytestmethod',signature=['int', 'int', 'int', 'int'])
def mytestmethod(a, b, c):
    '''
    Adds the three parameters together and returns the sum
    
    Parameters:
   
    - `a` - the first parameter
    - `b` - the second parameter
    - `c` - the third parameter
    
    Returns
      the sum of the 3 parameters
      
    '''
    
    return a + b + c
