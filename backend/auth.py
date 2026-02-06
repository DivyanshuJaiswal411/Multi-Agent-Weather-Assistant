import os
from fastapi import Header, HTTPException

BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")  # client → backend

def verify_api_key(x_api_key: str | None = Header(default=None)):
    if BACKEND_API_KEY and x_api_key != BACKEND_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
