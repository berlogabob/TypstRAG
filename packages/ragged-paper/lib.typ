#let ragged-paper(
  title: "Untitled Paper",
  authors: [],
  affiliation: [],
  abstract: [],
  body,
) = {
  set document(title: title)
  set page(paper: "a4", margin: 1.8cm)
  set text(font: "Libertinus Serif", size: 10pt)
  set par(justify: true)

  align(center)[
    #text(17pt, weight: "bold")[#title]

    #v(0.4em)
    #authors

    #v(0.4em)
    #text(9pt)[#affiliation]
  ]

  v(1em)
  block[#text(weight: "bold")[Abstract.] #abstract]

  set page(columns: 2)
  set columns(gutter: 14pt)

  body
}
