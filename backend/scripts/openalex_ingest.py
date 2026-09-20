#!/usr/bin/env python3
"""
OpenAlex → Make-Up-Your-Mind Evidence Pipeline
===============================================
Run this on the GX10 Ascend (or any machine with network access to S3).

DuckDB queries OpenAlex Parquet snapshots directly from S3 — no AWS
credentials required, no full download necessary.  The script filters for
works relevant to mental health decision-support (anxiety, OCD, memory,
counseling, decision-making) and writes a structured Parquet evidence
file that the backend's DuckDBService.search_evidence() already consumes.

Usage
-----
    # On the GX10 Ascend via SSH:
    pip install duckdb pandas pyarrow tqdm
    python scripts/openalex_ingest.py

    # Override output path (default: data/public_dataset.parquet):
    python scripts/openalex_ingest.py --output /path/to/evidence.parquet

    # Adjust parallelism for the GX10's cores:
    python scripts/openalex_ingest.py --threads 64

    # Dry-run: print SQL, don't execute:
    python scripts/openalex_ingest.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# OpenAlex S3 bucket — publicly accessible, no credentials needed
OPENALEX_S3_WORKS = "s3://openalex/data/parquet/works/*/*.parquet"

# Mental health & decision-support topics to filter on.
# OpenAlex concept IDs (level 1-2) for the domains we care about:
#   - Anxiety, OCD, Depression, Mental health, Decision making,
#     Cognitive behavioral therapy, Counseling psychology, etc.
# We also do a keyword search on titles/abstracts as a fallback.
TOPIC_KEYWORDS = [
    "anxiety",
    "obsessive compulsive",
    "ocd",
    "mental health",
    "decision making",
    "decision support",
    "cognitive behavioral",
    "counseling",
    "psychotherapy",
    "memory loss",
    "dementia",
    "cognitive decline",
    "rumination",
    "indecision",
    "choice overload",
    "behavioral therapy",
    "mindfulness",
    "stress management",
    "emotional regulation",
    "self-determination",
    "psychological wellbeing",
    "coping strategies",
]

# Minimum citation count — filters out very low-quality papers
MIN_CITED_BY_COUNT = 5

# Maximum number of evidence rows to keep (after ranking)
MAX_EVIDENCE_ROWS = 50_000

# Default output path (relative to backend/)
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "public_dataset.parquet"

LOG = logging.getLogger("openalex_ingest")


# ---------------------------------------------------------------------------
# DuckDB setup helpers
# ---------------------------------------------------------------------------

def create_connection(threads: int = 8, memory_limit: str = "8GB") -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection configured for S3 public access."""
    con = duckdb.connect(":memory:")

    # Install and load the httpfs extension for S3 access
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")

    # Configure for public S3 bucket — no credentials
    con.execute("SET s3_region = 'us-east-1';")
    con.execute("SET s3_access_key_id = '';")
    con.execute("SET s3_secret_access_key = '';")
    con.execute("SET s3_url_style = 'path';")

    # Performance tuning for the GX10
    con.execute(f"SET threads = {threads};")
    con.execute(f"SET memory_limit = '{memory_limit}';")

    # Enable progress bar for long queries
    con.execute("SET enable_progress_bar = true;")
    con.execute("SET enable_progress_bar_print = true;")

    LOG.info("DuckDB connection ready (threads=%d, memory=%s)", threads, memory_limit)
    return con


def build_keyword_filter(keywords: list[str]) -> str:
    """Build a SQL WHERE clause that matches any keyword in title or abstract."""
    conditions = []
    for kw in keywords:
        escaped = kw.replace("'", "''")
        conditions.append(
            f"(lower(title) LIKE '%{escaped}%' OR lower(abstract_inverted_index::VARCHAR) LIKE '%{escaped}%')"
        )
    return " OR ".join(conditions)


# ---------------------------------------------------------------------------
# Main extraction query
# ---------------------------------------------------------------------------

def build_extraction_sql(keywords: list[str], min_citations: int, max_rows: int) -> str:
    """
    Build the SQL that queries OpenAlex works on S3 and produces
    evidence rows compatible with the existing DuckDBService schema:
        id, title, category, summary, keywords
    """
    keyword_filter = build_keyword_filter(keywords)

    sql = f"""
    WITH raw_works AS (
        SELECT
            id                                     AS openalex_id,
            title,
            publication_year,
            cited_by_count,
            -- OpenAlex stores abstracts as inverted indexes; cast to string
            -- for keyword matching (full reconstruction happens in Python)
            abstract_inverted_index,
            -- Primary topic gives us a category label
            primary_topic.display_name              AS topic_name,
            primary_topic.subfield.display_name     AS subfield_name,
            primary_topic.field.display_name         AS field_name,
            primary_topic.domain.display_name        AS domain_name,
            -- Journal / source info
            primary_location.source.display_name    AS source_name,
            -- Concepts (legacy but still populated)
            concepts
        FROM read_parquet('{OPENALEX_S3_WORKS}',
                         hive_partitioning = false,
                         union_by_name = true)
        WHERE
            -- Must have a title
            title IS NOT NULL
            AND length(title) > 10
            -- Citation quality gate
            AND cited_by_count >= {min_citations}
            -- Topic/keyword relevance
            AND ({keyword_filter})
    ),
    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER (ORDER BY cited_by_count DESC, publication_year DESC) AS rank
        FROM raw_works
    )
    SELECT *
    FROM ranked
    WHERE rank <= {max_rows}
    ORDER BY rank;
    """
    return sql


# ---------------------------------------------------------------------------
# Abstract reconstruction
# ---------------------------------------------------------------------------

def reconstruct_abstract(inverted_index_str: str | None) -> str:
    """
    OpenAlex stores abstracts as inverted indexes: {"word": [pos1, pos2], ...}
    Reconstruct into readable text.
    """
    if not inverted_index_str:
        return ""
    try:
        inverted = json.loads(inverted_index_str) if isinstance(inverted_index_str, str) else inverted_index_str
        if not isinstance(inverted, dict):
            return str(inverted_index_str)[:500]
        # Find max position to size the array
        max_pos = max(pos for positions in inverted.values() for pos in positions) if inverted else 0
        words = [""] * (max_pos + 1)
        for word, positions in inverted.items():
            for pos in positions:
                if pos <= max_pos:
                    words[pos] = word
        return " ".join(w for w in words if w)
    except (json.JSONDecodeError, TypeError, ValueError):
        return str(inverted_index_str)[:500] if inverted_index_str else ""


def extract_concept_keywords(concepts_str: str | None) -> str:
    """Pull display_name from OpenAlex concepts array and join as keywords."""
    if not concepts_str:
        return ""
    try:
        concepts = json.loads(concepts_str) if isinstance(concepts_str, str) else concepts_str
        if isinstance(concepts, list):
            return " ".join(c.get("display_name", "") for c in concepts if isinstance(c, dict))
        return ""
    except (json.JSONDecodeError, TypeError):
        return ""


# ---------------------------------------------------------------------------
# Post-processing: transform raw OpenAlex rows → evidence schema
# ---------------------------------------------------------------------------

def transform_to_evidence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw OpenAlex query results into the evidence schema expected
    by DuckDBService.search_evidence():
        id (int), title (str), category (str), summary (str), keywords (str)
    """
    LOG.info("Transforming %d raw rows into evidence format...", len(df))

    records = []
    for idx, row in df.iterrows():
        # Reconstruct abstract as the summary
        abstract = reconstruct_abstract(row.get("abstract_inverted_index"))

        # Build a summary: abstract if available, else topic + source
        if abstract and len(abstract) > 50:
            summary = abstract[:1000]  # cap at 1000 chars
        else:
            parts = [
                f"Published in {row.get('publication_year', 'N/A')}",
                f"in {row['source_name']}" if pd.notna(row.get("source_name")) else "",
                f"({row.get('cited_by_count', 0)} citations)",
            ]
            summary = " ".join(p for p in parts if p)

        # Category: use subfield or field from the primary topic
        category = (
            row.get("subfield_name")
            or row.get("field_name")
            or row.get("domain_name")
            or "general"
        )

        # Keywords: combine topic name + concept names + title words
        kw_parts = []
        if pd.notna(row.get("topic_name")):
            kw_parts.append(row["topic_name"])
        concept_kw = extract_concept_keywords(row.get("concepts"))
        if concept_kw:
            kw_parts.append(concept_kw)
        # Add title words as extra keywords
        if pd.notna(row.get("title")):
            kw_parts.append(row["title"].lower())

        records.append({
            "id": idx + 1,
            "title": str(row.get("title", ""))[:300],
            "category": str(category).lower().strip()[:100],
            "summary": summary,
            "keywords": " ".join(kw_parts).lower()[:500],
        })

    result = pd.DataFrame(records)
    LOG.info("Produced %d evidence records", len(result))
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ingest OpenAlex S3 data into the Make-Up-Your-Mind evidence dataset"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output parquet file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=8,
        help="Number of DuckDB threads (match to your CPU cores; GX10 Ascend: try 64+)",
    )
    parser.add_argument(
        "--memory", "-m",
        type=str,
        default="8GB",
        help="DuckDB memory limit (e.g. '32GB' for GX10)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=MAX_EVIDENCE_ROWS,
        help=f"Maximum evidence rows to keep (default: {MAX_EVIDENCE_ROWS})",
    )
    parser.add_argument(
        "--min-citations",
        type=int,
        default=MIN_CITED_BY_COUNT,
        help=f"Minimum citation count filter (default: {MIN_CITED_BY_COUNT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the SQL query without executing",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    sql = build_extraction_sql(TOPIC_KEYWORDS, args.min_citations, args.max_rows)

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN — SQL that would be executed:")
        print("=" * 60)
        print(sql)
        return

    LOG.info("=" * 60)
    LOG.info("OpenAlex → Make-Up-Your-Mind Evidence Pipeline")
    LOG.info("=" * 60)
    LOG.info("Output:        %s", args.output)
    LOG.info("Threads:       %d", args.threads)
    LOG.info("Memory limit:  %s", args.memory)
    LOG.info("Max rows:      %d", args.max_rows)
    LOG.info("Min citations: %d", args.min_citations)
    LOG.info("Keywords:      %d topic filters", len(TOPIC_KEYWORDS))
    LOG.info("=" * 60)

    # Step 1: Connect to DuckDB with S3 support
    con = create_connection(threads=args.threads, memory_limit=args.memory)

    # Step 2: Run the extraction query against OpenAlex on S3
    LOG.info("Querying OpenAlex S3 Parquet files (this may take a while)...")
    t0 = time.time()
    try:
        raw_df = con.execute(sql).fetchdf()
    except Exception as e:
        LOG.error("Query failed: %s", e)
        LOG.info("Tip: On the GX10, make sure network access to S3 is available.")
        LOG.info("Try: aws s3 ls s3://openalex/data/parquet/works/ --no-sign-request")
        sys.exit(1)
    elapsed = time.time() - t0
    LOG.info("Query returned %d rows in %.1f seconds", len(raw_df), elapsed)

    if raw_df.empty:
        LOG.warning("No results returned! Check network connectivity to S3.")
        sys.exit(1)

    # Step 3: Transform into evidence schema
    evidence_df = transform_to_evidence(raw_df)

    # Step 4: Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    evidence_df.to_parquet(args.output, index=False)
    LOG.info("Wrote %d evidence records to %s", len(evidence_df), args.output)

    # Print summary stats
    LOG.info("=" * 60)
    LOG.info("SUMMARY")
    LOG.info("=" * 60)
    LOG.info("Total evidence records: %d", len(evidence_df))
    LOG.info("Categories:\n%s", evidence_df["category"].value_counts().head(20).to_string())
    LOG.info("Sample titles:")
    for title in evidence_df["title"].head(5):
        LOG.info("  • %s", title)
    LOG.info("=" * 60)
    LOG.info("Done! Your backend's DuckDBService will now use this richer dataset.")

    con.close()


if __name__ == "__main__":
    main()
