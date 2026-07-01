import json

import lancedb
from rich import print

from .config import CHUNKS_JSONL, LANCEDB_DIR, LANCEDB_TABLE
from .embed import embed_passages


def build_index() -> None:
    LANCEDB_DIR.mkdir(parents=True, exist_ok=True)
    chunks = [json.loads(line) for line in CHUNKS_JSONL.open(encoding="utf-8")]
    vectors = embed_passages([c["text"] for c in chunks])
    rows = []
    for chunk, vector in zip(chunks, vectors):
        row = dict(chunk)
        row["vector"] = vector
        rows.append(row)
    table = lancedb.connect(LANCEDB_DIR).create_table(LANCEDB_TABLE, data=rows, mode="overwrite")
    table.create_fts_index("text", replace=True)
    print(f"Indexed: {len(rows)} rows -> {LANCEDB_DIR}/{LANCEDB_TABLE}")
