from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def storage_path(name: str, default: Path) -> Path:
    """Resolve configured relative paths against the project root."""
    path = Path(os.getenv(name, str(default))).expanduser()
    return path if path.is_absolute() else BASE_DIR / path


DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(DATA_DIR / "analytics.duckdb"))
if DUCKDB_PATH != ":memory:":
    DUCKDB_PATH = str(storage_path("DUCKDB_PATH", DATA_DIR / "analytics.duckdb"))
PARQUET_DIR = storage_path("PARQUET_DIR", DATA_DIR / "parquet")
PUBLIC_DATASET_PATH = storage_path("PUBLIC_DATASET_PATH", DATA_DIR / "public_dataset.parquet")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
