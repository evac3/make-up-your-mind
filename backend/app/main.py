from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import SQLALCHEMY_DATABASE_URL
from app.database import build_engine, get_db, init_db
from app.duckdb_service import DuckDBService
from app.models import Decision, User
from app.schemas import (
    DecisionCreate,
    DecisionResponse,
    HistoryResponse,
    OutcomeCreate,
    OutcomeResponse,
    UserCreate,
    UserCreatedResponse,
    UserResponse,
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
    application = FastAPI(title="Make Up Your Mind", version="0.1.0", lifespan=lifespan)
    application.state.engine = db_engine or build_engine(SQLALCHEMY_DATABASE_URL)
    application.state.session_factory = sessionmaker(
        bind=application.state.engine,
        autoflush=False,
        expire_on_commit=False,
    )
    application.state.duckdb_service = duckdb_service or DuckDBService()

    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/")
    def read_root() -> dict[str, str]:
        return {"app": "make-up-your-mind", "status": "running"}

    @application.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/user", response_model=UserCreatedResponse)
    def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserCreatedResponse:
        user = User(
            name=payload.name.strip(),
            condition=payload.condition.strip(),
            about_me=payload.about_me.strip(),
            concerns=payload.concerns.strip(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserCreatedResponse(user_id=user.id)

    @application.get("/user/{user_id}", response_model=UserResponse)
    def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return UserResponse.model_validate(user)

    @application.post("/decision", response_model=DecisionResponse)
    def create_decision(payload: DecisionCreate, db: Session = Depends(get_db)) -> DecisionResponse:
        if db.get(User, payload.user_id) is None:
            raise HTTPException(status_code=404, detail="user not found")

        decision = Decision(
            user_id=payload.user_id,
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

    # Kept as a separate data-source seam for the later Voloridge integration.
    @application.get("/evidence")
    def get_evidence(
        query: str = Query(..., min_length=1),
        category: str | None = Query(None),
        duckdb_service: DuckDBService = Depends(get_duckdb_service),
    ) -> list[dict[str, Any]]:
        return duckdb_service.search_evidence(query, category=category)

    return application


app = create_app()
