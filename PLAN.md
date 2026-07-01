# Working Plan: Typst RAG with LanceDB

Ponytail target: working retrieval first. No Docker, LangChain, LlamaIndex, API, web UI, or multi-backend abstraction until retrieval passes.

## Progress

- [x] 0. Plan from `_income/typst_lancedb_rag_report.md`
- [x] 1. Retrieval-only MVP
  - [x] `uv` package skeleton
  - [x] minimal deps: LanceDB, sentence-transformers, pandas, typer, rich, gitpython
  - [x] config constants
  - [x] fetch Typst `v0.15.0`
  - [x] collect docs
  - [x] chunk docs
  - [x] embed and build LanceDB index
  - [x] search / ask CLI
  - [x] smoke checks
- [x] 2. Tiny retrieval eval
  - [x] `data/eval/questions.jsonl`
  - [x] `src/typst_rag/evaluate.py`
  - [x] `typst-rag eval`
  - [x] pass threshold >= 0.80
- [x] 3. Clean retrieval output
  - [x] remove duplicate source chunks from displayed results
  - [x] verify eval still passes
- [x] 4. LLM answer adapter
  - [x] `prompts/answer_system.md`
  - [x] `src/typst_rag/answer.py`
  - [x] OpenAI-compatible mode only
  - [x] cited answers from context only
- [x] 5. Stop / decide next
  - [x] CLI is enough for Ollama sidecar
  - [x] Hermes skill path added for any-model usage
- [ ] 6. Optional connector only if needed
  - [ ] Open WebUI/tool connector later, only if copy-paste/CLI is bottleneck

Current step: **6. Optional connector only if needed**.

## Evidence

```text
fetch/collect/chunk: 57 documents, 602 chunks
build-index: 602 LanceDB rows
ask "как сделать две колонки?": top result docs/content/guides/page-setup.typ, section Columns
compile: uv run python -m compileall -q src passed
eval: 5 questions, average expected-term hit rate 1.00
dedupe: search output now shows unique source_path entries
LLM adapter: `typst-rag ask --mode openai-compatible`, stdlib urllib, no new dependency
Hermes integration: `skills/typst-rag/SKILL.md` + `docs/USAGE.md`; use retrieval as context with any Hermes model
```

## Goal

Build a local `uv` Python CLI that indexes Typst `v0.15.0` docs into LanceDB and answers by retrieval-only first.

Pipeline:

```text
fetch Typst repo -> collect docs -> chunk -> embed -> LanceDB hybrid search -> retrieval answer
```

## Commands

```bash
uv run typst-rag build-all
uv run typst-rag ask "как сделать две колонки?" --limit 5
uv run typst-rag eval
```

## Acceptance

- [x] figure query finds figure/image docs
- [x] two-column query finds page/columns/layout docs
- [x] heading.where query finds show rules / heading selector docs
- [x] bibliography query finds bibliography/citation docs
- [x] page margin query finds page setup docs

## Skipped until needed

- [ ] Rust doc comments: add if symbol/API queries fail
- [ ] reranker: add if top 20 contains answer but top 5 does not
- [ ] stronger embeddings: add if multilingual-e5-small fails Russian/English retrieval
- [ ] FastAPI/web UI: add only after CLI is useful
- [ ] Docker: skipped; local embedded LanceDB + uv is enough
- [ ] LangChain/LlamaIndex: skipped; unnecessary for this pipeline
