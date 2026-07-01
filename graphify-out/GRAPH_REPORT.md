# Graph Report - TypstRAG  (2026-07-01)

## Corpus Check
- 19 files · ~7,828 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 120 nodes · 173 edges · 13 communities (12 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3ad57320`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]

## God Nodes (most connected - your core abstractions)
1. `RAG for Typst Documentation on LanceDB` - 26 edges
2. `collect_documents()` - 10 edges
3. `search()` - 10 edges
4. `Using TypstRAG` - 9 edges
5. `Working Plan: Typst RAG with LanceDB` - 8 edges
6. `chunk_documents()` - 7 edges
7. `retrieval_only()` - 6 edges
8. `build_index()` - 6 edges
9. `update_docs()` - 6 edges
10. `format_results()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `build_all()` --calls--> `build_index()`  [EXTRACTED]
  src/typst_rag/cli.py → src/typst_rag/build_index.py
- `build_index_cmd()` --calls--> `build_index()`  [EXTRACTED]
  src/typst_rag/cli.py → src/typst_rag/build_index.py
- `update_docs()` --calls--> `build_index()`  [EXTRACTED]
  src/typst_rag/cli.py → src/typst_rag/build_index.py
- `chunk()` --calls--> `chunk_documents()`  [EXTRACTED]
  src/typst_rag/cli.py → src/typst_rag/chunk.py
- `fetch()` --calls--> `fetch_typst()`  [EXTRACTED]
  src/typst_rag/cli.py → src/typst_rag/fetch_typst.py

## Import Cycles
- None detected.

## Communities (13 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (24): 10. Chunking strategy, 11. Embeddings, 12. Build LanceDB index, 13. Search module, 14. LLM-agnostic answer generation, 15. CLI, 16. End-to-end command sequence, 17. Evaluation plan (+16 more)

### Community 1 - "Community 1"
Cohesion: 0.27
Nodes (12): DataFrame, SearchMode, build_prompt(), openai_compatible(), retrieval_only(), ask(), eval_cmd(), search_cmd() (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (15): Ponytail prompt, 1. Local install, 2. Hermes skill: any Hermes model, 3. Local Ollama answer mode, 4. Plain Ollama chat, 5. ChatGPT or Claude web chat, 6. GitHub Pages / FTP hosting, 7. Example questions (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (12): Acceptance, Commands, Evidence, Goal, Next Improvements Roadmap, Phase 6. Package-quality local distribution, Phase 7. Professor-facing artifact, Phase 8. Typst Universe decision (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.39
Nodes (8): Path, collect(), collect_documents(), guess_kind(), iter_source_files(), section_for(), stable_id(), url_for()

### Community 5 - "Community 5"
Cohesion: 0.39
Nodes (6): SentenceTransformer, build_index(), build_index_cmd(), embed_passages(), embed_query(), model()

### Community 6 - "Community 6"
Cohesion: 0.33
Nodes (5): Boundaries, Optional local Ollama answer mode, Procedure, Setup, TypstRAG

### Community 7 - "Community 7"
Cohesion: 0.40
Nodes (5): 18.1 Better chunk metadata, 18.2 Add code block duplication, 18.3 Use stronger embeddings, 18.4 Add reranker, 18. Retrieval quality improvements

### Community 8 - "Community 8"
Cohesion: 0.40
Nodes (5): 21. Common failure modes, Problem: generated answers hallucinate Typst syntax, Problem: Russian questions retrieve weak results, Problem: Rust doc comments are noisy, Problem: search misses exact function names

### Community 9 - "Community 9"
Cohesion: 0.27
Nodes (9): chunk_documents(), sliding(), split_headings(), build_all(), chunk(), doctor(), fetch(), update_docs() (+1 more)

## Knowledge Gaps
- **59 isolated node(s):** `typst-rag`, `Progress`, `Evidence`, `Goal`, `Commands` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RAG for Typst Documentation on LanceDB` connect `Community 0` to `Community 8`, `Community 7`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `18. Retrieval quality improvements` connect `Community 7` to `Community 0`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `21. Common failure modes` connect `Community 8` to `Community 0`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **What connects `typst-rag`, `Progress`, `Evidence` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._