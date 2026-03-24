from fastapi import FastAPI, Header, HTTPException
from typing import Optional
import uvicorn

app = FastAPI(title="Задание 5.4")

@app.get("/headers")
async def get_headers(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    
    if not user_agent:
        raise HTTPException(
            status_code=400,
            detail="Missing required header: User-Agent"
        )

    if not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Missing required header: Accept-Language"
        )
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


if __name__ == "__main__":
    uvicorn.run("task_5_4:app", host="0.0.0.0", port=8000, reload=True)