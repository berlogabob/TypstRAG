# RAG sources for the academic paper example

| Feature | TypstRAG query | Source path | URL |
|---|---|---|---|
| Two-column layout and full-width title | `two column page layout` | `docs/content/guides/page-setup.typ` | https://typst.app/docs/guides/page-setup/ |
| Figure with caption and label | `figure image captions` | `docs/content/tutorial/1-writing.typ` | https://typst.app/docs/tutorial/1-writing/ |
| Bibliography and citations | `bibliography citations` | `docs/content/guides/for-latex-users.typ` | https://typst.app/docs/guides/for-latex-users/ |

Verification commands:

```bash
uv run typst-rag ask "two column page layout" --limit 5
uv run typst-rag ask "figure image captions" --limit 5
uv run typst-rag ask "bibliography citations" --limit 5
typst compile examples/academic-paper/main.typ examples/academic-paper/main.pdf
```
