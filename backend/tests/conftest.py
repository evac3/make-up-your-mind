import pytest
from fastapi.testclient import TestClient

from app.database import build_engine
from app.duckdb_service import DuckDBService
from app.main import create_app


@pytest.fixture
def application(tmp_path):
    engine = build_engine(f"sqlite:///{(tmp_path / 'app.db').as_posix()}")
    service = DuckDBService(
        db_path=tmp_path / "analytics.duckdb",
        parquet_dir=tmp_path / "parquet",
        dataset_path=tmp_path / "public_dataset.parquet",
    )
    application = create_app(db_engine=engine, duckdb_service=service)
    yield application
    engine.dispose()


@pytest.fixture
def client(application):
    # Entering TestClient runs the same startup and shutdown as the server.
    with TestClient(application) as client:
        yield client
