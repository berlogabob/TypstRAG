import typer
from rich import print

from .answer import openai_compatible, retrieval_only
from .build_index import build_index
from .chunk import chunk_documents
from .collect import collect_documents
from .evaluate import evaluate
from .fetch_typst import fetch_typst
from .search import format_results, search as run_search

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


@app.command("search")
def search_cmd(query: str, limit: int = 8, mode: str = "hybrid") -> None:
    print(format_results(run_search(query, limit=limit, mode=mode)))  # type: ignore[arg-type]


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
