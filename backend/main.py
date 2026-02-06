from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent import root_agent
from auth import verify_api_key
from rate_limit import rate_limit

# --------------------
# FASTAPI APP
# --------------------
app = FastAPI(title="Weather AI Agent")

# --------------------
# CORS (ALLOW FRONTEND)
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# AGENT RUNNER
# --------------------
runner = Runner(
    app_name="weather-agent",
    agent=root_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True,
)

# --------------------
# REQUEST MODEL
# --------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    unit: str | None = "Celsius"

# --------------------
# HEALTH CHECK (REQUIRED FOR CLOUD RUN)
# --------------------
@app.get("/")
def health():
    return {"status": "ok"}

# --------------------
# CHAT ENDPOINT
# --------------------
@app.post("/chat")
async def chat(
    req: ChatRequest,
    request: Request,
    user=Depends(verify_api_key) if os.getenv("REQUIRE_API_KEY", "false") == "true" else None
):
    # Cloud Run–safe IP detection
    client_ip = request.headers.get("x-forwarded-for", "unknown")
    rate_limit(client_ip)

    session_id = req.session_id or str(uuid.uuid4())
    
    user_msg = types.UserContent(parts=[types.Part(text=req.message)])
    
    reply_text = ""
    async for event in runner.run_async(
        user_id="user", # Default user ID
        session_id=session_id,
        new_message=user_msg,
        # state={"user_preference_temperature_unit": req.unit}, # State not supported in run_async args directly in 1.23.0
    ):
        # We only care about the content sent back to the user (usually from 'model')
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    reply_text += part.text

    return {
        "reply": reply_text,
        "session_id": session_id,
    }
