from fastapi import FastAPI, HTTPException, Response, Cookie, Depends, Request
from pydantic import BaseModel
from typing import Optional
import uuid
import hmac
import hashlib
import time
from datetime import datetime
import uvicorn

app = FastAPI(title="Задание 5.3")

SECRET_KEY = b"my-secret-key-for-the-task"

class LoginRequest(BaseModel):
    username: str
    password: str

users_db = {
    "user123": {"password": "password123", "name": "John Doe", "email": "john@example.com"},
    "admin": {"password": "admin123", "name": "Admin User", "email": "admin@example.com"}
}

def generate_signature(user_id: str, timestamp: int) -> str:
    message = f"{user_id}:{timestamp}".encode()
    signature = hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()
    return signature

def verify_token(token: str) -> tuple[Optional[str], Optional[int], Optional[str]]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None, None, "Invalid token format"
        
        user_id, timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        expected_signature = generate_signature(user_id, timestamp)
        if not hmac.compare_digest(signature, expected_signature):
            return None, None, "Invalid signature"
        
        return user_id, timestamp, None
        
    except (ValueError, IndexError):
        return None, None, "Invalid token"

def should_update_session(last_activity: int, current_time: int) -> bool:
    elapsed = current_time - last_activity
    return 180 <= elapsed < 300

def is_session_expired(last_activity: int, current_time: int) -> bool:
    elapsed = current_time - last_activity
    return elapsed >= 300

@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    current_timestamp = int(time.time())
    signature = generate_signature(login_data.username, current_timestamp)
    
    token = f"{login_data.username}.{current_timestamp}.{signature}"
    
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=300,
        samesite="lax"
    )
    
    return {"message": "Login successful"}

def get_current_user(session_token: Optional[str] = Cookie(None), response: Response = None):
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token")
    
    user_id, timestamp, error = verify_token(session_token)
    if error:
        raise HTTPException(status_code=401, detail=f"Invalid session: {error}")
    
    current_time = int(time.time())
    
    if is_session_expired(timestamp, current_time):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if should_update_session(timestamp, current_time):
        new_timestamp = current_time
        new_signature = generate_signature(user_id, new_timestamp)
        new_token = f"{user_id}.{new_timestamp}.{new_signature}"
        
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=300,
            samesite="lax"
        )
        
        return {
            "user_id": user_id,
            "name": user["name"],
            "email": user["email"],
            "session_updated": True
        }
    
    return {
        "user_id": user_id,
        "name": user["name"],
        "email": user["email"],
        "session_updated": False
    }

@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "profile": current_user,
        "message": "Welcome to your profile"
    }

@app.get("/session-info")
async def get_session_info(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return {"message": "No active session"}
    
    user_id, timestamp, error = verify_token(session_token)
    if error:
        return {"message": f"Invalid session: {error}"}
    
    current_time = int(time.time())
    elapsed = current_time - timestamp
    
    return {
        "user_id": user_id,
        "last_activity": datetime.fromtimestamp(timestamp).isoformat(),
        "seconds_since_activity": elapsed,
        "expired": is_session_expired(timestamp, current_time),
        "should_update": should_update_session(timestamp, current_time)
    }
    
if __name__ == "__main__":
    uvicorn.run("task_5_3:app", host="0.0.0.0", port=8000, reload=True)