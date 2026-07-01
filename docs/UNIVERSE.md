# Typst Universe companion

TypstRAG itself is a Python CLI/RAG and should not be submitted to Typst Universe.

The Universe-shaped companion is:

```text
packages/ragged-paper/
```

It is a small two-column academic paper template.

## Local verification

```bash
rm -rf /tmp/typst-packages /tmp/ragged-paper-init
mkdir -p /tmp/typst-packages/preview/ragged-paper/0.1.0
cp -R packages/ragged-paper/. /tmp/typst-packages/preview/ragged-paper/0.1.0/
TYPST_PACKAGE_PATH=/tmp/typst-packages typst init @preview/ragged-paper:0.1.0 /tmp/ragged-paper-init
TYPST_PACKAGE_PATH=/tmp/typst-packages typst compile /tmp/ragged-paper-init/main.typ /tmp/ragged-paper-init/main.pdf
```

## If submitting later

Copy `packages/ragged-paper` into a fork of `typst/packages` as:

```text
packages/preview/ragged-paper/0.1.0/
```

Then open a PR. Do not submit until the name/description are final.
