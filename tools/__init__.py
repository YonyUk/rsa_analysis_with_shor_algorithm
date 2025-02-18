'''
tools

a set of fucntion utils to use in the future
'''
import functools
from datetime import datetime

def egcd(a:int,b:int):
    '''
    extended Euclid's algorithm

    returns the gcd bettwen a and b and the Bezout's coeficents in a tuple
    '''

    if a == 0:
        return b,0,1
    
    gcd,x1,y1 = egcd(b%a,a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd,x,y

def iterative_egcd(a:int,b:int):

    stack = []
    gcd = None
    x1 = y1 = None
    while a > 0:
        stack.append((a,b))
        temp = a
        a = b%a
        b = temp
        pass
    gcd = b
    x1 = 0
    y1 = 1
    while len(stack) > 0:
        a,b = stack.pop()
        x = y1 - (b // a) * x1
        y = x1
        x1 = x
        y1 = y
        pass
    return gcd,x1,y1

def modular_inverse(a:int,N:int):
    '''
    return the modular inverse of a mod N
    '''
    gcd,x,_ = egcd(a,N)
    if gcd != 1:
        raise ValueError(f'There\'s no exists modular inverse for {a} mod {N}')

    return x % N

def get_coprimes_with(n:int):
    '''
    returns all the numbers coprimes with n and less than n
    '''
    return [i for i in range(n) if egcd(i,n)[0] == 1]

def modular_square_exponentiation(base:int,exponent:int,N:int):
    result = 1
    while exponent > 0:
        if exponent & 1 == 1:
            result *= base
            result %= N
            pass
        exponent = exponent >> 1
        base *= base
        base %= N
        pass

    return result

def printtiming(func):
    @functools.wraps(func)
    def envolture(*args,**kwargs):
        t = datetime.now()
        result = func(*args,**kwargs)
        print(f'time: {datetime.now() - t}')
        return result
    return envolture