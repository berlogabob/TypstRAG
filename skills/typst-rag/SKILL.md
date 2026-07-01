---
name: typst-rag
description: "Use when answering Typst questions or drafting Typst documents. Retrieve Typst docs from local TypstRAG first, then answer with the current Hermes model."
version: 1.0.0
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

## Procedure

1. Run retrieval from the local repo:

```bash
cd /Users/berloga/Documents/GitHub/TypstRAG
uv run typst-rag ask "<question>" --limit 5
```

2. Answer using only retrieved context unless clearly marked as general Typst knowledge.
3. Include source paths/URLs when giving syntax or publishing advice.
4. For document drafting, produce a complete `.typ` starter and cite which retrieved docs informed it.

## Optional local Ollama answer mode

If the user specifically wants the local Ollama model to write the final answer:

```bash
cd /Users/berloga/Documents/GitHub/TypstRAG
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"
export RAG_LLM_MODEL="gemma3"
uv run typst-rag ask "<question>" --mode openai-compatible
```

Replace `gemma3` with the exact model from `ollama list`.

## Ponytail boundary

Do not build a server, plugin, LangChain/LlamaIndex wrapper, or UI unless the CLI/skill workflow is not enough.
Ollama CLI itself has no native external-tool connector; use this skill from Hermes, or paste retrieval context into the local chat.
