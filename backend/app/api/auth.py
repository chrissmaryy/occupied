from fastapi import APIRouter, Response, HTTPException, Cookie
from app.db.db_manager import get_user_by_username, create_user
from app.services.auth.security import *
from app.db.db_manager import create_session, delete_session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(username: str, password: str, response: Response):
    user = get_user_by_username(username)

    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = create_session(user["id"])

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,     # lokal False, prod True
        samesite="lax"
    )

    return {"status": "logged_in"}

@router.post("/logout")
def logout(
    response: Response,
    session_id: str | None = Cookie(default=None)
):
    if session_id:
        delete_session(session_id)

    response.delete_cookie("session_id")
    return {"status": "logged_out"}

@router.post("/create_account")
def create_account(
    username: str,
    password: str
):
    
    return create_user_account(username, password)
