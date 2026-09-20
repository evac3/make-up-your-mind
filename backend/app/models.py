from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    # Auth fields (nullable so existing rows survive migration)
    email = Column(String(255), nullable=True, unique=True)
    phone_number = Column(String(50), nullable=True, unique=True)
    password_hash = Column(String(255), nullable=True)
    # Healthcare profile (retained for AI prompt routing)
    condition = Column(Text, nullable=False, server_default="")
    about_me = Column(Text, nullable=False, server_default="")
    concerns = Column(Text, nullable=False, server_default="")
    # Finch-style editable traits (JSON array stored as text, e.g. '["anxiety","student"]')
    traits = Column(Text, nullable=True)

    decisions = relationship("Decision", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    conversations = relationship("Conversation", back_populates="user")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    # Appearance
    appearance = Column(String(10), nullable=False, default="light")
    # Notification check-ins
    notifications_email = Column(Boolean, nullable=False, default=True)
    notifications_text = Column(Boolean, nullable=False, default=True)
    notifications_app = Column(Boolean, nullable=False, default=True)
    # Accessibility (important for cognitive & memory conditions)
    accessibility_large_text = Column(Boolean, nullable=False, default=False)
    accessibility_tts = Column(Boolean, nullable=False, default=False)
    # Privacy: when False the AI gateway must not log decisions
    privacy_save_chats = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="settings")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # AI-generated topic label shown in the Saved Conversations screen
    topic = Column(String(500), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="conversations")
    decisions = relationship(
        "Decision",
        back_populates="conversation",
        order_by="Decision.timestamp",
    )


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # nullable: standalone decisions (not part of a multi-turn conversation) allowed
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    # Outcome recorded at a later check-in (Finch-style follow-up)
    outcome = Column(Text, nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="decisions")
    conversation = relationship("Conversation", back_populates="decisions")

    __table_args__ = (Index("ix_decisions_user_timestamp", "user_id", "timestamp"),)
