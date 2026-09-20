import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel

from prompts.anxiety import get_anxiety_prompt
from prompts.memory import get_memory_prompt
from prompts.ocd import get_ocd_prompt


load_dotenv()

DB_BASE_URL = os.getenv("DB_BASE_URL", "http://localhost:8001")
DATABASE_TIMEOUT_SECONDS = int(os.getenv("DATABASE_TIMEOUT_SECONDS", "10"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Make Up Your Mind — AI Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"app": "make-up-your-mind-gateway", "status": "running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


class ChatRequest(BaseModel):
    user_id: int
    message: str
    condition: str = ""
    about_me: str = ""
    concerns: str = ""
    conversation_id: int | None = None


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_profile = requests.get(
            f"{DB_BASE_URL}/user/{request.user_id}",
            timeout=DATABASE_TIMEOUT_SECONDS,
        ).json()
        history = requests.get(
            f"{DB_BASE_URL}/history/{request.user_id}",
            timeout=DATABASE_TIMEOUT_SECONDS,
        ).json()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail="Database service is unavailable on port 8001",
        ) from exc

    condition = (request.condition or user_profile.get("condition", "")).lower()
    about_me = request.about_me or user_profile.get("about_me", "")
    concerns = request.concerns or user_profile.get("concerns", "")

    if "anxiety" in condition:
        prompt = get_anxiety_prompt(about_me, concerns, request.message)
    elif "memory" in condition:
        prompt = get_memory_prompt(about_me, concerns, request.message)
    elif "ocd" in condition:
        prompt = get_ocd_prompt(about_me, concerns, request.message)
    else:
        prompt = f"""
        You are a warm, casual decision-making assistant.
        Their condition: {condition}
        Their concerns: {concerns}

        User message: {request.message}
        """

    prompt = f"""
    {prompt}

    Additional context from the database:
    User profile: {user_profile}
    Past decisions: {history}
    """
    try:
        evidence_response = requests.get(
            f"{DB_BASE_URL}/evidence",
            params={"query": f"{condition} {concerns}".strip() or "general"},
            timeout=DATABASE_TIMEOUT_SECONDS,
        )
        evidence_response.raise_for_status()
        evidence = evidence_response.json()
    except requests.RequestException:
        evidence = []  # Fail silently if evidence unavailable

    prompt = f"""
    {prompt}

    Relevant research evidence:
    {evidence}
    """
    
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview"),
        contents=prompt,
    )

    post_payload = {
        "user_id": request.user_id,
        "message": request.message,
        "ai_response": response.text,
    }
    if request.conversation_id is not None:
        post_payload["conversation_id"] = request.conversation_id

    try:
        saved = requests.post(
            f"{DB_BASE_URL}/decision",
            json=post_payload,
            timeout=DATABASE_TIMEOUT_SECONDS,
        )
        saved.raise_for_status()
        decision_id = saved.json()["id"]
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not save the decision to the database service",
        ) from exc

    result = {"response": response.text, "decision_id": decision_id}
    if request.conversation_id is not None:
        result["conversation_id"] = request.conversation_id
    return result
