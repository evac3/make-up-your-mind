from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    condition: str = Field(..., min_length=1)
    about_me: str = Field(..., min_length=1)
    concerns: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    condition: str
    about_me: str
    concerns: str


class UserCreatedResponse(BaseModel):
    user_id: int
    message: str = "Profile created successfully"


class DecisionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: int
    message: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    ai_response: str
    outcome: str | None = None
    timestamp: datetime


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
