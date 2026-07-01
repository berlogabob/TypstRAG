# Ragged Paper

Small two-column academic paper.

Use it after publishing:

```typ
#import "@preview/ragged-paper:0.1.0": ragged-paper

#show: ragged-paper.with(
  title: "My Paper",
  authors: [Ada Example],
  affiliation: [Example Lab],
  abstract: [One paragraph summary.],
)

= Introduction

Your text.
```

Or initialize it once published:

```bash
typst init @preview/ragged-paper:0.1.0
```

This is a companion template for TypstRAG. The Python RAG itself is not a Typst Universe package.
