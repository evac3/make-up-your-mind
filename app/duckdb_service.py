from __future__ import annotations

from pathlib import Path
import re

import duckdb
import pandas as pd

from app.config import DUCKDB_PATH, PARQUET_DIR, PUBLIC_DATASET_PATH


class DuckDBService:
    def __init__(
        self,
        db_path: str | Path = DUCKDB_PATH,
        parquet_dir: str | Path = PARQUET_DIR,
        dataset_path: str | Path = PUBLIC_DATASET_PATH,
    ):
        self.db_path = str(db_path)
        self.parquet_dir = Path(parquet_dir)
        self.dataset_path = Path(dataset_path)

    def get_connection(self):
        """Return a live DuckDB connection for SQL queries against the analytical store."""
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(self.db_path)

    def _parquet_path(self, name: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise ValueError("Parquet names may contain only letters, numbers, underscores, and hyphens")
        return self.parquet_dir / f"{name}.parquet"

    def write_parquet(self, df: pd.DataFrame, name: str):
        """Write a pandas DataFrame to a Parquet file under the project data directory."""
        path = self._parquet_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        return path

    def read_parquet(self, name: str) -> pd.DataFrame:
        """Read a Parquet file back into a DataFrame if it exists."""
        path = self._parquet_path(name)
        if not path.exists():
            return pd.DataFrame()
        return pd.read_parquet(path)

    def ensure_public_dataset(self) -> Path:
        """Create demo evidence when missing; Voloridge ingestion is added separately."""
        if not self.dataset_path.exists():
            sample_rows = [
                {
                    "id": 1,
                    "title": "Housing costs",
                    "category": "economics",
                    "summary": "Median rent and housing affordability vary significantly by city and region.",
                    "keywords": "housing cost rent affordability city",
                },
                {
                    "id": 2,
                    "title": "Job market",
                    "category": "career",
                    "summary": "Remote work and emerging industries can change the value of relocation decisions.",
                    "keywords": "job market remote work relocation career growth",
                },
                {
                    "id": 3,
                    "title": "Lifestyle fit",
                    "category": "quality_of_life",
                    "summary": "Daily routines, social support, and transportation shape whether a move feels sustainable.",
                    "keywords": "lifestyle fit commute community transportation",
                },
                {
                    "id": 4,
                    "title": "Education access",
                    "category": "family",
                    "summary": "School quality, childcare, and local amenities can outweigh pure cost calculations.",
                    "keywords": "education school childcare family amenities",
                },
            ]
            df = pd.DataFrame(sample_rows)
            self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(self.dataset_path, index=False)
        return self.dataset_path

    def search_evidence(self, query: str, limit: int = 5):
        """Rank evidence by distinct matching words, ignoring common question words."""
        stop_words = {
            "a", "an", "and", "are", "as", "at", "be", "by", "can", "could", "do",
            "for", "from", "has", "have", "how", "i", "if", "in", "is", "it", "me",
            "my", "of", "on", "or", "our", "should", "that", "the", "their", "this",
            "to", "was", "we", "what", "when", "where", "whether", "which", "who",
            "will", "with", "would", "you", "your", "am",
        }
        terms = sorted(set(re.findall(r"[a-z0-9]+", query.lower())) - stop_words)
        if not terms or limit <= 0:
            return []
        path = self.ensure_public_dataset()
        with self.get_connection() as con:
            rows = con.execute(
                """
                WITH terms AS (SELECT unnest(?::VARCHAR[]) AS term),
                matches AS (
                    SELECT id, title, category, summary, keywords, count(*) AS score
                    FROM read_parquet(?) CROSS JOIN terms
                    WHERE list_contains(
                        regexp_extract_all(lower(concat_ws(' ', title, summary, keywords)), '[a-z0-9]+'),
                        term
                    )
                    GROUP BY id, title, category, summary, keywords
                )
                SELECT id, title, category, summary, keywords
                FROM matches
                ORDER BY score DESC, id
                LIMIT ?
                """,
                [terms, str(path), limit],
            ).fetchdf()
        return [
            {**row, "source": f"{path.name}#{row['id']}"}
            for row in rows.to_dict(orient="records")
        ]

    def query(self, sql: str):
        with self.get_connection() as con:
            return con.execute(sql).fetchdf()
