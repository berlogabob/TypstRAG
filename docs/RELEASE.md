# Release checklist

```bash
uv run python -m compileall -q src scripts
uv run typst-rag doctor
uv run python scripts/smoke.py
uv run typst-rag eval
git status --short
```

Then:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Check links:

- Repo: https://github.com/berlogabob/TypstRAG
- Wiki: https://github.com/berlogabob/TypstRAG/wiki
- Skill raw: https://raw.githubusercontent.com/berlogabob/TypstRAG/main/skills/typst-rag/SKILL.md
