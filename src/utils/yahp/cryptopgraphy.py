from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken as InvalidTokenException


cipher_suite = Fernet(settings.CRYPTO_KEY.encode("utf-8"))

def encrypt(val: str) -> str:
    return cipher_suite.encrypt(val.encode("utf-8")).decode("utf-8")

def decrypt(val: str) -> str:
    return cipher_suite.decrypt(val.encode("utf-8")).decode("utf-8")