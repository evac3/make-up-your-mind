# Make Up Your Mind

> An AI-powered cognitive decision-making companion tailored for neurodivergent individuals and those managing anxiety, OCD, or memory challenges.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%203.1%20Pro%20%2F%203.8%20Flash-4285F4.svg)](https://ai.google.dev/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5+-FFF000.svg)](https://duckdb.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

When faced with stressful choices, standard conversational AI tools often generate overwhelming lists of pros and cons, hedge with endless ambiguities, and trigger catastrophic overthinking or rumination loops.

**Make Up Your Mind** is designed around evidence-based cognitive intervention patterns:
* **Anxiety Mode:** Reframes catastrophic worst-case scenarios, limits choices, and breaks decisions into micro-steps.
* **OCD Mode:** Time-boxes decisions, prevents repetitive rumination, and provides definitive, grounded advice.
* **Memory Mode:** Repeats key constraints, uses direct language, and finishes with a clear summary checklist.
* **Closed-Loop Outcome Tracking:** Encourages users to log how decisions actually turned out, reinforcing self-efficacy over time.
* **Empirical Evidence Retrieval:** Embedded DuckDB engine searching columnar Parquet datasets for real-world statistical benchmarks.

---

## Documentation Index

| Document | Purpose |
| :--- | :--- |
| 📋 [**PRD.md**](PRD.md) | **Product Requirements Document**: User personas, problem statements, functional requirements, and roadmap. |
| 🏛️ [**Architecture.md**](Architecture.md) | **System Architecture**: System diagrams, sequence workflows, database models, and prompt strategy design. |
| 🔌 [**API.md**](API.md) | **REST API Reference**: Request/response contracts, status codes, and curl examples for all endpoints. |
| 💻 [**backend/README.md**](backend/README.md) | **Backend Developer Guide**: Environment variables, SQLite details, and data-layer tests. |

---

## Repository Structure

```
make-up-your-mind/
├── PRD.md                        # Product Requirements Document
├── Architecture.md               # Complete System Architecture Specification
├── Architecure.md                # Quick pointer to Architecture.md
├── API.md                        # Complete REST API contracts
├── LICENSE                       # MIT License
├── .gitignore                    # Top-level Git ignore rules
│
└── backend/                      # Python FastAPI Services & Storage
    ├── main.py                   # AI Gateway Service (Port 8000)
    ├── requirements.txt          # Python dependencies
    ├── .env.example              # Example environment configuration
    ├── .env                      # Local configuration (API keys & paths)
    ├── README.md                 # Backend documentation
    │
    ├── app/                      # Database & Analytical Microservice (Port 8001)
    │   ├── config.py             # Path resolution and settings
    │   ├── database.py           # SQLite connection and migration logic
    │   ├── duckdb_service.py     # DuckDB Parquet storage and keyword search
    │   ├── models.py             # SQLAlchemy models (User, Decision)
    │   ├── schemas.py            # Pydantic v2 schemas
    │   └── main.py               # Database Service FastAPI app
    │
    ├── prompts/                  # Condition-specific cognitive prompts
    │   ├── anxiety.py
    │   ├── memory.py
    │   └── ocd.py
    │
    ├── tests/                    # Pytest test suite (21 passing tests)
    │   ├── conftest.py
    │   ├── test_app.py
    │   └── test_data_layer.py
    │
    └── data/                     # Local data stores (SQLite, DuckDB, Parquet)
```

---

## Quickstart Guide

### 1. Environment Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` inside the `backend/` directory and add your Google Gemini API key:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-3.1-pro-preview
DB_BASE_URL=http://localhost:8001
```

### 3. Run the Services

The application consists of two communicating services. Run each in its own terminal:

#### Terminal 1 — Database & Analytics Service (Port 8001)
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8001
```
* **Interactive Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)
* **Health Check:** [http://localhost:8001/health](http://localhost:8001/health)

#### Terminal 2 — AI Gateway & Chat Service (Port 8000)
```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```
* **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Chat Endpoint:** `POST http://localhost:8000/chat`

---

## Running Automated Tests

Run the comprehensive test suite from the `backend/` directory:
```powershell
cd backend
python -m pytest -q -p no:cacheprovider
```
All 21 unit and integration tests verify API schemas, foreign key enforcement, data persistence across restarts, schema auto-migration, and DuckDB Parquet ranking.

---

## License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
