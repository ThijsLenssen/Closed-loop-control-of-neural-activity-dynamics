# Alternative dual multiplier: notation, proof and MATLAB test

This construction uses the notation of the supplied manuscript, *Dual Integral
Quadratic Constraint Representations for Robust Control of Partial Integral
Equations*, Definition 7, Theorem 3 and route R.2 (plant-side IQC duality).
The formal proposition and complete proof are in Section 2 of
[the compiled note](../../build/multipliers.pdf), with source
[alternative_multiplier.tex](alternative_multiplier.tex).

The paper uses **underlines** for dual quantities:

| Paper symbol | Meaning | MATLAB field |
| --- | --- | --- |
| $\Theta_\Delta$ | Primal square hard factor | `iqc.Theta_Delta` |
| $\mathcal N_\Delta$ | Primal signature weight | `iqc.N_Delta` |
| $\underline\Theta_\Delta$ | Dual square factor | `iqc.Theta_Delta_underlined` |
| $\underline{\mathcal N}_\Delta$ | Dual signature weight | `iqc.N_Delta_underlined` |
| $\mathcal X_\Delta,\mathcal Y_\Delta$ | Positive primal signature blocks | `iqc.X_Delta`, `iqc.Y_Delta` |
| $\hat J$ | Signature permutation | `iqc.hatJ` |

We specialize the paper's spatial operators to finite-dimensional matrices
for the delay-free STN/GPe model. The truncation $p_T$ restricts signals to
$[0,T]$. Filters start at zero. No dual or adjoint of the nonlinear sigmoid
is required.

## Define the alternative factor on the dual side

In the incremental application, the paper's uncertainty signals denote

$$z_\Delta=q^{(1)}-q^{(2)},\qquad
w_\Delta=S(q^{(1)})-S(q^{(2)}).$$

The componentwise sigmoid slope bound $0\le S_i'\le1$ implies
$w_\Delta=D(t)z_\Delta$, with diagonal entries of $D(t)$ in $[0,1]$.
The proof allows every measurable such diagonal slope signal, with no rate
bound, even though this is a larger class than actual sigmoid increments.

For pair $j$, choose $0<\rho_j<1$, $a_j>0$, integer $n_j\ge1$,
$0\le\beta_j<1$, and $t_j>0$. Set

$$R=\begin{bmatrix}1&1\\-1&0\end{bmatrix},\quad
h_j(s)=\left(\frac{\beta_j s+a_j}{s+a_j}\right)^{n_j},\quad
H_j=\rho_j h_j R,\quad \eta_j=\frac{(1-\rho_j)^2}{8}.$$

Put $H=\operatorname{blkdiag}(H_j)$,
$E=\operatorname{blkdiag}(\eta_j I_2)$ and
$W=\operatorname{blkdiag}(t_j I_2)$. Define

$$\boxed{\underline\Theta_\Delta=\begin{bmatrix}I&-H\\0&I\end{bmatrix},
\qquad \underline{\mathcal N}_\Delta=\operatorname{diag}(WE^{-1},-W).}$$

Equivalently, take $\underline\Psi_\Delta=\underline\Theta_\Delta$ and
$\underline{\mathcal V}_\Delta=\underline{\mathcal N}_\Delta$.
For fixed filters the dual weight is affine in the positive pair weights
$t_j$. The MATLAB implementation uses a shared pole, order and beta across
pairs and allows independent rho and pair weights.

## Recover the primal factor using the paper's map

The paper defines

$$\mathbf D(\Theta)=
(\mathcal M_{\hat J}^*\Theta'\mathcal M_{\hat J})^{-1},\qquad
\hat J=\begin{bmatrix}0&I\\-I&0\end{bmatrix}.$$

Here prime is the causal LTI dual: $(A,B,C,D)'=(A^\top,C^\top,B^\top,D^\top)$.
It is different from the generally anticausal half-line adjoint.
At a complex frequency, `Hprime(s)=H(s).'` uses a **nonconjugating** transpose.

Recovery gives

$$\boxed{\Theta_\Delta=\mathbf D(\underline\Theta_\Delta)
=\begin{bmatrix}I&-H'\\0&I\end{bmatrix},\qquad
\mathcal N_\Delta=-\mathbf D(\underline{\mathcal N}_\Delta)
=\operatorname{diag}(W^{-1},-EW^{-1}).}$$

Thus $\mathcal X_\Delta=W^{-1}$ and $\mathcal Y_\Delta=EW^{-1}$ are
coercive, and involutivity gives $\underline\Theta_\Delta=\mathbf D(\Theta_\Delta)$.
The inverses are explicitly

$$\Theta_\Delta^{-1}=\begin{bmatrix}I&H'\\0&I\end{bmatrix},\qquad
\underline\Theta_\Delta^{-1}=\begin{bmatrix}I&H\\0&I\end{bmatrix}.$$

Both are stable and causal. Also $\Theta_{\Delta,22}=I$ and
$\Gamma=\Theta_{\Delta,21}P+\Theta_{\Delta,22}=I$ for the uncertainty-only
plant partition. **No inverse of $H$ is needed.** In particular,
$\beta=0$ makes $H$ strictly proper, with no proper inverse, while all
factor inverse conditions still hold.

## Proposition: hard incremental admissibility

For every finite $T\ge0$ and every pair of sigmoid input trajectories,

$$\begin{aligned}
\mathcal I_\Delta(T)
&=\left\langle p_T\Theta_\Delta\begin{bmatrix}z_\Delta\\w_\Delta\end{bmatrix},
p_T\mathcal M_{\mathcal N_\Delta}\Theta_\Delta\begin{bmatrix}z_\Delta\\w_\Delta\end{bmatrix}\right\rangle_{L_2}\\
&=\sum_j\frac1{t_j}\left(\|z_{\Delta,j}-H_j'w_{\Delta,j}\|_{2,T}^2
-\eta_j\|w_{\Delta,j}\|_{2,T}^2\right)\\
&\ge\sum_j\frac{\eta_j}{t_j}\|z_{\Delta,j}\|_{2,T}^2\ge0.
\end{aligned}$$

**Proof.** For one pair define the auxiliary norm
$\nu_-(x)=\max(|x_1|,|x_2|,|x_1-x_2|)$, distinct from the paper's
signature weight $\mathcal N_\Delta$. Then

$$\nu_-(R^\top x)=\nu_-(x),\qquad
\nu_-(Dx)\le\nu_-(x),\qquad
\|x\|_2/\sqrt2\le\nu_-(x)\le\sqrt2\|x\|_2.$$

The first identity follows from $R^\top x=(x_1-x_2,x_1)$.
For the second, convexity reduces the maximum of
$|d_1x_1-d_2x_2|$ over the unit square to its four vertices.
Write $\|f\|_{\nu_-,T}^2=\int_0^T\nu_-(f(t))^2\,dt$.

Each stage of $h$ is $\beta+(1-\beta)a/(s+a)$. Its cascade expands into
a convex combination of identity and low-pass Erlang kernels of total
mass one. Young's inequality with zero extension of the input therefore
gives $\|hf\|_{\nu_-,T}\le\|f\|_{\nu_-,T}$ on every horizon, including
$\beta=0$. Consequently,

$$\|H'w_\Delta\|_{\nu_-,T}\le\rho\|w_\Delta\|_{\nu_-,T}
\le\rho\|z_\Delta\|_{\nu_-,T}.$$

For $r=z_\Delta-H'w_\Delta$, the reverse triangle inequality yields
$(1-\rho)\|z_\Delta\|_{\nu_-,T}\le\|r\|_{\nu_-,T}$.
Norm equivalence and the diagonal slope bound give

$$\|r\|_{2,T}^2\ge\frac{(1-\rho)^2}{4}\|z_\Delta\|_{2,T}^2
=2\eta\|z_\Delta\|_{2,T}^2,\qquad
\|w_\Delta\|_{2,T}\le\|z_\Delta\|_{2,T}.$$

Subtract $\eta\|w_\Delta\|_{2,T}^2$ and sum the pair inequalities with
weights $t_j^{-1}$ to obtain the claim. To complete Definition 7, take
$\Psi_\Delta=\Theta_\Delta$, $\mathcal V_\Delta=\mathcal N_\Delta$ and
$\mathcal U_\Delta=I$; the factorization equality is then immediate.
Coercivity and the stable causal inverse conditions were verified above.
This proves the uncertainty-channel factor admissibility. Neither
trajectory needs to be an equilibrium.

## Complementary inequality and scope

Following Theorem 3, use the graph of the **linear** dual $P'$:

$$\underline{\mathcal I}(T)=
\left\langle p_T\underline\Theta_\Delta\begin{bmatrix}P'\underline w\\\underline w\end{bmatrix},
p_T\mathcal M_{\underline{\mathcal N}_\Delta}\underline\Theta_\Delta\begin{bmatrix}P'\underline w\\\underline w\end{bmatrix}\right\rangle_{L_2}
\le-\underline\epsilon\|p_T\underline w\|_{L_2}^2.$$

On the illustrative matching plant $P=H'$, $P'=H$, the first filtered
output vanishes and the primal/dual supplies are exactly
$-\|w\|_{EW^{-1},T}^2$ and $-\|\underline w\|_{W,T}^2$.
These are strict complementary inequalities for a test plant; they are
not a certificate for the actual STN/GPe network or an unspecified fixed
controller. That requires its own strict inequality and well-posedness
checks. Additional performance channels must meet the paper's factor and
full input-coordinate assumptions as well.

An arbitrary conic sum of dual multipliers does not recover by conically
summing the primal multipliers: $\mathbf D$ includes inversion. Such a sum
requires its own admissible hard factorization. The positive pair-weight
family above avoids that issue.

## KYP feasibility test

The self-contained example is [verify_sigmoid_dual_kyp.m](verify_sigmoid_dual_kyp.m).
It contains the filter, matching test plant and KYP LMI in one 38-line
script. The general A/B/C/D solver [kyp_iqc_graph.m](kyp_iqc_graph.m) remains
optional.
Using the paper's notation, realize the filtered dual graph as

$$\underline\Theta_\Delta\begin{bmatrix}P'\\I\end{bmatrix}:
\quad\dot{\underline x}=\underline{\mathcal A}\underline x
+\underline{\mathcal B}\underline w,\qquad
\underline v=\underline{\mathcal C}\underline x+\underline{\mathcal D}\underline w.$$

The ODE specialization of the paper's dual KYP LPI is

$$\mathcal P\succeq0,\quad
\begin{bmatrix}
\underline{\mathcal A}^\top\mathcal P+\mathcal P\underline{\mathcal A}
&\mathcal P\underline{\mathcal B}\\
\underline{\mathcal B}^\top\mathcal P&\underline\epsilon I
\end{bmatrix}
+\begin{bmatrix}\underline{\mathcal C}^\top\\\underline{\mathcal D}^\top\end{bmatrix}
\underline{\mathcal N}_\Delta
\begin{bmatrix}\underline{\mathcal C}&\underline{\mathcal D}\end{bmatrix}
\preceq0.$$

Here $\mathcal P$ is the storage matrix, distinct from the plant $P$.
Along the filtered graph, this LMI gives
$\dot V+\underline v^\top\underline{\mathcal N}_\Delta\underline v
+\underline\epsilon\|\underline w\|^2\le0$.
Integrating from zero initial state and using $V(T)\ge0$ proves the
finite-horizon complementary inequality. Primal sigmoid admissibility
is the preceding proposition; this KYP test concerns the linear graph.

Run the test with YALMIP and SeDuMi installed:

```matlab
addpath('Notes/sigmoid_iiqc')
verify_sigmoid_dual_kyp
```

The script uses $\rho=0.95$, $a=1$, $n=10$, and defaults to beta=0.
Change `beta` to 0.5 at the top to test the biproper case. It assembles the
unreduced dual graph of the matching test plant $P'=H$, prescribes
$\underline\epsilon=0.5$, solves for the storage matrix, and checks the
storage and KYP eigenvalues. It uses a state-space cascade for h to avoid
high-order polynomial realizations. The sigmoid's primal admissibility
proof remains the preceding proposition.

For the simplest use, replace `Pprime = H` in the script with your fixed
dual state-space plant. The additional comparisons and automatic report
saving have been removed from the example. Earlier comparison results are
retained in `dual_kyp_results.mat` and `dual_kyp_run.log`.

For your own fixed plant, supply its numeric continuous-time realization
in `P.A`, `P.B`, `P.C`, `P.D` and use:

```matlab
iqc = sigmoid_dual_iiqc(0.95,100,10);
Pprime.A = P.A.'; Pprime.B = P.C.';
Pprime.C = P.B.'; Pprime.D = P.D.';
certificate = kyp_iqc_graph(Pprime,iqc.Theta_Delta_underlined, ...
                           iqc.N_Delta_underlined,1e-3,'sedumi');
certificate.passed
```

The prescribed margin `1e-3` can be changed. Failure of a particular
fixed-filter KYP test is not a proof of instability. The code requires
YALMIP and an SDP solver; the separate trajectory tests below do not.

## MATLAB trajectory and algebra tests

From the project root:

```matlab
addpath('Notes/sigmoid_iiqc')
iqc = sigmoid_dual_iiqc(0.95,100,10); % beta=0 by default
Theta_Delta = iqc.Theta_Delta;
N_Delta = iqc.N_Delta;
Theta_Delta_underlined = iqc.Theta_Delta_underlined;
N_Delta_underlined = iqc.N_Delta_underlined;
report = verify_sigmoid_dual_iiqc;
```

The factor structures contain numeric `A,B,C,D,M` and their zero initial
states. No toolbox is needed. The descriptive fields `iqc.primal` and
`iqc.dual` remain aliases. `N_Delta` is the paper's calligraphic weight,
not the realization feedthrough matrix `Theta_Delta.D`.

The test covers two/four channels, unequal pair weights, and both
`beta=0` and `beta=0.5`. It checks:

- Both square-factor inverses, the paper's filter/weight duality maps,
  coercive signature blocks, and the identity input-coordinate map.
- Actual PNAS sigmoid increments under independent, nearly equal,
  switching-common-input and correlated inputs.
- Arbitrary switching diagonal slopes, including the endpoints 0 and 1.
- The primal finite-prefix supply and the stronger proposition lower bound.
- Both complementary supplies for the matching plant, in the frequency
  and time domains, including unequal weights.
- The polyhedral norm identities and a test example where the diagonal
  static sector family fails its necessary determinant condition.

Held-input supplies are integrated by matrix exponentials, up to floating-point
error. There are 20 signal cases with 1001 prefixes each. These tests
supplement the analytic proof; sampling does not establish hardness.
The script saves `dual_verification_results.mat`; the retained console
output is in `dual_verification_run.log`.

The retained run passed all 20 cases and 20,020 prefixes. The largest
transfer duality-map error was below 1.4e-15. Time-domain complementary
identity errors were below 3.5e-18 (primal) and 7.2e-15 (dual).

The older rectangular primal-first construction in `README.md` and
`sigmoid_dynamic_iiqc.m` is retained for comparison. Its filter and weight
must not be mixed with this square dual construction.
