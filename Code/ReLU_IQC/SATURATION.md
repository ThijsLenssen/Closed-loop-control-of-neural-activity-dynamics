# Generic saturation analysis

Run the editable example with SOSTOOLS and MOSEK on the MATLAB path:

```matlab
addpath('Code/ReLU_IQC')
results = saturation_iqc_example;
```

The example now has two saturation channels with unequal, asymmetric limits,
input biases, and a nonzero operating point. The reusable solver is
`saturation_iqc_analysis.m`; the example file configures the plant and runs
the analysis and simulations.

## Simulations

The example also runs simulations and opens a four-panel figure: unforced
convergence from two initial states, a forced response, the input/output of
each saturation channel, and finite-horizon energy ratios against the IQC bound.
The supplied disturbances have amplitudes 0.1 and 3 and stop smoothly after
12 time units; the simulation continues to 30 to include the output tail.
Forced runs start at xeq, as required for the induced-gain comparison.

```matlab
[results, programs, simulations] = saturation_iqc_example;
simulations.forced{2}.x            % physical states, samples in rows
simulations.forced{2}.u            % clipped feedback signals
simulations.forced{2}.energyRatio  % sqrt(output energy / input energy)
```

Change the time grid, initial states, amplitudes, and input waveform in
`saturation_iqc_simulations.m`. It calls the generic `saturation_simulate.m`,
which simulates the actual clipped dynamics and integrates input/output energy
as additional ODE variables. The ratios are measured for the selected inputs,
not estimates that prove the worst-case induced gain.

To simulate another input without repeating the SDP solves:

```matlab
d = @(t) exp(-t)*ones(size(sys.E,2),1);
data = saturation_simulate(sys,lower,upper,d,sys.xeq,(0:.01:30)');
```

To skip simulations, run `saturation_iqc_example('mosek',false)`.
The generated example figure is saved in `saturation_simulations.png`.
In the tested run, both unforced state-error norms decrease from 2.5 to below
4e-8 by time 30. The weak and strong disturbance energy ratios finish at
1.07479 and 1.00051, respectively, below the IQC bound 2.08246. The large
disturbance reaches the saturation limits. All sampled finite-horizon ratios
were checked against the bound, and MATLAB Code Analyzer found no issues in
the simulation functions.
To save a new figure after your own run:

```matlab
exportgraphics(simulations.figure,'saturation_simulations.png','Resolution',150)
```

## Incremental comparison with slope ordering

```matlab
[results,programs,simulations] = saturation_iqc_example('mosek',true,'incremental');
```

The incremental mode compares the primal and dual LMIs for differences of
two trajectories of the same system. It compares the diagonal sector QC,
the original and sharpened pairwise QCs added to it, and the sharpened case
with saturation ordering. As discussed in the ReLU example, the dual uses
the transpose of the plant and the same family of diagonal slopes.

The ordering comes from the two shifted ReLUs of each actuator. For an
incremental actuator input $p$ and the lower and upper threshold output
increments $q_\ell,q_h$, the three quantities $q_h$, $q_\ell-q_h$ and
$p-q_\ell$ have the same sign. `qc_saturation_order_inc.m` adds their
pairwise products as QCs. It accounts for the reversed sign of the upper
channel on the dual graph. This ordering holds for any fixed limits, so
the numerical limits enter the simulations but are absent from the LMIs.
Equivalently, for $g=[q_h;\,q_\ell-q_h;\,p-q_\ell]$ the ordering is the
polyhedral norm constraint $\|g\|_1\le |p|$. The entries sum to $p$, so
equality in the triangle inequality holds exactly when the nonzero
entries have the same sign. The pairwise products encode this condition
as homogeneous QCs.

Both primal and dual give 2.4892 with the unordered QCs and 2.1501 with
the ordering QC. The paired simulations use actual clipping. The state
gap decays with a shared disturbance. Starting from equal states with
different disturbances gives a final energy ratio of about 1.1041. The
figure shows the secant slopes and both IQC bounds. See
[`saturation_incremental_simulations.png`](saturation_incremental_simulations.png).

## Sigmoids and saturations with the same center

For arbitrary output limits, use `[f,s,theta] = sigmoid_saturation(q,lower,upper,center,slope)`. The output midpoint is `(lower+upper)/2`, and `f = midpoint + theta.*s`. The input center and midpoint slope are optional. By default the comparison curve is ordinary clipping of `q` between the two limits.

Run the paper's STN/GPe example (no SDP solver required):

~~~matlab
[parameters,fig] = sigmoid_relu_uncertainty_example; % disease level Kd=1
exportgraphics(fig,'sigmoid_relu_uncertainty.png','Resolution',150)
~~~

The logistic sigmoid is

$$F(q)=h+h\tanh((q-c)/h),\qquad h=M/2,\qquad
c=\frac{M}{4}\log\frac{M-B}{B}.$$

Align the saturation midpoint with the sigmoid midpoint (c,h):

$$S(q)=h+s(q),\qquad s(q)=\operatorname{sat}_{[-h,h]}(q-c)
=-h+\operatorname{ReLU}(q-c+h)-\operatorname{ReLU}(q-c-h).$$

Both F and S pass through (c,h), have slope one there, and approach
output levels 0 and M. With r=(q-c)/h, the exact representation is

$$F(q)=h+\theta(q)s(q),\qquad
\theta(q)=\frac{\tanh r}{\operatorname{sat}_{[-1,1]}(r)},\qquad
\theta(c)=1.$$

Globally, tanh(1)<=theta(q)<=1. These bounds are tight: the lower bound
is attained at r=+/-1, and the upper bound at r=0 and asymptotically.
For 0<|r|<=1, tanh(|r|)/|r| decreases from 1 to tanh(1); for |r|>=1,
tanh(|r|) increases from tanh(1) to 1.

Equivalently, F lies between the two saturation curves h+s(q) and
h+tanh(1)*s(q). Their order reverses at q=c. The gain multiplies the
centered saturation output s, with h added afterward.

| Channel | Input center c | Output center h | Global gain interval |
| --- | ---: | ---: | --- |
| STN | 210.92 | 150 | [0.76159416, 1] |
| GPe | 146.63 | 200 | [0.76159416, 1] |

For time-dependent inputs, set theta(t)=theta(q(t)). Allowing arbitrary
measurable theta(t) in this interval enlarges the class to include other
nonlinearities. For y=F(q)-h, its ordinary QC is
(y-tanh(1)*s)*(s-y)>=0. No incremental QC is needed for this representation.

The sigmoid midpoint generally differs from the closed-loop equilibrium.
For a supplied equilibrium input q0 and input deviation v, retain the offsets:

$$\delta(v)=F(q_0+v)-F(q_0)
=\theta(q_0+v)s(q_0+v)-\theta(q_0)s(q_0).$$

This is generally not theta(q0+v)*(s(q0+v)-s(q0)). If the gain is relaxed
to arbitrary time variation, a noncentral equilibrium is not automatically
preserved: at v=0 the output deviation can be (theta(t)-theta(q0))*s(q0).
A stability or L2 analysis about that equilibrium must account for this
additional freedom or impose an appropriate equilibrium-preserving constraint.
The plotting example checks the exact representation, including equilibrium
subtraction; it does not add this uncertainty block to saturation_iqc_analysis.

The figure shows the aligned curves and their envelope, the exact gain,
and its time history along an illustrative input. Reconstruction agrees
within 2e-13 for both channels, and MATLAB Code Analyzer reports no issues.
The parameters and figure are in sigmoid_uncertainty_parameters.csv and
sigmoid_relu_uncertainty.png.

## Compare gain outside and inside saturation

```matlab
[results,fig] = sigmoid_gain_placement_comparison;
```

This solver-free plot uses normalized coordinates r=(q-c)/h and
y=(F-h)/h, so it applies to both STN and GPe. It compares the exact
identities y=theta(r)*sat(r) and y=sat(kappa(r)*r), where
theta=tanh(r)/sat(r), kappa=tanh(r)/r, and both gains equal one at r=0.
The shared saturation has limits [-1,1] and uses two ReLUs.

The shaded regions allow arbitrary gains in their global intervals:
theta in [tanh(1),1] and kappa in [0,1]. Both reproduce the sigmoid
exactly with their specified input-dependent gains. The inside-gain
envelope is larger when the dependence on input is discarded, including
zero normalized output at every input. The final panel compares the
exact gains; kappa tends to zero at large input magnitudes, while theta
tends to one. The exported plot is sigmoid_gain_placement_comparison.png.

## Analyze your own system

The model is

$$\dot x=Ax+Bu+Ed+f,\qquad
v=Cx+Dd+b,\qquad u=\operatorname{sat}_{[\ell,h]}(v).$$

Here saturation means componentwise clipping:
$\operatorname{sat}_{[\ell,h]}(v)=\min(\max(v,\ell),h)$.
In the notation sat_[a,b], a is lower and b is upper. They need not be
symmetric or straddle zero. Each channel can have different limits.

```matlab
sys.A = [-1 .4; -.2 -1.2];
sys.B = .5*[1; .4];
sys.C = [1 -.5];
sys.E = [1; .5];
lower = -1;
upper = .7;

options.center = false;                 % raw ReLU outputs (default)
options.cases = {'M12','matrix'; 'Mc','matrix'};
[results, programs] = saturation_iqc_analysis(sys,lower,upper,options);
programs{1}.solinfo                     % raw SOSTOOLS results
```

Required fields are A, B, C, and E. B has one column and C one row per
saturation channel. Limits are finite scalars (shared by all channels) or
column vectors with one entry per channel.

| Optional sys field | Default | Meaning |
| --- | --- | --- |
| D | zero | disturbance feedthrough into v; no u-to-v algebraic loop |
| b | zero | bias in v |
| f | zero | constant drive in the state equation |
| xeq | zero | supplied equilibrium at d=0 |
| Cz | identity | state part of the performance output |
| Dz | zero | saturation-output part of the performance output |
| Ez | zero | disturbance feedthrough into the performance output |

The performance output is defined relative to the operating point:

$$z=C_z(x-x_{\rm eq})+D_z(u-u_{\rm eq})+E_zd,\qquad
u_{\rm eq}=\operatorname{sat}_{[\ell,h]}(Cx_{\rm eq}+b).$$

Supply an equilibrium satisfying $Ax_{\rm eq}+Bu_{\rm eq}+f=0$.
The code checks this equation to numerical tolerance; it does not find an
equilibrium or silently alter the plant. The example deliberately chooses f
to make its specified operating point an equilibrium.

Options are solver (default 'mosek'), center (default false), epsilon
(default 1e-5), and cases. Cases select M1, M2, M3, M12, or Mc and, when
applicable, matrix, sos0, or sos1. All eleven comparisons run by default.
M1 and M3 use 'none'. The full Mc construction has exponentially many sign
patterns, so select a smaller comparison list for larger models.

## Exact ReLU representation and optional centering

For arbitrary finite limits $\ell<h$,

$$\operatorname{sat}_{[\ell,h]}(v)
=\ell+\operatorname{ReLU}(v-\ell)-\operatorname{ReLU}(v-h).$$

`saturation_relu(v,lower,upper)` evaluates this identity.
The original calls saturation_relu(v) and saturation_relu(v,h) still mean
limits [-1,1] and [-h,h], respectively. For vector limits, use column vectors
and put channels in rows of v.

Define $a=[v-\ell;v-h]$, $w=\operatorname{ReLU}(a)$ and $J=[I\ -I]$.
Then $u=\ell+Jw$. The auxiliary coordinate is r=w-shift:

- center=false: shift=0, so r is the raw ReLU output.
- center=true: shift=w0, its value at the supplied equilibrium.

Both retain all constant offsets and apply the ordinary QC to raw ReLU inputs
and outputs. No incremental QC is used. Physical state deviations
e=x-xeq define the storage in either mode.

The QC also includes the known ReLU pair (1,1). The paper's homogeneous
quadratic constraints admit both ReLU and flipped ReLU. Appending ReLU(1)=1
excludes the flipped orientation, which could otherwise prevent a valid
equilibrium analysis with asymmetric limits or biases. This adds no unknown
auxiliary output. With p saturation channels the QC has m=2*p+1 ReLU channels.

## Dissipation inequality

The storage is $V=e^TPe$ with $P\succ0$. Using $\xi=[e;r;d;1]$, the program
requires

$$\dot V+z^Tz-\rho d^Td+q_{\rm ReLU}
\le-\epsilon(\|e\|^2+\|d\|^2),\qquad \rho=\gamma^2.$$

The constant coordinate is not a state or an L2 input. There is no strict
margin on it or on the auxiliary coordinates. The ordinary QC is pointwise
nonnegative, so finite-horizon integration gives the gain bound without
assuming the constant signal belongs to L2 on an infinite horizon.

In the selected coordinates the equilibrium vector is
$\xi_{\rm eq}=[0;w_0-\mathrm{shift};0;1]$.
The code imposes $L\xi_{\rm eq}=0$, then a negative semidefinite constraint on
the principal block excluding the constant coordinate. Together these are
equivalent to the full affine matrix inequality, since $\xi_{\rm eq}$ has
last entry one. This works in both coordinate choices; it does not incorrectly
set the last column to zero in raw coordinates.

Feasibility implies global exponential stability about xeq when d=0, and
$\|z\|_{L_2}\le\gamma\|d\|_{L_2}$ when x(0)=xeq. A different initial state
adds $(x(0)-x_{\rm eq})^TP(x(0)-x_{\rm eq})$ to the energy bound. For nonzero
equilibrium outputs the bound concerns the output deviation defined above.

## Raw results

The table reports Gamma, pinf, dinf, numerr, and elapsed time.
NaN indicates no gain was extracted after infeasibility or a missing solution;
inspect the raw solver diagnostics. An infeasible QC test does not establish
instability.

The current two-channel example, tested in MATLAB R2023a/SOSTOOLS 4/MOSEK 11,
gives the following results (full precision in saturation_results.csv):

| QC | COP method | Gamma |
| --- | --- | ---: |
| M1 | none | infeasible |
| M2 | matrix / sos0 / sos1 | infeasible |
| M3 | none | infeasible |
| M1+M2 | matrix / sos0 / sos1 | 2.0825 |
| Mc | matrix / sos0 / sos1 | 2.0825 |

The reference pair makes m=5 here: M2 uses COP matrices of order 10 and Mc
uses 32 COP matrices of order 5. These matrix and finite SOS constructions
are inner approximations, not exact COP constraints in general. Agreement
of these bounds on this example does not mean the multiplier cones are equal.

Validation also covered a separate biased two-channel model with a nonzero
equilibrium, two disturbance inputs, and state/control/disturbance performance
terms. Raw and centered coordinates agreed within 1e-5 relative tolerance for
M12 and Mc. Clipping identities, including the kinks and the original symmetric
calling convention, passed; an incorrect equilibrium was rejected. MATLAB
Code Analyzer reported no issues in the saturation functions.

The underlying ordinary ReLU QC definitions are from
[Noori et al.](https://arxiv.org/abs/2407.06888). The affine lift and operating-point
handling are part of this example; see also the workspace's
[saturation note](../../Notes/saturation_iqc/saturation_iqc.tex).
