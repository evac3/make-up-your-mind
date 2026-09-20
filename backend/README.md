# Make Up Your Mind backend

FastAPI database service for a decision-making assistant. It stores free-text user
profiles and decision history in SQLite so the Gemini integration can personalize
each response.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Terminal 1: Database & Analytics microservice (port 8001)
python -m uvicorn app.main:app --reload --port 8001

# Terminal 2: AI Gateway & Chat service (port 8000)
python -m uvicorn main:app --reload --port 8000
```

Open `http://127.0.0.1:8001/docs` for the Database API docs and `http://127.0.0.1:8000/docs` for the Chat Gateway API. React development servers on ports 3000 and 5173 are allowed by the CORS configuration.

Run the isolated test suite with:

```powershell
python -m pytest -q -p no:cacheprovider
```

## Database contract

The `users` table contains `id`, `name`, `condition`, `about_me`, and `concerns`.
All profile text comes directly from the user.

The `decisions` table contains `id`, `user_id`, `message`, `ai_response`, `outcome`,
and `timestamp`. A new decision has a null outcome until the later check-in.

The database API consists of:

- `POST /user` — create a user profile
- `GET /user/{id}` — return the profile used in Gemini prompts
- `POST /decision` — store the user's message and Gemini response
- `GET /history/{user_id}` — return that user's past decisions
- `POST /outcome` — record how a decision turned out

Operational routes `GET /` and `GET /health` are also available. `GET /evidence`
is retained as the integration seam for the upcoming Voloridge/Parquet work; it
is separate from the five SQLite endpoints.

### Create a profile

```json
{
  "name": "John",
  "condition": "I have anxiety and struggle with big decisions",
  "about_me": "I'm a college student dealing with a lot of stress",
  "concerns": "I worry about making the wrong choice and regretting it"
}
```

The response is:

```json
{
  "user_id": 1,
  "message": "Profile created successfully"
}
```

### Store a decision

```json
{
  "user_id": 1,
  "message": "Should I drop this class?",
  "ai_response": "Let's think through this together..."
}
```

### Record an outcome

```json
{
  "decision_id": 1,
  "outcome": "I stayed and passed the class"
}
```

## AI integration flow

For each chat message, the Gemini layer should fetch `GET /user/{id}` and
`GET /history/{user_id}`, include both responses in its prompt, call Gemini, then
send the user message and generated response to `POST /decision`.

## Project structure

- `app/main.py` defines the HTTP contract and CORS policy.
- `app/models.py` defines the two SQLite tables.
- `app/schemas.py` validates request and response bodies.
- `app/database.py` creates connections, enforces foreign keys, and upgrades the
  earlier local prototype schema without changing record IDs.
- `app/duckdb_service.py` is reserved for the later Voloridge data integration.
- `tests/test_app.py` verifies the API contract.
- `tests/test_data_layer.py` verifies persistence, constraints, and analytical
  storage helpers.

Generated databases and Parquet files live under `data/` and are ignored by Git.
Copy `.env.example` to `.env` to override the local storage paths.
