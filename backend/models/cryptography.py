import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encrypt_secret(secret: str, passphrase: str) -> bytes:
    salt = os.urandom(12)
    nonce = os.urandom(12)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    key = kdf.derive(passphrase.encode())
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, secret.encode(), None)

    return salt + nonce + ciphertext


def decrypt_secret(hex_data: str, passphrase: str) -> str:
    raw = bytes.fromhex(hex_data)
    salt = raw[:12]
    nonce = raw[12:24]
    ciphertext = raw[24:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    key = kdf.derive(passphrase.encode())
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
