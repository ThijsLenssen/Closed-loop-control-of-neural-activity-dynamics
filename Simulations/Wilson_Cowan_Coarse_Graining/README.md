# Wilson-Cowan temporal memory, coarse graining and transport

Run in MATLAB from this folder:

```matlab
results = plot_wilson_cowan_models;
```

The function plots three independently integrated models on the same axes:

1. Equation (9) of Wilson and Cowan (1972): explicit refractory-history integral and exponentially filtered input.
2. Equation (10): the temporal coarse-grained ODE.
3. The transport-PDE realization of Equation (9), retaining its history integral.

The lower panel shows the numerical difference between Equation (9) and the transport realization. Their continuous models are equivalent with compatible histories; the first-order upwind age discretization introduces a finite-grid difference.

The paper's Figure 3 states `r = 3 ms`, but does not give a complete numerical setup. The remaining defaults are **illustrative**, not a claimed reproduction of the original curves. The input is a step at time zero, with zero activity and input prehistory. The sigmoid is an unshifted logistic, as used before the paper's later baseline-shifting step. All times are in milliseconds. `alpha` is the decay **rate** in the printed exponential `exp(-alpha*(t-s))`; its time constant is `1/alpha`. The coarse-grained gain defaults to `k = 1/alpha` to match the convolution's DC gain.

Change the parameter block in the function or pass overrides:

```matlab
results = plot_wilson_cowan_models(struct('tau', 1.5, 'P0', 0.8));
```

To refine the transport discretization and time step together:

```matlab
fine = plot_wilson_cowan_models(struct('nAge', 600, 'nHistory', 2400), false);
```

The default uses `nAge = 300`, `nHistory = 1200`, so `da = r/nAge`, `dt = r/nHistory`, and the transport CFL number is 0.25. The direct-history model uses trapezoidal moving-window quadrature; the transport model uses conservative upwind finite volumes. Both use Heun time stepping, as does the coarse-grained model. No additional MATLAB toolboxes are required.

Plots and results are saved in `output/` when plotting is enabled. The `.m` function is the deliverable; the PowerPoint is not required to run it.

Source: Wilson and Cowan (1972), *Excitatory and Inhibitory Interactions in Localized Populations of Model Neurons*, Eqs. (9)-(10), pp. 8-10. DOI: [10.1016/S0006-3495(72)86068-5](https://doi.org/10.1016/S0006-3495(72)86068-5). The history transport formulation is derived here from Equation (9); it is not another equation quoted from that paper.
