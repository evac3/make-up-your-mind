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

DB_BASE_URL = "http://localhost:8001"
DATABASE_TIMEOUT_SECONDS = 10

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_id: int
    message: str
    condition: str
    about_me: str = ""
    concerns: str = ""


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

    condition = request.condition.lower()
    if "anxiety" in condition:
        prompt = get_anxiety_prompt(request.about_me, request.concerns, request.message)
    elif "memory" in condition:
        prompt = get_memory_prompt(request.about_me, request.concerns, request.message)
    elif "ocd" in condition:
        prompt = get_ocd_prompt(request.about_me, request.concerns, request.message)
    else:
        prompt = f"""
        You are a warm, casual decision-making assistant.
        Their condition: {request.condition}
        Their concerns: {request.concerns}

        User message: {request.message}
        """

    prompt = f"""
    {prompt}

    Additional context from the database:
    User profile: {user_profile}
    Past decisions: {history}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    try:
        requests.post(
            f"{DB_BASE_URL}/decision",
            json={
                "user_id": request.user_id,
                "message": request.message,
                "ai_response": response.text,
            },
            timeout=DATABASE_TIMEOUT_SECONDS,
        ).raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not save the decision to the database service",
        ) from exc

    return {"response": response.text}
