# Saturation and saturation-envelope IQCs

[Technical note](saturation_iqc.tex) using the notation of Vahedi Noori, Hu,
Dullerud and Seiler, *A Complete Set of Quadratic Constraints for Repeated ReLU
and Generalizations*, arXiv:2407.06888v2.

The note derives, in order:

1. Fixed saturation maps: exact ReLU realization, lifted QC/IQC families, and
   complete copositive characterizations of ordinary and affine graph QCs.
2. Fixed saturation maps: the complete homogeneous incremental QC cone, equal
   (after slope normalization) to the paper's complete incremental ReLU cone;
   the corresponding hard IIQCs follow by integration.
3. Functions between two fixed saturation envelopes: lifted ReLU/slack QCs and
   complete copositive characterizations of graph and incremental QCs.
4. Why the unrestricted sandwich class, even with continuity, has only trivial
   positive-semidefinite homogeneous difference multipliers when every channel
   has a positive envelope gap.
5. A useful sigmoid subclass combining the sandwich with slope bounds, including
   a sufficient lifted family and an SDP implication for eliminating auxiliaries.
6. Proved global saturation sandwiches for the workspace's tanh-form sigmoids,
   including horizontally shifted equal-slope ramps with small vertical margins
   matching the proposed sketch, necessary and sufficient horizontal-shift
   thresholds, and an optional exactly zero lower floor.

The note distinguishes exact class-membership tests and complete copositive
multiplier characterizations from sufficient lifted elimination and SDP
relaxations. The sandwich-product condition is an iff membership test when the
envelope signals are retained.

These are static hard IQCs/IIQCs, not new dynamic multiplier factorizations.
Affine lifts and two-copy lifts are distinguished from the paper's homogeneous
QCs on the original input/output signals. Exact copositive tests are separated
from sufficient SDP relaxations. No particular delayed closed loop is certified.

Build from this directory:

```powershell
pdflatex '--output-directory=..\build' '--interaction=nonstopmode' '--halt-on-error' saturation_iqc.tex
pdflatex '--output-directory=..\build' '--interaction=nonstopmode' '--halt-on-error' saturation_iqc.tex
```

The result is [the PDF](../build/saturation_iqc.pdf).

Check the graph generators, scaling constructions, envelopes and two-copy maps:

```powershell
python verify_saturation_iqc.py
```

The script requires NumPy and writes `verification_results.json`. Its numerical
checks supplement the analytic proofs; they do not prove universal copositivity
or establish feasibility of a plant/controller inequality.
