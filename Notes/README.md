# Technical notes

- [Saturation and saturation-envelope IQCs/IIQCs](saturation_iqc/README.md) ([PDF](build/saturation_iqc.pdf)): paper notation, complete copositive graph tests, incremental constraints, and a slope-restricted sigmoid subclass.
- [Projection lemmas](PIE_projection_lemma.tex) ([PDF](build/PIE_projection_lemma.pdf)): Lemmas 4.14 and 4.15 in PI-operator notation, with their proofs and additional requirements marked inline.
- [Nonzero initial conditions and IQCs](IQC_nonzero_initial_conditions.tex): existing notes on initialized plants and IQC stability.
- [Dual-first hard incremental IQCs for paired sigmoids](sigmoid_iiqc/dual_first.md): square dual/primal factors, primal admissibility, and MATLAB verification; H need not have a stable proper inverse. The earlier [primal-first construction](sigmoid_iiqc/README.md) is retained for comparison.

Build the projection note from this directory:

```powershell
latexmk -pdf -synctex=1 -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build PIE_projection_lemma.tex
```
