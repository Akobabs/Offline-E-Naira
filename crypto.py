from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json

# Mock key (in real apps, store securely)
KEY = b'1234567890123456'  # 16-byte key for AES

def encrypt_data(data):
    cipher = AES.new(KEY, AES.MODE_EAX)
    data_bytes = json.dumps(data).encode()
    ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
    return {
        'nonce': base64.b64encode(cipher.nonce).decode(),
        'ciphertext': base64.b64encode(ciphertext).decode(),
        'tag': base64.b64encode(tag).decode()
    }

def decrypt_data(encrypted_data):
    nonce = base64.b64decode(encrypted_data['nonce'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    tag = base64.b64decode(encrypted_data['tag'])
    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    data_bytes = cipher.decrypt_and_verify(ciphertext, tag)
    return json.loads(data_bytes.decode())