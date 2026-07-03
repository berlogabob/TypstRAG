# TypstRAG
What is TypstRAG? It's a local [Retrieval-Augmented Generation (RAG)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation) system for [Typst](https://typst.app), the modern [typesetting](https://en.wikipedia.org/wiki/Typesetting) system. It allows you to ask questions about Typst and get answers based on the official documentation (and other trusted sources in future).

Local RAG build over Typst official `v0.15.0` docs.
To work with it: clone repo, build the index once, then ask Typst questions from CLI, Hermes, or local Ollama.

## Install locally
### Dependencies
[git](https://git-scm.com/), [uv](https://github.com/astral-sh/uv) for [Python](https://www.python.org/) 3.12.


```bash
git clone https://github.com/berlogabob/TypstRAG.git
cd TypstRAG
uv sync
uv run typst-rag build-all
uv run typst-rag doctor
uv run python scripts/smoke.py
uv run typst-rag ask "how to make a two-column academic paper?" --limit 5

# when Typst releases a new docs tag
uv run typst-rag update-docs v0.16.0
```

## Use from Hermes as a skill

```bash
hermes skills install \
  https://raw.githubusercontent.com/berlogabob/TypstRAG/main/skills/typst-rag/SKILL.md \
  --name typst-rag

export TYPST_RAG_DIR="$PWD"
```

Then in Hermes:

```text
/skill typst-rag
Prepare a Typst paper template with title, authors, abstract, two columns, figures, and bibliography.
```

Hermes uses TypstRAG for retrieval and any current Hermes model for the final answer.

## Use with local Ollama

```bash
cd "${TYPST_RAG_DIR:-$HOME/TypstRAG}"
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"
export RAG_LLM_MODEL="ornith:9b"   # or exact name from `ollama list`
uv run typst-rag ask "prepare a Typst layout for an academic article" --mode openai-compatible
```

## More examples

See:

- [docs/USAGE.md](docs/USAGE.md)
- [docs/DEMO.md](docs/DEMO.md)
- [docs/RAG-SOURCES.md](docs/RAG-SOURCES.md)
- [docs/PONYTAIL.md](docs/PONYTAIL.md)
- [docs/RELEASE.md](docs/RELEASE.md)
- [docs/UNIVERSE.md](docs/UNIVERSE.md)
- [examples/academic-paper](examples/academic-paper)
- [packages/ragged-paper](packages/ragged-paper)
- [wiki](https://github.com/berlogabob/TypstRAG/wiki)
