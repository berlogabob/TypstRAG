import json

from rich import print

from .config import DATA_DIR
from .search import search

QUESTIONS = DATA_DIR / "eval" / "questions.jsonl"
REPORT = DATA_DIR / "eval" / "retrieval_report.jsonl"


def evaluate(limit: int = 5) -> None:
    rows = []
    for line in QUESTIONS.read_text(encoding="utf-8").splitlines():
        q = json.loads(line)
        df = search(q["query"], limit=limit)
        text = "\n".join(df["text"].astype(str)).lower()
        expected = [term.lower() for term in q["expected_terms"]]
        hits = [term for term in expected if term in text]
        rows.append({
            "id": q["id"],
            "query": q["query"],
            "expected_terms": expected,
            "hits": hits,
            "hit_rate": len(hits) / len(expected),
            "top_sources": df["source_path"].head(limit).tolist(),
        })

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    avg = sum(r["hit_rate"] for r in rows) / len(rows)
    print(f"Average expected-term hit rate: {avg:.2f}")
    print(f"Report: {REPORT}")
    if avg < 0.8:
        raise SystemExit(1)
