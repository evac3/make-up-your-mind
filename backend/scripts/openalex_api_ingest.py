#!/usr/bin/env python3
"""
Fast OpenAlex API ingestion — uses the REST API instead of scanning S3.
Gets top-cited mental health research in minutes, not hours.

Usage:
    pip install requests pandas pyarrow
    python scripts/openalex_api_ingest.py --output data/public_dataset.parquet
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import pandas as pd
import requests

LOG = logging.getLogger("openalex_api")

# OpenAlex concept IDs for mental health topics
# Trimmed to core topics matching app conditions — fast hackathon build
SEARCH_QUERIES = [
    ("anxiety disorder treatment", "anxiety"),
    ("obsessive compulsive disorder therapy", "ocd"),
    ("memory loss cognitive decline", "memory"),
    ("cognitive behavioral therapy", "cbt"),
    ("decision making psychology", "decision_making"),
    ("mindfulness mental health", "mindfulness"),
]

API_BASE = "https://api.openalex.org/works"

# Polite pool — OpenAlex gives faster responses with a contact email
HEADERS = {
    "User-Agent": "MakeUpYourMind/1.0 (hackathon project)",
}


def fetch_works(query: str, category: str, per_page: int = 50, pages: int = 1) -> list[dict]:
    """Fetch works from OpenAlex API for a search query."""
    records = []
    for page in range(1, pages + 1):
        params = {
            "search": query,
            "filter": "cited_by_count:>4,has_abstract:true,language:en",
            "sort": "cited_by_count:desc",
            "per_page": per_page,
            "page": page,
        }
        try:
            resp = requests.get(API_BASE, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            for work in results:
                abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
                if not abstract or len(abstract) < 50:
                    continue
                # Extract concept keywords
                concepts = work.get("concepts", [])
                concept_names = " ".join(
                    c.get("display_name", "") for c in concepts[:10]
                    if isinstance(c, dict)
                )
                title = work.get("title", "") or ""
                records.append({
                    "title": title[:300],
                    "category": category,
                    "summary": abstract[:1000],
                    "keywords": f"{concept_names} {title}".lower()[:500],
                })
            LOG.info("  [%s] page %d: got %d works", category, page, len(results))
            # Be polite — small delay between requests
            time.sleep(0.2)
        except Exception as e:
            LOG.warning("  [%s] page %d failed: %s", category, page, e)
            break
    return records


def reconstruct_abstract(inverted_index: dict | None) -> str:
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    try:
        max_pos = max(pos for positions in inverted_index.values() for pos in positions)
        words = [""] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                if pos <= max_pos:
                    words[pos] = word
        return " ".join(w for w in words if w)
    except (ValueError, TypeError):
        return ""


def main():
    parser = argparse.ArgumentParser(description="Fast OpenAlex API evidence ingestion")
    parser.add_argument("--output", "-o", type=Path,
                        default=Path(__file__).resolve().parent.parent / "data" / "public_dataset.parquet")
    parser.add_argument("--pages-per-topic", type=int, default=1,
                        help="Pages to fetch per topic (50 results/page, default: 1)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    LOG.info("=" * 50)
    LOG.info("OpenAlex API → Evidence Pipeline (FAST MODE)")
    LOG.info("=" * 50)
    LOG.info("Topics: %d searches", len(SEARCH_QUERIES))
    LOG.info("Pages per topic: %d (up to %d results each)", args.pages_per_topic, args.pages_per_topic * 200)
    LOG.info("Output: %s", args.output)

    all_records = []
    for query, category in SEARCH_QUERIES:
        LOG.info("Fetching: %s", query)
        records = fetch_works(query, category, pages=args.pages_per_topic)
        all_records.extend(records)
        LOG.info("  → %d records (total so far: %d)", len(records), len(all_records))

    if not all_records:
        LOG.error("No records fetched! Check network connectivity.")
        return

    # Deduplicate by title
    df = pd.DataFrame(all_records)
    df = df.drop_duplicates(subset=["title"], keep="first").reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)

    LOG.info("=" * 50)
    LOG.info("DONE!")
    LOG.info("Total evidence records: %d", len(df))
    LOG.info("Categories:\n%s", df["category"].value_counts().to_string())
    LOG.info("Output: %s", args.output)
    LOG.info("=" * 50)


if __name__ == "__main__":
    main()
