"""
Шифрование данных at rest
"""
from cryptography.fernet import Fernet
from typing import bytes

class DataEncryption:
    """Шифрование данных для хранения"""
    
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key.encode())
    
    def encrypt(self, data: str) -> bytes:
        """Шифрование данных"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Расшифровка данных"""
        return self.cipher.decrypt(encrypted_data).decode()
