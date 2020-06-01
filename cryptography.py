from base64 import b64encode, b64decode
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random

# Ключ, использующийся для шифрования и дешифрования
KEY = 'rGfEBN5{ZRTVLXBZfGYhF}M@Jt4f$cFNH?87ZH0Ut?DsLGd?vtfGMCKPZczDxapJ'


# Функция XOR-шифрования
def xor_bytes(text):
    key = KEY
    while len(key) < len(text):
        key += ' '
    return (''.join([chr(ord(c1) ^ ord(c2)) for (c1, c2) in zip(text, key)])).encode('utf-8')


# Функция XOR-дешифрования
def xor_str(enc):
    text = enc.decode('utf-8')
    key = KEY
    while len(key) < len(text):
        key += ' '
    return ''.join([chr(ord(c1) ^ ord(c2)) for (c1, c2) in zip(text, key)])


# Функция AES-шифрования
def aes_encrypt(raw):
    private_key = sha256(KEY.encode('utf-8')).digest()
    raw = pad(raw.encode('utf-8'), AES.block_size)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw))


# Функция AES-дешифрования
def aes_decrypt(enc):
    private_key = sha256(KEY.encode('utf-8')).digest()
    enc = b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:]), AES.block_size).decode('utf-8')
