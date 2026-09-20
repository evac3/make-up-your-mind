import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


gemini_client = genai.Client()

# Import condition-specific prompt builders
from prompts.anxiety import get_anxiety_prompt
from prompts.ocd import get_ocd_prompt
from prompts.memory import get_memory_prompt
app = FastAPI(title="Make Up Your Mind — AI Gateway", version="0.1.0")

PROMPT_BUILDERS = {
    "anxiety": get_anxiety_prompt,
    "ocd": get_ocd_prompt,
    "memory": get_memory_prompt,
}


class UserRequest(BaseModel):
    user_id: int
    message: str
    condition: str
    about_me: str
    concerns: str

@app.post("/chat")
async def chat(req: UserRequest):
    async with httpx.AsyncClient() as client:
        try:
            db_res = await client.get(
                "http://localhost:8001/evidence",
                params={
                    "query": f"{req.condition} {req.concerns}",
                    "category": req.condition.lower(),
                },
                timeout=10.0
            )
            evidence_data = db_res.json() if db_res.status_code == 200 else []
        except Exception:
            evidence_data = []

    # Format evidence into readable citations
    if evidence_data:
        evidence_block = "\n\nRelevant Academic Research (cite by number when applicable):\n"
        for i, ev in enumerate(evidence_data, 1):
            title = ev.get("title", "Untitled")
            summary = ev.get("summary", "")[:300]
            evidence_block += f"\n[{i}] {title}\n    {summary}\n"
    else:
        evidence_block = "\n\n(No academic evidence available for this query.)\n"

    # Use condition-specific prompt builder if available, else generic
    builder = PROMPT_BUILDERS.get(req.condition.lower())
    if builder:
        prompt = builder(req.about_me, req.concerns, req.message)
        prompt += evidence_block
        prompt += "\nWhere relevant, briefly reference the research above (by number) to support your points."
    else:
        prompt = f"""
    User Context:
    - Condition: {req.condition}
    - About Me: {req.about_me}
    - Concerns: {req.concerns}
    - User Message: {req.message}
    {evidence_block}
    Provide a supportive, grounded response addressing the user's message. Where relevant, briefly reference the numbered research above to support your points.
    """

    import asyncio

    primary_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    fallback_model = "gemini-2.5-flash"
    models_to_try = [primary_model] if primary_model == fallback_model else [primary_model, fallback_model]

    last_error = None
    for model in models_to_try:
        for attempt in range(3):
            try:
                response = await gemini_client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return {
                    "response": response.text,
                    "evidence": evidence_data
                }
            except Exception as e:
                last_error = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    wait = 2 ** attempt  # 1s, 2s, 4s
                    await asyncio.sleep(wait)
                    continue
                raise HTTPException(status_code=500, detail=str(e))
        # If all retries failed for this model, try the fallback
    raise HTTPException(status_code=500, detail=f"All retries exhausted: {last_error}")
