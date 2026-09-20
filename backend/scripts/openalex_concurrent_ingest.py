#!/usr/bin/env python3
"""
Concurrent OpenAlex ingestion — fetches all topics in parallel.
Run on a fast machine to get a bigger dataset in seconds.

Usage:
    pip install aiohttp pandas pyarrow
    python scripts/openalex_concurrent_ingest.py --output data/public_dataset.parquet
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import time
from pathlib import Path

import aiohttp
import pandas as pd

LOG = logging.getLogger("openalex_concurrent")

# Broader topic list — we can afford it with concurrent fetching
SEARCH_QUERIES = [
    ("anxiety disorder treatment", "anxiety"),
    ("obsessive compulsive disorder therapy", "ocd"),
    ("memory loss cognitive decline", "memory"),
    ("cognitive behavioral therapy", "cbt"),
    ("decision making psychology", "decision_making"),
    ("mindfulness mental health", "mindfulness"),
    ("stress management coping", "stress"),
    ("rumination overthinking", "rumination"),
    ("choice overload decision fatigue", "decision_fatigue"),
    ("depression coping strategies", "depression"),
    ("emotional regulation", "emotional_regulation"),
    ("panic disorder treatment", "panic"),
]

API_BASE = "https://api.openalex.org/works"

HEADERS = {
    "User-Agent": "MakeUpYourMind/1.0 (hackathon project)",
}

# Limit concurrency so we don't hammer the API
MAX_CONCURRENT = 4


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


async def fetch_page(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    query: str,
    category: str,
    page: int,
    per_page: int,
) -> list[dict]:
    """Fetch a single page of results."""
    params = {
        "search": query,
        "filter": "cited_by_count:>4,has_abstract:true,language:en",
        "sort": "cited_by_count:desc",
        "per_page": per_page,
        "page": page,
    }
    records = []
    async with semaphore:
        try:
            async with session.get(API_BASE, params=params, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                results = data.get("results", [])
                for work in results:
                    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
                    if not abstract or len(abstract) < 50:
                        continue
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
                LOG.info("  [%s] page %d: %d usable records", category, page, len(records))
        except Exception as e:
            LOG.warning("  [%s] page %d failed: %s", category, page, e)
    return records


async def run_ingestion(pages_per_topic: int, per_page: int, output: Path):
    """Fire off all fetches concurrently and collect results."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    # Build all (query, category, page) tasks
    tasks = []
    async with aiohttp.ClientSession() as session:
        for query, category in SEARCH_QUERIES:
            for page in range(1, pages_per_topic + 1):
                tasks.append(fetch_page(session, semaphore, query, category, page, per_page))

        LOG.info("Launching %d concurrent fetches (%d topics × %d pages)...",
                 len(tasks), len(SEARCH_QUERIES), pages_per_topic)

        results = await asyncio.gather(*tasks)

    # Flatten
    all_records = [rec for batch in results for rec in batch]

    if not all_records:
        LOG.error("No records fetched! Check network connectivity.")
        return

    # Deduplicate by title
    df = pd.DataFrame(all_records)
    df = df.drop_duplicates(subset=["title"], keep="first").reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output, index=False)

    LOG.info("=" * 50)
    LOG.info("DONE!")
    LOG.info("Total evidence records: %d", len(df))
    LOG.info("Categories:\n%s", df["category"].value_counts().to_string())
    LOG.info("Output: %s", output)
    LOG.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Concurrent OpenAlex evidence ingestion")
    parser.add_argument("--output", "-o", type=Path,
                        default=Path(__file__).resolve().parent.parent / "data" / "public_dataset.parquet")
    parser.add_argument("--pages-per-topic", type=int, default=3,
                        help="Pages to fetch per topic (default: 3)")
    parser.add_argument("--per-page", type=int, default=200,
                        help="Results per page (default: 200, max: 200)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    LOG.info("=" * 50)
    LOG.info("OpenAlex CONCURRENT Ingestion")
    LOG.info("=" * 50)
    LOG.info("Topics: %d | Pages/topic: %d | Per page: %d",
             len(SEARCH_QUERIES), args.pages_per_topic, args.per_page)
    LOG.info("Max concurrent requests: %d", MAX_CONCURRENT)
    LOG.info("Output: %s", args.output)

    t0 = time.time()
    asyncio.run(run_ingestion(args.pages_per_topic, args.per_page, args.output))
    LOG.info("Wall-clock time: %.1f seconds", time.time() - t0)


if __name__ == "__main__":
    main()
