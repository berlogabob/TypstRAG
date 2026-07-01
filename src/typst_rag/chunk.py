import json
import re

from rich import print

from .config import CHUNK_OVERLAP_CHARS, CHUNK_TARGET_CHARS, CHUNKS_JSONL, DOCUMENTS_JSONL, PROCESSED_DIR


def split_headings(text: str) -> list[str]:
    sections: list[list[str]] = []
    current: list[str] = []
    heading = re.compile(r"^\s*(=+|#+)\s+.+")
    for line in text.replace("\r\n", "\n").splitlines():
        if heading.match(line) and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)
    return ["\n".join(s).strip() for s in sections if "\n".join(s).strip()]


def sliding(text: str) -> list[str]:
    if len(text) <= CHUNK_TARGET_CHARS:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_TARGET_CHARS
        window = text[start:end]
        boundary = window.rfind("\n\n")
        if end < len(text) and boundary > CHUNK_TARGET_CHARS * 0.55:
            end = start + boundary
            window = text[start:end]
        chunks.append(window.strip())
        if end >= len(text):
            break
        start = max(0, end - CHUNK_OVERLAP_CHARS)
    return [c for c in chunks if len(c) > 120]


def chunk_documents() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    with DOCUMENTS_JSONL.open(encoding="utf-8") as src, CHUNKS_JSONL.open("w", encoding="utf-8") as out:
        for line in src:
            doc = json.loads(line)
            idx = 0
            for section in split_headings(doc["text"]):
                for text in sliding(section):
                    chunk = {k: doc[k] for k in ["source_path", "kind", "section", "version", "url"]}
                    chunk.update({
                        "id": f"{doc['id']}-chunk-{idx:04d}",
                        "document_id": doc["id"],
                        "chunk_index": idx,
                        "text": text,
                    })
                    out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                    idx += 1
                    count += 1
    print(f"Chunks: {count} -> {CHUNKS_JSONL}")
