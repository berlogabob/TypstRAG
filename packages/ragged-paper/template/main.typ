#import "@preview/ragged-paper:0.1.0": ragged-paper

#show: ragged-paper.with(
  title: "A Small Paper Built from Retrieved Docs",
  authors: [Ada Example #sym.dot Bob Example],
  affiliation: [Local-first document tooling],
  abstract: [This starter demonstrates a two-column academic paper with a figure, citation, and bibliography.],
)

= Introduction

This template keeps the styling small and leaves the paper content plain. It is intended as a companion artifact for TypstRAG, not as a full journal class.

Readable technical writing benefits from small source files and reproducible tooling @knuth1984.

= Method

#figure(
  rect(width: 100%, height: 4cm, fill: luma(235), stroke: 0.6pt)[
    #align(center + horizon)[Figure placeholder]
  ],
  caption: [A placeholder figure with a caption.],
) <fig:placeholder>

Figure @fig:placeholder shows where a generated or measured result can go.

= Conclusion

Use this template as a starting point, then delete anything your paper does not need.

#bibliography("refs.bib", style: "apa")
