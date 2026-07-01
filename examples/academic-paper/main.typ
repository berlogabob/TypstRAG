#set document(title: "TypstRAG Example Paper")
#set page(paper: "a4", margin: 1.8cm)
#set text(font: "Libertinus Serif", size: 10pt)
#set par(justify: true)

#align(center)[
  #text(17pt, weight: "bold")[TypstRAG Example Paper]

  #v(0.4em)
  Berloga Bob #sym.dot Christopher Example

  #v(0.4em)
  #text(9pt)[Local RAG over Typst documentation]
]

#v(1em)
#block[
  #text(weight: "bold")[Abstract.] This minimal paper demonstrates the Typst features that TypstRAG retrieves from local Typst documentation: page columns, figures with captions, and bibliography references. The goal is a professor-facing artifact that compiles without a custom template.
]

#set page(columns: 2)
#set columns(gutter: 14pt)

= Introduction

TypstRAG indexes a pinned Typst documentation tag into a local LanceDB database. The workflow is deliberately small: clone the project, build the index, ask a question, and inspect cited documentation sources.

The example cites prior work on readable markup systems @knuth1984 and local retrieval workflows @lewis2020.

= Method

The pipeline has four steps: fetch Typst docs, collect source files, split documents into chunks, and build a vector index. A user can then query the index from the CLI or let Hermes use the retrieved context with any current model.

#figure(
  rect(width: 100%, height: 4cm, fill: luma(235), stroke: 0.6pt)[
    #align(center + horizon)[TypstRAG pipeline placeholder]
  ],
  caption: [Minimal professor-facing pipeline diagram.],
) <fig:pipeline>

As shown in @fig:pipeline, the artifact is intentionally local-first. This avoids hosting a Python backend just to share a reproducible academic demo.

= Result

The current smoke checks verify that the local index opens, search returns rows, and the retrieval evaluation keeps an expected-term hit rate of 1.00 on the small built-in query set.

= Conclusion

The project is ready to share as a local RAG package and demo. A future Typst Universe submission should be a separate Typst template package, not the Python RAG itself.

#bibliography("refs.bib", style: "apa")
