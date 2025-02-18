'''
tiny rsa

an small implementation of the rsa system
'''
from tools import printtiming
from .core import RSA,RSADecrypter,RSAEncrypter

class TextEncrypter:
    def __init__(self,key:tuple):
        self._cipher = RSAEncrypter(key)
        pass

    def encrypt(self,msg:str,encoding:str='utf-8',**kwargs):
        '''
        if 'num' is passed as True, them the result is a number
        '''
        msg_num = int.from_bytes(msg.encode(encoding),'big')
        ciphered_num = self._cipher.encrypt(msg_num)
        if 'num' in kwargs.keys() and kwargs['num']:
            return ciphered_num
        hex_r = hex(ciphered_num)
        t = bytearray.fromhex(hex_r[2:])
        return t.decode('latin5')
    
    @printtiming
    def encrypt_with_timing(self,msg:str,encoding:str='utf-8',**kwargs):
        '''
        decorated version of encrypt
        '''
        return self.encrypt(msg,encoding,**kwargs)

    pass

class TextDecrypter:
    def __init__(self,key:tuple):
        self._dcipher = RSADecrypter(key)
        pass

    def decrypt(self,msg,encoding:str='utf-8'):
        ciphered_num = None
        if type(msg) == int:
            ciphered_num = msg
            pass
        elif type(msg) == str:
            t = bytearray(msg,'latin5')
            ciphered_num = int(t.hex(),16)
            pass
        else:
            raise ValueError()
        msg_num = self._dcipher.decrypt(ciphered_num)
        return msg_num.to_bytes((msg_num.bit_length() + 7) >> 3,'big').decode(encoding,errors='ignore')

    @printtiming
    def decrypt_with_timing(self,msg,encoding:str='utf-8'):
        '''
        decorated version of decrypt
        '''
        return self.decrypt(msg,encoding)

    pass