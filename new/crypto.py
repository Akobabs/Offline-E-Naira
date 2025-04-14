from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json
import os

# Load key from environment variable (ensure 16 bytes)
KEY = os.getenv('ENAIRA_AES_KEY', 'default-16-byte-key').encode()[:16]

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