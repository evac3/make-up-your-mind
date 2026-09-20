# 🦆 Make Up Your Mind

> **A Cognitive AI Decision Companion with Clinical Evidence Backing**  
> Tailored for neurodivergent individuals and students managing anxiety, OCD loops, or memory overload.

[![React Native](https://img.shields.io/badge/React%20Native-Expo%2053+-498DCB.svg)](https://reactnative.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%20Flash%20%7C%20Multi--Model-4285F4.svg)](https://ai.google.dev/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5+-FFF000.svg)](https://duckdb.org/)
[![OpenAlex](https://img.shields.io/badge/Dataset-OpenAlex%20Research-FF6B6B.svg)](https://openalex.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Overview

When faced with high-stress decisions, standard AI chatbots often dump endless pros and cons, hedge with overwhelming ambiguities, or fuel catastrophic overthinking.

**Make Up Your Mind** (featuring our mascot **Decision Duck**) acts like a thoughtful, empathetic human counselor. It delivers concise, grounded responses (~130 words) backed by **peer-reviewed clinical psychology research** from **OpenAlex**, tailored to your unique cognitive mindset:

* **😰 Overthinking & Anxiety:** De-escalates catastrophizing, limits decision fatigue, reframes realistic scenarios, and breaks choices into micro-steps.
* **🔁 Doubt & OCD Loops:** Time-boxes decisions, interrupts repetitive certainty-seeking loops, and offers definitive grounding.
* **🧠 Focus & Memory Aid (ADHD):** Keeps language clear and direct, tracks previous constraints, and provides a bite-sized checklist.
* **📚 Live OpenAlex Research Grounding:** Searches a 2,000+ paper columnar Parquet dataset via embedded DuckDB, citing relevant peer-reviewed studies directly in the conversation.
* **💬 Multi-Turn Conversational Memory:** Remembers your name, major, background constraints, and family context across consecutive questions without restarting.
* **🎙️ Voice Synthesis & Accessibility:** Built-in Text-to-Speech (TTS) and customizable accessibility controls for large text and dark mode.

---

## 🏗️ System Architecture

```
                               ┌────────────────────────────────────────────────┐
                               │           React Native / Expo Frontend         │
                               │  - Decision Duck Mascot & Themed UI (Port 8081)│
                               │  - Mindset Selector (Anxiety / OCD / Memory)   │
                               │  - Interactive OpenAlex Research Drawer        │
                               │  - Multi-Turn Chat & Expo Speech TTS           │
                               └───────────┬────────────────────────┬───────────┘
                                           │                        │
                     Account Setup & Auth  │                        │ AI Decision Chat
                  POST /user (Port 8001)   │                        │ POST /chat (Port 8000)
                                           ▼                        ▼
┌──────────────────────────────────────────────┐        ┌──────────────────────────────────────────────┐
│       Database & Analytics Microservice      │        │             AI Gateway Service               │
│               (FastAPI - Port 8001)          │        │            (FastAPI - Port 8000)             │
├──────────────────────────────────────────────┤        ├──────────────────────────────────────────────┤
│ • SQLite Database (Users, Decisions, Settings)│◄───────┤ • Multi-Turn Conversation Memory Tracker     │
│ • DuckDB Columnar Parquet Engine             │Evidence│ • Condition-Specific Clinical Prompt Builders │
│ • OpenAlex 2,000+ Research Paper Index       │ Search │ • Multi-Model Gemini Engine (Quota Resilient)│
│ • Category Relevance +3 Scoring Algorithm    │        │ • Evidence Citation Formatter ([1], [2], ...)│
└──────────────────────────────────────────────┘        └──────────────────────────────────────────────┘
```

---

## 🔬 Dataset & Evidence Pipeline

To ground AI advice in empirical evidence, we built an ingestion pipeline that pulls metadata and abstracts from **OpenAlex**:
* **High-Throughput Concurrent Ingestion:** An asynchronous fetch script (`backend/scripts/openalex_concurrent_ingest.py`) gathers peer-reviewed papers across 12 mental health and cognitive domains (*anxiety, OCD, rumination, decision fatigue, stress, student mental health, CBT, mindfulness, etc.*).
* **Accelerated Ingestion:** High-speed parallel collection run on an **Ascend GX10** machine to assemble `public_dataset.parquet`.
* **DuckDB Scoring Engine:** When a user asks a question, DuckDB queries the dataset with condition-category boosting (`+3` relevance multiplier) and feeds the top research abstracts to the AI model.
* **In-App Research Drawer:** In the chat UI, users can tap **"▼ View OpenAlex Research Sources"** below any AI response to inspect the exact titles, categories, and findings cited.

---

## 📁 Repository Structure

```
make-up-your-mind/
├── frontend/                         # React Native / Expo Application
│   ├── assets/images/                # Mascot branding (duck_full.png, duck_icon.png)
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/               # Setup, login, and mindset selection
│   │   │   ├── (main)/               # Home, conversation, profile, history
│   │   │   └── _layout.tsx           # Navigation root layout
│   │   ├── components/
│   │   │   ├── chat/                 # MessageBubble with OpenAlex citations drawer
│   │   │   ├── duck/                 # Decision Duck mascot components
│   │   │   └── ui/                   # Buttons, inputs, and toggles
│   │   ├── hooks/                    # useConversation, useTheme, useSpeech
│   │   ├── lib/api.ts                # Dual-port API client (8000 AI + 8001 DB)
│   │   └── store/                    # Zustand persistent state (auth, profile, chats)
│   └── package.json
│
├── backend/                          # Python Backend Services & Data Engine
│   ├── main.py                       # AI Gateway & Gemini chat service (Port 8000)
│   ├── requirements.txt              # Backend dependencies
│   ├── .env.example                  # Environment template
│   ├── prompts/                      # Condition-tailored clinical prompts
│   │   ├── anxiety.py                # Anxiety & catastrophizing reframing
│   │   ├── ocd.py                    # OCD rumination time-boxing
│   │   └── memory.py                 # Memory & ADHD clear checklists
│   ├── scripts/                      # Data ingestion utilities
│   │   ├── openalex_api_ingest.py    # Local OpenAlex ingestion
│   │   └── openalex_concurrent_ingest.py # Async GX10 high-speed ingestion
│   ├── app/                          # Database & DuckDB Service (Port 8001)
│   │   ├── duckdb_service.py         # DuckDB Parquet keyword search & boosting
│   │   ├── database.py               # SQLite connection & schema management
│   │   ├── models.py                 # SQLAlchemy models
│   │   └── main.py                   # FastAPI service for user & evidence
│   └── data/                         # Persistent SQLite & OpenAlex Parquet files
│
├── PRD.md                            # Product Requirements Document
├── Architecture.md                   # Complete Architecture Specification
├── API.md                            # REST API Contracts
└── README.md
```

---

## 🚀 Quickstart Guide

### Prerequisites
* **Node.js** (v18+) & **npm**
* **Python** (3.11+)
* A **Google Gemini API Key** ([Get one here](https://aistudio.google.com/))

---

### Step 1: Backend Setup

1. **Clone the repository and enter `backend`**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment & install dependencies**:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` inside `backend/` and add your Gemini API key:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key
   GEMINI_MODEL=gemini-flash-latest
   DB_BASE_URL=http://localhost:8001
   ```

4. **Start the Backend Services**:
   Open **two separate terminals**:

   **Terminal 1 — Database & OpenAlex Analytics (Port 8001):**
   ```bash
   python -m uvicorn app.main:app --app-dir backend --reload --port 8001
   ```
   *Swagger Docs:* [http://localhost:8001/docs](http://localhost:8001/docs)

   **Terminal 2 — AI Gateway & Chat Service (Port 8000):**
   ```bash
   python -m uvicorn main:app --app-dir backend --reload --port 8000
   ```
   *Swagger Docs:* [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Step 2: Frontend Setup

Open a **third terminal**:

```bash
cd frontend
npm install
npx expo start --web
```
* **Web App:** Visit [http://localhost:8081](http://localhost:8081) in your browser.
* **Mobile App:** Scan the terminal QR code with **Expo Go** on iOS or Android.

---

## 💡 Demo Walkthrough

1. **Mindset Selection**: Open the app and create your profile. Choose your decision-making focus (*e.g., Overthinking & Anxiety*).
2. **Initial Question**: Ask Decision Duck a life dilemma:
   > *"Hey I'm Sunrut, a Computer Engineering student trying to balance a part-time job with school. It's getting overwhelming—should I drop out?"*
3. **Evidence-Grounded Response**: Decision Duck gives an empathetic, structured answer (~130 words) citing research papers (`[1]`, `[2]`).
4. **Expandable OpenAlex Sources**: Tap **"▼ View OpenAlex Research Sources"** to see the peer-reviewed studies backing the response.
5. **Multi-Turn Conversational Memory**: Follow up naturally without repeating yourself:
   > *"What about taking a gap semester instead?"*  
   Decision Duck recalls your name, major, and family situation, directly comparing the gap semester against dropping out.

---

## 🧪 Testing

Run automated tests on the data layer and API schemas:
```bash
cd backend
python -m pytest -q -p no:cacheprovider
```

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
