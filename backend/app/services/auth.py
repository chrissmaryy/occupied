from db.db_manager import get_user_by_username
from security import verify_password

def login(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        raise ValueError("Invalid credentials")

    if not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid credentials")

    return user["id"]
