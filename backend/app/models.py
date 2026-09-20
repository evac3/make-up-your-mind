from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    condition = Column(Text, nullable=False)
    about_me = Column(Text, nullable=False)
    concerns = Column(Text, nullable=False)

    decisions = relationship("Decision", back_populates="user")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    outcome = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    user = relationship("User", back_populates="decisions")

    __table_args__ = (Index("ix_decisions_user_timestamp", "user_id", "timestamp"),)
