from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
import json
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password, verify_password
from app.config import SQLALCHEMY_DATABASE_URL
from app.database import build_engine, get_db, init_db
from app.duckdb_service import DuckDBService
from app.models import Conversation, Decision, User, UserSettings
from app.schemas import (
    ConversationCreate,
    ConversationListItem,
    ConversationResponse,
    DecisionCreate,
    DecisionResponse,
    HistoryResponse,
    LoginRequest,
    LoginResponse,
    MessageCreate,
    OutcomeCreate,
    OutcomeResponse,
    SignupRequest,
    UserCreate,
    UserCreatedResponse,
    UserResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
    UserUpdate,
)


def get_duckdb_service(request: Request) -> DuckDBService:
    return request.app.state.duckdb_service


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db(application.state.engine)
    application.state.duckdb_service.ensure_public_dataset()
    yield


def create_app(
    db_engine: Engine | None = None,
    duckdb_service: DuckDBService | None = None,
) -> FastAPI:
    application = FastAPI(title="Make Up Your Mind", version="0.2.0", lifespan=lifespan)
    application.state.engine = db_engine or build_engine(SQLALCHEMY_DATABASE_URL)
    application.state.session_factory = sessionmaker(
        bind=application.state.engine,
        autoflush=False,
        expire_on_commit=False,
    )
    application.state.duckdb_service = duckdb_service or DuckDBService()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Operational Endpoints ────────────────────────────────────────────────
    @application.get("/")
    def read_root() -> dict[str, str]:
        return {"app": "make-up-your-mind", "status": "running"}

    @application.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    # ── Auth Endpoints ───────────────────────────────────────────────────────
    @application.post("/auth/signup", status_code=status.HTTP_201_CREATED)
    def signup(payload: SignupRequest, db: Session = Depends(get_db)):
        existing_email = db.query(User).filter(User.email == payload.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        existing_phone = db.query(User).filter(User.phone_number == payload.phone_number).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this phone number already exists",
            )

        user = User(
            name=payload.name.strip(),
            email=payload.email.strip().lower(),
            phone_number=payload.phone_number.strip(),
            password_hash=hash_password(payload.password),
            condition=payload.condition.strip(),
            about_me=payload.about_me.strip(),
            concerns=payload.concerns.strip(),
            traits=json.dumps(payload.traits) if payload.traits else None,
        )
        db.add(user)
        db.flush()

        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(user)

        return {"user_id": user.id, "message": "User registered successfully"}

    @application.post("/auth/login", response_model=LoginResponse)
    def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
        user = None
        if payload.email:
            user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
        elif payload.phone_number:
            user = db.query(User).filter(User.phone_number == payload.phone_number.strip()).first()

        if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/phone or password",
            )

        return LoginResponse(user_id=user.id, name=user.name)

    # ── User Profile Endpoints ───────────────────────────────────────────────
    @application.post("/user", response_model=UserCreatedResponse)
    def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserCreatedResponse:
        user = User(
            name=payload.name.strip(),
            condition=payload.condition.strip(),
            about_me=payload.about_me.strip(),
            concerns=payload.concerns.strip(),
        )
        db.add(user)
        db.flush()

        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(user)
        return UserCreatedResponse(user_id=user.id)

    @application.get("/user/{user_id}", response_model=UserResponse)
    def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return UserResponse.model_validate(user)

    @application.patch("/user/{user_id}", response_model=UserResponse)
    def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")

        if payload.name is not None:
            user.name = payload.name.strip()
        if payload.password is not None:
            user.password_hash = hash_password(payload.password)
        if payload.condition is not None:
            user.condition = payload.condition.strip()
        if payload.about_me is not None:
            user.about_me = payload.about_me.strip()
        if payload.concerns is not None:
            user.concerns = payload.concerns.strip()
        if payload.traits is not None:
            user.traits = json.dumps(payload.traits)

        db.commit()
        db.refresh(user)
        return UserResponse.model_validate(user)

    # ── Settings Endpoints ───────────────────────────────────────────────────
    @application.get("/settings/{user_id}", response_model=UserSettingsResponse)
    def get_settings(user_id: int, db: Session = Depends(get_db)) -> UserSettingsResponse:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")

        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if settings is None:
            settings = UserSettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return UserSettingsResponse.model_validate(settings)

    @application.put("/settings/{user_id}", response_model=UserSettingsResponse)
    def update_settings(user_id: int, payload: UserSettingsUpdate, db: Session = Depends(get_db)) -> UserSettingsResponse:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")

        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if settings is None:
            settings = UserSettings(user_id=user_id)
            db.add(settings)

        if payload.appearance is not None:
            settings.appearance = payload.appearance
        if payload.notifications_email is not None:
            settings.notifications_email = payload.notifications_email
        if payload.notifications_text is not None:
            settings.notifications_text = payload.notifications_text
        if payload.notifications_app is not None:
            settings.notifications_app = payload.notifications_app
        if payload.accessibility_large_text is not None:
            settings.accessibility_large_text = payload.accessibility_large_text
        if payload.accessibility_tts is not None:
            settings.accessibility_tts = payload.accessibility_tts
        if payload.privacy_save_chats is not None:
            settings.privacy_save_chats = payload.privacy_save_chats

        db.commit()
        db.refresh(settings)
        return UserSettingsResponse.model_validate(settings)

    # ── Conversations Endpoints ──────────────────────────────────────────────
    @application.get("/conversations/{user_id}", response_model=list[ConversationListItem])
    def get_conversations(user_id: int, db: Session = Depends(get_db)) -> list[ConversationListItem]:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")

        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )
        return [
            ConversationListItem(
                id=c.id,
                topic=c.topic,
                updated_at=c.updated_at,
                message_count=len(c.decisions),
            )
            for c in conversations
        ]

    @application.get("/conversation/{conversation_id}", response_model=ConversationResponse)
    def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> ConversationResponse:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="conversation not found")

        decisions = (
            db.query(Decision)
            .filter(Decision.conversation_id == conversation_id)
            .order_by(Decision.timestamp.asc())
            .all()
        )
        return ConversationResponse(
            id=conversation.id,
            topic=conversation.topic,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[DecisionResponse.model_validate(d) for d in decisions],
        )

    @application.post("/conversation", response_model=ConversationResponse)
    def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)) -> ConversationResponse:
        user = db.get(User, payload.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")

        conversation = Conversation(
            user_id=payload.user_id,
            topic=payload.topic.strip(),
        )
        db.add(conversation)
        db.flush()

        decisions = []
        if payload.message and payload.ai_response:
            decision = Decision(
                user_id=payload.user_id,
                conversation_id=conversation.id,
                message=payload.message.strip(),
                ai_response=payload.ai_response.strip(),
            )
            db.add(decision)
            db.flush()
            decisions.append(decision)

        db.commit()
        db.refresh(conversation)

        return ConversationResponse(
            id=conversation.id,
            topic=conversation.topic,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[DecisionResponse.model_validate(d) for d in decisions],
        )

    @application.post("/conversation/{conversation_id}/message", response_model=DecisionResponse)
    def add_conversation_message(
        conversation_id: int,
        payload: MessageCreate,
        db: Session = Depends(get_db),
    ) -> DecisionResponse:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="conversation not found")

        decision = Decision(
            user_id=payload.user_id,
            conversation_id=conversation_id,
            message=payload.message.strip(),
            ai_response=payload.ai_response.strip(),
        )
        db.add(decision)
        conversation.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(decision)

        return DecisionResponse.model_validate(decision)

    # ── Decisions & Outcomes Endpoints (Preserved) ───────────────────────────
    @application.post("/decision", response_model=DecisionResponse)
    def create_decision(payload: DecisionCreate, db: Session = Depends(get_db)) -> DecisionResponse:
        if db.get(User, payload.user_id) is None:
            raise HTTPException(status_code=404, detail="user not found")

        decision = Decision(
            user_id=payload.user_id,
            conversation_id=payload.conversation_id,
            message=payload.message.strip(),
            ai_response=payload.ai_response.strip(),
        )
        db.add(decision)
        db.commit()
        db.refresh(decision)
        return DecisionResponse.model_validate(decision)

    @application.get("/history/{user_id}", response_model=HistoryResponse)
    def get_history(user_id: int, db: Session = Depends(get_db)) -> HistoryResponse:
        if db.get(User, user_id) is None:
            raise HTTPException(status_code=404, detail="user not found")

        decisions = (
            db.query(Decision)
            .filter(Decision.user_id == user_id)
            .order_by(Decision.timestamp.desc(), Decision.id.desc())
            .all()
        )
        return HistoryResponse(
            decisions=[DecisionResponse.model_validate(decision) for decision in decisions]
        )

    @application.post("/outcome", response_model=OutcomeResponse)
    def update_outcome(payload: OutcomeCreate, db: Session = Depends(get_db)) -> OutcomeResponse:
        decision = db.get(Decision, payload.decision_id)
        if decision is None:
            raise HTTPException(status_code=404, detail="decision not found")

        decision.outcome = payload.outcome.strip()
        db.commit()
        return OutcomeResponse(decision_id=decision.id, outcome=decision.outcome)

    @application.get("/evidence")
    def get_evidence(
        query: str = Query(..., min_length=1),
        duckdb_service: DuckDBService = Depends(get_duckdb_service),
    ) -> list[dict[str, Any]]:
        return duckdb_service.search_evidence(query)

    return application


app = create_app()
