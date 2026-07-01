import hashlib
import json
import re
from pathlib import Path

from rich import print

from .config import DOCUMENTS_JSONL, PROCESSED_DIR, TYPST_REPO_DIR, TYPST_VERSION


def stable_id(*parts: str) -> str:
    raw = "::".join(parts)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw.lower()).strip("-")[:80]
    digest = hashlib.sha1(raw.encode()).hexdigest()[:10]
    return f"{slug}-{digest}"


def guess_kind(rel_path: str) -> str:
    if "/tutorial/" in rel_path:
        return "tutorial"
    if "/reference/" in rel_path:
        return "reference"
    if "/guides/" in rel_path:
        return "guide"
    if rel_path.startswith("docs/dev/"):
        return "dev"
    return "doc"


def section_for(rel_path: str) -> str:
    parts = []
    for part in Path(rel_path).parts:
        if part in {"docs", "content"}:
            continue
        part = re.sub(r"\.(typ|md)$", "", part)
        parts.append(part.replace("-", " ").replace("_", " ").title())
    return " / ".join(parts)


def url_for(rel_path: str) -> str:
    if not rel_path.startswith("docs/content/"):
        return f"https://github.com/typst/typst/blob/{TYPST_VERSION}/{rel_path}"
    path = re.sub(r"\.(typ|md)$", "", rel_path.removeprefix("docs/content/")).strip("/")
    return "https://typst.app/docs/" if path == "index" else f"https://typst.app/docs/{path}/"


def iter_source_files() -> list[Path]:
    paths: list[Path] = []
    for base in [TYPST_REPO_DIR / "docs" / "content", TYPST_REPO_DIR / "docs" / "dev"]:
        if base.exists():
            paths.extend(base.rglob("*.typ"))
            paths.extend(base.rglob("*.md"))
    return sorted(set(paths))


def collect_documents() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    with DOCUMENTS_JSONL.open("w", encoding="utf-8") as out:
        for path in iter_source_files():
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if len(text) < 80:
                continue
            rel_path = path.relative_to(TYPST_REPO_DIR).as_posix()
            doc = {
                "id": stable_id(TYPST_VERSION, rel_path),
                "source_path": rel_path,
                "kind": guess_kind(rel_path),
                "section": section_for(rel_path),
                "version": TYPST_VERSION,
                "url": url_for(rel_path),
                "text": text,
            }
            out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            count += 1
    print(f"Documents: {count} -> {DOCUMENTS_JSONL}")
