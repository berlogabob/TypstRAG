---
name: typst-rag
description: "Use when answering Typst questions or drafting Typst documents. Retrieve Typst docs from local TypstRAG first, then answer with the current Hermes model."
version: 1.0.1
author: BerlogaBob
license: MIT
requires:
  - uv
metadata:
  hermes:
    tags: [typst, rag, docs, retrieval, local]
---

# TypstRAG

Use this skill for Typst syntax, layout, bibliography, figures, page setup, and drafting publishable `.typ` documents.

## Setup

Clone and build once:

```bash
git clone https://github.com/berlogabob/TypstRAG.git "$HOME/TypstRAG"
cd "$HOME/TypstRAG"
uv sync
uv run typst-rag build-all
```

If cloned elsewhere, set:

```bash
export TYPST_RAG_DIR="/path/to/TypstRAG"
```

## Procedure

1. Run retrieval from the local repo:

```bash
cd "${TYPST_RAG_DIR:-$HOME/TypstRAG}"
uv run typst-rag ask "<question>" --limit 5
```

2. Answer using only retrieved context unless clearly marked as general Typst knowledge.
3. Include source paths/URLs when giving syntax or publishing advice.
4. For document drafting, produce a complete `.typ` starter and cite which retrieved docs informed it.

## Optional local Ollama answer mode

If the user specifically wants the local Ollama model to write the final answer:

```bash
cd "${TYPST_RAG_DIR:-$HOME/TypstRAG}"
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"
export RAG_LLM_MODEL="ornith:9b"
uv run typst-rag ask "<question>" --mode openai-compatible
```

Replace `ornith:9b` with the exact model from `ollama list`.

## Boundaries

- GitHub repo/wiki/Pages/FTP can share docs and code, but cannot run the RAG backend.
- ChatGPT web needs a public HTTPS API if it must call TypstRAG as a tool.
- Claude Desktop can use a local MCP server if added later.
- Plain web chat/manual Ollama: paste retrieval output as context.

Do not build a server, plugin, LangChain/LlamaIndex wrapper, or UI unless the CLI/skill workflow is not enough.
