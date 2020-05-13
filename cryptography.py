from base64 import b64encode, b64decode
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random


def xor_bytes(text, key):
    while len(key) < len(text):
        key += ' '
    return (''.join([chr(ord(c1) ^ ord(c2)) for (c1, c2) in zip(text, key)])).encode('utf-8')


def xor_str(enc, key):
    text = enc.decode('utf-8')
    while len(key) < len(text):
        key += ' '
    return ''.join([chr(ord(c1) ^ ord(c2)) for (c1, c2) in zip(text, key)])


def aes_encrypt(raw, password):
    private_key = sha256(password.encode('utf-8')).digest()
    raw = pad(raw.encode('utf-8'), AES.block_size)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw))


def aes_decrypt(enc, password):
    private_key = sha256(password.encode('utf-8')).digest()
    enc = b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:]), AES.block_size).decode('utf-8')
