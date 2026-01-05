from fastapi import FastAPI, Depends
from app.api.reservations import router as reservations_router
from app.api.auth import router as auth_router
from app.services.auth.dependencies import get_current_user

app = FastAPI()

app.include_router(reservations_router)

app.include_router(auth_router)

@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"]
    }

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
def health_check():
    return {"status": "alive"}