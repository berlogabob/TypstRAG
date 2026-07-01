# Using TypstRAG

TypstRAG is meant to run locally. The GitHub repo stores code + a Hermes skill; each user clones it, builds an index once, and queries it locally.

## 1. Local install

```bash
git clone https://github.com/berlogabob/TypstRAG.git
cd TypstRAG
uv sync
uv run typst-rag build-all
uv run typst-rag doctor
uv run python scripts/smoke.py
uv run typst-rag ask "how to make a two-column academic paper?" --limit 5
```

When Typst releases a new docs tag:

```bash
uv run typst-rag update-docs v0.16.0
```

Optional portable path for tools/skills:

```bash
export TYPST_RAG_DIR="$PWD"
```

## 2. Hermes skill: any Hermes model

Install from GitHub:

```bash
hermes skills install \
  https://raw.githubusercontent.com/berlogabob/TypstRAG/main/skills/typst-rag/SKILL.md \
  --name typst-rag
```

Then ask Hermes:

```text
/skill typst-rag
Prepare a Typst paper template with title, authors, abstract, two columns, figures, and bibliography.
```

The skill runs retrieval locally:

```bash
cd "${TYPST_RAG_DIR:-$HOME/TypstRAG}"
uv run typst-rag ask "<question>" --limit 5
```

Hermes then writes the final answer with whichever model you selected.

## 3. Local Ollama answer mode

Use this when you want Gemma, Ornith, or another Ollama model to write the final answer locally.

```bash
cd "${TYPST_RAG_DIR:-$HOME/TypstRAG}"
ollama serve
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"
export RAG_LLM_MODEL="ornith:9b"   # or exact name from `ollama list`
uv run typst-rag ask "prepare a Typst layout for an academic article" --mode openai-compatible
```

## 4. Plain Ollama chat

Ollama CLI/chat has no native external-tool connector. Use TypstRAG as a sidecar:

```bash
uv run typst-rag ask "how do I add figure captions?" --limit 5
```

Paste the returned context into Ollama chat and ask it to draft the final `.typ`.

## 5. ChatGPT or Claude web chat

Normal ChatGPT/Claude web pages cannot call your local TypstRAG directly.

Working options:

- Manual: paste `typst-rag ask ...` output into the web chat.
- ChatGPT Custom GPT Action: requires public HTTPS API around TypstRAG.
- Claude Desktop: use a local MCP server if you need tool calling.
- Claude web: no simple arbitrary local tool connector.

Ponytail default: use manual paste or Hermes skill first; build an API only if copy-paste becomes the bottleneck.

## 6. GitHub Pages / FTP hosting

GitHub Pages and FTP are static hosting. They can host docs, examples, exported chunks, or a static demo page.

They cannot run:

- Python
- LanceDB queries
- sentence-transformers embeddings
- Ollama/local LLM
- ChatGPT Action backend API

For a real web-callable RAG, use:

```text
TypstRAG CLI/API on Mac/VPS/Raspberry Pi
+ HTTPS endpoint, e.g. Cloudflare Tunnel or ngrok
+ ChatGPT Custom GPT Action or other client
```

## 7. Example questions

```bash
uv run typst-rag ask "как сделать две колонки?" --limit 5
uv run typst-rag ask "how do I add figure captions?" --limit 5
uv run typst-rag ask "bibliography and citations in Typst" --limit 5
uv run typst-rag ask "academic paper with title authors abstract two columns figures bibliography" --limit 5
```

## 8. Ponytail prompt

For a full anti-overengineering prompt, see [PONYTAIL.md](PONYTAIL.md).
