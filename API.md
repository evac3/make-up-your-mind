# REST API Specification

This document details all HTTP endpoints exposed by the **Make Up Your Mind** backend ecosystem.

---

## Service Overview

The backend is composed of two coordinated FastAPI services:
* **AI Gateway Service** (`http://localhost:8000`): Conversational endpoint orchestrating condition prompts, Google Gemini reasoning, and decision tracking.
* **Database & Analytics Service** (`http://localhost:8001`): Persistent data layer for users, decisions, outcomes, and analytical research evidence.

---

## 1. AI Gateway Endpoints (Port 8000)

### 1.1 Process User Chat & Generate Decision
* **Route:** `POST /chat`
* **Description:** Ingests user input, retrieves user background and past decision history, selects a cognitive prompt strategy (Anxiety, OCD, Memory loss, or Default), queries relevant evidence, requests reasoning from Google Gemini, and records the interaction.

#### Request Body
```json
{
  "user_id": 1,
  "message": "Should I accept the new job offer in Chicago or stay at my current remote role?",
  "condition": "I have anxiety and struggle with big life changes",
  "about_me": "Early career developer, living near family",
  "concerns": "Fear of feeling isolated and regretting moving"
}
```

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | Integer | Yes | Unique ID of the registered user. |
| `message` | String | Yes | The user's specific dilemma or question. |
| `condition` | String | Yes | Declared condition (e.g., contains `anxiety`, `ocd`, or `memory`). |
| `about_me` | String | No | Background context (defaults to `""`). |
| `concerns` | String | No | Specific fears or pain points (defaults to `""`). |

#### Response (`200 OK`)
```json
{
  "response": "Let's break this choice down step-by-step to avoid feeling overwhelmed...\n\n1. Short-Term vs. Long-Term Impact: ..."
}
```

#### Error Responses
* `503 Service Unavailable`: Raised if the Database Service at `http://localhost:8001` is unreachable when fetching profile or saving decisions.

---

## 2. Database & Analytics Endpoints (Port 8001)

### 2.1 Health Check & Root
* **`GET /`**: Returns basic service information.
  ```json
  {"app": "make-up-your-mind", "status": "running"}
  ```
* **`GET /health`**: Health status probe.
  ```json
  {"status": "ok"}
  ```

---

### 2.2 Create User Profile
* **Route:** `POST /user`
* **Description:** Registers a new user profile.

#### Request Body
```json
{
  "name": "Alex",
  "condition": "Anxiety and panic disorder",
  "about_me": "College student balancing studies and a part-time job",
  "concerns": "Over-analyzing choices and fearing catastrophic outcomes"
}
```

#### Response (`200 OK`)
```json
{
  "user_id": 1,
  "message": "Profile created successfully"
}
```

#### Error Responses
* `422 Unprocessable Entity`: Raised if any required field is missing or contains only whitespace.

---

### 2.3 Get User Profile
* **Route:** `GET /user/{user_id}`
* **Description:** Retrieves the user profile by ID.

#### Response (`200 OK`)
```json
{
  "id": 1,
  "name": "Alex",
  "condition": "Anxiety and panic disorder",
  "about_me": "College student balancing studies and a part-time job",
  "concerns": "Over-analyzing choices and fearing catastrophic outcomes"
}
```

#### Error Responses
* `404 Not Found`: `{"detail": "user not found"}`

---

### 2.4 Store a Decision
* **Route:** `POST /decision`
* **Description:** Logs a decision question and the AI's generated response for a user.

#### Request Body
```json
{
  "user_id": 1,
  "message": "Should I drop my calculus course before the refund deadline?",
  "ai_response": "Let's evaluate the realistic consequences: 1. Your GPA is preserved..."
}
```

#### Response (`200 OK`)
```json
{
  "id": 4,
  "message": "Should I drop my calculus course before the refund deadline?",
  "ai_response": "Let's evaluate the realistic consequences: 1. Your GPA is preserved...",
  "outcome": null,
  "timestamp": "2026-09-19T21:45:00Z"
}
```

#### Error Responses
* `404 Not Found`: If `user_id` does not exist in the database.

---

### 2.5 Get Decision History
* **Route:** `GET /history/{user_id}`
* **Description:** Retrieves all prior decisions for a specific user, sorted from newest to oldest.

#### Response (`200 OK`)
```json
{
  "decisions": [
    {
      "id": 4,
      "message": "Should I drop my calculus course before the refund deadline?",
      "ai_response": "Let's evaluate the realistic consequences...",
      "outcome": "I dropped the course and retook it during summer with an A.",
      "timestamp": "2026-09-19T21:45:00Z"
    },
    {
      "id": 1,
      "message": "Should I move to an off-campus apartment?",
      "ai_response": "Here is a comparison between commute and living cost...",
      "outcome": null,
      "timestamp": "2026-09-15T14:20:00Z"
    }
  ]
}
```

---

### 2.6 Record Decision Outcome
* **Route:** `POST /outcome`
* **Description:** Records or updates the real-world outcome of a past decision.

#### Request Body
```json
{
  "decision_id": 4,
  "outcome": "I dropped the course and retook it during summer with an A."
}
```

#### Response (`200 OK`)
```json
{
  "decision_id": 4,
  "outcome": "I dropped the course and retook it during summer with an A.",
  "message": "Outcome updated successfully"
}
```

#### Error Responses
* `404 Not Found`: `{"detail": "decision not found"}`

---

### 2.7 Analytical Evidence Search
* **Route:** `GET /evidence`
* **Query Parameters:**
  * `query` (String, required): Search query keywords.

#### Example Request
```http
GET /evidence?query=housing+rent+costs+city
```

#### Response (`200 OK`)
```json
[
  {
    "id": 1,
    "title": "Housing costs",
    "category": "economics",
    "summary": "Median rent and housing affordability vary significantly by city and region.",
    "keywords": "housing cost rent affordability city",
    "source": "public_dataset.parquet#1"
  }
]
```
