# Neural Control Engineering

[Open the merged book and errata](Neural%20Control%20Engineering%20-%20merged.pdf).

The merged PDF contains **401 pages** from all **18 supplied files**, in this order:

1. Series foreword and preface.
2. Chapters 1–13, in chapter order.
3. Bibliography.
4. Index, including the colour plates contained in that PDF.
5. Publisher errata, appended as a supplement.

All original PDFs remain in `individual_pdfs/`. Blank pages, colour plates and publisher download watermarks are preserved. Bookmarks identify each part and the colour plates; PDF page labels distinguish the main text from the preface, plates and errata.

`merge_manifest.json` records the source filenames, source hashes, page counts and merged page ranges. All 13 chapter headings were checked against their filenames, and every merged page's extracted text was verified against its original.

Rebuild from the workspace root:

    python "References/modeling and control/Neural Control Engineering/merge_local_pdfs.py"

The earlier `Neural Control Engineering - available sample and errata.pdf` is the old 33-page partial collection. `download_and_merge.py` and `download_manifest.json` document that earlier attempt; use `merge_local_pdfs.py` for the current assembled book.
