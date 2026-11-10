# Optical measurement: PDE and exponential convolution

Run in MATLAB from this folder:

```matlab
results = simulate_photon_measurement;
```

The first figure puts the PDE fluorescence output and the exponential convolution side by side, with an overlay in the third column. It shows two inputs: a finite-width unit-area pulse and an illustrative population firing rate. The paper's single-spike exponential is included as a separate reference for the pulse example. A finite-width pulse approximates that reference; it does not reproduce the instantaneous onset exactly.

The second figure shows the inputs and the PDE's distributed state. The third separates the Heaviside step function from the paper's full exponential response, then compares that response with the PDE, including an onset zoom. Figures (`.png`, `.fig`) and numerical results (`.mat`) are saved in `output/`.

Generated plots: [fluorescence comparison](output/fluorescence_comparison.png), [rate inputs and PDE states](output/rate_inputs_and_pde_states.png), and [step function, exponential and PDE](output/theta_exponential_and_pde.png).

In the third figure, time is measured relative to the pulse onset. The standalone step is dimensionless and gates the paper's single-spike fluorescence response; it is not the rate input to the PDE. The simulated PDE uses a finite-width pulse with unit area. Its fluorescence therefore rises over the pulse duration, while the ideal single-spike reference jumps at onset. The shaded interval marks that finite pulse. All response panels subtract `F0` so the activation is visible.

The model uses the fixed domain `a in [0,L]`:

```text
z_t + z_a = -z/tau
z(t,0) = r(t) + z(t,L)
z(0,a) = 0
S(t) = F0 + A * integral_0^L z(t,a) da
```

The convolution reference integrates the same piecewise-constant rate input against the exponential kernel. The PDE uses a conservative upwind finite-volume method and a time step that preserves positivity. Their finite-step discrepancy should decrease under refinement; a small nonzero numerical error is expected.

Verified in MATLAB R2025b using the default parameters: maximum PDE/convolution differences were 0.08065 photons/s (0.0410% of the peak fluorescence increment) for the finite pulse and 0.09093 photons/s (0.0143%) for the population input. Halving the time step and refining the spatial grid reduced each maximum error by a factor of approximately two. The unit pulse integrates to one spike; the convolution also passed independent analytic checks for a rectangular pulse and a constant rate.

Edit the parameters and `populationRate` near the top of the function. To use your neural model, substitute its firing-rate output for this illustrative input. `tau = 0.15 s` is an example considered by Wilt, Fitzgerald and Schnitzer (2013), *Photon Shot Noise Limits on Optical Detection of Neuronal Spikes and Estimation of Spike Timing*, Eq. (1), DOI: [10.1016/j.bpj.2012.07.058](https://doi.org/10.1016/j.bpj.2012.07.058). The population-rate extension and recirculating PDE are derived here. Other parameter values are illustrative and are not experimental estimates.

These are mean-fluorescence simulations; photon-counting noise is not added. All simulated rate inputs are ordinary locally square-integrable functions. No Dirac input is simulated. MATLAB is sufficient; no extra toolbox is needed.
