from __future__ import annotations

from pathlib import Path

from fastapi import Request
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import declarative_base

from app.config import BASE_DIR

Base = declarative_base()


def build_engine(database_url: str) -> Engine:
    """Configure SQLite consistently for the application and isolated tests."""
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite":
        raise ValueError("This data layer requires a SQLite DATABASE_URL")
    if url.database and url.database != ":memory:":
        path = Path(url.database).expanduser()
        if not path.is_absolute():
            path = BASE_DIR / path
        url = url.set(database=str(path))
    options = {}
    if not url.database or url.database == ":memory:":
        from sqlalchemy.pool import StaticPool

        options["poolclass"] = StaticPool
    engine = create_engine(url, connect_args={"check_same_thread": False}, **options)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _sqlite_table_columns(engine: Engine, table_name: str) -> set[str]:
    with engine.begin() as connection:
        rows = connection.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _rebuild_tables(engine: Engine, user_columns: set[str], decision_columns: set[str]) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql("ALTER TABLE users RENAME TO users_legacy")
        connection.exec_driver_sql("ALTER TABLE decisions RENAME TO decisions_legacy")
        connection.exec_driver_sql(
            """CREATE TABLE users (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                condition TEXT NOT NULL,
                about_me TEXT NOT NULL,
                concerns TEXT NOT NULL
            )"""
        )
        connection.exec_driver_sql(
            """CREATE TABLE decisions (
                id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                outcome TEXT,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users (id)
            )"""
        )
        condition = "COALESCE(condition, '')" if "condition" in user_columns else "''"
        about_me = "COALESCE(about_me, '')" if "about_me" in user_columns else "''"
        concerns = "COALESCE(concerns, '')" if "concerns" in user_columns else "''"
        connection.exec_driver_sql(
            f"""INSERT INTO users (id, name, condition, about_me, concerns)
                SELECT id, name, {condition}, {about_me}, {concerns} FROM users_legacy"""
        )
        message = "message" if "message" in decision_columns else "question"
        timestamp = "timestamp" if "timestamp" in decision_columns else "created_at"
        outcome = "NULLIF(outcome, 'pending')" if "outcome" in decision_columns else "NULL"
        connection.exec_driver_sql(
            f"""INSERT INTO decisions (id, user_id, message, ai_response, outcome, timestamp)
                SELECT id, user_id, {message}, ai_response, {outcome}, {timestamp}
                FROM decisions_legacy"""
        )
        connection.exec_driver_sql("DROP TABLE decisions_legacy")
        connection.exec_driver_sql("DROP TABLE users_legacy")
        connection.exec_driver_sql(
            "CREATE INDEX ix_decisions_user_timestamp ON decisions (user_id, timestamp)"
        )


def init_db(engine: Engine) -> None:
    # Register tables even when initialization is called outside app.main.
    from app import models  # noqa: F401

    if engine.url.database and engine.url.database != ":memory:":
        Path(engine.url.database).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)

    if engine.url.get_backend_name() != "sqlite":
        return

    expected_users = {"id", "name", "condition", "about_me", "concerns"}
    expected_decisions = {"id", "user_id", "message", "ai_response", "outcome", "timestamp"}
    users_columns = _sqlite_table_columns(engine, "users")
    decisions_columns = _sqlite_table_columns(engine, "decisions")
    if users_columns != expected_users or decisions_columns != expected_decisions:
        _rebuild_tables(engine, users_columns, decisions_columns)


def get_db(request: Request):
    with request.app.state.session_factory() as db:
        yield db
