# Ajouter ce fichier: src/utils/password.py

import hashlib
import secrets

def hash_password(password: str) -> str:
    
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                  password.encode('utf-8'), 
                                  salt.encode('utf-8'), 
                                  100000)
    return salt + pwdhash.hex()

def verify_password(password: str, stored_password: str) -> bool:
    
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256',
                                  password.encode('utf-8'), 
                                  salt.encode('utf-8'), 
                                  100000)
    return pwdhash.hex() == stored_hash