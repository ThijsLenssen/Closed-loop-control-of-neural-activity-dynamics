**Assessment of fitted tremor and Parkinson's models for delayed population-model control**

Completed 12 November 2026. Scope: all 17 PDFs now recursively present in References/tremor and parkinsons, including the pathologic behaviour and testbed subfolders. The initial inventory contained 13 PDFs across that folder and References/parkinsons; the reassessment chapter has since moved into the tremor folder and four additional PDFs are now included. The project is currently at C:/Users/thijs/Desktop/Closed-loop control of time-delayed neural activity dynamics; the earlier IDE path under Graduation_Project_TML/Documentation no longer exists.

This is a literature assessment and proposed research protocol. No patient data were fitted and no controller-performance results were generated in this review. S01–S13 refer to the supplied PDFs, indexed at the end. Page references below are PDF page numbers unless journal pagination is explicitly stated.

**1. Main finding and recommended starting point**

The most defensible first identification problem is essential tremor: reproduce the two-state stochastic Wilson–Cowan (WC) fits of Duchet et al. (2020, S08), using the measured stimulation–tremor recordings of Cagnan et al. (2017, S13). Duchet et al. (2021, S05) then supplies a model-based control benchmark. The output is a measured manifestation of the disorder, not merely a neural biomarker.

For Parkinson's disease (PD), Mirkhani et al. (2025, S11) provides a useful independent identification dataset from parkinsonian rats, explicit oscillator fits, and stimulation-response validation. It does not establish clinical symptom relief or provide healthy-control recordings in that analysis. Fleming et al. (2020, S12) is the strongest tractable delayed population model for synthesis among these PDFs, but its parameter identification uses simulated conductance-network data rather than individual human recordings. Steffen et al. (2024, S02) is a useful alternative low-order input–output benchmark with an observer and MPC; its stimulation-response component is based on averaged patient data from an unpublished reference.

The updated folder also includes Davidson et al. (2016, S15), which is an important low-order human stimulation-response fit: second- and fourth-order nonlinear models reproduce beta power versus stimulation amplitude in four patients (reported R² 0.69–0.99). It is a stronger human input–output calibration example than S12, but does not validate complete transient responses or a healthy-control comparison. Its finding that second order suffices is evidence against adding memory without an independent prediction benefit.

There is no single paper in these folders that provides all of: a small physiological E/I model, strong individual-patient stimulation-response prediction, healthy-control validation, and a demonstrated clinical controller.

**Central distinction:** an exact transport-PDE realization of an existing delay/history model has the same input–output behaviour and attainable fit as that model. A fit can improve by retaining memory omitted from a coarse model or adding justified dynamics, not by changing the mathematical realization alone.

**2. Evidence assessment of every supplied paper**

Fit quality, clinical relevance, and usefulness for control are separate questions. A high classification AUC is not waveform-prediction accuracy, a spectral R² is not an input–output validation score, and suppression of a recorded rhythm is not by itself proof of symptom relief.

| Source | Model and fit evidence | Evidence that the output is pathological | Assessment for this project |
|---|---|---|---|
| S08, Duchet et al., 2020 | Two-state stochastic WC; fits tremor PSD, envelope PDF, envelope PSD, and block phase-response curve (bPRC). Combined feature R² = 0.795, 0.823, 0.830 for patients 1, 5, 6. The amplitude-response curve (bARC) is predicted although not included in the cost. | Fits actual essential-tremor acceleration during phase-locked DBS; S13 demonstrates symptom reduction with related recordings. | Best first fit. Selected phase-responsive cases, ten fitted parameters, no whole-study independent replication cohort. |
| S05, Duchet et al., 2021 | Reuses S08's three patient models; evaluates phase-space/isostable stimulation in simulations. Not a new identification study. | Inherits the symptom connection from S08/S13; modeled tremor power is the performance output. | Strong control baseline, not independent evidence that the fit generalizes. Full-state knowledge in simulations requires an observer in an implementable comparison. |
| S13, Cagnan et al., 2017 | Clinical phase-response and tremor-dynamics analysis; not a fitted WC population model. | Direct human tremor suppression, up to 87% in selected essential-tremor patients, at less than half conventional stimulation energy. Responses vary; dystonic tremor and independent oscillators complicate interpretation. | Strongest direct clinical justification for the tremor objective; provides the experimental basis of several later papers. |
| S10, Weerasinghe et al., 2019 | Reduced coupled-oscillator theory predicts phase/amplitude dependence. Strong support for the combined predictions is limited to one patient. | Uses actual essential-tremor stimulation recordings. | Useful alternative mechanism and phase-control benchmark. Do not count it as broad patient-specific predictive validation. |
| S04, Weerasinghe et al., 2021 | Multi-population Kuramoto model. A Lorentzian fit to one patient-5 block's PSD has R² = 0.95; noisy network PSD fits reported as 0.90 and 0.89. | Symptom interpretation inherited from essential-tremor data and the synchrony hypothesis; multi-contact efficacy assessed in simulations. | Useful multi-input benchmark. A good one-block spectrum does not validate the electrode geometry or multi-contact stimulation responses. Optimality is greedy/per-step, not global over time. |
| S11, Mirkhani et al., 2025 | Noisy finite Kuramoto networks fitted to signal PSD, envelope PDF and envelope PSD in parkinsonian rat ECoG. Four parameters are optimized. ARC–PRC-derivative relation supported in 12/13 animals; correlations exceed 0.8 in phase-responsive animals. | Recorded beta activity in a PD animal model, modulated by phase-locked pallidal stimulation. No clinical symptom-benefit endpoint in this paper. | Strong secondary dataset and explicit stimulation-response mechanism test. Parameters are not individually recoverable reliably; amplitude variability remains under-reproduced. |
| S12, Fleming et al., 2020 | Two-population delayed firing-rate model plus a detailed conductance-based network/field/LFP model. Reduced-model identification is against simulated network responses. | Disease-related beta is supported through clinical literature and simulated pathological regimes. | Best delayed synthesis baseline. Simulated cross-model validation is valuable, but is not a human fitted-model validation. |
| S02, Steffen et al., 2024 | Two-state stimulation-response model plus an order-5 model of log-envelope increments; parameters for nominal beta identified from 5 s of one patient's recordings. Controller simulations also use 220 s of recorded baseline activity. | Targets beta above a baseline/threshold, motivated by PD motor literature. | Good low-order observer/MPC benchmark. Patient-data replay plus simulated attenuation is not observed patient response under the proposed controller. Stimulation response is not identified separately for that individual. |
| S03, Lainscsek et al., 2013 | Scalar polynomial DDE feature models with up to two delays and two or three terms. Nine PD patients and nine controls. Controls vs PD-OFF AUC 0.81–0.94 on the second trial set. | Healthy-control separation and model-feature association with motor severity (R = 0.68, p < 0.005). | Useful pathology-sensitive features. No identified stimulation channel; AUC does not validate a plant suitable for controller synthesis. |
| S09, Holt et al., 2019 | Human physiological study of phase-dependent beta modulation; no fitted E/I plant. Ten patients recorded, eight analysed. | Beta amplitude and rhythmic neuronal output can be changed without an overall firing-rate change. Behavioural efficacy of phase-specific suppression remains to be established. | Valuable response data and a warning against equating rate suppression with therapeutic control. |
| S06, Little et al., 2013 | Clinical beta-triggered on/off controller, not a fitted plant. Eight PD patients. | Blinded motor improvement of 50% relative to no stimulation; reported 27% better than continuous DBS, with 56% less stimulation time. | Direct clinical support for beta-guided intervention in this cohort. Does not prove beta is the unique causal mechanism or validate a particular WC topology. |
| S07, Kühn et al., 2008 | Physiological/behavioural study; no fitted population plant. Eleven selected patients with persistent benefit after stimulation cessation. | Beta suppression covaries with improved movement amplitude; individual beta power vs movement amplitude r = -0.555, p = 0.007. | Strong symptom association with an intervention, but a selected cohort and correlation rather than a complete causal explanation. |
| S01, De la Crompe et al., 2025 | Review chapter reassessing STN–GPe circuit mechanisms; no newly fitted model. | Reviews healthy/transient vs dopamine-depleted/prolonged beta and circuit-specific interventions. Motor deficits can precede sustained beta. | Essential biological constraint: rodent evidence favours a central GPe role and challenges a universal STN-driven reciprocal-loop explanation. Transport memory cannot repair an incorrect circuit topology. |

| S14, Burghi and Sepulchre, 2024 | Adaptive observers for conductance-based single-neuron/circuit models; RLS and contraction-based analysis, numerical examples. | No fitted PD/ET patient cohort or healthy–diseased validation in this study. | Useful observer methodology under its measurement, model-structure and excitation assumptions; not directly a population-level WC observer or a pathological-activity fit. |
| S15, Davidson et al., 2016 | Second-order and fourth-order nonlinear macroscopic oscillators; four human PD patients; beta-power suppression versus stimulation amplitude fitted with R² = 0.69–0.99. | Actual pathological LFP recordings with DBS; symptom linkage relies substantially on the surrounding beta literature rather than a newly validated symptom mapping. | Strong tractable human stimulation-response benchmark. Static/steady oscillation-power curves are not full transient validation; fourth order does not improve the clinical fits enough to justify its complexity. |
| S16, Fleming, Dunn and Lowery, 2020 | Detailed conductance-based cortico-basal ganglia model, extracellular field, afferent axons and LFP; simulations compare on/off, dual-threshold, P and PI. | Disease-related beta and qualitative clinical comparators; not an individual-patient plant fit. | Valuable higher-fidelity control testbed and source of rate limits/tuning constraints. Reported post-stimulation rebound mismatch limits biological validation. |
| S17, Fleming, Senneff and Lowery, 2023 | Detailed neural network plus motoneuron/EMG/muscle-force simulation; supervisory bank of controllers and dual pulse-amplitude/duration control. | Modeled tremor and beta biomarkers; controller outcomes assessed computationally, not a new clinical trial. | Useful multi-objective and actuator-aware testbed. This addresses more than beta suppression, but does not independently validate the fitted transport-WC model. |

S08 fit details: PDF pp. 17–20, Table 2, Eq. (22), Figs. 7–9; interpretation and limitations pp. 26–28. S04 spectrum fits and greedy optimality: pp. 14, 16–17. S11 fitting/parameter recovery/amplitude limitations: pp. 5, 8–11. S02 identification, replay experiment and robustness: pp. 2–5. S03 model-selection/classification/severity: pp. 3–5. S12 model, identification and guarantees: pp. 3–7. S01 mechanism reassessment: chapter pp. 343–352, especially 348–352.

**3. Models that should be implemented and compared**

**3.1 Essential tremor: fitted stochastic WC model, S08/S05**

Using the paper's notation, weights w_PR denote a connection from P to R:

\[
\begin{aligned}
dE &= \frac{-E+f(\theta_E+w_{EE}E-w_{IE}I)}{\tau}\,dt+\zeta\,dW_E,\\
dI &= \frac{-I+f(\theta_I+w_{EI}E)}{\tau}\,dt+\zeta\,dW_I,\\
f(v)&=\frac{1}{1+\exp[-\beta(v-1)]}.
\end{aligned}
\]

Thus w_IE is inhibitory I-to-E coupling, and w_EI is excitatory E-to-I coupling. These subscripts differ from the receiver-first convention used in some other papers.

Stimulation is a direct positive increment of E at delayed stimulation times:

\[
E((t_k+d_u)^+)=E((t_k+d_u)^-)+\delta_E.
\]

The numerical implementation follows the paper's pulse/burst convention; it should not be silently replaced by a negative input inside the sigmoid. The observation is essentially the centred/scaled E component as a proxy for tremor acceleration. The fitted circuit mapping is VIM/nRT, with cortical pathways absorbed into effective couplings; no limb-mechanics model is identified.

| Parameter | Patient 1 | Patient 5 | Patient 6 |
|---|---:|---:|---:|
| w_IE, I to E | 9.4014 | 26.048 | 5.2064 |
| w_EI, E to I | 9.6306 | 25.3384 | 24.4813 |
| w_EE | 6.7541 | 1.548 | 2.7514 |
| beta, sigmoid steepness | 1.1853 | 2.4234 | 4.1933 |
| tau, seconds | 0.0758 | 0.29984 | 0.2513 |
| theta_E | 1.4240 | 22.8621 | 2.9127 |
| theta_I | -3.2345 | -9.9279 | -3.4008 |
| zeta, diffusion coefficient | 0.0457 | 0.013707 | 0.0263 |
| delta_E | 0.001684 | 0.00598 | 0.001686 |
| d_u, milliseconds | 138.8366 | 444.1573 | 183.4711 |

These are S08 Table 2 values, not new estimates. The fitted data were filtered and normalized, so state amplitudes/input gains should not be interpreted directly as calibrated physiological firing rates or electrical current.

Their feature score is

\[
R^2_{\rm features}
=1-\frac14\sum_{j=1}^{4}
\frac{\|F_j^{\rm data}-F_j^{\rm model}\|_2^2}
{\|F_j^{\rm data}-\overline F_j^{\rm data}\|_2^2}.
\]

It is not an R² for predicting every waveform sample. bARC validation tests an omitted feature from the related recordings, not an entirely independent clinical cohort. The best models are stable foci driven by noise; pathology is persistent tremor amplitude, not necessarily mathematical instability. S08 preferentially selects a focus when competing costs are statistically tied.

**3.2 Oscillator alternative: S10/S11, with the multi-population extension S04**

The common finite-network structure is

\[
\dot\vartheta_n
=\omega_n+\frac{K}{N}\sum_{m=1}^N
\sin(\vartheta_m-\vartheta_n)
+I(t)Z(\vartheta_n)+\xi_n(t).
\]

The collective state and an illustrative measurement mapping are

\[
q_N=\frac1N\sum_n e^{i\vartheta_n}=\rho e^{i\psi},
\qquad y=c\,\Re(q_N)+v.
\]

Here rho is synchrony, not the refractory duration r of WC. The output amplitude is proportional to synchrony under the assumed observation mapping.

For Z(theta) = -sin(theta), a Lorentzian frequency distribution, the noiseless infinite-population reduction used in S11 is

\[
\begin{aligned}
\dot\rho&=-\gamma\rho+\frac K2\rho(1-\rho^2)
+\frac{I(t)}2(1-\rho^2)\cos\psi,\\
\dot\psi&=\omega_0-\frac{I(t)}{2\rho}(1+\rho^2)\sin\psi.
\end{aligned}
\]

The polar form is singular at rho = 0; a Cartesian order parameter avoids that coordinate singularity. This reduction is not an exact two-state realization of every finite, noisy fitted network.

S11 fits omega_0, gamma, K, and noise level to three normalized signal features. Fits use finite networks (N = 200 in optimization) with repeated noise realizations. Individual parameters could not be recovered reliably in synthetic recovery tests, whereas inferred mean synchrony was more robust. The report should therefore compare predictive quantities and uncertainty, not claim unique physiological coupling estimates. In its reduced scalar representation, weakly coupled oscillators do not separately model synaptic voltage and refractory-history dynamics.

S04 uses several such populations, cross-couplings, electrode-to-population gains and measurement weights. A generic representation is

\[
\dot\vartheta_{\sigma n}
=\omega_{\sigma n}
+\sum_\lambda\frac{K_{\sigma\lambda}}{N_\lambda}
\sum_m\sin(\vartheta_{\lambda m}-\vartheta_{\sigma n})
+Z(\vartheta_{\sigma n})\sum_\ell b_{\sigma\ell}u_\ell.
\]

Measurements combine population order parameters according to assumed geometry. The controller chooses contact currents to favour immediate desynchronization. This provides a multi-input comparator, but the geometry and contact responses in the simulations are not individually validated by the reported one-block PSD fit.

**3.3 PD population plant: delayed STN–GPe firing-rate model, S12**

With the receiver-first c_ij convention, the paper's plant is

\[
\begin{aligned}
\tau_1\dot x_1&=-x_1+
S_1\!\left(c_{11}x_1(t-\delta_{11})
-c_{12}x_2(t-\delta_{12})+b_1u_1(t)\right),\\
\tau_2\dot x_2&=-x_2+
S_2\!\left(c_{21}x_1(t-\delta_{21})
-c_{22}x_2(t-\delta_{22})-b_2u_2(t)\right).
\end{aligned}
\]

x_1 is STN activity, x_2 GPe activity; u_1 and u_2 represent cortical/striatal drives. DBS is introduced as an additional effective input mu in the STN sigmoid for the control analysis. For equilibrium-centred analysis, the activation functions/inputs are shifted consistently.

This is already a delay model. Its transport realization does not add dynamics. It is also not the same memory mechanism as absolute refractoriness in the original WC history formulation.

The proposed baseline feedback is

\[
\mu=-\theta(t)x_1,\qquad
\tau_\theta\dot\theta=|x_1|-\sigma\theta,
\]

with a variant that uses a beta biomarker in the adaptation law. Under the stated small-GPe-self-coupling condition, ell_2 c_22 < 1, the analysis gives boundedness and a bound on long-time average oscillation amplitude; decreasing sigma tightens that bound. The exact unfiltered theorem should not be transferred automatically to every filtered, delayed-sensing, saturated implementation.

The conductance-based validation contains additional neuronal, field, stimulation and LFP measurement dynamics. Treat the negative centred population feedback mu and the nonnegative physical pulse-amplitude command as different input coordinates. A fair implementation requires their mapping rather than directly sending a signed mathematical rate command to an electrode.

**3.4 PD envelope plant and predictor: S02**

This is a biomarker model rather than an E/I physiological model:

\[
z(t)=z_\beta(t)e^{-\eta(t)}+\zeta(t),
\]

\[
\dot x_c=
\begin{bmatrix}-1/\tau_1&0\\ k/\tau_2&-1/\tau_2\end{bmatrix}x_c+
\begin{bmatrix}k/\tau_1\\0\end{bmatrix}u,
\qquad
\eta=\begin{bmatrix}0&1\end{bmatrix}x_c.
\]

The supplied PDF prints k in both gains. Its nominal values are k = 62.11, tau_1 = 0.05, tau_2 = 0.25. It describes the input as stimulation voltage near Eq. (2), but also refers to instantaneous power in the preceding discussion. Electrical calibration and units need resolving before calling a command penalty actual energy.

Taking logarithms gives approximately

\[
y_k=\ln z_k=\beta_k-\eta_k+v_k,
\quad
\Delta\beta_k=\sum_{j=1}^{5}\alpha_j\Delta\beta_{k-j}+\epsilon_k,
\quad
\beta_k=\beta_{k-1}+\Delta\beta_k.
\]

The additive-noise approximation after the logarithm assumes sufficiently small measurement noise and a positive envelope. It is not a global exact transformation of additive noisy data.

The two attenuation states, nominal beta level and five increment-history coordinates form an eight-state predictor before the additional previous-input augmentation for MPC. Sampling is 20 ms; baseline identification uses 5 s. In the patient-replay experiment, the threshold is the 75th percentile of the recorded baseline signal, not a threshold established by healthy-control physiology.

A Kalman filter estimates nominal activity and attenuation. The paper already compares MPC, PI and bang-bang methods. Benefits shrink with response-model mismatch; at 20% or greater mismatch, MPC can have larger tracking error than PI despite reduced input. This argues for comparing uncertainty sensitivity and the full effort–performance trade-off.

**3.5 Healthy-control discriminator: S03**

The candidate DDE library is

\[
\begin{aligned}
\dot x={}&a_1x_1+a_2x_2+a_3x_1^2+a_4x_1x_2+a_5x_2^2\\
&+a_6x_1^3+a_7x_1^2x_2+a_8x_1x_2^2+a_9x_2^3,
\qquad x_j=x(t-\tau_j).
\end{aligned}
\]

Only two or three terms are retained per candidate; the two delays and structure are selected for classification. The coefficients and derivative-fit errors become classification features. This is a compact delay embedding of EEG, not an identified STN/GPe circuit with physiological conduction delays.

The reported discrimination includes participant-level resampling and an additional set of 50 trials from the same participants. It is not an external independent-patient validation cohort. It may supply candidate disease-sensitive features for validating outputs, but it cannot determine the stimulation-response input matrix or justify forcing EEG into one healthy trajectory.

**3.6 Human PD stimulation-response fit: S15**

Davidson et al. (2016) models two nonlinear neural ensembles, each represented by an arctangent-shaped static nonlinearity and a second-order linear dynamic block. In its reduced fourth-order series model the dynamic blocks have

\[
G_r(s)=\frac{k}{(s+b)^2}.
\]

The blocks are connected in an excitatory–inhibitory loop and DBS is added at the input to the first nonlinearity (paper Fig. 2 and Eq. (19), PDF pp. 3–5). Two such blocks yield four dynamic states; the earlier single-loop model has two states. A time-domain realization of each block is ddot(x) + 2b dot(x) + b²x = k v, with v the appropriate nonlinear feedback/stimulation signal. Recover the exact interconnection signs and nonlinear scaling from the paper before reproducing its numerical fits.

Describing-function analysis predicts steady oscillation amplitude/power and its suppression under a high-frequency biphasic rectangular input. The clinical comparison uses four patients, stimulation fixed at 130 Hz and pulse width 60 microseconds except one patient's 90 microseconds, varying amplitude. The reported R² range 0.69–0.99 measures agreement of beta-power suppression curves, not trajectory prediction or clinical-score prediction. Its second-order and fourth-order models fit similarly; the paper concludes that second order suffices for these data.

This is a strong low-order baseline for testing the proposed transport model. Fit the same amplitude-suppression curves first, then demand an improvement in independently measured ON/OFF transients or responses to new pulse modulation before adding distributed memory. Any causal interpretation of the oscillators remains phenomenological; a good suppression curve does not identify a unique STN–GPe circuit.

S16 and S17 provide more detailed conductance-based simulation environments for checking controllers beyond the reduced identification model. S17 includes EMG/force and tremor as well as beta, and pulse-duration/amplitude constraints. S14 offers observer design ideas for biophysical circuits, but its conductance-based measurement structure and excitation conditions cannot be assumed for aggregate population recordings.


**4. What transport WC could improve, and what it cannot**

**4.1 Separate three different types of memory**

1. Axonal/synaptic transmission delay: an activity value arrives later at another population.
2. Refractoriness: recent firing determines what fraction of a population is available.
3. Stimulation and measurement dynamics: electrode/opsin/neural recruitment and, for tremor, downstream mechanics and sensor/filter delays.

They should not be represented by the same fitted delay unless the intent is explicitly an effective input–output approximation.

For a transmission delay d > 0, normalized history is exactly

\[
z_j(t,a)=x_j(t-da),\quad 0\le a\le1,
\qquad
\partial_t z_j+\frac1d\partial_a z_j=0,\quad
z_j(t,0)=x_j(t),\quad x_j(t-d)=z_j(t,1).
\]

For refractory duration r_i > 0 and firing rates n_i in inverse seconds,

\[
z_i^r(t,a)=n_i(t-r_i a),\qquad
R_i(t)=r_i\int_0^1 z_i^r(t,a)\,da.
\]

If x_i is normalized activity and n_i = nu_i x_i, then R_i = nu_i r_i integral(z_i^r da), with z_i^r storing x_i instead. Normalizing the age coordinate does not remove the duration/Jacobian or the firing-rate scale.

These are age/history coordinates, not physical spatial coordinates. A finite-grid transport simulation introduces numerical dispersion/diffusion; apparent improvement from changing a grid is not evidence of a better continuous biological model.

**4.2 A proposed identifiable extension, not an equation claimed from these patient papers**

A rate-based WC history model could be

\[
\begin{aligned}
\tau_i\dot n_i&=-n_i+(1-R_i)F_i(V_i)+b_i v_u,\\
T_i\dot V_i&=-V_i+
\sum_j \varepsilon_j w_{ij} n_j(t-d_{ij})+P_i,\\
R_i(t)&=\int_{t-r_i}^{t}n_i(s)\,ds,
\end{aligned}
\]

where epsilon_j is +1 for excitatory sources and -1 for inhibitory ones. F_i returns a firing rate, so R_i is dimensionless. v_u is a calibrated actuation output; its location inside or outside F_i must be chosen and fitted against stimulation-response data. The displayed additive rate input is one hypothesis, not an assertion about all DBS.

Use y = H_measure[n] + noise, with a justified low-order observation mapping. A limb acceleration output may need downstream filtering/second-order mechanics; an LFP output may require a different population-to-field mapping.

The deterministic refractory derivative is dot(R_i) = n_i(t) - n_i(t-r_i), with consistent initial histories. This gives a convenient equivalent DDE simulation for fitting. The normalized transport realization is exact for the same histories. Positivity and admissible refractory fractions must be checked; the population approximation is not automatically physically valid for every fitted parameter vector.

Adding white diffusion directly to activity states can violate rate bounds. If used to reproduce an existing SDE fit, preserve its interpretation; for the refractory extension, consider bounded rates driven by noisy inputs or another explicitly justified stochastic formulation.

**4.3 Specific reasons to test added dynamics**

| Observation in the supplied papers | Extension worth testing | What would substantiate improvement? |
|---|---|---|
| S08 fits effective stimulation delays of 139–444 ms; biological interpretation remains unexplained. It identifies tremor acceleration directly with population activity. | Separate a short stimulation latency, a parsimonious recurrent transmission delay, and a downstream measurement/limb-response filter. | Improved held-out phase AND amplitude responses and ON/OFF transients, with plausible parameter ranges and less unexplained aggregate delay. Do not simply redistribute an unidentifiable delay among blocks. |
| S08 omits explicit cortical transmission although its E-to-E and E-to-I pathways are mapped through cortex. | Add one effective loop delay before adding separate pathway delays. | Better frequency-dependent phase and transient recovery across several conditions. |
| S11 acknowledges insufficient oscillation-amplitude variability and uncertain individual oscillator parameters. | Compare a stochastic E/I model with explicit synaptic/refractory memory against the finite oscillator model; also compare an equally small colored-input-noise model. | Better held-out envelope PDF/PSD and burst distributions without losing stimulation-response accuracy. The paper itself also suggests adaptive coupling/generalized amplitude oscillators; memory is a competing hypothesis. |
| S12 includes transmission delays but assumes a two-population circuit and simple activation responses. | Retain its existing delays exactly; add refractory memory only when residual history dependence warrants it. | Better fit to the same observed neural responses. Its existing DDE-to-PDE conversion cannot itself improve fit. |
| S01 reports different roles for GPe subtypes and circuit-specific intervention results in rodents. | Compare a small alternative topology or external-drive explanation before adding many delays to one STN–GPe loop. | Better cross-site phase relations and perturbation predictions, not merely matching a beta peak. |
| S02's averaged stimulation response limits robustness; its baseline predictor and attenuation dynamics are separated. | First identify individual actuation/attenuation dynamics and delays. Compare transport WC only if it predicts the same measured envelope at least as well. | Better independent stimulation-response prediction and uncertainty calibration. Increased physiological detail alone is insufficient. |

Absolute refractory memory is not an obvious explanation for the long S08 effective delay. For illustration, with r = 3 ms, the normalized rectangular-history average has

\[
\overline H_r(s)=\frac{1-e^{-rs}}{rs},\qquad
\overline H_r(i\omega)=e^{-i\omega r/2}
\frac{\sin(\omega r/2)}{\omega r/2}.
\]

Its phase lag is 2.7 degrees at 5 Hz and 10.8 degrees at 20 Hz. Those numbers concern the memory-average operator itself; recurrent closed-loop dynamics can amplify its consequences near a stability boundary. They nevertheless argue against explaining hundreds of milliseconds by a few milliseconds of absolute refractoriness alone.

S08 explicitly concludes that additional complexity is not warranted by the available selected recordings because the simple model already reproduces them (discussion, PDF p. 28). Our proposal must therefore be a testable extension using stronger validation or new stimulation conditions, not a claim that the supplied data already prove the transport model superior.

**4.4 Keep delays exact when linearizing for synthesis**

Around a fitted operating point,

\[
\tau_i\delta\dot n_i
=-\delta n_i+(1-R_i^\star)F_i'(V_i^\star)\delta V_i
-F_i(V_i^\star)\delta R_i+b_i\delta v_u,
\qquad
\delta R_i=\int_{t-r_i}^{t}\delta n_i(s)\,ds.
\]

The factors 1-R_i and F_i together must be linearized; replacing only the sigmoid leaves a bilinear product when refractory fractions vary.

The operators e^(-sd) and (1-e^(-sr))/s remain exact. No Padé/Taylor delay approximation is required. Alternatively retain the sigmoid as a sector/slope-bounded nonlinearity for IQC analysis, subject to a declared operating region and the remaining refractory product. A product of unknown refractory availability and a sigmoid is not automatically covered by an IQC for the sigmoid alone.

A deterministic local or robust stability certificate and stochastic output-variance attenuation answer different questions. S08's stable-focus tremor requires disturbance attenuation even when the deterministic equilibrium is already stable.

**5. Identification protocol that can test the fit claim**

**Stage A: reproduce available baselines before extending them.**

- ET: reproduce S08's four features and omitted bARC using Table 2; quantify Monte Carlo uncertainty.
- PD rats: reproduce S11's finite-network feature fits, including its amplitude-variability limitation and parameter-recovery ambiguity.
- PD human response: reproduce S15's amplitude-suppression curves and compare its second-order baseline before testing added delays or memory.
- PD synthesis: reproduce S12's delayed rate model and reference feedback. Keep its synthetic-network calibration distinct from patient identification.
- Envelope benchmark: reproduce S02's baseline predictor and attenuation equations. Document the unavailable unpublished individual-response evidence rather than implying full reproducibility.

No model needs to be fitted independently to every controller.

**Stage B: fit a small, nested model sequence.**

M0 is the published baseline. M1 adds one effective recurrent delay. M2 adds a minimal observation/actuation filter; fit delay and filtering jointly only where the data can distinguish them. M3 adds explicit refractory history. Also test a parsimonious colored-input-noise or small alternative-topology model where the corresponding residual pattern exists.

Zero delay, vanishing filter time constant, or vanishing refractory duration should recover the relevant simpler model in the continuous formulation. The transport speed 1/d is singular at d = 0, so implement zero-delay cases as separate algebraic branches, not by division by zero.

In the noisy case, compare simulated statistics or likelihood/prediction methods that account for process noise. Do not minimize waveform sample error between independently generated noise realizations. For deterministic evoked responses with measurement noise, weighted output-error fitting may be appropriate.

**Stage C: validate against information that was not used in fitting.**

Use complete held-out trials/blocks and, when available, recording sessions and stimulation conditions. Avoid randomly interleaving neighbouring samples from the same oscillation between fit and validation sets. Keep feature normalization and filtering fixed across candidates.

The data should ideally contain several stimulation amplitudes/timings/rates or another informative modulation around an operating point. The existing phase-locked ET data already constrain response curves but are not a universal broadband input–output experiment. Multiple conditions and ON/OFF transients help distinguish a delay from phase shifts modulo one oscillation period.

Score at least: signal PSD, envelope PDF and PSD, burst-duration distribution for PD, phase-response and amplitude-response curves, stimulus ON/OFF response time, and prediction of withheld stimulation conditions. Report each score separately alongside any aggregate.

Investigate parameter profiles and bootstrap uncertainty, including coupling/noise/delay/measurement confounding. Compare equal or penalized complexity. A fit improvement is credible only if it survives held-out prediction and exceeds simulation/measurement uncertainty; the estimated new time scale should be distinguishable from zero or unnecessary alternatives.

For two-population models with only one aggregate output, broad predictive uncertainty may remain even when spectra are accurately matched. Cross-site recordings and known stimulation commands are more informative than additional optimizer starts alone.

**Stage D: interpret pathology separately from fitting.**

For ET, use tremor output and any available clinical ratings. For PD, beta suppression is supported by S06/S07 for relevant motor symptoms and cohorts, but S01 prevents equating all beta with disease or all motor impairment with one oscillation mechanism. S09 shows mean firing rate can remain unchanged while rhythmicity changes. A good model must reproduce the feature tied to the selected symptom, not merely any oscillation.

Healthy-control data can define a distribution of acceptable features, but the available fitted WC/oscillator studies here do not provide the complete matched human healthy-vs-diseased stimulation-response dataset. Medication-ON PD is not interchangeable with a healthy control.

**6. Comparing controllers after fitting**

Freeze the identified nominal plants, uncertainty sets, output definition, estimator assumptions, and test protocols before comparing controllers. Tune on designated training/tuning scenarios and evaluate on different conditions. If controllers are each evaluated only on their own fitted model, comparisons become confounded by model changes.

An illustrative common objective is

\[
J=\mathbb E\int_0^T z_{\rm path}(t)^2\,dt
+\lambda\,\mathcal E(u),
\]

where z_path is a declared tremor/beta output and E(u) is actual stimulation energy when calibrated electrical quantities are available; otherwise label it a normalized effort proxy. For PD, an excess-over-target or burst-duration objective may be preferable to driving all beta to zero. Penalize changes in non-target activity where the measurements permit it.

Useful comparison set:

1. Constant high-frequency stimulation/reference condition and a no-stimulation baseline.
2. Threshold/on-off control inspired by S06.
3. Tuned PI/proportional control, with anti-windup if needed.
4. Phase-locked stimulation from S13/S10.
5. S05 isostable phase-space control for the two-state ET baseline.
6. S12 adaptive/self-tuning control for the delayed PD plant.
7. Observer-based state feedback and dynamic output feedback, including a robust delay-preserving design if feasible.
8. MPC based on the same observation/input channels; S02 provides an envelope-based alternative.

Use the same physical input bounds, pulse-generation rules, sensing delays, filter latency, noise assumptions and electrical effort accounting. Evaluate observer error and computational burden; ideal full-state controllers can be reported separately as optimistic benchmarks. S05's two-dimensional amplitude-field machinery is not automatically a deployable controller for a history-state PDE.

Test on independent trials/noise seeds, parameter perturbations, delay uncertainty, changing baseline drives and measurement artifacts. Where possible evaluate on a higher-fidelity or independently fitted plant as well. Report suppression versus effort curves, residual burst/phase-response behaviour, transient recovery, estimator quality and limits of stability/performance guarantees. A theorem for the nominal plant does not establish clinical efficacy.

**7. Data and code paths**

- Human essential-tremor recordings: DOI 10.5287/bodleian:xq24eN2Km, cited by S08/S10/S04. Dataset record: https://data.mrc.ox.ac.uk/data-set/tremor-data-measured-essential-tremor-patients-subjected-phase-locked-deep-brain. The record is a source of accelerometer traces, stimulation triggers and block information. Archive entries, datasets and unique patients must not be treated as the same count.
- S05 code for amplitude fields: https://github.com/benoit-du/amplitudeFields. This is not automatically the complete original S08 fitting pipeline.
- S04 multi-contact code: https://github.com/gihan-weerasinghe/neurolab.
- S11 parkinsonian rat recordings: DOI https://doi.org/10.5287/bodleian:9omadD7Pp. S11 points to https://github.com/Bogacz-Group for analysis/modeling code; the supplied PDF does not name a specific repository in that statement.
- S12 rate-model code: https://github.com/silvanx/self-tuning-control; conductance model: ModelDB accession 262046 (https://modeldb.science/262046).
- S02: the individual baseline recording is described, but a reusable patient-data package was not located in the supplied PDF. The averaged attenuation model cites an unpublished paper. Do not assume the raw stimulation-response data are public.
- S03/S06/S07/S09/S13: clinical recording procedures are described; access to all raw recordings is not established by the supplied PDFs alone. The ET subset used by the modeling sequence has the separate archive above.
- Existing local history/transport demonstration: Simulations/Wilson_Cowan_Coarse_Graining/plot_wilson_cowan_models.m and its README. It verifies numerical equivalence for illustrative parameters; it is not a patient fit.

No dataset was downloaded or analysed in this review. Data availability citations identify candidate next inputs; access and metadata must be checked before fitting.

**8. Research claim supported by this assessment**

A defensible proposed study is:

"Fit a small delayed E/I population model to measured symptom-related activity and stimulation responses, test whether explicitly retained history or separated measurement dynamics improve independent prediction relative to published WC/oscillator/envelope baselines, and then compare control methods under identical sensing and actuation constraints."

For the first demonstration, choose ET/Cagnan–Duchet. For human PD input–output calibration, include Davidson's second-order suppression-curve model. Use the PD rat data as a second biological test, the delayed STN–GPe/envelope models as synthesis benchmarks, and the detailed S16/S17 networks as independent simulation testbeds. A claim that transport WC already improves fit, reproduces a unique disease mechanism, or defines a universal controller is not supported by the reviewed papers.


**9. Source register: supplied local PDFs**

- **S01: De la Crompe et al. (2025)**. [Reevaluating the role of the STN-GPe network in generating beta synchronized oscillatory activity in parkinsonism.pdf](<../References/tremor and parkinsons/Reevaluating the role of the STN-GPe network in generating beta synchronized oscillatory activity in parkinsonism.pdf>). Main locations: Chapter pp. 343-352.
- **S02: Steffen et al. (2024)**. [Model Predictive Control for Closed-Loop DBS.pdf](<../References/tremor and parkinsons/Model Predictive Control for Closed-Loop DBS.pdf>). Main locations: PDF pp. 2-5.
- **S03: Lainscsek et al. (2013)**. [non-linear dynamical analysis of EEG time series distinguishes patients with PD from healthy individuals.pdf](<../References/tremor and parkinsons/non-linear dynamical analysis of EEG time series distinguishes patients with PD from healthy individuals.pdf>). Main locations: PDF pp. 3-5.
- **S04: Weerasinghe et al. (2021)**. [Optimal closed-loop dbs using multiple independently controlled contacts.pdf](<../References/tremor and parkinsons/Optimal closed-loop dbs using multiple independently controlled contacts.pdf>). Main locations: PDF pp. 14,16-17.
- **S05: Duchet et al. (2021)**. [Optimizing dbs based isostable amplitude in essential tremor patient models.pdf](<../References/tremor and parkinsons/Optimizing dbs based isostable amplitude in essential tremor patient models.pdf>). Main locations: PDF pp. 3-4,12,15-17.
- **S06: Little et al. (2013)**. [Adaptive DBS in Advanced PD.pdf](<../References/tremor and parkinsons/pathologic behaviour/Adaptive DBS in Advanced PD.pdf>). Main locations: PDF pp. 1-4.
- **S07: Kuhn et al. (2008)**. [HF stimulation improves motor performance.pdf](<../References/tremor and parkinsons/pathologic behaviour/HF stimulation improves motor performance.pdf>). Main locations: PDF pp. 1,5-6.
- **S08: Duchet et al. (2020)**. [Phase-dependence of response curves to dbs and their relationship - from essential tremor patient data to a Wilson-Cowan model.pdf](<../References/tremor and parkinsons/Phase-dependence of response curves to dbs and their relationship - from essential tremor patient data to a Wilson-Cowan model.pdf>). Main locations: PDF pp. 8-9,17-20,26-28.
- **S09: Holt et al. (2019)**. [Phase-Dependent Suppression of Beta Oscillations in Parkinsons Disease Patients.pdf](<../References/tremor and parkinsons/Phase-Dependent Suppression of Beta Oscillations in Parkinsons Disease Patients.pdf>). Main locations: PDF pp. 1,5-7,14-15.
- **S10: Weerasinghe et al. (2019)**. [Predicting the effects of dbs using a reduced coupled oscillator model.pdf](<../References/tremor and parkinsons/Predicting the effects of dbs using a reduced coupled oscillator model.pdf>). Main locations: PDF pp. 6-12,18-22.
- **S11: Mirkhani et al. (2025)**. [Response of Neuronal Populations to Phase-Locked Stimulation - Model Based Predictions and Validation.pdf](<../References/tremor and parkinsons/Response of Neuronal Populations to Phase-Locked Stimulation - Model Based Predictions and Validation.pdf>). Main locations: PDF pp. 5,7-11.
- **S12: Fleming et al. (2020)**. [Self-Tuning DBS Controller for Suppression of Beta Oscillations - Analytical Derivation and Numerical Validation.pdf](<../References/tremor and parkinsons/Self-Tuning DBS Controller for Suppression of Beta Oscillations - Analytical Derivation and Numerical Validation.pdf>). Main locations: PDF pp. 3-7,17-18.
- **S13: Cagnan et al. (2017)**. [Stimulating at the right time - phase-specific dbs.pdf](<../References/tremor and parkinsons/Stimulating at the right time - phase-specific dbs.pdf>). Main locations: PDF pp. 1-4,6-9.
- **S14: Burghi and Sepulchre (2024)**. [Adaptive_Observers_for_Biophysical_Neuronal_Circuits.pdf](<../References/tremor and parkinsons/Adaptive_Observers_for_Biophysical_Neuronal_Circuits.pdf>). Main locations: PDF pp. 1-3, numerical examples.
- **S15: Davidson et al. (2016)**. [Analysis_of_Oscillatory_Neural_Activity_in_Series_Network_Models_of_Parkinsons_Disease_During_Deep_Brain_Stimulation.pdf](<../References/tremor and parkinsons/Analysis_of_Oscillatory_Neural_Activity_in_Series_Network_Models_of_Parkinsons_Disease_During_Deep_Brain_Stimulation.pdf>). Main locations: PDF pp. 3-5,7-10.
- **S16: Fleming, Dunn and Lowery (2020)**. [Simulation of Closed-Loop DBS Control Schemes for Suppression of Pathological Beta Oscillations in PD.pdf](<../References/tremor and parkinsons/Simulation of Closed-Loop DBS Control Schemes for Suppression of Pathological Beta Oscillations in PD.pdf>). Main locations: PDF pp. 1-8, discussion.
- **S17: Fleming, Senneff and Lowery (2023)**. [Multivariable closed-loop control of deep brain stimulation for Parkinsons disease.pdf](<../References/tremor and parkinsons/testbed/Multivariable closed-loop control of deep brain stimulation for Parkinsons disease.pdf>). Main locations: PDF pp. 2-8, results and discussion.
