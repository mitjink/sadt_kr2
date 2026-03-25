from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
import uvicorn

app = FastAPI(title="Задание 5.2")

SECRET_KEY = "my-very-secret-key"
serializer = URLSafeTimedSerializer(SECRET_KEY)

users_db = {
    "user123": {"password": "password123", "name": "John Doe", "email": "john@example.com"},
    "admin": {"password": "admin123", "name": "Admin User", "email": "admin@example.com"}
}

class LoginRequest(BaseModel):
    username: str
    password: str
    
def verify_credentials(username: str, password: str) -> Optional[dict]:
    user = users_db.get(username)
    if user and user["password"] == password:
        return {"user_id": username, "name": user["name"], "email": user["email"]}
    return None

@app.post("/login")
async def login(login_data: LoginRequest, response: Response):
    user_data = verify_credentials(login_data.username, login_data.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    signed_token = serializer.dumps(user_data["user_id"])
    
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        secure=False,
        max_age=3600,
        samesite="lax"
    )
    
    return {"message": "Login successful"}

def get_current_user(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized - No token")
    
    try:
        user_id = serializer.loads(session_token, max_age=3600)
        
        user = users_db.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {"user_id": user_id, "name": user["name"], "email": user["email"]}
        
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid session - Tampered token")
    except SignatureExpired:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Profile information",
        "user": current_user
    }
    
if __name__ == "__main__":
    uvicorn.run("task_5_2:app", host="0.0.0.0", port=8000, reload=True)