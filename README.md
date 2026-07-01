# Typst RAG LanceDB

Local RAG over Typst `v0.15.0` docs.

```bash
uv run typst-rag build-all
uv run typst-rag ask "как сделать две колонки?" --limit 5
```

Local Ollama answer mode:

```bash
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"
export RAG_LLM_MODEL="gemma3"
uv run typst-rag ask "prepare a Typst layout for an academic article" --mode openai-compatible
```

Hermes skill / usage notes: [docs/USAGE.md](docs/USAGE.md).
