# ReLU IQCs: stability and L2 performance

From the repository root, run:

```matlab
addpath('Code/ReLU_IQC')
results = relu_iqc_example;
```

For a separate system with general componentwise saturation limits, run
`results = saturation_iqc_example;`. See [the saturation example notes](SATURATION.md)
for the reusable `saturation_iqc_analysis(sys,lower,upper,options)` interface,
its exact ReLU lift, and optional centering of the auxiliary outputs.

Requires SOSTOOLS 4 (included with PIETOOLS) and MOSEK on the MATLAB path.
These are already available in the local MATLAB setup. For another installation,
add the toolbox and solver folders to the MATLAB path first. To use SeDuMi:

```matlab
[results, programs] = relu_iqc_example('sedumi');
programs{1}.solinfo                  % complete raw SOSTOOLS solver output
```

The example prints the solver output and returns a table containing `Gamma`,
`pinf`, `dinf`, `numerr`, and elapsed seconds (construction plus solution).
`NaN` means no gain was extracted because the solver reported infeasibility or
returned no solution. A failed QC test does not establish instability. Inspect
the raw diagnostics, especially `numerr`, when interpreting a returned gain.

## Files and switches

| File | Purpose |
| --- | --- |
| `relu_iqc_example.m` | System matrices, comparison list, dissipation LMI, solve |
| `qc_M1.m` | Free diagonal complementarity multiplier, Eq. (3) |
| `qc_M2.m` | Copositive positivity multiplier, Eq. (4) |
| `qc_M3.m` | Doubly hyperdominant slope multiplier, Eq. (6) |
| `qc_Mc.m` | Free symmetric multiplier with one COP constraint per sign pattern, Theorem 1 |
| `qc_M12_dual.m` | Convex dual step with recovered primal multiplier in M1+M2 |
| `qc_Mc_dual.m` | Earlier fixed-factor construction for comparison |
| `relu_iqc_dual_example.m` | Dual analysis LMI for the same homogeneous ReLU system |
| `relu_dual_results.csv` | Raw dual results and numerical residual checks |
| `cop_matrix.m` | COP approximation: PSD matrix plus entrywise nonnegative matrix |
| `cop_sos.m` | COP approximation using an SOS polynomial |
| `results.csv` | Raw comparison from the tested MATLAB/MOSEK run |

Edit `A`, `B`, `C`, and `E` at the top of the example to change the system.
Edit `cases` to select `M1`, `M2`, `M3`, `M12` (the sum M1+M2), or `Mc`.
M1 and M3 have no COP constraint. For M2, M12, and Mc choose `matrix`, `sos0`, or
`sos1`. The QC functions can also be called and added directly:

```matlab
[prog,M1] = qc_M1(prog,m);
[prog,M2] = qc_M2(prog,m,'sos1',y);
M = M1+M2;
```

To use the complete ReLU family instead:

```matlab
[prog,M] = qc_Mc(prog,m,'matrix',y);
```

Mc uses a free symmetric matrix M and, for each of the `2^m` diagonal
sign matrices D, imposes copositivity of

$$Q_D=R_D^TMR_D,\qquad R_D=\begin{bmatrix}D\\(I+D)/2\end{bmatrix}.$$

Each sign pattern gets its own COP constraint. The selected method replaces
COP with the corresponding matrix or SOS inner approximation; in general this
implements a relaxation of the complete cone. It does not restrict M to the
M1+M2 structure. The cone helpers accept an optional existing matrix expression,
which is how Mc constrains each Q_D.

## What is being verified?

The system is continuous time:

$$\dot x=Ax+B\operatorname{ReLU}(Cx)+Ed,\qquad z=x.$$

There are two states, three repeated ReLUs, and one disturbance. With
$V=x^TPx$, the optimization minimizes $\rho=\gamma^2$ subject to $P\succ0$ and

$$\dot V+z^Tz-\rho d^Td+[v;w]^TM[v;w]<0.$$

Each QC is pointwise nonnegative on the ReLU graph, hence also a hard IQC.
A feasible strict LMI implies global exponential stability when $d=0$, and
$\|z\|_{L_2}\le\gamma\|d\|_{L_2}$ when $x(0)=0$. For nonzero initial conditions,
the energy bound includes $x(0)^TPx(0)$.

The multiplier definitions follow Eqs. (3), (4), and (6), and Theorem 1 of
[Noori et al., *A Complete Set of Quadratic Constraints for Repeated ReLU and
Generalizations*](https://arxiv.org/abs/2407.06888).
The paper uses discrete-time dynamics; this example uses the continuous-time
dissipation inequality above to give an L2 result.

## Incremental analysis on both sides

```matlab
[results, programs, simulations] = relu_iqc_example('mosek','incremental');
programs{1}.solinfo
```

Use `incremental-primal` or `incremental-dual` to run only one side. The
incremental mode compares `M1inc`, `M2inc`, `M12inc` (their sum), and `Mcinc`.
Each has a separate QC function, with `M12inc` formed by adding the first
two. `M2inc4` and `M12inc4` use the sharper pairwise inequality
$(\delta v_i-\delta v_j)^2+4\delta w_i\delta w_j\ge0$. The original
paper uses 2. `Mcinc` runs with the matrix and both SOS COP approximations.

For two trajectories, the difference state $e=x-\hat x$ and external input
difference $d-\hat d$ drive the same plant matrices. The ReLU difference is
$\delta w=\Lambda(t)\delta v$, where $\Lambda$ is diagonal with entries in
$[0,1]$. The primal LMI certifies a common bound for this family. The dual
mode transposes the plant and interchanges its input/output roles, including
the performance channels. The transpose of $\Lambda$ equals $\Lambda$,
and time reversal keeps it in the same family. The finite-horizon dual
bound therefore transfers to the original difference system. Both sides
search directly over the same incremental QC weights in a single SDP for
each case. The dual route here concerns diagonal slope blocks and is distinct
from the plant-side multiplier inversion in `relu_iqc_dual_example.m`.

For `Mcinc`, write $(\delta v,\delta w)=(D(a+b),Db)$ with $a,b\ge0$ and
$D$ diagonal with entries $\pm1$. Every such pair can be realized by taking
scalar ReLU inputs on opposite sides of zero in each channel. Conversely,
the unit slope bound puts every incremental ReLU pair in this form. Thus,
before the COP approximation, it is enough to impose $R_D^TMR_D\in
\mathrm{COP}^{2m}$ with $R_D=\begin{bmatrix}D&D\\0&D\end{bmatrix}$. The
test for $-D$ is identical, so the code uses $2^{m-1}$ tests. This is a
condensed form of the exact cone in Theorem 3 of Noori et al.

On the benchmark, both sides give approximately 2.9314 for `M1inc`,
`M12inc`, `M12inc4`, and all three `Mcinc` cases. `M2inc` and `M2inc4` alone
are infeasible on both sides. The diagonal slope family contains the constant all-active mode,
whose DC gain is about 2.9313, so the tested bounds are already close to a
lower bound for this uncertainty family.

By default these modes simulate two actual ReLU trajectories. The figure
shows convergence under a shared disturbance from different initial states,
then a finite-horizon energy ratio from equal initial states with different
disturbances. The measured ratio at the final time is about 1.9994. Pass
`false` as the third argument for a solver-only run. See
[`relu_incremental_simulations.png`](relu_incremental_simulations.png).

## Matrix versus SOS

`matrix` imposes $Q=S+N$, $S\succeq0$, and $N\ge0$ **entrywise**.
`sos0` and `sos1` instead impose

$$\left(\sum_i y_i^2\right)^r (y\circ y)^TQ(y\circ y)\ \text{is SOS},$$

with $r=0$ and $r=1$. The squared-variable substitution is essential:
requiring $y^TQy$ to be SOS would impose PSD, rather than this COP relaxation.
The quartic level `sos0` is equivalent to `matrix`. The sextic level `sos1`
allows a larger cone but need not improve the gain on every system. See
[Parrilo's SOS copositivity construction](https://web.mit.edu/~a_a_a/Public/Publications/refs_for_seb_blog/Parrilo_MathProg.pdf).
For M2/M12, Q is 6-by-6; these are inner approximations, not exact COP
constraints. For Mc, there are eight 3-by-3 matrices Q_D. Since PSD plus
entrywise nonnegative is exact for COP matrices of order at most four,
the Mc matrix formulation is exact for the multiplier cone in this example.
Consequently, SOS0 and SOS1 cannot improve that cone here. This does not make
the quadratic-storage stability/performance condition necessary and sufficient.

Tested with MATLAB R2023a, SOSTOOLS 4, and MOSEK 11:

| QC | COP method | Gamma |
| --- | --- | ---: |
| M1 | none | 2.9314 |
| M2 | matrix / sos0 / sos1 | infeasible |
| M3 | none | 2.9314 |
| M1+M2 | matrix | 2.0296 |
| M1+M2 | sos0 | 2.0296 |
| M1+M2 | sos1 | 2.0296 |
| Mc | matrix | 2.0296 |
| Mc | sos0 | 2.0296 |
| Mc | sos1 | 2.0296 |

M2 alone only uses positivity of `[w-v;w]` and allows `v=0,w>0`, so it
cannot satisfy this strict dissipation LMI. Combining it with complementarity
(M1) gives the useful comparison. In this example the next SOS level does not
improve the bound. All three successful M1+M2 runs agree to solver accuracy.
Mc also gives the same bound for this particular system; the multiplier
families are not generally equal.

## Dual analysis with primal M1+M2

~~~matlab
[results,programs,multipliers] = relu_iqc_dual_example;
programs{1}.solinfo              % raw output for the accepted solve
multipliers{1}                   % recovered primal M in M1+M2
~~~

Theorem 2 in Lenssen et al., *Dual Integral Quadratic Constraint
Representations for Robust Control of Partial Integral Equations*, applies to
LTI uncertainties. ReLU can be written as w=D(v)v with the diagonal activation
mask D(v)=diag(1_{v_i>0}). A frozen mask is LTI with dual D'=D. A whole
ReLU trajectory instead selects its own masks, so there is no direct
application of Theorem 2 to this sign-dependent map. An arbitrary switching
family of masks covers the ReLU trajectories but drops the sign conditions
w>=0 and w-v>=0 that the M2 QC uses.

The example uses the plant-side route R.2 and the ODE specialization of
Eq. (12). Write K=M^{-1}, where M is the primal multiplier. The total
static dual multiplier is

$$J=\begin{bmatrix}0&I\\-I&0\end{bmatrix},\qquad
\underline V=-J^TKJ.$$

The helper qc_M12_dual uses a free symmetric K and the existing qc_M1 and
qc_M2 functions to build M12. It constrains K^{-1}>=M12 through a convex
sufficient condition. In particular, in the coordinates T*[v;w]=[w-v;w],
T is invertible. For any PSD G, T^{-T}*G*T^{-1} is PSD and is allowed by
each COP approximation. Therefore adding G to M12 preserves M1+M2
membership, including under the selected COP approximation.

At each solve, fix a symmetric primal expansion matrix M0 and a matrix S
spanning a negative subspace of K0=M0^{-1}. The code uses
S=[-K0_11^{-1}*K0_12;I]. Impose K11>=epsilon*I and W=-S'*K*S>=epsilon*I.
The two subspaces give K inertia (m,m), and K11>0 implies M22<0 by block
inversion. In the basis with columns [I;0] and S, eliminating the negative
block gives K^{-1}>=-S*W^{-1}*S'. Thus, with F=(I-M0*K)*S,

$$\begin{aligned}
K^{-1}
&=2M_0-M_0 K M_0+(I-M_0K)K^{-1}(I-KM_0)\\
&\succeq 2M_0-M_0 K M_0-FW^{-1}F^T .
\end{aligned}$$

Enforce the affine Schur complement constraint

$$\begin{bmatrix}2M_0-M_0KM_0-M_{12}&F\\F^T&W\end{bmatrix}\succeq0.$$

This yields M>=M12 and hence M in the chosen M1+M2 family. The lower bound
is exact at K0. The helper uses no fixed IQC factor. For the paper's hard
factorization, block elimination gives a lower triangular factor with
identity diagonal blocks, weight blocks given by the positive Schur complement of M22
and M22<0, and an invertible Theta22. ReLU's pointwise QC gives hardness.
The strictly proper example plant has invertible input-coordinate feedthrough
and a well-posed inverse realization. The feedback ODE is globally Lipschitz.

For the dual realization Ad=A', Bd=[C' I], Hdelta selects the dual
uncertainty output and input and Hp selects the dual performance output
and input. Each convex problem maximizes eta=1/gamma^2 with P>0 and

$$\begin{bmatrix}A_d^TP+PA_d&PB_d\\B_d^TP&0\end{bmatrix}
+H_\Delta^T\underline V H_\Delta
+H_p^T\operatorname{diag}(\eta I,-I)H_p\preceq-\epsilon I.$$

The example starts from the complementarity QC with Q1=I and updates M0 to
the recovered primal matrix after each accepted solve. Each solve is convex.
The sequence is a local search through sufficient conditions for the
inverse constraint, with no claim of a global optimum. Use
relu_iqc_dual_example('mosek',{'matrix'},6) to select a method and the maximum
number of solves. The returned programs are the accepted solves.

| COP | Dual gamma after six steps |
| --- | ---: |
| matrix | 2.0572 |
| sos0 | 2.0561 |
| sos1 | 2.0545 |

All runs have pinf=dinf=numerr=0, M-M12 positive definite at the recovered
solutions, and strict negative dual LMI and M22 eigenvalues. Matrix and sos0
model the same COP approximation, but different intermediate solutions
can lead to different expansion points. The direct primal M1+M2 LMI gives
2.0296 on the same benchmark. This example uses homogeneous ReLU. Applying
the dual theorem to the affine saturation lift would require separate
justification of its constant coordinate and anchor.

### Exact inverse constraint on the dual side

The full inverse image of the matrix version of M1+M2 is nonconvex even
with strictly positive-negative primal multipliers. The following example
uses two ReLU channels and the same matrix convention as qc_M2.

```matlab
I = eye(2); O = zeros(2);
T = [-I I; O I];
M1 = [O I; I -2*I];
Q2a = eye(4)/16; Q2a(1,4) = 1/4; Q2a(4,1) = 1/4;
Q2b = eye(4)/16; Q2b(3,4) = 1;   Q2b(4,3) = 1;
Ma = M1 + T.'*Q2a*T;
Mb = M1 + T.'*Q2b*T;
Kmid = (Ma\eye(4) + Mb\eye(4))/2;
g = [0;1;0;1];                 % [v;ReLU(v)] with v=[0;1]
g.'*(Kmid\g)                   % -47751/1031120
```

Both Q2 matrices are entrywise nonnegative. Both primal multipliers have
positive definite upper-left blocks and negative definite lower-right
blocks. At the midpoint of their inverse matrices, the recovered primal
quadratic form is negative on the ReLU graph. The map K to the total dual
multiplier -J'*K*J is linear and invertible, so its image is nonconvex too.
An affine LMI with auxiliary variables has a convex projection onto K and
cannot describe this entire set exactly.

A direct, exact optimization model keeps the plant-side dual LMI and uses
the constraints below. M is an algebraic auxiliary variable in this model.

$$M=M_1+T^T(S+N)T,\qquad S\succeq0,\quad N\ge0\ \text{entrywise},
\qquad KM=I,\qquad K_{11}\succ0,\quad M_{22}\prec0.$$

The inverse equality is bilinear. The block conditions give the balanced
inertia and static factorization used above. For the strictly proper
benchmark plant this gives the exact direct dual model for the chosen
matrix COP approximation and negative lower-right block condition. For
fixed gain, positive semidefiniteness can also be expressed by principal
minors, giving a polynomial feasibility problem. Global semialgebraic
methods can address it in principle. Numerical spatial branch and bound
requires justified variable bounds to certify a result for the whole set.
The MATLAB example above implements the local convex steps, so its reported
results do not verify a global solution of this model.
