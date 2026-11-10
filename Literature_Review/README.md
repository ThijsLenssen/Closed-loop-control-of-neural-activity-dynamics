# Literature notes

The general questions, proposed neural model and derived multiplier family are in `literature_review.tex`.

The included [medical and neuroscience nomenclature](medical_nomenclature.tex) explains the terminology in plain English, grouped by topic. The compiled review links to it near the beginning and includes a PDF bookmark for quick access.

The [paper notes index](Paper_Notes/README.md) links a separate LaTeX file and compiled PDF for each reference paper. Each answers the three paper-note questions in the notebook, with concise findings, model relevance and cited follow-ups. Notes use the reference PDFs independently, without drawing context from the PNAS manuscript or assuming beta suppression is the clinical objective.

It also records the derived PIE multiplier family with scalar input/output, distributed states, and scalar feedthrough variable d. The conditions are d > 0, a_j(s) > 0, and beta_j(s) >= 0 for polynomial profiles on [0,1]. Its transfer functions, scaled Zames–Falb normalization, and exact scalar impulse-response L1 bound are included; no upper bound on the integrated weights S is required.

Compile from this directory:

    latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build literature_review.tex

Open `build/literature_review.pdf` to see this build. Build the separate notes with:

    python Paper_Notes/build_notes.py
