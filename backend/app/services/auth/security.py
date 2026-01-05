from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# from app.db.db_manager import get_user_by_username
# #from security import verify_password

# def login(username: str, password: str):
#     user = get_user_by_username(username)
#     if not user:
#         raise ValueError("Invalid credentials")

#     if not verify_password(password, user["password_hash"]):
#         raise ValueError("Invalid credentials")

#     return user["id"]
