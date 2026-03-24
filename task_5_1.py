from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

app = FastAPI(title="Задание 5.1")

sessions = {}

class LoginRequest(BaseModel):
    username: str
    password: str

VALID_CREDENTIALS = {
    "user123": "password123",
    "admin": "admin123"
}

def verify_credentials(username: str, password: str) -> bool:
    return VALID_CREDENTIALS.get(username) == password

@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    if not verify_credentials(login_data.username, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_token = str(uuid.uuid4())
    
    sessions[session_token] = {
        "username": login_data.username,
        "created_at": datetime.now().isoformat()
    }
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        max_age=3600,
        samesite="lax"
    )
    
    return {"message": "Login succesful"}

def get_current_user(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return sessions[session_token]

@app.get("/user")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Profile information",
        "user": current_user
    }
    
@app.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token and session_token in sessions:
        del sessions[session_token]
    response.delete_cookie(key="session_token")
    return {"message": "Logout successful"}