**Combining anticausal/noncausal rational Zames–Falb searches with dual PIE-IQC synthesis**

12 November 2026. This note compares the supplied Carrasco–Maya-Gonzalez–Lanzon–Heath paper (Systems & Control Letters 70, 2014, pp. 17–22) with the supplied manuscript, Dual Integral Quadratic Constraint Representations for Robust Control of Partial Integral Equations, root.pdf. It identifies a conditional construction, not a completed implementation or a theorem of unrestricted joint convex co-design.

**1. Conclusion**

Yes: use a rational Zames–Falb (ZF) multiplier as the nonlinear uncertainty description, obtain an admissible causal hard factorization of its IQC, and apply the manuscript's plant-side duality route R.2 to the PIE plant. This retains transport/delay dynamics exactly. The causal, anticausal and noncausal multiplier families then provide alternative certificates for analysis and candidate synthesis.

Two distinctions are essential:

- A noncausal frequency-domain multiplier is not the causal filter required in the manuscript's finite-horizon theorem.
- Convex multiplier search for a fixed finite-dimensional plant and convex controller synthesis for a fixed dual filter do not automatically imply one convex joint search over controller and all multiplier dynamics.

**2. The relevant results in each supplied paper**

Carrasco et al. Definition 1.1 and Theorem 2.1 use bilateral L2 multipliers of the form

\[
M(s)=1-H(s),\qquad
\int_{-\infty}^{\infty}|h(t)|dt<1.
\]

Its central analysis condition for stable rational G in the negative-feedback convention is

\[
\Re\{M(j\omega)(1+kG(j\omega))\}>0
\quad \text{for all frequencies, including infinity}.
\]

The paper's displayed theorem/search propositions assume a static odd nonlinearity with slope in [0,k]. Section 4 introduces the anticausal search and a Popov-augmented noncausal subset. It does not supply an unrestricted complete noncausal search or a PIE controller-synthesis theorem.

The supplied root.pdf has the appropriate route in Section VI-B: nonlinear uncertainties are handled by plant-side duality R.2, not by assigning a linear adjoint/dual realization to the sigmoid under R.1. Definition 7 requires a stable LTI hard factor Theta with a signature-type weight, bounded causal inverses for Theta and Theta_22, and the finite-horizon uncertainty inequality. Theorem 3 gives the primal–dual conversion under its additional input-coordinate inverse conditions. Section VII's plant-side state-feedback corollary then supplies the synthesis LPI.

The manuscript explicitly states that the synthesis inequality is affine in the storage P, feedback variable Z and multiplier weight V for a FIXED dual filter. Its dynamic controller realization also assumes availability of the required plant and nonlinear-channel signals.

**3. Put the ZF description into an IQC**

Let w = phi(v), phi(0) = 0, with fixed memoryless phi having slope in [0,k]. A standard frequency-domain form is

\[
\Pi_{\rm ZF}(j\omega)=
\begin{bmatrix}
0 & kM(j\omega)^*\\
kM(j\omega)&-[M(j\omega)+M(j\omega)^*]
\end{bmatrix}.
\]

It describes the nonnegative quadratic form associated with 2 Re <w,M(kv-w)>.

Check the feedback sign carefully. Carrasco's convention is negative feedback; the corresponding root manuscript graph can use P = -G when w = phi(v). Changing this convention without changing the plant sign reverses the certificate interpretation.

For a general monotone slope-restricted nonlinearity that is not odd, use the positive-kernel ZF subclass h(t) >= 0 together with its mass bound. The absolute-L1 signed-kernel freedom in the supplied 2014 theorem relies on oddness. A sigmoid shifted about an arbitrary equilibrium is not generally odd; a logistic shifted about its inflection point and centred in output is odd. Do not assume all fitted neural operating points satisfy that special symmetry.

For several independent scalar sigmoid channels, begin with a block-diagonal collection of scalar multipliers. Arbitrary cross-channel multipliers require additional structure and a validity argument. The broad time-varying uncertainty classes in root.pdf also do not automatically make a ZF multiplier valid for a time-varying nonlinearity; cross-time monotonicity must be justified for the actual class.

**4. Why direct insertion of an anticausal filter fails**

Anticausal M may have right-half-plane poles while defining a bounded bilateral operator. Example (10) of Carrasco et al. is

\[
M(s)=\frac{s-0.0012}{s-1.09}.
\]

Its anticausal interpretation has

\[
H(s)=\frac{1.0888}{1.09-s},\qquad
h(t)=1.0888e^{1.09t}\,1_{\{t<0\}},
\]

with L1 mass 1.0888/1.09 < 1. The same rational expression implemented as an ordinary forward-time filter is unstable.

Therefore M cannot simply be placed in the time-domain augmented plant and declared an admissible Theta. A causal stable factorization of the self-adjoint IQC is the bridge. Likewise, a stable but arbitrary factorization of a frequency IQC is not automatically hard on every finite horizon; terminal filter energy matters.

The P < 0 in the anticausal multiplier-search derivation is an auxiliary certificate for that multiplier realization. It does not authorize negative physical storage in the PIE synthesis LPI, where the required storage remains nonnegative/coercive.

**5. A concrete finite-channel factorization route**

The raw ZF matrix has Pi_11 = 0, so it does not directly satisfy the strict positive–negative condition used in the standard J-spectral-factorization existence result. A sufficient regularization is

\[
\Pi_\epsilon=\Pi_{\rm ZF}+
\epsilon\begin{bmatrix}I&0\\0&0\end{bmatrix},
\qquad \epsilon>0.
\]

This remains a valid uncertainty IQC: it adds epsilon times the squared norm of the input, a nonnegative term.

If norm(h)_1 <= 1-eta with eta > 0, then Re M(j omega) >= eta, so

\[
\Pi_{\epsilon,11}=\epsilon I\succ0,\qquad
\Pi_{\epsilon,22}\preceq-2\eta I\prec0.
\]

For proper rational finite-dimensional channels, this is a strict positive–negative multiplier. Seiler (2015), Theorem 4, gives a stable/minimum-phase J-spectral factorization

\[
\Pi_\epsilon=\Theta^\sim J_s\Theta,\qquad
J_s=\operatorname{diag}(I,-I),\qquad
\Theta,\Theta^{-1}\in RH_\infty,
\]

and hardness. This is a sufficient bridge; it is not a claim that the unregularized ZF multiplier can never have a suitable factorization. The manuscript's Theta_22 and input-coordinate conditions must still be checked explicitly for the factor/interconnection used.

The regularization is compatible with an already strict plant certificate. If a fixed stable plant P satisfies

\[
[P;I]^*\Pi_{\rm ZF}[P;I]\preceq-\delta I
\]

uniformly in frequency, then the extra term is epsilon P*P. Choosing epsilon norm(P)_infty² < delta preserves strict negativity. Thus an arbitrarily small positive regularization can provide strict PN structure when there is a uniform margin. This argument requires a bounded fixed plant and should not be asserted blindly for an unstable open-loop model or an unknown candidate controller.

Source for the finite-dimensional factorization step: Peter Seiler, Stability Analysis With Dissipation Inequalities and Integral Quadratic Constraints, IEEE TAC 60(6), 1704–1709, 2015, Theorem 4:
https://dept.aem.umn.edu/~SeilerControl/Papers/2015/Seiler_15TAC_StabilityAnalysisWithDIandIQCs.pdf

For the neural application, two scalar E/I nonlinear channels remain finite-dimensional even if the linear plant contains infinite-dimensional transport histories. The finite-channel factorization theorem therefore applies to the multiplier matrix; the plant can still be treated by a PIE certificate. A nonlinearity distributed pointwise over a physical continuum is a different case and requires an operator/spatial lifting justification. The manuscript itself flags the infinite-channel factorization issue.

**6. Apply the manuscript's dual construction**

Once an admissible hard factorization has been established, use its definition

\[
\underline\Theta=\mathbf D(\Theta)
=(\hat J^*\Theta'\hat J)^{-1},
\qquad
\underline N=-\mathbf D(N).
\]

Here prime means the manuscript's CAUSAL LTI system dual. It must not be confused with the bilateral L2 adjoint M^sim(s) = M(-s)^T used in the 2014 paper. Transposing a causal state-space realization preserves stable pole locations; time-reversing the operator is a different operation.

Augment the dual PIE with the stable finite-dimensional filter states. For a fixed admissible dual filter, solve the manuscript's synthesis LPI in storage P and Z = P K*, then recover

\[
K=Z^*P^{-1}
\]

under the manuscript's coercivity and PI-representability conditions. Apply its R.2 well-posedness, finite-horizon, feedthrough and input-coordinate-inverse hypotheses. Dynamic controller implementation requires its signal-availability assumptions; a full-state result is not automatically an output-feedback observer result.

A noncausal multiplier in this derivation does not require a noncausal controller or future neural measurements. It is a certificate; the realized filters/controller must be causal.

**7. What remains convex**

| Design task | Status |
|---|---|
| Analyze a fixed plant with the supplied finite-dimensional rational search | Covered by Carrasco's search assumptions, including its scalar line searches and nonlinear class. |
| Verify a fixed admissible rational IQC on an exact transport/PIE plant | A plausible PIE/KYP/LPI application after factorization; retains exact delays. |
| Synthesize a controller with a fixed admissible dual filter | Convex LPI in the manuscript's declared variables. |
| Jointly optimize admissible weights in a fixed dual-filter family | Potentially convex where validity constraints and weights remain affine; requires a family-specific proof. |
| Jointly optimize arbitrary multiplier poles, residues, spectral factor and controller | Not established by combining the two papers. Unknown filter dynamics multiply storage/controller variables; factorization/inversion also depends nonlinearly on the multiplier. |

A conservative first implementation is an outer search over admissible multiplier candidates, with a fixed-filter synthesis LPI inside. Search/analysis for a fixed controller, factorization and verification, synthesis, and final verification can be alternated, but this is not a globally optimal joint convex method.

Do not insert a bare Popov term q s into a framework requiring bounded proper filters. Carrasco treats it through limiting/extended arguments. Begin with the proper anticausal rational family, or use a carefully justified proper rational approximation to the Popov extension and verify membership/factorization.

The original 2014 LMIs use a finite-dimensional stable rational plant. Their derivation cannot be copied verbatim to an infinite-dimensional delayed plant. Use them to generate candidates on an appropriate finite-dimensional benchmark or approximation, then certify the actual PIE plant; alternatively derive the corresponding operator inequalities. Candidate generation on an approximate plant does not replace verification on the exact delayed plant.

**8. Suggested first experiment**

Use one scalar slope-restricted channel and a small stable ODE benchmark first. Recover an anticausal multiplier from the 2014 examples, regularize if needed, compute its hard J factor and verify the graph inequalities and R.2 hypotheses. Then repeat with an exact one-delay transport PIE and compare sector-only, causal ZF, anticausal ZF and proper noncausal candidates. Only after the analysis comparison works, add controller synthesis and compare certified slope/delay margins or performance bounds.

For the fitted neural plant, use the two sigmoid channels with the same actuation/output constraints across all designs. Preserve delays exactly. If explicit refractory availability multiplies the sigmoid, isolate and bound that additional nonlinearity; a ZF IQC for the sigmoid does not certify the product automatically.

No combined search, numerical certificate, or controller has been implemented in this note. The proposed construction identifies the factorization proof and fixed-filter synthesis route needed before such a claim can be made.

**Supplied documents**

- Carrasco et al. (2014), [LMI searches for anticausal and noncausal rational ZF multipliers](<../References/Zames Falb/LMI searches for anticausal and noncausal rational ZF multipliers.pdf>), especially Definition 1.1, Theorem 2.1, Section 4 and Table 3. DOI: https://doi.org/10.1016/j.sysconle.2014.05.005.
- Lenssen et al., [Dual IQC manuscript, root.pdf](<C:/Users/thijs/Desktop/Graduation_Project_TML/Documentation/Dual Integral Quadratic Constraints Representation for Robust Control of Partial Integral Equations/build/root.pdf>), Definition 7, Theorem 3, route R.2 and Section VII's plant-side state-feedback synthesis.
