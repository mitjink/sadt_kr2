from fastapi import FastAPI, Header, Request, Response, Depends
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timezone
import re
import uvicorn

app = FastAPI(
    title="Headers API - Задание 5.4",
    version="1.0.0",
    description="API для работы с HTTP заголовками"
)

class CommonHeaders(BaseModel):
    user_agent: str = Header(
        ...,
        alias="User-Agent",
        description="User-Agent заголовок браузера клиента"
    )
    accept_language: str = Header(
        ...,
        alias="Accept-Language",
        description="Предпочтительный язык клиента"
    )
    
    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if not v:
            raise ValueError('Accept-Language header cannot be empty')
        
        pattern = r'^[a-zA-Z\-*]+(;[qQ]=[0-9.]+)?(,[a-zA-Z\-*]+(;[qQ]=[0-9.]+)?)*$'
        
        if not re.match(pattern, v):
            simple_pattern = r'^[a-zA-Z\-*]+(,[a-zA-Z\-*]+)*$'
            if not re.match(simple_pattern, v):
                raise ValueError(
                    f'Invalid Accept-Language format: {v}. '
                    'Expected format like: en-US,en;q=0.9,ru;q=0.8'
                )
        
        return v

@app.get("/headers")
async def get_headers(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }

@app.get("/headers-model")
async def get_headers_model(
    headers: CommonHeaders = Depends()
):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/info")
async def get_info(
    headers: CommonHeaders = Depends(),
    response: Response = None
):
    current_time = datetime.now(timezone.utc).isoformat(timespec='seconds')
    response.headers["X-Server-Time"] = current_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        },
        "server_time": current_time
    }

@app.get("/all-headers")
async def get_all_headers(request: Request):
    headers_dict = dict(request.headers)
    
    return {
        "total_headers": len(headers_dict),
        "headers": headers_dict
    }

@app.get("/parse-language")
async def parse_language(accept_language: Optional[str] = Header(None, alias="Accept-Language")):
    if not accept_language:
        return {"message": "No Accept-Language header provided"}
    
    languages = []
    
    for part in accept_language.split(','):
        part = part.strip()
        if ';q=' in part:
            lang, q_value = part.split(';q=')
            try:
                q = float(q_value)
            except ValueError:
                q = 1.0
        else:
            lang = part
            q = 1.0
        
        languages.append({
            "language": lang,
            "priority": q
        })
    languages.sort(key=lambda x: x["priority"], reverse=True)
    
    return {
        "raw": accept_language,
        "parsed": languages,
        "preferred_language": languages[0]["language"] if languages else None
    }

@app.get("/parse-user-agent")
async def parse_user_agent(user_agent: Optional[str] = Header(None, alias="User-Agent")):
    if not user_agent:
        return {"message": "No User-Agent header provided"}
    info = {
        "raw": user_agent,
        "is_mobile": any(x in user_agent.lower() for x in ['mobile', 'android', 'iphone']),
        "is_bot": any(x in user_agent.lower() for x in ['bot', 'crawler', 'spider']),
    }
    if 'Chrome' in user_agent:
        info['browser'] = 'Chrome'
    elif 'Firefox' in user_agent:
        info['browser'] = 'Firefox'
    elif 'Safari' in user_agent:
        info['browser'] = 'Safari'
    elif 'Edge' in user_agent:
        info['browser'] = 'Edge'
    else:
        info['browser'] = 'Unknown'
    if 'Windows' in user_agent:
        info['os'] = 'Windows'
    elif 'Mac' in user_agent:
        info['os'] = 'macOS'
    elif 'Linux' in user_agent:
        info['os'] = 'Linux'
    elif 'Android' in user_agent:
        info['os'] = 'Android'
    elif 'iPhone' in user_agent or 'iPad' in user_agent:
        info['os'] = 'iOS'
    else:
        info['os'] = 'Unknown'
    
    return info

@app.get("/headers-demo")
async def headers_demo(request: Request):
    server_time = datetime.now(timezone.utc)
    headers = dict(request.headers)
    accept_language = headers.get('accept-language')
    preferred_langs = []
    if accept_language:
        for part in accept_language.split(','):
            lang = part.strip().split(';')[0]
            preferred_langs.append(lang)
    
    return {
        "server_info": {
            "timestamp": server_time.isoformat(),
            "timezone": "UTC"
        },
        "client_info": {
            "user_agent": headers.get('user-agent'),
            "accept_language": accept_language,
            "preferred_languages": preferred_langs,
            "client_ip": request.client.host if request.client else "unknown"
        },
        "all_headers": headers,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    uvicorn.run("task_5_4:app", host="0.0.0.0", port=8000, reload=True)