import json
import os
import urllib.request

from .search import format_results, search


def retrieval_only(query: str, limit: int = 8) -> str:
    return format_results(search(query, limit=limit, mode="hybrid"))


def build_prompt(query: str, context: str) -> str:
    with open("prompts/answer_system.md", encoding="utf-8") as f:
        system = f.read().strip()
    return f"""{system}

# Question
{query}

# Context
{context}

# Answer
"""


def openai_compatible(query: str, limit: int = 8) -> str:
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("RAG_LLM_MODEL")
    if not base_url or not model:
        raise RuntimeError("OPENAI_BASE_URL and RAG_LLM_MODEL are required")

    prompt = build_prompt(query, retrieval_only(query, limit=limit))
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }).encode()
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "local"),
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.load(response)
    return data["choices"][0]["message"]["content"]
