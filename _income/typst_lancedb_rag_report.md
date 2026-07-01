# RAG for Typst Documentation on LanceDB

**Format:** implementation report / project blueprint  
**Storage:** LanceDB local embedded database  
**Package manager:** `uv` is mandatory  
**LLM provider:** agnostic — any local model, OpenAI-compatible endpoint, hosted API, or manual retrieval-only mode  
**Target corpus:** Typst documentation and developer-facing source documentation  
**Recommended first pinned Typst version:** `v0.15.0`

---

## 1. Goal

Build a local Retrieval-Augmented Generation system for Typst documentation.

The system must answer questions like:

- “How do I create a two-column layout in Typst?”
- “What is the difference between set rules and show rules?”
- “How do I write a reusable template?”
- “How do I reference a figure?”
- “Which arguments does `grid` accept?”

The RAG must not depend on one LLM vendor. Retrieval, storage, embeddings, and generation should be separate modules.

The chosen first implementation uses **LanceDB** because it can run locally as an embedded Python library, store text + metadata + vectors together, and support vector, full-text, and hybrid search.

---

## 2. Why LanceDB for this project

For a Typst documentation RAG, retrieval quality depends on two kinds of search:

1. **Semantic search**: finds meaning.
   - User: “how to split page into two columns?”
   - Relevant docs may say: “set `columns: 2` on `page`”.

2. **Exact keyword search**: finds symbols and API names.
   - `#grid`
   - `#show heading`
   - `heading.where(level: 2)`
   - `bibliography`
   - `#set page`

Pure vector search is not enough for programming-language documentation because symbols, function names, parameters, and code fragments often matter more than general semantic similarity.

LanceDB supports vector search and hybrid search. Its documentation describes hybrid search as a combination of vector and full-text search with reranking. By default, LanceDB uses reciprocal rank fusion reranking for hybrid results unless configured otherwise.

Recommended retrieval mode for this project:

```text
hybrid search = vector search + full-text search + reranking
```

---

## 3. Sources to ingest

Do **not** use the PDF as the primary source if repository sources are available. PDF is useful as a version snapshot and verification artifact, but it loses source paths, stable anchors, and code/doc structure.

Use the Typst repository as the primary source:

```text
https://github.com/typst/typst
```

Recommended source layers:

```text
1. docs/content/
   Main user-facing documentation: tutorial, reference pages, guides, changelog.

2. docs/dev/
   Developer-facing architecture and contribution documentation.

3. crates/**/*.rs
   Rust doc comments for generated reference material: functions, elements, types.
```

The Typst open-source page explains that the compiler is the open-source software that translates Typst markup into PDFs, images, and web pages. The official repository is the best source for source-level documentation.

For version consistency, pin the repository:

```bash
git checkout v0.15.0
```

This is important because the uploaded PDF snapshot is Typst Documentation 0.15.0.

---

## 4. Final project architecture

```text
typst-rag-lancedb/
  .python-version
  pyproject.toml
  uv.lock
  README.md

  data/
    raw/
      typst/                    # cloned Typst repository
    processed/
      documents.jsonl           # extracted source documents
      chunks.jsonl              # semantic chunks
    lancedb/                    # local LanceDB database
    eval/
      questions.jsonl
      retrieval_report.jsonl

  src/
    typst_rag/
      __init__.py
      config.py
      fetch_typst.py
      collect.py
      chunk.py
      embed.py
      build_index.py
      search.py
      answer.py
      evaluate.py
      cli.py

  prompts/
    answer_system.md

  scripts/
    smoke_test.sh
```

The stages are intentionally separated:

```text
fetch source -> collect docs -> chunk -> embed/index -> search -> answer -> evaluate
```

This makes the project storage-agnostic and LLM-agnostic. LanceDB can later be replaced with Qdrant, SQLite, Chroma, Supabase/pgvector, or another backend without rewriting chunking and prompt logic.

---

## 5. Install from zero with uv

Create the project:

```bash
uv init typst-rag-lancedb
cd typst-rag-lancedb
uv python pin 3.12
```

Add dependencies:

```bash
uv add lancedb sentence-transformers pyarrow pandas tqdm rich typer pydantic gitpython pyyaml
```

Optional, only if you want HTTP API later:

```bash
uv add fastapi uvicorn
```

Optional, only if you want OpenAI-compatible generation:

```bash
uv add openai
```

Run every command through `uv run`:

```bash
uv run python -m typst_rag.cli --help
```

Reason: `uv run` keeps the project environment locked and synced against `pyproject.toml` / `uv.lock`.

---

## 6. `pyproject.toml`

Example:

```toml
[project]
name = "typst-rag-lancedb"
version = "0.1.0"
description = "Provider-agnostic RAG over Typst documentation using LanceDB and uv"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "gitpython>=3.1.0",
    "lancedb>=0.25.0",
    "pandas>=2.0.0",
    "pyarrow>=15.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "rich>=13.0.0",
    "sentence-transformers>=3.0.0",
    "tqdm>=4.66.0",
    "typer>=0.12.0",
]

[project.scripts]
typst-rag = "typst_rag.cli:app"

[tool.uv]
package = true
```

Then run:

```bash
uv sync
```

---

## 7. Configuration

Create `src/typst_rag/config.py`:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LANCEDB_DIR = DATA_DIR / "lancedb"
EVAL_DIR = DATA_DIR / "eval"

TYPST_REPO_URL = "https://github.com/typst/typst.git"
TYPST_REPO_DIR = RAW_DIR / "typst"
TYPST_VERSION = "v0.15.0"

DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"

LANCEDB_TABLE = "typst_chunks"

# Good first model because the user may ask in Russian while docs are English.
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_DIM = 384

CHUNK_TARGET_CHARS = 1800
CHUNK_OVERLAP_CHARS = 250
```

Why multilingual embeddings: the documentation is mostly English, but questions may be Russian, English, Portuguese, or mixed. A multilingual retrieval model reduces the risk that Russian questions miss English documentation.

---

## 8. Fetch Typst repository

Create `src/typst_rag/fetch_typst.py`:

```python
from git import Repo
from rich import print

from .config import RAW_DIR, TYPST_REPO_DIR, TYPST_REPO_URL, TYPST_VERSION


def fetch_typst() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if TYPST_REPO_DIR.exists():
        print(f"[yellow]Repository already exists:[/yellow] {TYPST_REPO_DIR}")
        repo = Repo(TYPST_REPO_DIR)
        repo.remotes.origin.fetch(tags=True)
    else:
        print(f"[green]Cloning Typst repository...[/green]")
        repo = Repo.clone_from(TYPST_REPO_URL, TYPST_REPO_DIR)
        repo.remotes.origin.fetch(tags=True)

    print(f"[green]Checking out {TYPST_VERSION}[/green]")
    repo.git.checkout(TYPST_VERSION)

    print(f"[green]Ready:[/green] {TYPST_REPO_DIR}")
```

Run:

```bash
uv run python -c "from typst_rag.fetch_typst import fetch_typst; fetch_typst()"
```

---

## 9. Document collection

The collection stage converts raw repository files into normalized JSONL records.

Each document record:

```json
{
  "id": "typst-v0.15.0-docs-content-tutorial-writing",
  "source_path": "docs/content/tutorial/writing.typ",
  "kind": "tutorial",
  "section": "Tutorial / Writing",
  "symbol": "",
  "version": "v0.15.0",
  "url": "https://typst.app/docs/tutorial/",
  "text": "..."
}
```

Create `src/typst_rag/collect.py`:

```python
import hashlib
import json
import re
from pathlib import Path

from rich import print

from .config import DOCUMENTS_JSONL, PROCESSED_DIR, TYPST_REPO_DIR, TYPST_VERSION


def stable_id(*parts: str) -> str:
    raw = "::".join(parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw.lower()).strip("-")[:80]
    return f"{slug}-{digest}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def guess_kind(path: Path) -> str:
    p = path.as_posix()
    if "/tutorial/" in p:
        return "tutorial"
    if "/reference/" in p:
        return "reference"
    if "/guides/" in p:
        return "guide"
    if "/changelog" in p:
        return "changelog"
    if "/docs/dev/" in p:
        return "dev"
    if p.endswith(".rs"):
        return "rust-doc-comment"
    return "doc"


def path_to_section(rel_path: str) -> str:
    parts = Path(rel_path).parts
    cleaned = []
    for part in parts:
        if part in {"docs", "content"}:
            continue
        part = re.sub(r"\.(typ|md|rs)$", "", part)
        part = part.replace("-", " ").replace("_", " ").title()
        cleaned.append(part)
    return " / ".join(cleaned)


def path_to_url(rel_path: str) -> str:
    # Best-effort mapping for docs/content paths.
    if not rel_path.startswith("docs/content/"):
        return f"https://github.com/typst/typst/blob/{TYPST_VERSION}/{rel_path}"

    path = rel_path.removeprefix("docs/content/")
    path = re.sub(r"\.(typ|md)$", "", path)
    path = path.strip("/")

    if path == "index":
        return "https://typst.app/docs/"

    return f"https://typst.app/docs/{path}/"


def extract_rust_doc_comments(text: str) -> str:
    """Simple extraction of Rust doc comments.

    This is intentionally conservative. It does not fully parse Rust syntax;
    it extracts lines beginning with `///` or `//!` and keeps their order.
    """
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("///"):
            lines.append(stripped.removeprefix("///").strip())
        elif stripped.startswith("//!"):
            lines.append(stripped.removeprefix("//!").strip())
    return "\n".join(lines).strip()


def iter_source_files() -> list[Path]:
    paths: list[Path] = []

    for base in [TYPST_REPO_DIR / "docs" / "content", TYPST_REPO_DIR / "docs" / "dev"]:
        if base.exists():
            paths.extend(base.rglob("*.typ"))
            paths.extend(base.rglob("*.md"))

    # Rust doc comments contain important generated reference material.
    crates_dir = TYPST_REPO_DIR / "crates"
    if crates_dir.exists():
        paths.extend(crates_dir.rglob("*.rs"))

    return sorted(set(paths))


def collect_documents() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    docs = []

    for path in iter_source_files():
        rel_path = path.relative_to(TYPST_REPO_DIR).as_posix()
        text = read_text(path)

        if path.suffix == ".rs":
            text = extract_rust_doc_comments(text)
            if len(text) < 200:
                continue

        if len(text.strip()) < 80:
            continue

        doc = {
            "id": stable_id(TYPST_VERSION, rel_path),
            "source_path": rel_path,
            "kind": guess_kind(path),
            "section": path_to_section(rel_path),
            "symbol": "",
            "version": TYPST_VERSION,
            "url": path_to_url(rel_path),
            "text": text.strip(),
        }
        docs.append(doc)

    with DOCUMENTS_JSONL.open("w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"[green]Documents written:[/green] {len(docs)} -> {DOCUMENTS_JSONL}")
```

Run:

```bash
uv run python -c "from typst_rag.collect import collect_documents; collect_documents()"
```

---

## 10. Chunking strategy

Do not split Typst documentation blindly every N tokens. For documentation, chunk boundaries should follow structure:

```text
heading -> explanation -> examples -> parameters -> notes
```

Good chunk size for a first version:

```text
1200–2200 characters, with 150–300 characters overlap
```

Why character-based first: it is robust, dependency-light, and easy to debug. Token-based chunking can be added later.

Each chunk should preserve metadata:

```json
{
  "id": "...-chunk-0003",
  "document_id": "...",
  "source_path": "docs/content/reference/layout/grid.typ",
  "kind": "reference",
  "section": "Reference / Layout / Grid",
  "symbol": "grid",
  "version": "v0.15.0",
  "url": "https://typst.app/docs/reference/layout/grid/",
  "chunk_index": 3,
  "text": "..."
}
```

Create `src/typst_rag/chunk.py`:

```python
import json
import re
from pathlib import Path

from rich import print

from .config import CHUNK_OVERLAP_CHARS, CHUNK_TARGET_CHARS, CHUNKS_JSONL, DOCUMENTS_JSONL, PROCESSED_DIR


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def split_by_headings(text: str) -> list[str]:
    """Split on common Typst/Markdown headings while keeping sections readable."""
    lines = text.splitlines()
    sections: list[list[str]] = []
    current: list[str] = []

    heading_re = re.compile(r"^\s*(=+|#+)\s+.+")

    for line in lines:
        if heading_re.match(line) and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append(current)

    return ["\n".join(s).strip() for s in sections if "\n".join(s).strip()]


def sliding_chunks(text: str, target: int, overlap: int) -> list[str]:
    if len(text) <= target:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + target
        window = text[start:end]

        # Prefer ending at paragraph boundary.
        if end < len(text):
            boundary = window.rfind("\n\n")
            if boundary > target * 0.55:
                end = start + boundary
                window = text[start:end]

        chunks.append(window.strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)

    return [c for c in chunks if len(c) > 120]


def chunk_documents() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    docs = load_jsonl(DOCUMENTS_JSONL)
    chunks = []

    for doc in docs:
        text = normalize_text(doc["text"])
        sections = split_by_headings(text)

        idx = 0
        for section_text in sections:
            for chunk_text in sliding_chunks(section_text, CHUNK_TARGET_CHARS, CHUNK_OVERLAP_CHARS):
                chunk = {
                    "id": f"{doc['id']}-chunk-{idx:04d}",
                    "document_id": doc["id"],
                    "source_path": doc["source_path"],
                    "kind": doc["kind"],
                    "section": doc["section"],
                    "symbol": doc.get("symbol", ""),
                    "version": doc["version"],
                    "url": doc["url"],
                    "chunk_index": idx,
                    "text": chunk_text,
                }
                chunks.append(chunk)
                idx += 1

    with CHUNKS_JSONL.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"[green]Chunks written:[/green] {len(chunks)} -> {CHUNKS_JSONL}")
```

Run:

```bash
uv run python -c "from typst_rag.chunk import chunk_documents; chunk_documents()"
```

---

## 11. Embeddings

Recommended first embedding model:

```text
intfloat/multilingual-e5-small
```

Reasons:

- small enough for local development;
- works with multilingual queries;
- suitable for English docs + Russian questions;
- fast enough on a normal laptop.

E5 models conventionally use prefixes:

```text
passage: <document chunk>
query: <user question>
```

Keep embedding generation in its own module so that the model can be replaced later.

Create `src/typst_rag/embed.py`:

```python
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from .config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_passages(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    vectors = model.encode(
        ["passage: " + t for t in texts],
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode(
        "query: " + query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vector.tolist()
```

---

## 12. Build LanceDB index

Create `src/typst_rag/build_index.py`:

```python
import json
from pathlib import Path

import lancedb
from rich import print

from .config import CHUNKS_JSONL, LANCEDB_DIR, LANCEDB_TABLE
from .embed import embed_passages


def load_chunks(path: Path) -> list[dict]:
    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def build_index() -> None:
    LANCEDB_DIR.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks(CHUNKS_JSONL)

    texts = [chunk["text"] for chunk in chunks]
    vectors = embed_passages(texts)

    rows = []
    for chunk, vector in zip(chunks, vectors):
        rows.append(
            {
                "id": chunk["id"],
                "document_id": chunk["document_id"],
                "text": chunk["text"],
                "vector": vector,
                "source_path": chunk["source_path"],
                "url": chunk["url"],
                "version": chunk["version"],
                "kind": chunk["kind"],
                "section": chunk["section"],
                "symbol": chunk.get("symbol", ""),
                "chunk_index": int(chunk["chunk_index"]),
            }
        )

    db = lancedb.connect(LANCEDB_DIR)
    table = db.create_table(LANCEDB_TABLE, data=rows, mode="overwrite")

    # Required for hybrid/full-text search.
    table.create_fts_index("text", replace=True)

    print(f"[green]LanceDB table created:[/green] {LANCEDB_TABLE}")
    print(f"[green]Rows:[/green] {len(rows)}")
    print(f"[green]Path:[/green] {LANCEDB_DIR}")
```

Run:

```bash
uv run python -c "from typst_rag.build_index import build_index; build_index()"
```

---

## 13. Search module

Create `src/typst_rag/search.py`:

```python
from typing import Literal

import lancedb
import pandas as pd

from .config import LANCEDB_DIR, LANCEDB_TABLE
from .embed import embed_query


SearchMode = Literal["vector", "fts", "hybrid"]


def get_table():
    db = lancedb.connect(LANCEDB_DIR)
    return db.open_table(LANCEDB_TABLE)


def search(query: str, limit: int = 8, mode: SearchMode = "hybrid") -> pd.DataFrame:
    table = get_table()

    if mode == "vector":
        vector = embed_query(query)
        return table.search(vector).limit(limit).to_pandas()

    if mode == "fts":
        return table.search(query, query_type="fts").limit(limit).to_pandas()

    vector = embed_query(query)
    return (
        table.search(query_type="hybrid")
        .vector(vector)
        .text(query)
        .limit(limit)
        .to_pandas()
    )


def format_sources(df: pd.DataFrame) -> str:
    blocks = []
    for i, row in df.iterrows():
        blocks.append(
            f"[{i + 1}] {row.get('section', '')}\n"
            f"source_path: {row.get('source_path', '')}\n"
            f"url: {row.get('url', '')}\n"
            f"kind: {row.get('kind', '')}\n"
            f"text:\n{row.get('text', '')}"
        )
    return "\n\n---\n\n".join(blocks)
```

Test search:

```bash
uv run python - <<'PY'
from typst_rag.search import search

for q in [
    "как сделать две колонки в Typst?",
    "show rule heading where level 2",
    "how to cite bibliography",
]:
    print("\nQUERY:", q)
    df = search(q, limit=5, mode="hybrid")
    print(df[["section", "source_path", "url"]].to_string(index=False))
PY
```

---

## 14. LLM-agnostic answer generation

The answer module should not know which LLM provider is used. It should accept:

```text
query + retrieved context -> answer
```

Three modes:

```text
1. retrieval-only
   Print top chunks. No LLM.

2. openai-compatible
   Use any OpenAI-compatible endpoint: local server, hosted API, etc.

3. custom adapter
   Add your own function later.
```

Create `prompts/answer_system.md`:

```markdown
You answer questions using only the provided Typst documentation context.

Rules:
- If the context is insufficient, say what is missing.
- Prefer concise, practical answers.
- Include Typst code examples when useful.
- Cite source_path and version for important claims.
- Do not invent function arguments or syntax.
- If multiple retrieved chunks disagree, mention the version/source difference.
```

Create `src/typst_rag/answer.py`:

```python
import os
from pathlib import Path

from .search import format_sources, search


SYSTEM_PROMPT_PATH = Path("prompts/answer_system.md")


def build_prompt(query: str, context: str) -> str:
    system = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return f"""{system}

# User question
{query}

# Retrieved context
{context}

# Answer
"""


def answer_retrieval_only(query: str, limit: int = 8) -> str:
    df = search(query, limit=limit, mode="hybrid")
    return format_sources(df)


def answer_openai_compatible(query: str, limit: int = 8) -> str:
    """Optional adapter for OpenAI-compatible APIs.

    Environment variables:
    - OPENAI_BASE_URL
    - OPENAI_API_KEY
    - RAG_LLM_MODEL
    """
    from openai import OpenAI

    df = search(query, limit=limit, mode="hybrid")
    context = format_sources(df)
    prompt = build_prompt(query, context)

    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY", "not-needed-for-some-local-servers"),
    )

    model = os.environ.get("RAG_LLM_MODEL", "local-model")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    return response.choices[0].message.content or ""
```

The project remains agnostic because this is only one optional adapter. You can add another adapter for Ollama, llama.cpp server, MLX server, Anthropic, Gemini, or any internal model.

---

## 15. CLI

Create `src/typst_rag/cli.py`:

```python
import typer
from rich import print

from .answer import answer_openai_compatible, answer_retrieval_only
from .build_index import build_index
from .chunk import chunk_documents
from .collect import collect_documents
from .fetch_typst import fetch_typst
from .search import search

app = typer.Typer(help="RAG over Typst documentation using LanceDB")


@app.command()
def fetch() -> None:
    """Clone/update Typst repo and checkout pinned version."""
    fetch_typst()


@app.command()
def collect() -> None:
    """Collect raw documentation into documents.jsonl."""
    collect_documents()


@app.command()
def chunk() -> None:
    """Split documents into semantic chunks."""
    chunk_documents()


@app.command("build-index")
def build_index_cmd() -> None:
    """Embed chunks and build LanceDB table."""
    build_index()


@app.command()
def build_all() -> None:
    """Run the full pipeline from repository fetch to LanceDB index."""
    fetch_typst()
    collect_documents()
    chunk_documents()
    build_index()


@app.command()
def search_cmd(
    query: str,
    limit: int = 8,
    mode: str = "hybrid",
) -> None:
    """Search Typst docs."""
    df = search(query, limit=limit, mode=mode)  # type: ignore[arg-type]
    for i, row in df.iterrows():
        print("\n[bold cyan]--- Result", i + 1, "---[/bold cyan]")
        print(f"[bold]Section:[/bold] {row.get('section', '')}")
        print(f"[bold]Path:[/bold] {row.get('source_path', '')}")
        print(f"[bold]URL:[/bold] {row.get('url', '')}")
        print(str(row.get("text", ""))[:1200])


@app.command()
def ask(
    query: str,
    limit: int = 8,
    mode: str = "retrieval-only",
) -> None:
    """Ask a question. Default mode prints retrieved context only."""
    if mode == "retrieval-only":
        print(answer_retrieval_only(query, limit=limit))
    elif mode == "openai-compatible":
        print(answer_openai_compatible(query, limit=limit))
    else:
        raise typer.BadParameter("mode must be retrieval-only or openai-compatible")


if __name__ == "__main__":
    app()
```

Run full build:

```bash
uv run typst-rag build-all
```

Search:

```bash
uv run typst-rag search-cmd "как сделать две колонки в Typst?" --limit 5
```

Ask without LLM:

```bash
uv run typst-rag ask "чем set rule отличается от show rule?" --mode retrieval-only
```

Ask with OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="local"
export RAG_LLM_MODEL="your-local-model"

uv run typst-rag ask "чем set rule отличается от show rule?" --mode openai-compatible
```

---

## 16. End-to-end command sequence

From zero to finished local RAG:

```bash
# 0. Create project
uv init typst-rag-lancedb
cd typst-rag-lancedb
uv python pin 3.12

# 1. Add dependencies
uv add lancedb sentence-transformers pyarrow pandas tqdm rich typer pydantic gitpython pyyaml

# 2. Add the source files from this report
mkdir -p src/typst_rag prompts data/raw data/processed data/lancedb data/eval

# 3. Sync environment
uv sync

# 4. Fetch Typst source, collect docs, chunk, embed, build LanceDB
uv run typst-rag build-all

# 5. Test retrieval
uv run typst-rag search-cmd "how to create a table in Typst?" --limit 5
uv run typst-rag search-cmd "как сделать заголовки с нумерацией?" --limit 5
uv run typst-rag search-cmd "show heading where level 2" --limit 5

# 6. Use retrieval-only answer mode
uv run typst-rag ask "как сослаться на figure в Typst?" --mode retrieval-only

# 7. Optional generation mode through any OpenAI-compatible endpoint
export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="local"
export RAG_LLM_MODEL="your-model"
uv run typst-rag ask "как создать шаблон статьи в Typst?" --mode openai-compatible
```

---

## 17. Evaluation plan

Do not trust the RAG until retrieval is tested. Start with 30–50 questions.

Create `data/eval/questions.jsonl`:

```jsonl
{"id":"q001","query":"How do I add a figure with a caption in Typst?","expected_terms":["figure","caption","image"]}
{"id":"q002","query":"как сделать две колонки в Typst?","expected_terms":["page","columns"]}
{"id":"q003","query":"What is the difference between set rules and show rules?","expected_terms":["set","show"]}
{"id":"q004","query":"How do I reference a heading or equation?","expected_terms":["label","reference","@"]}
{"id":"q005","query":"heading.where(level: 2)","expected_terms":["where","heading","level"]}
```

Create `src/typst_rag/evaluate.py`:

```python
import json
from pathlib import Path

from rich import print

from .config import EVAL_DIR
from .search import search


QUESTIONS_PATH = EVAL_DIR / "questions.jsonl"
REPORT_PATH = EVAL_DIR / "retrieval_report.jsonl"


def evaluate(limit: int = 8) -> None:
    rows = []
    with QUESTIONS_PATH.open("r", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f]

    for q in questions:
        df = search(q["query"], limit=limit, mode="hybrid")
        combined = "\n".join(df["text"].astype(str).tolist()).lower()
        expected = [term.lower() for term in q.get("expected_terms", [])]
        hits = [term for term in expected if term in combined]

        row = {
            "id": q["id"],
            "query": q["query"],
            "expected_terms": expected,
            "hits": hits,
            "hit_rate": len(hits) / max(1, len(expected)),
            "top_sources": df["source_path"].head(5).tolist(),
        }
        rows.append(row)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    avg = sum(r["hit_rate"] for r in rows) / max(1, len(rows))
    print(f"[green]Average expected-term hit rate:[/green] {avg:.2f}")
    print(f"[green]Report:[/green] {REPORT_PATH}")
```

Add CLI command later:

```python
@app.command()
def eval() -> None:
    from .evaluate import evaluate
    evaluate()
```

Minimum acceptance criteria:

```text
- top 5 chunks contain a relevant source for at least 80% of test questions;
- exact symbol questions retrieve symbol pages or Rust doc-comment chunks;
- Russian questions retrieve English documentation reliably;
- generated answers cite source_path/version;
- generated answers do not invent unsupported Typst syntax.
```

---

## 18. Retrieval quality improvements

Start simple, then improve only if tests show a problem.

### 18.1 Better chunk metadata

Add `symbol` extraction from paths and headings:

```text
docs/content/reference/layout/grid.typ -> symbol = grid
docs/content/reference/model/figure.typ -> symbol = figure
```

This helps filtering and debugging.

### 18.2 Add code block duplication

For API reference chunks, duplicate the function name and signature in each subchunk:

```text
Function: grid
Section: Reference / Layout / Grid
Path: docs/content/reference/layout/grid.typ

<chunk text>
```

This improves embedding quality and source attribution.

### 18.3 Use stronger embeddings

If `multilingual-e5-small` is not good enough, try:

```text
BAAI/bge-m3
intfloat/multilingual-e5-base
```

Tradeoff: stronger models are slower and use more memory.

### 18.4 Add reranker

For better final precision:

```text
retrieve top 30 -> rerank -> send top 8 to LLM
```

Possible rerankers:

```text
BAAI/bge-reranker-base
jinaai/jina-reranker-v2-base-multilingual
```

Keep reranking optional because it increases latency.

---

## 19. Update workflow

When Typst releases a new version:

```bash
# edit TYPST_VERSION in config.py
uv run typst-rag build-all
```

Better production approach:

```text
Table name includes version:
  typst_chunks_v0_15_0
  typst_chunks_v0_16_0

or metadata filter:
  version = v0.15.0
  version = v0.16.0
```

For a learning project, one table with a `version` column is enough.

---

## 20. Backup and portability

Everything is local:

```text
data/raw/typst/          cloned source
data/processed/*.jsonl   reproducible intermediate corpus
data/lancedb/            local LanceDB database
uv.lock                  reproducible Python dependencies
```

Backup:

```bash
tar -czf typst-rag-backup.tar.gz data pyproject.toml uv.lock src prompts README.md
```

Regenerate from source:

```bash
rm -rf data/lancedb data/processed
uv run typst-rag build-all
```

---

## 21. Common failure modes

### Problem: search misses exact function names

Fix:

```text
- check FTS index exists;
- test mode="fts" separately;
- add symbol field;
- duplicate symbol in chunk text;
- use hybrid mode, not vector-only.
```

### Problem: Russian questions retrieve weak results

Fix:

```text
- use multilingual embedding model;
- add bilingual query expansion before retrieval;
- try bge-m3;
- evaluate with Russian test questions.
```

### Problem: generated answers hallucinate Typst syntax

Fix:

```text
- lower temperature;
- force source_path citation;
- answer only from context;
- return “not enough context” when evidence is weak;
- improve retrieval before changing LLM.
```

### Problem: Rust doc comments are noisy

Fix:

```text
- initially index only docs/content and docs/dev;
- add Rust doc comments in a separate table or kind;
- filter Rust docs by markers like #[func], #[elem], #[ty] later;
- evaluate whether Rust chunks improve or hurt retrieval.
```

---

## 22. Recommended first milestone

Build a working retrieval-only system first:

```text
Milestone 1:
- uv project works;
- Typst repo is cloned and pinned;
- docs are collected;
- chunks are created;
- LanceDB table is built;
- hybrid search returns good sources;
- 30 test questions pass retrieval checks.
```

Only after this add generation:

```text
Milestone 2:
- LLM adapter added;
- answers cite source_path/version;
- hallucination checks pass;
- CLI ask mode works.
```

Then optional API:

```text
Milestone 3:
- FastAPI endpoint;
- simple web UI;
- version filters;
- package docs from Typst Universe.
```

---

## 23. Final recommendation

For this project, start directly with:

```text
LanceDB local + multilingual embeddings + hybrid search + uv-only workflow
```

Do not add Qdrant, Supabase, Docker, LangChain, or LlamaIndex in the first version. They are not necessary for the core problem and will make debugging harder.

Keep the pipeline small:

```text
collect -> chunk -> embed -> LanceDB -> hybrid search -> answer
```

The most important engineering decision is not the vector database. It is preserving source metadata well enough that every answer can point back to:

```text
source_path + url + version + section
```

That is what makes the RAG trustworthy.

---

## 24. References checked

- Typst repository: https://github.com/typst/typst
- Typst open-source compiler page: https://typst.app/open-source/
- Typst documentation: https://typst.app/docs/
- LanceDB quickstart: https://docs.lancedb.com/quickstart
- LanceDB hybrid search: https://docs.lancedb.com/search/hybrid-search
- uv project guide: https://docs.astral.sh/uv/guides/projects/
- uv locking and syncing: https://docs.astral.sh/uv/concepts/projects/sync/

---

## 25. Minimal smoke test checklist

Run this after implementing the files:

```bash
uv run typst-rag build-all

uv run typst-rag search-cmd "how to add a figure caption" --limit 5
uv run typst-rag search-cmd "как сделать две колонки" --limit 5
uv run typst-rag search-cmd "show heading where level 2" --limit 5
uv run typst-rag search-cmd "bibliography citation style" --limit 5
uv run typst-rag search-cmd "set page margin" --limit 5
```

Expected behavior:

```text
- figure query finds figure/image docs;
- two-column query finds page/columns/layout docs;
- heading.where query finds show rules / heading selector docs;
- bibliography query finds bibliography/citation docs;
- page margin query finds page setup docs.
```

If these pass, the retrieval foundation is good enough to connect an LLM.
