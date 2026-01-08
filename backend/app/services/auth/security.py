import os
import hashlib
import binascii
from app.db.db_manager import get_user_by_username, create_user

# --- Konfiguration ---
ITERATIONS = 100_000
HASH_NAME = "sha256"
SALT_SIZE = 16  # bytes

# --- Passwort hashen ---
def hash_password(password: str) -> str:
    salt = os.urandom(SALT_SIZE)  # einzigartig pro Passwort
    pwd_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )
    # Speicherung als hex: salt + hash
    return f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(pwd_hash).decode()}"

# --- Passwort prüfen ---
def verify_password(password: str, stored_hash: str) -> bool:
    salt_hex, hash_hex = stored_hash.split(":")
    salt = binascii.unhexlify(salt_hex)
    stored_pwd_hash = binascii.unhexlify(hash_hex)

    test_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )
    return test_hash == stored_pwd_hash

def create_user_account(username: str, password: str):
    if get_user_by_username(username):
        raise ValueError("Username already taken")
    
    password_hashed = hash_password(password)
    
    return create_user(username, password_hashed)


# from app.db.db_manager import get_user_by_username
# #from security import verify_password

# def login(username: str, password: str):
#     user = get_user_by_username(username)
#     if not user:
#         raise ValueError("Invalid credentials")

#     if not verify_password(password, user["password_hash"]):
#         raise ValueError("Invalid credentials")

#     return user["id"]
