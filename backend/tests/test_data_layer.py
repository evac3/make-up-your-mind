import json
import os
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.database import build_engine, init_db
from app.duckdb_service import DuckDBService
from app.main import create_app
from app.models import Decision


def test_foreign_keys_enforced(client, application):
    with application.state.session_factory() as db:
        db.add(Decision(user_id=999, message="Orphan", ai_response="Answer"))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    # A second physical connection must enforce the same constraint.
    with application.state.engine.connect() as first, application.state.engine.connect() as second:
        assert first.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
        assert second.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


def test_data_survives_app_restart(application):
    with TestClient(application) as client:
        created = client.post("/user", json={
            "name": "Alice",
            "condition": "Anxiety",
            "about_me": "College student",
            "concerns": "Regretting decisions",
        }).json()
        user_id = created["user_id"]
        user = client.get(f"/user/{user_id}").json()
        decision = client.post("/decision", json={
            "user_id": user_id, "message": "Question", "ai_response": "Answer",
        }).json()
        client.post("/outcome", json={
            "decision_id": decision["id"], "outcome": "accepted",
        })
    restarted = create_app(
        db_engine=build_engine(str(application.state.engine.url)),
        duckdb_service=application.state.duckdb_service,
    )
    with TestClient(restarted) as client:
        assert client.get(f"/user/{user_id}").json() == user
        saved = client.get(f"/history/{user_id}").json()["decisions"]
        assert len(saved) == 1
        assert saved[0]["id"] == decision["id"]
        assert saved[0]["outcome"] == "accepted"


def test_parquet_round_trip_and_search_ranking(tmp_path):
    service = DuckDBService(tmp_path / "db" / "analytics.duckdb", tmp_path / "exports", tmp_path / "input" / "evidence.parquet")
    frame = pd.DataFrame([
        {"id": 1, "title": "Housing", "category": "demo", "summary": "Rent", "keywords": "housing"},
        {"id": 2, "title": "Housing costs", "category": "demo", "summary": "Compare rent", "keywords": "housing costs city"},
    ])
    path = service.write_parquet(frame, "round_trip")
    assert path == tmp_path / "exports" / "round_trip.parquet"
    pd.testing.assert_frame_equal(service.read_parquet("round_trip"), frame)
    assert service.read_parquet("missing").empty
    service.dataset_path.parent.mkdir()
    frame.to_parquet(service.dataset_path, index=False)
    assert service.ensure_public_dataset() == service.dataset_path
    pd.testing.assert_frame_equal(pd.read_parquet(service.dataset_path), frame)
    rows = service.search_evidence("Should I compare housing costs in the city?", limit=1)
    assert [row["id"] for row in rows] == [2]
    assert rows[0]["source"] == "evidence.parquet#2"
    assert service.search_evidence("housing", limit=0) == []
    assert service.query("SELECT 42 AS value").iloc[0]["value"] == 42
    with pytest.raises(ValueError):
        service.write_parquet(frame, "../outside")


def test_configuration_and_import_do_not_create_storage(tmp_path):
    env = os.environ.copy()
    env.update({
        "DATABASE_URL": f"sqlite:///{(tmp_path / 'sqlite' / 'app.db').as_posix()}",
        "DUCKDB_PATH": str(tmp_path / "duck" / "analytics.duckdb"),
        "PARQUET_DIR": str(tmp_path / "exports"),
        "PUBLIC_DATASET_PATH": str(tmp_path / "input" / "evidence.parquet"),
    })
    code = """
import json
from app.main import app
service = app.state.duckdb_service
print(json.dumps([str(app.state.engine.url.database), service.db_path, str(service.parquet_dir), str(service.dataset_path)]))
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True)
    configured = [Path(value) for value in json.loads(result.stdout)]
    assert configured == [tmp_path / "sqlite" / "app.db", tmp_path / "duck" / "analytics.duckdb", tmp_path / "exports", tmp_path / "input" / "evidence.parquet"]
    assert list(tmp_path.iterdir()) == []


def test_relative_sqlite_path_uses_project_root(tmp_path, monkeypatch):
    from app.config import BASE_DIR

    monkeypatch.chdir(tmp_path)
    engine = build_engine("sqlite:///data/app.db")
    assert Path(engine.url.database) == BASE_DIR / "data" / "app.db"
    engine.dispose()


def test_in_memory_sqlite_is_shared_across_request_threads(tmp_path):
    service = DuckDBService(":memory:", tmp_path / "exports", tmp_path / "demo.parquet")
    application = create_app(build_engine("sqlite:///:memory:"), service)
    with TestClient(application) as client:
        created = client.post("/user", json={
            "name": "Memory",
            "condition": "Anxiety",
            "about_me": "Test user",
            "concerns": "Uncertainty",
        }).json()
        profile = client.get(f"/user/{created['user_id']}")
        assert profile.status_code == 200
        assert profile.json()["name"] == "Memory"


def test_database_initialization_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "app.db"
    engine = build_engine(f"sqlite:///{path.as_posix()}")
    try:
        init_db(engine)
        assert path.exists()
        with engine.connect() as connection:
            tables = connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").scalars().all()
            users = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(users)")}
            decisions = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(decisions)")}
        assert set(tables) == {"users", "decisions", "user_settings", "conversations"}
        assert users == {"id", "name", "email", "phone_number", "password_hash", "condition", "about_me", "concerns", "traits"}
        assert decisions == {"id", "user_id", "conversation_id", "message", "ai_response", "outcome", "timestamp"}
    finally:
        engine.dispose()


def test_legacy_schema_is_upgraded_without_changing_ids(tmp_path):
    path = tmp_path / "legacy.db"
    engine = build_engine(f"sqlite:///{path.as_posix()}")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                """CREATE TABLE users (
                    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
                    created_at DATETIME NOT NULL
                )"""
            )
            connection.exec_driver_sql(
                """CREATE TABLE decisions (
                    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL,
                    question TEXT NOT NULL, ai_response TEXT NOT NULL,
                    evidence JSON, outcome TEXT, outcome_notes TEXT,
                    created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )"""
            )
            connection.exec_driver_sql(
                "INSERT INTO users VALUES (7, 'Legacy user', 'legacy@example.com', CURRENT_TIMESTAMP)"
            )
            connection.exec_driver_sql(
                """INSERT INTO decisions VALUES (
                    9, 7, 'Legacy question', 'Legacy answer', '[]', 'pending', '',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )"""
            )

        init_db(engine)

        with engine.connect() as connection:
            profile = connection.exec_driver_sql(
                "SELECT id, name, condition, about_me, concerns FROM users"
            ).one()
            decision = connection.exec_driver_sql(
                "SELECT id, user_id, message, ai_response, outcome FROM decisions"
            ).one()
        assert profile == (7, "Legacy user", "", "", "")
        assert decision == (9, 7, "Legacy question", "Legacy answer", None)
    finally:
        engine.dispose()
