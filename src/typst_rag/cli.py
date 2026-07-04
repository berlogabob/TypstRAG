import json

import lancedb
import typer
from rich import print

from .answer import openai_compatible, retrieval_only
from .build_index import build_index
from .chunk import chunk_documents
from .collect import collect_documents
from .config import CHUNKS_JSONL, DOCUMENTS_JSONL, EMBEDDING_MODEL, LANCEDB_DIR, LANCEDB_TABLE, TYPST_REPO_DIR, TYPST_VERSION
from .evaluate import evaluate
from .fetch_typst import fetch_typst
from .search import format_results, json_results, search as run_search

app = typer.Typer(help="Retrieval-only RAG over Typst docs using LanceDB")


@app.command()
def fetch() -> None:
    fetch_typst()


@app.command()
def collect() -> None:
    collect_documents()


@app.command()
def chunk() -> None:
    chunk_documents()


@app.command("build-index")
def build_index_cmd() -> None:
    build_index()


@app.command("build-all")
def build_all() -> None:
    fetch_typst()
    collect_documents()
    chunk_documents()
    build_index()


@app.command("update-docs")
def update_docs(version: str) -> None:
    fetch_typst(version)
    collect_documents(version)
    chunk_documents()
    build_index()
    doctor()


@app.command()
def doctor(json_output: bool = typer.Option(False, "--json")) -> None:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("typst repo", TYPST_REPO_DIR.exists(), f"{TYPST_REPO_DIR} @ {TYPST_VERSION}"))
    checks.append(("documents", DOCUMENTS_JSONL.exists(), str(DOCUMENTS_JSONL)))
    checks.append(("chunks", CHUNKS_JSONL.exists(), str(CHUNKS_JSONL)))
    if DOCUMENTS_JSONL.exists():
        checks.append(("document count", True, str(sum(1 for _ in DOCUMENTS_JSONL.open(encoding="utf-8")))))
    if CHUNKS_JSONL.exists():
        chunks = [json.loads(line) for line in CHUNKS_JSONL.open(encoding="utf-8")]
        versions = sorted({str(chunk.get("version", "")) for chunk in chunks})
        checks.append(("chunk count", True, str(len(chunks))))
        checks.append(("indexed version", True, ", ".join(versions)))
    try:
        table = lancedb.connect(LANCEDB_DIR).open_table(LANCEDB_TABLE)
        checks.append(("lancedb table", True, f"{LANCEDB_TABLE}: {table.count_rows()} rows"))
    except Exception as exc:
        checks.append(("lancedb table", False, str(exc)))
    checks.append(("embedding model", True, EMBEDDING_MODEL))
    failed = False
    for name, ok, detail in checks:
        failed |= not ok
    if json_output:
        typer.echo(json.dumps({"ok": not failed, "checks": [
            {"name": name, "ok": ok, "detail": detail} for name, ok, detail in checks
        ]}))
    else:
        for name, ok, detail in checks:
            print(f"{'OK' if ok else 'FAIL'} {name}: {detail}")
    if failed:
        raise typer.Exit(1)


@app.command("search")
def search_cmd(
    query: str,
    limit: int = 8,
    mode: str = "hybrid",
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    results = run_search(query, limit=limit, mode=mode)  # type: ignore[arg-type]
    if json_output:
        typer.echo(json.dumps(json_results(results), ensure_ascii=False))
    else:
        print(format_results(results))


@app.command()
def ask(query: str, limit: int = 8, mode: str = "retrieval-only") -> None:
    if mode == "retrieval-only":
        print(retrieval_only(query, limit=limit))
    elif mode == "openai-compatible":
        print(openai_compatible(query, limit=limit))
    else:
        raise typer.BadParameter("mode must be retrieval-only or openai-compatible")


@app.command("eval")
def eval_cmd(limit: int = 5) -> None:
    evaluate(limit=limit)
