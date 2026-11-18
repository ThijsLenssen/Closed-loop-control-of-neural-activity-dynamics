# A constructive linear dynamic hard IIQC for paired sigmoids

**Current formulation: [dual-first filter and primal admissibility](dual_first.md).**
Use `sigmoid_dual_iiqc.m` and `verify_sigmoid_dual_iiqc.m` for the
plant-side duality route in the supplied PIE paper. The square triangular
factors have bounded causal inverses even when H is strictly proper.
The default of the new generator is beta=0; an inverse of H is not required.

The primal-first construction below and `sigmoid_dynamic_iiqc.m` are
retained as a comparison, including the optional stable-H-inverse variant.
Their rectangular factor and old weight are different from the new square
dual/primal factors and must not be mixed.

## Simple KYP example

[verify_sigmoid_dual_kyp.m](verify_sigmoid_dual_kyp.m) is a self-contained
38-line script: define H, define the dual multiplier, assemble the KYP LMI,
and solve it. It needs Control System Toolbox, YALMIP and SeDuMi.

```matlab
addpath('Notes/sigmoid_iiqc')
verify_sigmoid_dual_kyp
```

The parameters are at the top. Change `beta` from 0 to 0.5 to test the
biproper filter. `Pprime = H` is the matching test plant; replace this line
with your fixed dual plant to test another system. The script prints the
input margin and the storage/KYP eigenvalues. It has no helper dependencies.

The hard sigmoid IQC proof is in [dual_first.md](dual_first.md) and
[Proposition 1 of the PDF](../../build/multipliers.pdf). The KYP equation is
in Section 2.3. The separate `kyp_iqc_graph.m` remains available for general
numeric A/B/C/D structures, but is not needed for this example.

## Earlier primal-first comparison

This note derives a continuous-time **sufficient family** of hard incremental
IQCs. The filter is causal, stable, rational and linear, and the auxiliary
transfer matrix H has a causal, proper, stable inverse. The construction
applies jointly to the STN and GPe sigmoid channels and can be repeated for
the observer pair. It is not a claim of a complete multiplier characterization,
and it does not certify the user's particular fixed controller until its
complementary inequality has been checked.

The construction was motivated by the polyhedral-norm example in Section
III.C of Qin and Karimi, *On the Incremental Stability of Recurrent Neural
Networks*, November 2026 preprint:
https://infoscience.epfl.ch/entities/publication/36724941-6c26-4580-ab14-077c05600c87
The downloaded source is retained in this folder. That paper concerns
discrete-time systems and infinite-horizon IQCs. The continuous-time,
finite-horizon proof below is a separate derivation; it is what establishes
hardness for this construction.

## Signals and the multiplier family

Let `F(q)=[FS(qS);FG(qG)]` apply the two PNAS sigmoids componentwise. Their
derivatives lie in `[0,1]`, regardless of their differing maximum and
baseline rates. For two arbitrary input trajectories define

```text
v = q - qtilde,
w = F(q) - F(qtilde).
```

Pointwise, `w=D(t)v` for some diagonal `D(t)` with entries in `[0,1]`.
No derivative or rate bound on `D` is imposed.

Choose fixed parameters `0 < rho < 1`, `a > 0`, `0 < beta < 1`, and integer
`n >= 1`. The default beta (MATLAB option `directRatio`) is 0.5.
Define

```text
R = [1 1; -1 0],
h(s) = ((beta s+a)/(s+a))^n,
H(s) = rho h(s) R,
eta = (1-rho)^2/8.
```

The proposed IQC is

```text
r = Psi(s) [v;w],

         [ I   -H(s) ]
Psi(s) = [ I      0  ],     M = diag(I,-eta I,-eta I).
         [ 0      I  ]

integral_0^T r(t)' M r(t) dt >= 0,    every T >= 0.
```

The state of `H` and hence `Psi` is zero initially. Both channels use the
same scalar `h`. The negative entry in `R` is allowed; its special norm
identity below, rather than positivity of all entries of `H`, proves the
constraint. Each scalar factor is a convex combination of the identity
and a unit-DC-gain low-pass filter. Thus h retains a nonnegative proper
impulse response and a nonnegative direct term, with total gain one.

### Stable causal inverse

The original strictly proper choice `(a/(s+a))^n` had an improper inverse.
The new biproper factor fixes this without changing the hard-IIQC bound:

```text
H^{-1}(s) = (1/rho) ((s+a)/(beta s+a))^n R^{-1},
R^{-1} = [0 -1; 1 1].
```

H has poles at `-a` and zeros at `-a/beta`; its inverse has poles at
`-a/beta` and zeros at `-a`. Both are proper, causal, rational and stable.
The direct term `H(infinity)=rho beta^n R` is nonsingular. The MATLAB
generator returns separate cascade realizations `iqc.H` and `iqc.Hinv`,
whose state matrices are triangular with these analytic pole locations.
For multiple pairs the formula applies blockwise with the corresponding rho.

Stability does not bound the inverse gain by one: the inverse scalar factor
has high-frequency gain `beta^(-n)`, equal to 1024 for beta=0.5 and n=10.
The full inverse also includes `(1/rho)R^{-1}`. This gain is finite and is
relevant when choosing orders for numerical use.

For a library of fixed `(rho,a,n,beta)` choices, an SDP-ready conic family is

```text
Pi_theta(s) = sum_j theta_j Psi_j(s)' M_j Psi_j(s),  theta_j >= 0.
```

Here the prime on transfer functions denotes the frequency-domain adjoint.
To realize the hard factorization, stack all `Psi_j` and use
`M_theta=blkdiag(theta_j M_j)`. The theta variables are linear SDP variables;
rho, pole, order and directRatio are outer-loop library choices. Static incremental
sector constraints may also be appended with nonnegative weights.

For four sigmoid channels use two pairs. The generator accepts a two-entry
rho vector and uses `H=blkdiag(H_1,H_2)` and the corresponding pairwise eta
weights. Channel ordering is plant STN/GPe, then observer STN/GPe.

## Proof of the hard incremental IQC

Define the polyhedral norm

```text
N(x) = max(|x1|, |x2|, |x1+x2|).
```

The following hold for every x and every diagonal `0 <= D <= I`:

```text
N(Rx) = N(x),
N(Dx) <= N(x),
||x||_2/sqrt(2) <= N(x) <= sqrt(2)||x||_2.
```

For the second identity, the first two entries contract immediately. The
third entry is `|d1 x1+d2 x2|`; maximizing this convex function over the
unit square reduces to its four vertices, giving `0`, `|x1|`, `|x2|`,
or `|x1+x2|`. Thus `N(w(t)) <= N(v(t))` pointwise.

For a finite horizon define

```text
||x||_{N,T} = sqrt(integral_0^T N(x(t))^2 dt).
```

Each scalar stage can be written as

```text
(beta s+a)/(s+a) = beta + (1-beta) a/(s+a).
```

The direct term has nonnegative weight beta, and the low-pass impulse
response `a exp(-a t)` is nonnegative with integral one. More explicitly,

```text
h(s) = sum_{j=0}^n binomial(n,j) beta^(n-j) (1-beta)^j (a/(s+a))^j.
```

All coefficients are nonnegative and sum to one. Every term, including
the identity for j=0, has induced finite-horizon N-norm gain at most one.
For j>=1 this follows from Young's convolution inequality and the
nonnegative unit-integral Erlang kernel, on a zero extension of the input
beyond T. Thus the same estimate used in the strictly proper construction
still holds, by the norm triangle inequality and `N(Rx)=N(x)`:

```text
||Hw||_{N,T} <= rho ||w||_{N,T} <= rho ||v||_{N,T}.
```

Let `r0=v-Hw`. On every finite horizon,

```text
(1-rho) ||v||_{N,T} <= ||r0||_{N,T}.
```

The norm-equivalence constants give

```text
||v||_{2,T} <= 2/(1-rho) ||r0||_{2,T}.
```

Also, `||w||_{2,T} <= ||v||_{2,T}` by the componentwise slope bounds.
Combining these estimates gives

```text
||r0||_{2,T}^2 >= (1-rho)^2/8 * (||v||_{2,T}^2+||w||_{2,T}^2),
```

which is exactly the claimed IQC. This proof holds for arbitrary input
pairs on every finite horizon. It does not assume that either input is
an equilibrium or that the observer receives the cortical disturbance.

The sigmoid formula is used to justify the slope bounds. This family is
also valid for other componentwise slope-[0,1] functions: the added power
comes from a coupled dynamic certificate and a nonquadratic norm argument,
not an unproved temporal property of an isolated scalar sigmoid.

## A genuine improvement over the diagonal static sector test

Consider the delay-free continuous-time Lur'e interconnection

```text
v = G(s) w + e,    w = F(v),
G(s) = H(s), rho=0.95, a=1, n=10, beta=0.5.
```

Center `F` at its known value `F(0)` if zero-preserving operators are
required; the constant offset is then included in the exogenous input.
Incremental differences are unaffected.

The dynamic complementary hard inequality holds immediately: on the
linear graph `v=Hw`, the first filter output `v-Hw` is zero. Therefore its
supply is

```text
-eta (||v||_{2,T}^2+||w||_{2,T}^2),  eta=0.0003125.
```

The new G has direct feedthrough, so its algebraic loop must be checked.
The instantaneous map `v -> e + H(infinity) F(v)` has contraction factor
`rho beta^n < 1` in N. This gives a unique instantaneous solution for
every exogenous input and strictly proper filter state; together with
the finite-dimensional Lipschitz dynamics it gives a well-posed causal
interconnection. Theorem 2 in Su and Khong, *An
Input-Output Approach to Incremental Feedback Stability*, then applies.
Its guarantee is incremental input-output stability; arbitrary initial-state
exponential convergence needs additional internal-state analysis.

In contrast, every diagonal static sector multiplier

```text
M_sector = [0 Lambda; Lambda -2 Lambda],
Lambda=diag(lambda1,lambda2)>0,
```

requires `G(jw)' Lambda + Lambda G(jw)-2 Lambda < 0`. Put `h=hr+i hi`
and `r=lambda1/lambda2`. The determinant divided by `4 lambda1 lambda2` is

```text
1-rho hr - rho^2/4 * [hr^2(r+1/r-2)+hi^2(r+1/r+2)]
<= 1-rho hr-rho^2 hi^2,
```

because `r+1/r>=2`. Set

```text
omega=a/8,
h=((beta i omega+a)/(i omega+a))^n.
```

For the parameters above the right-hand side is approximately
`-0.0007426377104`. Hence the determinant cannot be positive, for any positive
diagonal Lambda. This rules out the entire diagonal static sector family,
whereas the dynamic hard IIQC certifies this example analytically.
This example is not the PNAS network. It proves that the construction can
be more useful than the diagonal static test, not that it certifies the
particular fixed controller in the user's workspace or beats every possible
static full-block multiplier.

## MATLAB and application to the fixed STN/GPe loop

```matlab
addpath('Notes/sigmoid_iiqc')
iqc = sigmoid_dynamic_iiqc(0.95,100,10);      % Two sigmoid channels.
iqc4 = sigmoid_dynamic_iiqc([0.9 0.95],100,10); % Plant and observer pairs.
iqc = sigmoid_dynamic_iiqc(0.95,100,10,0.5); % Explicit directRatio=beta.
inverse = iqc.Hinv; % Numeric A,B,C,D realization of stable proper H^{-1}.
report = verify_sigmoid_dynamic_iiqc;
```

The IQC structures contain numeric `A,B,C,D,M` matrices for the filter,
`H` for the auxiliary transfer matrix, `Hinv` for its stable inverse,
and `eta`. Filter inputs are `[v;w]`. The filter's first direct-output
block is `[I,-H.D]`; its direct term must be retained in state-space assembly.
For the augmented fixed plant-observer linear block

```text
Xdot=A_cl X+B_cl w,    v=C_cl X,
```

the filter composition has state `[X;xpsi]` and matrices

```text
Abar = [A_cl,               0;
        Bpsi_v C_cl,        Apsi],
Bbar = [B_cl; Bpsi_w],
Cbar = [Dpsi_v C_cl, Cpsi],
Dbar = Dpsi_w.
```

A sufficient complementary hard inequality follows by finding `P>=0`
and `epsilon>0` such that

```text
[Abar'P+P Abar, P Bbar; Bbar'P,0]
+ [Cbar Dbar]' M [Cbar Dbar]
+ epsilon*[C_cl 0 0; 0 0 I]'*[C_cl 0 0; 0 0 I] < 0.
```

The last matrix maps `[X;xpsi;w]` to `[v;w]`. Use zero filter initial
states. Nonnegative conic combinations can be searched by stacking filter
realizations. P is the storage of the linear block plus filters; it is
distinct from the polyhedral norm used to prove nonlinear-block admissibility.
Filter poles, orders, rho values and directRatio can be swept outside the SDP. The
linear-block test may fail for a particular library or controller; such
failure is not proof of instability.

The reference-free observer/controller implementation is unchanged: these
filters belong to the certificate, not to the controller's measured inputs.

## Numerical checks

`verify_sigmoid_dynamic_iiqc.m` computes finite-prefix supply integrals for
piecewise-constant actual PNAS sigmoid input pairs using exact matrix
exponentials, checks the two polyhedral-norm identities, verifies the
state-space multiplier realization, and computes the static obstruction.
It also checks stability of H and Hinv, their analytic pole locations,
both inverse products across a frequency grid, and feedthrough invertibility.
The analytic proof above establishes hardness; the numerical tests check
the implementation and illustrate it. The verification output is saved
in `verification_results.mat`.

The retained MATLAB run passed all eight two-/four-channel signal cases
(1001 finite-prefix checks per case, including the zero prefix), the
state-space realization identity, norm checks, pole checks, and inverse
checks. For pole=10 and directRatio=0.5, the H and Hinv poles were -10 and
-20. Both inverse products matched the identity to within `8.2e-13` over
the frequency grid, including mixed rho values in the four-channel case.
The diagonal-static obstruction for the biproper example was
`-0.0007426377103535`, and the analytic complementary dynamic strictness
remains `0.0003125`. Supply integrals are exact for the held inputs up to
matrix-exponential floating-point error. See `verification_run.log` and
`verification_results.mat`. These checks supplement the proof; they do
not establish feasibility for an unspecified fixed plant-observer-controller.
