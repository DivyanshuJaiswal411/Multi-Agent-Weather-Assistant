import time
from fastapi import HTTPException

REQUESTS = {}
LIMIT = 20
WINDOW = 60  # seconds

def rate_limit(client_id: str):
    now = time.time()
    window_start = now - WINDOW

    REQUESTS.setdefault(client_id, [])
    REQUESTS[client_id] = [t for t in REQUESTS[client_id] if t > window_start]

    if len(REQUESTS[client_id]) >= LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    REQUESTS[client_id].append(now)
