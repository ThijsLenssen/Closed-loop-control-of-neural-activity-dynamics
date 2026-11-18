# Exogenous cortical input and frozen equilibria

From this folder in MATLAB:

```matlab
results = simulate_cortical_disturbance;
```

This standalone experiment uses the **PNAS manuscript's two-population firing-rate model**, with its diseased-case weights, sigmoids, population time constants, and physical transmission delays. It uses base MATLAB `dde23` and `fzero`; no PIETOOLS or extra toolbox is needed. Stimulation is zero. Striatal activity stays at 2 spikes/s. All times in the code are in **seconds**.

Four prescribed cortical inputs are compared: constant at 27 spikes/s, a smooth ramp from 27 to 42, and 1 Hz and 20 Hz sinusoids with the same amplitude of 5 spikes/s. The ramp and sinusoidal turn-on are smooth. These disturbances are illustrative. The cortex has no dependence on the simulated STN or GPe rates.

At each sample, the code freezes the current cortex value and solves

```text
S* = FS(-wGS G* + wCS Ctx(t))
G* = FG(wSG S* - wGG G* - wXG Str).
```

The dashed curves are these **frozen-input equilibria**. Constant states remove delays from these algebraic equations. The actual firing-rate trajectories still contain all three transmission delays. A changing frozen equilibrium is generally not itself a solution of the time-varying delay system. The plotted difference is therefore a response diagnostic, not a convergence guarantee. Subtracting this moving reference in a stability derivation would introduce reference-derivative and delayed-reference mismatch terms.

The constant-input case provides a baseline for endogenous oscillations. The initial history is the initial frozen equilibrium plus `[0.1; -0.1]` spikes/s, held over the whole delay interval. The default diseased open-loop system is not assumed stable; oscillations away from a frozen equilibrium need not be explained solely by lag behind the cortex.

Each column of the main figure shows cortex, STN rate versus equilibrium, GPe rate versus equilibrium, and both differences. A separate beta zoom resolves the final 250 ms. Figures and a MAT file are saved in `output/`. In each `results.cases(k)`, `rates`, `equilibrium`, and `trackingError` have columns `[STN GPe]`. The solver solution is retained for interpolation with `deval`. RMS differences are time-weighted over the whole experiment, including the initial transient.

Change the input without changing the model:

```matlab
cfg = struct;
cfg.duration = 5;
cfg.cortex = @(t) 27 + 5*sin(2*pi*2*t);
results = simulate_cortical_disturbance(cfg);
```

For sampled cortex, provide a scalar handle using `interp1` with interpolation and explicit endpoint handling. For discontinuous inputs, also set `cfg.jumps` to the jump times so `dde23` can account for their propagated discontinuities. The prehistory still uses the frozen equilibrium at `Ctx(0)` plus the specified perturbation.

For the four built-in inputs with other amplitudes or frequencies:

```matlab
cfg = struct('amplitude', 2, 'slowFrequency', 0.5, 'betaFrequency', 25);
results = simulate_cortical_disturbance(cfg);
```

To calculate without figures or saved files:

```matlab
results = simulate_cortical_disturbance(struct, false);
```

To initialize exactly at the initial equilibrium, set `initialPerturbation` to `[0;0]`. An unstable equilibrium can amplify numerical roundoff, so remaining numerically stationary for a finite time is not evidence of stability. Parameters are copied from `main.tex`, Table 1; neither the manuscript nor the existing controller simulations are modified.

After generating the default results, run `validate_cortical_disturbance` to check equilibrium residuals, firing-rate bounds, a short stationary-equilibrium case, and numerical convergence. The refinement divides both solver tolerances by 100 and halves its maximum step. The acceptance criterion is a maximum trajectory difference below 0.1 percent of each population's refined peak rate. This is a numerical accuracy check, not a stability certificate.

The default run passed these checks: the largest refinement difference was approximately 0.030 spikes/s (0.021 percent of the corresponding peak), all frozen-equilibrium residuals were below 1e-9 spikes/s, and the short stationary test remained at equilibrium. Increasing constant cortex from 27 to 42 spikes/s shifts the frozen equilibrium from approximately `[20.4425, 21.8366]` to `[28.8272, 32.1112]` spikes/s. The actual diseased open-loop trajectories sustain oscillations in both constant-input conditions.
