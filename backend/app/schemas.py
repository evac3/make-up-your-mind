from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Legacy / internal schemas (kept for backward compatibility with AI gateway)
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Legacy internal endpoint — AI gateway still uses POST /user."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    condition: str = Field(..., min_length=1)
    about_me: str = Field(..., min_length=1)
    concerns: str = Field(..., min_length=1)


class UserCreatedResponse(BaseModel):
    user_id: int
    message: str = "Profile created successfully"


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=3)
    phone_number: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=6)
    # Optional healthcare onboarding fields
    condition: str = Field(default="")
    about_me: str = Field(default="")
    concerns: str = Field(default="")
    traits: list[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # Either email or phone_number must be provided
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def require_email_or_phone(self) -> "LoginRequest":
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone_number must be provided")
        return self


class LoginResponse(BaseModel):
    user_id: int
    name: str
    message: str = "Login successful"


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Full profile returned to the frontend and to the AI gateway."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    condition: str
    about_me: str
    concerns: str
    traits: list[str] = Field(default_factory=list)

    @field_validator("traits", mode="before")
    @classmethod
    def parse_traits(cls, v: object) -> list[str]:
        """Deserialize the JSON-encoded traits string from SQLite."""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        try:
            parsed = json.loads(v)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            return []


class UserUpdate(BaseModel):
    """Only name, password, and traits are editable — email & phone are immutable."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    password: Optional[str] = Field(default=None, min_length=6)
    condition: Optional[str] = None
    about_me: Optional[str] = None
    concerns: Optional[str] = None
    traits: Optional[list[str]] = None


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    appearance: str
    notifications_email: bool
    notifications_text: bool
    notifications_app: bool
    accessibility_large_text: bool
    accessibility_tts: bool
    privacy_save_chats: bool


class UserSettingsUpdate(BaseModel):
    appearance: Optional[str] = Field(default=None, pattern="^(light|dark)$")
    notifications_email: Optional[bool] = None
    notifications_text: Optional[bool] = None
    notifications_app: Optional[bool] = None
    accessibility_large_text: Optional[bool] = None
    accessibility_tts: Optional[bool] = None
    privacy_save_chats: Optional[bool] = None


# ---------------------------------------------------------------------------
# Conversations (multi-turn chat sessions)
# ---------------------------------------------------------------------------

class ConversationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: int
    topic: str = Field(..., min_length=1, max_length=500)
    # First message and its AI response (optional — topic-only creation also allowed)
    message: Optional[str] = None
    ai_response: Optional[str] = None


class ConversationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    updated_at: datetime
    message_count: int = 0


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    created_at: datetime
    updated_at: datetime
    messages: list["DecisionResponse"] = Field(default_factory=list)


class MessageCreate(BaseModel):
    """Append a follow-up question/answer to an existing conversation."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: int
    message: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Decisions (retained in full for AI gateway & outcome check-ins)
# ---------------------------------------------------------------------------

class DecisionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: int
    message: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    ai_response: str
    outcome: Optional[str] = None
    timestamp: datetime
    conversation_id: Optional[int] = None


class OutcomeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    decision_id: int
    outcome: str = Field(..., min_length=1)


class OutcomeResponse(BaseModel):
    decision_id: int
    outcome: str
    message: str = "Outcome updated successfully"


class HistoryResponse(BaseModel):
    decisions: list[DecisionResponse]
