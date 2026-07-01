from typst_rag.chunk import sliding, split_headings
from typst_rag.collect import stable_id
from typst_rag.search import search


sections = split_headings("= A\ntext\n\n== B\nmore")
assert len(sections) == 2, sections
assert sliding("x" * 2000), "sliding produced no chunks"
assert stable_id("v0.15.0", "docs/content/index.typ") == stable_id("v0.15.0", "docs/content/index.typ")

results = search("two columns page setup", limit=3)
assert not results.empty, "search returned no rows"
assert "source_path" in results.columns, results.columns

print("smoke ok")
