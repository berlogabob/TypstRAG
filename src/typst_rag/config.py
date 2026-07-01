from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LANCEDB_DIR = DATA_DIR / "lancedb"

TYPST_REPO_URL = "https://github.com/typst/typst.git"
TYPST_REPO_DIR = RAW_DIR / "typst"
TYPST_VERSION = "v0.15.0"

DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"

LANCEDB_TABLE = "typst_chunks"
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

CHUNK_TARGET_CHARS = 1800
CHUNK_OVERLAP_CHARS = 250
