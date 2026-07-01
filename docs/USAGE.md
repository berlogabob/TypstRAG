# Using TypstRAG

TypstRAG has two useful modes.

## 1. Hermes skill: any Hermes model

This is the default next step. Hermes uses TypstRAG only for retrieval, then your current Hermes model writes the answer.

Install/copy the skill from:

```text
skills/typst-rag/SKILL.md
```

Then ask Hermes:

```text
/skill typst-rag
How do I prepare a Typst paper with title, authors, abstract, two columns, figures, and bibliography?
```

The skill runs:

```bash
cd /Users/berloga/Documents/GitHub/TypstRAG
uv run typst-rag ask "<question>" --limit 5
```

This works with any Hermes model because the LLM does not need direct access to LanceDB.

## 2. Local Ollama answer mode

Use this when you want Gemma/Ornith/etc. to write the final answer locally.

```bash
cd /Users/berloga/Documents/GitHub/TypstRAG
uv run typst-rag build-all

export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"
export RAG_LLM_MODEL="gemma3"   # or exact name from `ollama list`
uv run typst-rag ask "prepare a Typst layout for an academic article" --mode openai-compatible
```

## 3. Plain Ollama chat

Ollama CLI/chat does not have a native external-tool connector. Ponytail answer: do not build a fake plugin.

Use retrieval sidecar:

```bash
uv run typst-rag ask "how do I add figure captions?" --limit 5
```

Paste the returned context into the Ollama chat and ask it to draft the final `.typ`.

Add Open WebUI / API connector only if copy-paste becomes the bottleneck.
