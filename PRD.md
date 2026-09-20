# Product Requirements Document (PRD)

## Project: Make Up Your Mind
**Version:** 1.0.0  
**Status:** In Active Development  
**Target Platform:** Web Application (FastAPI Backend + React Frontend)

---

## 1. Executive Summary & Vision

**Make Up Your Mind** is an AI-powered cognitive decision-making assistant specifically designed for neurodiverse individuals and those experiencing decision paralysis, chronic anxiety, obsessive-compulsive tendencies (OCD), or memory challenges.

Traditional generative AI chatbots often fail neurodivergent users when faced with difficult decisions. Standard LLMs frequently output exhaustive lists of pros and cons, hedge with open-ended ambiguity (*"there are many factors to consider..."*), and present overwhelming choices. For someone experiencing anxiety or OCD, this amplifies rumination loops, catastrophic forecasting, and decision paralysis.

**Make Up Your Mind** re-engineers this experience by combining:
1. **Condition-adaptive cognitive prompt engineering** (time-boxing, worst-case reframing, structured repetition, and manageable step-by-step action plans).
2. **Persistent user profile and contextual memory** (storing free-text conditions, background, and personal concerns).
3. **Decision tracking with a closed-loop outcome check-in** (logging how choices actually turned out to build confidence over time).
4. **Fast analytical evidence retrieval** using local DuckDB and Parquet datasets for grounded, objective facts.

---

## 2. Problem Statement & User Pain Points

| Condition / Struggle | Standard Chatbot Failure Mode | Make Up Your Mind Solution |
| :--- | :--- | :--- |
| **Anxiety & Fear of Regret** | Provides too many hypothetical scenarios, exacerbating catastrophic "what if" thinking. | Reframes worst-case scenarios realistically, limits choices to 1–2 actionable options, clearly contrasts short vs. long-term outcomes, and offers calm, grounded reassurance. |
| **OCD & Rumination Loops** | Engages in indefinite reassurance-seeking conversations and deep-dive analysis. | Avoids feeding reassurance loops, enforces explicit decision **time-boxing** (e.g., *"this decision only needs 5 minutes of thought"*), and delivers definitive guidance. |
| **Memory Loss & Executive Dysfunction** | Produces dense paragraphs where key takeaways and context are easily lost. | Uses concise, direct language, repeats critical anchors throughout the message, and ends with an explicit summary checklist. |
| **Lack of Follow-through** | Decisions are forgotten once the chat window closes. | Tracks decision history and enables users to record the **actual outcome** later, reinforcing self-efficacy when things turn out fine. |

---

## 3. Target User Personas

### Persona 1: Anxious Alex (21, University Student)
* **Profile**: Struggles with major academic and social decisions (e.g., dropping a course, choosing housing, switching majors).
* **Pain Point**: Spends hours agonizing over worst-case scenarios and feeling paralyzed by regret before the decision is even made.
* **Goal**: Needs a compassionate sounding board that breaks decisions down into manageable micro-steps and dispels irrational catastrophes.

### Persona 2: Rumination Riley (28, Software Professional)
* **Profile**: Diagnosed with OCD; prone to circular research loops, seeking reassurance, and over-analyzing minor everyday choices.
* **Pain Point**: Gets trapped comparing dozens of options and asking friends for repeated reassurance.
* **Goal**: Needs a system that will not indulge compulsive over-analysis, establishes clear time boundaries, and helps make a definitive pick.

### Persona 3: Overwhelmed Morgan (34, Freelancer with ADHD / Brain Fog)
* **Profile**: Experiences cognitive fatigue, working memory bottlenecks, and sensory overwhelm.
* **Pain Point**: Forgets the core constraints mid-deliberation; feels inundated by wall-of-text responses.
* **Goal**: Needs bite-sized clarity, continuous reinforcement of key criteria, and a concise summary checklist at the end of every answer.

---

## 4. Key Value Propositions & Features

### 4.1 Condition-Adaptive Prompt Orchestration
* Automatically tailors the system prompt based on the user's declared condition (`anxiety`, `ocd`, `memory`, or general).
* Employs specialized clinical communication strategies:
  * **Anxiety Strategy**: Manageable steps, realistic risk assessment, reassurance without false guarantees.
  * **OCD Strategy**: Strict time-boxing, anti-rumination guardrails, decisive conclusions.
  * **Memory Strategy**: Periodic repetition of salient anchors, simplified prose, closing action summary.

### 4.2 Persistent Profile & Longitudinal Context
* Stores persistent personal context: `name`, `condition`, `about_me`, and `concerns`.
* Automatically injects past decisions into future prompts so the assistant remembers recurring themes, historical preferences, and past dilemmas.

### 4.3 Decision Lifecycle & Outcome Verification
* **Phase 1: Decision Generation** — User submits a question; Gemini analyzes user context and logs the recommendation (`outcome = null`).
* **Phase 2: Outcome Check-In** — At a later date, the user updates the decision with the real-world outcome (`POST /outcome`).
* **Phase 3: Reinforcement** — Future prompts learn from what actually happened, grounding the user in evidence that previous difficult choices worked out.

### 4.4 Embedded Analytical Evidence Engine
* Integrates an embedded DuckDB analytical layer querying columnar Parquet datasets.
* Provides non-judgmental, grounded empirical data (e.g., housing costs, relocation tradeoffs, job market statistics, education access) to counterbalance emotional cognitive distortions.

---

## 5. Functional Requirements

### 5.1 Profile Management (Data Service)
* **FR-1.1**: The system must allow creating a user profile with `name`, `condition`, `about_me`, and `concerns`.
* **FR-1.2**: All profile fields must be trimmed of extraneous whitespace and validated for non-empty content.
* **FR-1.3**: The system must return profile data via `GET /user/{user_id}` formatted for prompt consumption.

### 5.2 Conversational AI Gateway (`/chat`)
* **FR-2.1**: Accept `user_id`, `message`, `condition`, `about_me`, and `concerns`.
* **FR-2.2**: Fetch existing profile and decision history from the database service before constructing the LLM prompt.
* **FR-2.3**: Retrieve relevant research evidence via `/evidence` based on condition and concerns; fail gracefully (empty evidence) if the data store is unreachable.
* **FR-2.4**: Generate responses using the Google GenAI SDK (`gemini-3.1-pro-preview` / `gemini-3.8-flash`).
* **FR-2.5**: Record the generated response and user question to the database service via `POST /decision`.

### 5.3 History & Outcome Tracking
* **FR-3.1**: Return decisions for a user ordered newest first (`timestamp DESC, id DESC`).
* **FR-3.2**: Enable users to update `outcome` for any existing decision ID.
* **FR-3.3**: Ensure foreign keys are strictly enforced so decisions cannot be orphaned without a valid `user_id`.

### 5.4 Analytical Evidence Search
* **FR-4.1**: Accept free-text query strings, strip common English stop-words, and tokenize search keywords.
* **FR-4.2**: Execute Parquet unnested token matching inside DuckDB to score and rank relevant evidence items.
* **FR-4.3**: Provide source attribution tags (e.g., `public_dataset.parquet#1`) for all returned evidence records.

---

## 6. Non-Functional Requirements

### 6.1 Performance & Scalability
* **Database Latency**: SQLite point lookups by primary key must complete in under 5ms.
* **Analytical Queries**: DuckDB Parquet keyword searches must execute in under 50ms for local datasets.
* **Concurrency**: SQLite must operate with `check_same_thread=False` and connection pools capable of handling multi-threaded FastAPI workers.

### 6.2 Reliability & Fault Tolerance
* If the analytical evidence engine fails or returns no matches, the AI Gateway must continue execution smoothly without throwing a 500 error to the client.
* Schema auto-migration must preserve existing user IDs and historical decision records during upgrades.

### 6.3 Security & Privacy
* Local `.env` credentials (`GEMINI_API_KEY`) must never be committed to source control.
* Parquet file access must enforce strict whitelist regex (`^[A-Za-z0-9_-]+$`) to prevent directory traversal attacks.
* CORS headers must be restricted to authorized local frontend development ports (`3000`, `5173`) in development.

---

## 7. Technical Roadmap

```
├── Phase 1: Core Dual Microservice Architecture (Completed)
│   ├── SQLite persistence for Users, Decisions, Outcomes
│   ├── Condition prompt routing (Anxiety, OCD, Memory)
│   ├── DuckDB Parquet evidence search engine
│   └── Automated zero-data-loss schema migration
│
├── Phase 2: Client Application & User Interface (Next Step)
│   ├── Modern React / Vite frontend
│   ├── Conversational UI with condition selection
│   ├── Interactive Decision History timeline
│   └── "Check-In" modal for outcome updates
│
├── Phase 3: Voloridge Evidence Corpus Expansion
│   ├── Automated ingestion pipeline for real-world statistical benchmarks
│   ├── Semantic embedding search complementing keyword matching
│   └── Multi-source citation displays
│
└── Phase 4: Long-Term Behavioral Insights
    ├── "Outcome Calibration" score (reflecting how often worst-case fears did not occur)
    ├── Exportable decision logs for therapy sessions
    └── Offline local model fallback (e.g. Gemma via llama.cpp)
```
