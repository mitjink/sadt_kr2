from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import uvicorn

app = FastAPI(title="Задание 3.1")

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=70, description="Имя пользователя (обязательное поле)")
    email: EmailStr = Field(..., description="Email пользователя (должен быть в формате email)")
    age: Optional[int] = Field(None, ge=0, description="Возраст пользователя (опционально, положительное число)")
    is_subscribed: Optional[bool] = Field(False, description="Подписка на новостную рассылку")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Имя не может быть пустым или состоять только из пробелов')
        return v.strip()
    
    @field_validator
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError('Возраст должен быть положительным числом')
        return v
    
app.post("/create_user", response_model=UserCreate)
async def create_user(user: UserCreate):
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)