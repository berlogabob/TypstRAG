from typing import Literal

import lancedb
import pandas as pd

from .config import LANCEDB_DIR, LANCEDB_TABLE
from .embed import embed_query

SearchMode = Literal["vector", "fts", "hybrid"]


def table():
    return lancedb.connect(LANCEDB_DIR).open_table(LANCEDB_TABLE)


def search(query: str, limit: int = 8, mode: SearchMode = "hybrid") -> pd.DataFrame:
    tbl = table()
    if mode == "vector":
        return tbl.search(embed_query(query)).limit(limit).to_pandas()
    if mode == "fts":
        return tbl.search(query, query_type="fts").limit(limit).to_pandas()
    return tbl.search(query_type="hybrid").vector(embed_query(query)).text(query).limit(limit).to_pandas()


def format_results(df: pd.DataFrame, max_chars: int = 1200) -> str:
    blocks = []
    seen = set()
    for _, row in df.iterrows():
        key = row.get("source_path", "")
        if key in seen:
            continue
        seen.add(key)
        text = str(row.get("text", ""))[:max_chars]
        blocks.append(
            f"[{len(blocks) + 1}] {row.get('section', '')}\n"
            f"source_path: {row.get('source_path', '')}\n"
            f"url: {row.get('url', '')}\n"
            f"version: {row.get('version', '')}\n\n"
            f"{text}"
        )
    return "\n\n---\n\n".join(blocks)


def json_results(df: pd.DataFrame, max_chars: int = 1200) -> list[dict[str, object]]:
    results = []
    seen = set()
    for _, row in df.iterrows():
        source = str(row.get("source_path", ""))
        if source in seen:
            continue
        seen.add(source)
        score = row.get("_relevance_score", row.get("_distance"))
        results.append(
            {
                "section": str(row.get("section", "")),
                "source_path": source,
                "url": str(row.get("url", "")),
                "version": str(row.get("version", "")),
                "excerpt": str(row.get("text", ""))[:max_chars],
                "score": None if pd.isna(score) else float(score),
            }
        )
    return results
