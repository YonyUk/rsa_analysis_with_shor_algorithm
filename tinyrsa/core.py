'''
core

the core of the rsa system
'''

import random
from tools import get_coprimes_with,modular_inverse,modular_square_exponentiation,printtiming
from sympy.ntheory.generate import randprime
from math import gcd

class RSA:
    '''
    RSA keys generator
    
    length: the size of the primes to generate keys
    '''

    def __init__(self,length:int,default_pub_key=True):
        self._dpk = default_pub_key
        self._pub_key = 65537        
        self._module = None
        self._phi = None
        self._length = length
        pass

    @property
    @printtiming
    def keys(self):
        self._generate_module()
        priv = self._generate_private_key()

        class RSAPair:
            '''
            define a public-private keys pair
            '''
            def __init__(self,pub:int,priv:int,n:int):
                self._pub = pub
                self._priv = priv
                self._n = n
                pass

            @property
            def public(self):
                '''
                public key
                '''
                return self._pub,self._n
            
            @property
            def private(self):
                '''
                private key
                '''
                return self._priv,self._n

            pass

        return RSAPair(self._pub_key,priv,self._module)

    def _generate_module(self):
        # generamos dos primos aleatorios del tamano especificado
        p1 = randprime(1 << self._length - 1,1 << self._length)
        p2 = randprime(1 << self._length - 1,1 << self._length)
        while p2 == p1:
            p1 = randprime(1 << self._length - 1,1 << self._length)
            pass
        # calculamos el modulo para ambas claves
        self._module = p1 * p2
        # calculamos la funcion totiente de euler
        self._phi = (p1 - 1) * (p2 - 1)
        if not self._dpk:
            for i in range(2,self._phi):
                if gcd(i,self._phi) == 1:
                    self._pub_key = i
                    break
                pass
            pass
        pass
    
    def _generate_private_key(self):
        # hayamos el inverso modular de la clave publica
        return modular_inverse(self._pub_key,self._phi)

    pass

class RSAEncrypter:
    '''
    an rsa-based cipher
    '''

    def __init__(self,key):
        self._pubk,self._module = key
        pass

    def encrypt(self,msg:int):
        '''
        return the number msg ciphered
        '''
        return modular_square_exponentiation(msg,self._pubk,self._module)

    pass

class RSADecrypter:
    '''
    an rsa-based de-cipher
    '''

    def __init__(self,key):
        self._privk,self._module = key
        pass

    def decrypt(self,cmsg:int):
        '''
        return the number cmsg de-ciphered
        '''
        return modular_square_exponentiation(cmsg,self._privk,self._module)

    pass
