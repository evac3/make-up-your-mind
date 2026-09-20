# Make Up Your Mind — LLM Handoff

## Purpose

This document gives another LLM enough context to continue debugging and developing the project without repeating earlier setup work.

## Project layout

The repository is organized as follows:

```text
make-up-your-mind/
├── backend/
│   ├── main.py                 # AI gateway service, port 8000
│   ├── app/main.py             # Database/analytics service, port 8001
│   ├── app/duckdb_service.py   # DuckDB + Parquet evidence search
│   ├── app/database.py         # SQLite setup and migrations
│   ├── app/models.py           # User and Decision models
│   ├── app/schemas.py          # API schemas
│   ├── prompts/                # Anxiety, memory, and OCD prompts
│   ├── tests/                  # Backend tests
│   ├── data/                   # SQLite, DuckDB, and Parquet files
│   ├── .env                    # Local secrets/configuration; never expose contents
│   └── requirements.txt
├── frontend/                   # Frontend work in progress
├── API.md
├── Architecture.md
├── PRD.md
└── README.md
```

## Services

### AI gateway — port 8000

Entry point: `backend/main.py`

Endpoint:

```text
POST http://127.0.0.1:8000/chat
```

Request body:

```json
{
  "user_id": 2,
  "message": "Should I keep working on this project?",
  "condition": "anxiety",
  "about_me": "I am a college student",
  "concerns": "I worry about making the wrong decision"
}
```

The gateway:

1. Fetches the user profile from port 8001.
2. Fetches the user’s decision history from port 8001.
3. Fetches evidence from `GET /evidence?query=...` on port 8001.
4. Builds a condition-specific prompt.
5. Calls Gemini through the `google-genai` SDK.
6. Saves the generated decision to port 8001.
7. Returns `{ "response": "..." }`.

### Database/analytics service — port 8001

Entry point: `backend/app/main.py`

Start it with:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --port 8001
```

Important endpoints:

```text
GET  /health
POST /user
GET  /user/{user_id}
GET  /history/{user_id}
POST /decision
POST /outcome
GET  /evidence?query=...
```

The service stores user profiles and decisions in `backend/data/app.db`. It uses DuckDB and Parquet for evidence search. Restarting the service does not clear the database.

## Starting both services

Run each service in its own terminal. From the repository root:

Terminal 1:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --port 8001
```

Terminal 2:

```powershell
python -m uvicorn main:app --app-dir backend --reload --port 8000
```

Swagger URLs:

```text
http://127.0.0.1:8001/docs
http://127.0.0.1:8000/docs
```

If port 8000 or 8001 reports Windows error 10048, another process is already using that port. Find the process with:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object OwningProcess
Get-NetTCPConnection -LocalPort 8001 -State Listen | Select-Object OwningProcess
```

Stop only the relevant old process, or press Ctrl+C in the terminal where it is running.

## Creating and testing a user

On `http://127.0.0.1:8001/docs`, use `POST /user`:

```json
{
  "name": "Test User",
  "condition": "anxiety",
  "about_me": "I am a college student",
  "concerns": "I worry about making the wrong decision"
}
```

Use the returned `user_id` in the AI gateway’s `POST /chat` request. Then verify persistence with `GET /history/{user_id}` on port 8001. In Swagger, enter only the numeric path value, such as `2`, not `{user_id}` or `user_id=2`.

## Environment configuration

`backend/main.py` explicitly loads `backend/.env` relative to the file, so the services can be started from the repository root. Required configuration includes:

```text
GEMINI_API_KEY=<local secret; do not copy into handoff documents>
GEMINI_MODEL=<configured Gemini model>
DB_BASE_URL=http://localhost:8001
```

Do not print, commit, or paste the actual API key.

## Important debugging history

- The original project had a single root-level `main.py`; the current project has moved the application into `backend/`.
- The AI gateway previously had multiple `/chat` route definitions. It was consolidated into one route.
- The gateway now includes `user_id` in `ChatRequest` and saves decisions after Gemini responds.
- Evidence retrieval was initially added at module scope, which caused startup errors because `request` and `prompt` did not exist during import. It was moved inside `chat()` after the request and base prompt are available.
- `backend/main.py` now loads `.env` using `Path(__file__).resolve().parent`, fixing ASGI startup failures caused by launching Uvicorn from the repository root.
- A prior `500` response was traced to Gemini’s outbound Python request failing with Windows error 10013. A basic TCP test can pass while Python’s HTTPS request is still blocked by firewall, VPN, proxy, or network policy.
- A prior port error, Windows error 10048, meant an old Uvicorn process was still listening on port 8000.
- The database save occurs only after Gemini returns successfully. If Gemini fails, no decision is posted to `/decision`.

## Current status

- Both backend imports were verified successfully after the `.env` path fix.
- The database service is designed to persist data across restarts.
- The main remaining validation is to start both services, create/verify a user, call `/chat`, and check `/history/{user_id}`.

## Recommended next debugging steps

If `/chat` fails:

1. Confirm `GET http://127.0.0.1:8001/health` returns `{"status":"ok"}`.
2. Confirm `GET /user/{user_id}` works for the ID being sent.
3. Confirm the request body includes an integer `user_id`.
4. Check the terminal running port 8000 for the traceback.
5. If the error occurs at `client.models.generate_content`, test Gemini connectivity and API credentials separately.
6. If Gemini succeeds but the response is a database error, inspect the status/body returned by `POST /decision`.
7. Do not delete `backend/data/app.db` unless a clean database is explicitly desired; back it up first.

## Guidance for the next LLM

Start by asking for the exact traceback if one is not provided. Distinguish among:

- ASGI import/startup errors
- Port conflicts
- Database service connectivity or validation errors
- Gemini API/network/authentication errors
- Failed decision persistence after a successful Gemini response

Do not assume that restarting the server resets data. Do not expose or request the contents of `backend/.env`; only verify whether required keys are present.
