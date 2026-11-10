# Technical notes

- [Projection lemmas](PIE_projection_lemma.tex) ([PDF](build/PIE_projection_lemma.pdf)): Lemmas 4.14 and 4.15 in PI-operator notation, with their proofs and additional requirements marked inline.
- [Nonzero initial conditions and IQCs](IQC_nonzero_initial_conditions.tex): existing notes on initialized plants and IQC stability.

Build the projection note from this directory:

```powershell
latexmk -pdf -synctex=1 -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build PIE_projection_lemma.tex
```
