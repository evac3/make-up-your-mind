from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os
from prompts.anxiety import get_anxiety_prompt
from prompts.memory import get_memory_prompt
from prompts.ocd import get_ocd_prompt

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    condition: str
    about_me: str
    concerns: str

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = f"""
    You are a warm, casual decision-making assistant.
    About the user: {request.about_me}
    Their condition: {request.condition}
    Their concerns: {request.concerns}
    
    User message: {request.message}
    """
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return {"response": response.text}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Route to correct prompt based on condition
    condition = request.condition.lower()
    
    if "anxiety" in condition:
        prompt = get_anxiety_prompt(request.about_me, request.concerns, request.message)
    elif "memory" in condition:
        prompt = get_memory_prompt(request.about_me, request.concerns, request.message)
    elif "ocd" in condition:
        prompt = get_ocd_prompt(request.about_me, request.concerns, request.message)
    else:
        # Default fallback for anything else
        prompt = f"""
        You are a warm, casual decision-making assistant.
        About the user: {request.about_me}
        Their concerns: {request.concerns}
        User message: {request.message}
        """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return {"response": response.text}

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = f"""
    You are a concise, direct decision-making assistant.
    About the user: {request.about_me}
    Their condition: {request.condition}
    Their concerns: {request.concerns}

    RULES YOU MUST FOLLOW:
    - Keep responses SHORT, 3-5 sentences maximum
    - Always end with a clear, definitive recommendation
    - Format like this:
        DECISION: (your clear recommendation in one sentence)
        WHY: (1-2 sentences max)
        SHORT TERM: (one consequence)
        LONG TERM: (one consequence)
    - Never ask multiple follow up questions
    - Do not over-explain

    User message: {request.message}
    """