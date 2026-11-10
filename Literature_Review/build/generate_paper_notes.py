"""Generate standalone reading notes from the manually reviewed local PDFs."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Literature_Review' / 'Paper_Notes'
INVENTORY = json.loads((ROOT / 'Literature_Review/build/paper_texts/inventory.json').read_text(encoding='utf-8'))

# Each entry is an independent reading of the indicated reference PDF.
# No findings or problem formulation are imported from main.tex.
NOTES = [
dict(id=1, slug='chikermane_2024_cortical_beta',
title='Cortical beta oscillations map to shared brain networks modulated by dopamine',
authors='Chikermane et al.', year='2024', kind='Human recordings and network mapping', doi='10.7554/eLife.97184',
relation=r'''Measurement and the network basis of beta activity. Useful for deciding what a beta measurement represents before selecting a feedback objective.''',
findings=r'''\textbf{Measured.} Recordings selected from clinically normal cortical regions in epilepsy patients are combined with normative connectivity and dopamine-related PET maps. Regions with prominent beta activity share connectivity with a distributed cortico-subcortical network (PDF pp.~1--9).

\textbf{Interpretation.} Beta is also a physiological rhythm associated with several functions. The spatial correspondence with dopamine markers supports a network hypothesis; it does not demonstrate that beta causes symptoms or that suppressing it improves behaviour. This is not a DBS treatment trial.

\textbf{Model relevance.} Supports considering cortical inputs and distributed coupling rather than assigning beta exclusively to one nucleus. The connectivity maps do not identify dynamical coupling gains, transmission delays, or a firing-rate-to-LFP measurement equation for the notebook model (PDF pp.~8--12).''',
followups=r'''\begin{itemize}
\item Hammond, Bergman and Brown (2007), \emph{Pathological synchronization in Parkinson's disease: networks, models and treatments}: competing mechanisms (references, PDF p.~15).
\item Gilron et al. (2021), \emph{Long-term wireless streaming of neural recordings for circuit discovery and adaptive stimulation in individuals with Parkinson's disease}: chronic sensing (PDF p.~15).
\end{itemize}'''),

dict(id=2, slug='yin_2022_cortical_pac_freezing',
title='Cortical phase-amplitude coupling is key to the occurrence and treatment of freezing of gait',
authors='Yin et al.', year='2022', kind='Human walking study', doi='10.1093/brain/awac121',
relation=r'''Measurement, freezing of gait, and the choice of a clinical control objective. Tests whether a cortical coupling measure tracks freezing and changes with STN stimulation.''',
findings=r'''\textbf{Measured and manipulated.} Motor-cortex ECoG and gait were recorded during walking tasks in 16 patients with Parkinson's disease. Beta--gamma phase-amplitude coupling (PAC) was higher in trials with freezing and related to freezing severity. STN-DBS reduced PAC and alleviated freezing (PDF pp.~1--10).

\textbf{Usable insight.} Freezing still improved with DBS when comparing trials with similar PAC. Therefore, PAC reduction alone does not explain the benefit. A proposed ``bandwidth'' account combines baseline synchrony, task demands, and processing capacity; it is a conceptual explanation rather than an identified dynamical model (PDF pp.~9--13).

\textbf{Model relevance.} The supported behavioural objective is reducing freezing while preserving walking. PAC is a candidate feedback feature, requiring a nonlinear signal-processing block beyond the notebook's linear measurement equation. The paper supplies no delayed rate-model parameterization or implemented PAC-based adaptive controller.''',
followups=r'''\begin{itemize}
\item Pozzi et al. (2019), \emph{Freezing of gait in Parkinson's disease reflects a sudden derangement of locomotor network dynamics}: network context (ref.~13, PDF p.~14).
\item Cole et al. (2017), \emph{Nonsinusoidal beta oscillations reflect cortical pathophysiology in Parkinson's disease}: waveform contributions to PAC (ref.~41, PDF p.~14).
\end{itemize}'''),

dict(id=3, slug='rajamani_2024_symptom_networks',
title="Deep brain stimulation of symptom-specific networks in Parkinson's disease",
authors='Rajamani et al.', year='2024', kind='Multicentre connectomic DBS study', doi='10.1038/s41467-024-48731-1',
relation=r'''What DBS can control and how to choose the performance objective. Examines whether different symptoms benefit from stimulation of different networks.''',
findings=r'''\textbf{Evidence.} Stimulation locations and tract engagement were related to changes in tremor, rigidity, bradykinesia and axial symptoms. The study included 232 retrospective patients and five additional prospective patients (PDF pp.~1--10).

\textbf{Usable insight.} Symptom improvement maps to partly distinct networks. The proposed network-blending approach weights these networks according to an individual's symptom profile when choosing stimulation settings. This supports a symptom-dependent performance objective rather than assuming one physiological feature captures all treatment benefit (PDF pp.~7--10).

\textbf{Model relevance.} Tract engagement can inform hypotheses about where control enters a network and which outputs matter. It does not directly determine the notebook's temporal gains, delays, nonlinearities, or measurement matrix. Connectomic associations and the small prospective demonstration do not establish a universal stimulation-to-symptom transfer function; normative tractography is a stated limitation.''',
followups=r'''\begin{itemize}
\item Horn et al. (2017), \emph{Connectivity Predicts Deep Brain Stimulation Outcome in Parkinson Disease}: connectivity-based outcome prediction (ref.~19, PDF p.~14).
\item Roediger et al. (2023), \emph{Automated deep brain stimulation programming based on electrode location}: randomized crossover programming trial (ref.~41, PDF p.~15).
\end{itemize}'''),

dict(id=4, slug='koehler_2024_volitional_action',
title="Dopamine and deep brain stimulation accelerate the neural dynamics of volitional action in Parkinson's disease",
authors='Koehler et al.', year='2024', kind='Published human electrophysiology study', doi='10.1093/brain/awae219',
relation=r'''Measurement, impaired movement initiation, and the control objective. Relates treatment effects to the interval between preparatory neural activity and muscle activation.''',
findings=r'''\textbf{Measured.} Sensorimotor ECoG, STN-LFP and EMG were recorded during self-initiated movements in 25 patients. Readiness potentials and classifiers estimated preparatory activity; directional spectral analyses assessed cortico-subthalamic communication (PDF pp.~1--8).

\textbf{Treatment effect.} Dopaminergic medication and STN-DBS shortened preparation-to-execution latencies and shifted directional coupling towards theta. These findings associate treatment benefit with changes in the timing and frequency structure of communication; they do not establish beta-power minimization as a sufficient objective (PDF pp.~8--11).

\textbf{Model relevance.} Movement-initiation latency is a useful behavioural outcome. These latencies should not be substituted directly for axonal delays in the notebook model: they summarize distributed preparation and execution processes. No nonlinear delayed-state model or feedback controller is identified.

\textbf{Version.} This is the published counterpart of note~05; the two files are not independent studies.''',
followups=r'''\begin{itemize}
\item Kornhuber and Deecke (1965), work on the \emph{Bereitschaftspotential}: origin of the preparatory-potential measure (ref.~2, PDF p.~11).
\item Lofredi et al. (2018), \emph{Dopamine-dependent scaling of subthalamic gamma bursts with movement velocity in patients with Parkinson's disease}: another movement-related outcome (ref.~56, PDF p.~12).
\end{itemize}'''),

dict(id=5, slug='koehler_2023_volitional_action_preprint',
title="Dopamine and neuromodulation accelerate the neural dynamics of volitional action in Parkinson's disease",
authors='Koehler et al.', year='2023', kind='bioRxiv preprint; overlaps note 04', doi='10.1101/2023.10.30.564700',
relation=r'''Movement-intention measurements and a possible treatment objective based on successful action initiation. Provides the preprint version of the study in note~04.''',
findings=r'''\textbf{Measured.} Combined cortical and STN recordings in 25 patients were analysed with readiness potentials, movement-intention classifiers and directional connectivity measures. EMG provided the execution reference (PDF pp.~1--8).

\textbf{Finding.} Medication and STN-DBS shortened intention-to-execution latencies, accompanied by a shift from beta towards theta cortico-subthalamic coupling. This motivates studying restoration of movement-related network dynamics. The preprint does not demonstrate that directly suppressing beta alone is the therapeutic mechanism (PDF pp.~8--12).

\textbf{Model relevance.} Supplies observable signals and behavioural timing measures, but no identified delayed neural rate model, actuator map, or stability certificate. The measured preparation interval is not an identified neural transmission delay.

\textbf{Version.} The local PDF is explicitly a non-peer-reviewed preprint. Use the published paper in note~04 for the final account and count the shared experiment once in a synthesis.''',
followups=r'''\begin{itemize}
\item Lofredi et al. (2018), \emph{Dopamine-dependent scaling of subthalamic gamma bursts with movement velocity in patients with Parkinson's disease} (ref.~39, PDF p.~20).
\item Gilron et al. (2020), \emph{Chronic wireless streaming of invasive neural recordings at home for circuit discovery and adaptive stimulation}: cited in its preprint form (ref.~40, PDF p.~20).
\end{itemize}'''),

dict(id=6, slug='yin_2024_sleep_decoding',
title='Generalized sleep decoding with basal ganglia signals in multiple movement disorders',
authors='Yin et al.', year='2024', kind='Human sleep-decoding study', doi='10.1038/s41746-024-01115-7',
relation=r'''What implanted electrodes can measure, and how feedback could account for sleep. Evaluates a sleep-state estimator across people, diagnoses and recording targets.''',
findings=r'''\textbf{Measured.} Synchronized polysomnography and intracranial field potentials provided training labels and neural features. After exclusions, 140 nights from 121 patients were analysed. BGOOSE achieved approximately 85\% average accuracy for awake/NREM/REM classification; additional ECoG improved decoding (PDF pp.~1--7).

\textbf{Usable insight.} Cross-subject evaluation and external datasets support using neural sensing to estimate context without individual polysomnography calibration. Performance is not uniform across stages: separating NREM substages is substantially harder. Classification results do not themselves show that sleep-triggered stimulation improves sleep (PDF pp.~6--8, 11).

\textbf{Model relevance.} A sleep estimator could select operating conditions or feedback policies. Its spectral, waveform and entropy features require an observation/processing layer beyond a linear $y=Cx$. No stimulation-to-neural-state dynamics or delayed-model coefficients are identified. Sleep quality would require its own validated performance output.''',
followups=r'''\begin{itemize}
\item Smyth et al. (2023), \emph{Adaptive deep brain stimulation for sleep stage targeting in Parkinson's disease}: intervention-oriented follow-up (ref.~12, PDF p.~12).
\item Gilron et al. (2021), \emph{Long-term wireless streaming of neural recordings for circuit discovery and adaptive stimulation in individuals with Parkinson's disease}: chronic sensing (ref.~28, PDF p.~12).
\end{itemize}'''),

dict(id=7, slug='neumann_2023_circuit_intervention',
title='Insights and opportunities for deep brain stimulation as a brain circuit intervention',
authors='Neumann, Horn and Kuehn', year='2023', kind='Review', doi='10.1016/j.tins.2023.03.009',
relation=r'''Measurement, stimulation targets, symptom mechanisms and feedback objectives. Connects local physiology with whole-network DBS effects.''',
findings=r'''\textbf{Measured and controlled.} The review connects unit activity, LFP oscillations, cortical signals and imaging with stimulation of neural circuits. DBS can change synchrony and symptoms through distributed pathways; the effect depends on anatomy and stimulation settings (PDF pp.~1--8).

\textbf{Usable insight.} Connectomic targeting and physiological feedback address complementary spatial and temporal aspects. Adaptive stimulation can use symptom-linked biomarkers, but the review explicitly leaves their causal role open. Physiological and pathological synchrony must be distinguished before selecting an objective (PDF pp.~5--6, 12).

\textbf{Model relevance.} Supports choosing measurement and actuation channels around an explicit symptom/network hypothesis. Tract correlations alone cannot establish whether a pathway is activated or inhibited, or the direction of propagation. The review supplies neither a single fitted delayed rate model nor a PIE multiplier construction (PDF pp.~8--12).''',
followups=r'''\begin{itemize}
\item Little et al. (2013), \emph{Adaptive deep brain stimulation in advanced Parkinson disease}: early biomarker-driven intervention (ref.~73, PDF p.~14).
\item Gradinaru et al. (2009), \emph{Optical deconstruction of parkinsonian neural circuitry}: pathway-specific causal interrogation (ref.~147, PDF p.~16).
\end{itemize}'''),

dict(id=8, slug='oswal_2021_hyperdirect_pathway',
title="Neural signatures of hyperdirect pathway activity in Parkinson's disease",
authors='Oswal et al.', year='2021', kind='Human recordings, tractography and modelling', doi='10.1038/s41467-021-25366-0',
relation=r'''Network measurements and possible origins of beta synchronization. Helps distinguish frequency bands and pathways rather than treating beta as one homogeneous signal.''',
findings=r'''\textbf{Measured.} STN/GPi recordings, MEG and tractography linked supplementary-motor-area--STN high-beta coherence (21--30~Hz) to hyperdirect fibre density. Directional analyses supported cortical drive at high beta; the corresponding relationship was absent for low beta (PDF pp.~1--7).

\textbf{Mechanism.} A coupled cortical/basal-ganglia model showed that enhanced high-beta hyperdirect input can provoke lower-beta subcortical synchronization. This is a model-based explanation supported by multimodal associations, not a selective clinical test proving that either band must be suppressed (PDF pp.~8--11).

\textbf{Model relevance.} Motivates adding cortical populations and hyperdirect coupling to an STN--GPe model. Transmission delays and time constants shape the simulated spectra. The full parameter set is referred to Supplementary Table~2; tract density and coherence should not be substituted directly for dynamical gains. The local main-article PDF alone does not supply a complete numerical notebook parameterization.''',
followups=r'''\begin{itemize}
\item Nevado Holgado, Terry and Bogacz (2010), \emph{Conditions for the generation of beta oscillations in the subthalamic nucleus--globus pallidus network}: delayed rate model (ref.~33, PDF p.~13).
\item Hammond, Bergman and Brown (2007), \emph{Pathological synchronization in Parkinson's disease: networks, models and treatments} (ref.~38, PDF p.~13).
\end{itemize}'''),

dict(id=9, slug='neumann_2023_dbs_mechanisms',
title='Neurophysiological mechanisms of deep brain stimulation across spatiotemporal resolutions',
authors='Neumann, Steiner and Milosevic', year='2023', kind='Review and physiological synthesis', doi='10.1093/brain/awad239',
relation=r'''What DBS acts on and what can be measured during stimulation. Useful for selecting a defensible actuator model and avoiding a universal excitation/inhibition assumption.''',
findings=r'''\textbf{Mechanisms.} Electrical stimulation recruits axons and propagates activity through circuits; local firing can nevertheless be suppressed. Synaptic depression and the balance of excitatory/inhibitory inputs depend on the target and stimulation frequency. Thus a local firing-rate effect does not characterize the entire network response (PDF pp.~2--7).

\textbf{Measurements and objective.} Unit activity, spontaneous LFP rhythms and evoked responses provide complementary observations. Beta suppression accompanies motor improvement in several cited studies, but its precise mechanistic role remains disputed. Evoked responses may also inform programming (PDF pp.~6--9).

\textbf{Model relevance.} A constant additive input is a simplification requiring validation. Frequency-dependent synaptic effects may require extra dynamic states or uncertain gains, rather than only a memoryless monotone nonlinearity. The review provides no unique numerical delayed-model parameterization and does not establish beta suppression as a sufficient clinical objective.''',
followups=r'''\begin{itemize}
\item Yu et al. (2020), \emph{Frequency-Specific optogenetic deep brain stimulation of subthalamic nucleus improves parkinsonian motor behaviors}: intervention evidence (ref.~44, PDF p.~11).
\item Steiner et al. (2019), \emph{Connectivity and dynamics underlying synaptic control of the subthalamic nucleus}: synaptic mechanisms (ref.~60, PDF p.~11).
\end{itemize}'''),

dict(id=10, slug='yin_2023_pallidal_beta_sleep',
title="Pathological pallidal beta activity in Parkinson's disease is sustained during sleep and associated with sleep disturbance",
authors='Yin et al.', year='2023', kind='Human overnight recordings; offline controller simulation', doi='10.1038/s41467-023-41128-6',
relation=r'''Measurement and sleep-related control objectives. Tests whether a waking motor biomarker can be interpreted the same way during sleep.''',
findings=r'''\textbf{Measured.} Pallidal LFPs were recorded alongside polysomnography in patients off dopaminergic medication, with a dystonia comparison group. Parkinsonian beta remained elevated during wakefulness, NREM and REM sleep and was associated with disturbed sleep (PDF pp.~1--7).

\textbf{Usable insight.} Offline adaptive-DBS simulations using waking beta thresholds produced sleep-dependent stimulation patterns. A controller calibrated during wakefulness can therefore misrepresent therapeutic demand during sleep. These simulations do not demonstrate improved or worsened sleep under an actual adaptive intervention (PDF pp.~7--9).

\textbf{Model relevance.} Supports including operating context and evaluating sleep outcomes separately from motor scores. The results are correlations; suppressing nocturnal beta is not established as a sufficient treatment. No delayed neural model is identified, and the target is pallidal: its biomarker behaviour should not automatically be assigned to STN recordings.''',
followups=r'''\begin{itemize}
\item Zahed et al. (2021), \emph{The neurophysiology of sleep in Parkinson's disease}: sleep mechanisms (ref.~1, PDF p.~10).
\item Yin et al. (2023), \emph{Pallidal activities during sleep and sleep decoding in dystonia, Huntington's, and Parkinson's disease}: decoding context (ref.~25, PDF p.~11).
\end{itemize}'''),

dict(id=11, slug='tan_2022_adaptive_dbs_freezing',
title='Towards adaptive deep brain stimulation for freezing of gait',
authors='Huiling Tan', year='2022', kind='Scientific commentary on Yin et al. (note 02)', doi='10.1093/brain/awac172',
relation=r'''Feedback-signal selection and the distinction between a predictive biomarker and a causal stimulation target, especially for freezing of gait.''',
findings=r'''\textbf{Argument.} The commentary discusses cortical beta--gamma PAC as a freezing-related signal and the finding that DBS can improve freezing beyond its effect on PAC. It contributes interpretation, not a new patient experiment (PDF pp.~1--3).

\textbf{Usable insight.} Statistical PAC can reflect nested oscillations or non-sinusoidal waveform shape. A PAC change should therefore not automatically be interpreted as altered interaction between two independent rhythms. Biomarker-triggered treatment and stimulation designed to directly disrupt a causal pathological process require different levels of mechanistic evidence (PDF pp.~1--3).

\textbf{Model relevance.} Useful criteria for choosing feedback: symptom relevance, reliable estimation and a justified treatment response. Freezing is the clinical outcome; PAC or beta suppression is a proposed intermediate mechanism to test. PAC estimation is not a linear state measurement, and the commentary gives no delayed-state parameterization or demonstrated PAC-driven controller.''',
followups=r'''\begin{itemize}
\item Yin et al. (2022), \emph{Cortical phase-amplitude coupling is key to the occurrence and treatment of freezing of gait}: underlying experiment (ref.~2, PDF p.~3).
\item Cole et al. (2017), \emph{Nonsinusoidal beta oscillations reflect cortical pathophysiology in Parkinson's disease}: PAC interpretation (ref.~3, PDF p.~3).
\end{itemize}'''),

dict(id=12, slug='liu_2018_graphene_closed_loop',
title='A Compact Closed-Loop Optogenetics System Based on Artifact-Free Transparent Graphene Electrodes',
authors='Liu et al.', year='2018', kind='Electrode and feedback-hardware validation', doi='10.3389/fnins.2018.00132',
relation=r'''Practical measurement during optogenetic stimulation and implementation latency. Relevant to the sensor/actuator interface, rather than the origin of neurological symptoms.''',
findings=r'''\textbf{Measured and controlled.} Transparent graphene electrodes reduced light-induced recording artifacts compared with gold electrodes under the tested conditions. A portable acquisition/microcontroller/LED system triggered light using a threshold detector (PDF pp.~2--10).

\textbf{Validation boundary.} Closed-loop tests used artificial electrical signals applied in saline, not demonstrated feedback regulation of an animal's neural activity. The reported approximately $40\,\mu\mathrm{s}$ processing response is a hardware-test result, not the total physiological sensor-to-neuron delay (PDF pp.~10--11).

\textbf{Model relevance.} Supports separating electrical sensing, signal processing and optical actuation. Residual artifacts and total loop delay should be characterized in the actual preparation. The equivalent circuit explains electrode artifacts; it is not a fitted neural-network model. Seizure-control applications discussed in the paper are proposed uses or prior work, so this paper does not establish beta suppression or another disease-specific control objective.''',
followups=r'''\begin{itemize}
\item Paz et al. (2013), \emph{Closed-loop optogenetic control of thalamus as a tool for interrupting seizures after cortical injury}: biological feedback validation (references, PDF p.~13).
\item Siegle and Wilson (2014), \emph{Enhancement of encoding and retrieval functions through theta phase-specific manipulation of hippocampus}: phase-dependent intervention (PDF p.~13).
\end{itemize}'''),

dict(id=13, slug='grosenick_2015_optogenetic_control',
title='Closed-Loop and Activity-Guided Optogenetic Control',
authors='Grosenick, Marshel and Deisseroth', year='2015', kind='Review of feedback, sensing and optical actuation', doi='10.1016/j.neuron.2015.03.034',
relation=r'''What can be measured and controlled optogenetically, and how to formulate an experiment-specific control objective and model.''',
findings=r'''\textbf{Framework.} Distinguishes feedback based on ongoing measurements from stimulation patterns chosen using earlier observations. Reviews electrical recordings, optical indicators and cell/projection-targeted light actuation, alongside on/off, PID, adaptive and predictive control approaches (PDF pp.~1--12).

\textbf{Usable insight.} The desired neural or behavioural trajectory determines sensor bandwidth, actuator choice and the meaning of successful control. Calcium signals do not necessarily resolve individual spike timing; opsin kinetics, saturation, targeting, heating and nonstationarity constrain achievable responses. Optogenetic actuation does not itself provide a neural measurement.

\textbf{Model relevance.} Supports system identification and explicit sensor/opsin dynamics before feedback design. A memoryless input map or time-invariant delayed rate model is a chosen approximation, not a property guaranteed by the technology. Examples include seizure interruption and manipulation of oscillations, but no universal beta-suppression objective or PIE Zames--Falb optimization is provided (PDF pp.~10--12, 24--26).''',
followups=r'''\begin{itemize}
\item Paz et al. (2013), \emph{Closed-loop optogenetic control of thalamus as a tool for interrupting seizures after cortical injury} (references, PDF p.~32).
\item Krook-Magnuson et al. (2014), \emph{Cerebellar directed optogenetic intervention inhibits spontaneous hippocampal seizures in a mouse model of temporal lobe epilepsy} (PDF p.~30).
\end{itemize}'''),

dict(id=14, slug='zaaimi_2023_primate_closed_loop',
title='Closed-loop optogenetic control of the dynamics of neural activity in non-human primates',
authors='Zaaimi et al.', year='2023 (online 2022)', kind='Mouse slices, anaesthetized primates and modelling', doi='10.1038/s41551-022-00945-8',
relation=r'''Direct evidence for feedback control of neural oscillations and seizure-like activity. Also supplies a concrete rate-model structure compatible with the notebook.''',
findings=r'''\textbf{Measured and controlled.} LFP-dependent, phase-shifted optical stimulation enhanced or attenuated oscillations and modulated chemically induced seizure-like bursts. The same excitatory actuator could have opposite network effects depending on feedback phase (PDF pp.~2--11).

\textbf{Objective.} The experiments target oscillatory dynamics and seizure-burst duration, not Parkinsonian beta or demonstrated clinical recovery. Phase and measurement filtering matter; reducing stimulation intensity alone does not describe the intervention.

\textbf{Model mapping.} Their two-population model is
\[
\dot E={-E+\sigma(aE-bI+S+P)\over\tau_e}+\eta_e,
\quad
\dot I={-I+\sigma(cE-dI+Q)\over\tau_i}+\eta_i.
\]
After equilibrium centring, take $x=(E,I)$, linear decay $(-1/\tau_e,-1/\tau_i)$, signed input rows $(a,-b)$ and $(c,-d)$, and $u=S$ inside the excitatory sigmoid. Intrinsic delays are zero. The logistic has slope at most $1/4$, so scaled nonlinearities have bounds $1/(4\tau_i)$. LFP filtering and the feedback FIR filter require additional dynamics; numerical parameters are in the separately referenced Supplementary Table~2 (PDF pp.~14--15).''',
followups=r'''\begin{itemize}
\item Nicholson et al. (2018), \emph{Analogue closed-loop optogenetic modulation of hippocampal pyramidal cells dissociates gamma frequency and amplitude} (ref.~8, PDF p.~15).
\item Wang et al. (2014), \emph{Dynamic mechanisms of neocortical focal seizure onset}: model background (ref.~15, PDF p.~15).
\end{itemize}'''),

dict(id=15, slug='kumari_2023_optogenetic_devices',
title='Electrophysiology-Based Closed Loop Optogenetic Brain Stimulation Devices: Recent Developments and Future Prospects',
authors='Kumari and Kouzani', year='2023 (online 2022)', kind='Methodological review', doi='10.1109/RBME.2022.3141369',
relation=r'''What can be recorded and optically actuated, and which hardware constraints belong in a realistic closed-loop model.''',
findings=r'''\textbf{Signal chain.} Reviews neural electrodes, acquisition electronics, feature extraction, classification, control logic and light-delivery circuitry. LFPs and action potentials provide electrical feedback; opsins translate optical stimulation into cellular effects (PDF pp.~1--7).

\textbf{Usable insight.} Sensor bandwidth, stimulation artifacts, processing latency, wireless power and tissue heating limit implementation. Threshold detection and PID are examples of controller approaches, not evidence that a particular controller is optimal for every circuit. A feature detector and a neural actuator should be represented as separate blocks (PDF pp.~8--15).

\textbf{Model relevance.} Helps specify admissible input intensity, sampling and delay, and identify observation noise/artifacts. It supplies an architecture and comparisons of existing devices, rather than one identified delayed population model. The reviewed applications have different outcomes, such as seizure detection/interruption; the review does not justify adopting beta suppression as a generic objective.''',
followups=r'''\begin{itemize}
\item Krook-Magnuson et al. (2013), \emph{On-demand optogenetic control of spontaneous seizures in temporal lobe epilepsy}: biological validation (ref.~98, PDF p.~18).
\item Xia et al. (2017), \emph{A low power flash-FPGA based brain implant micro-system of PID control}: embedded feedback implementation (ref.~102, PDF p.~18).
\end{itemize}'''),

dict(id=16, slug='deisseroth_2011_optogenetics',
title='Optogenetics', authors='Karl Deisseroth', year='2011', kind='Foundational perspective; author manuscript', doi='10.1038/nmeth.f.326',
relation=r'''What optogenetics can control and how selective perturbations can test causal circuit hypotheses. Provides terminology rather than a disease-specific feedback objective.''',
findings=r'''\textbf{Actuation.} Genetically targeted light-sensitive tools enable rapid excitation, inhibition and modulation of defined cells or projections. Tool choice changes temporal precision, light sensitivity and the duration of induced excitability changes (PDF pp.~1--5, 9).

\textbf{Measurement and causality.} Electrical recordings or optical readouts must separately establish the resulting neural activity. Selective interventions can test whether a cell class or projection contributes to a phenotype, whereas observing its activity alone cannot establish that contribution. The article also stresses that reliable targeting and validated opsin function matter (PDF pp.~2--6).

\textbf{Model relevance.} Supports selecting where $u$ enters a circuit and checking its sign and dynamics experimentally. It gives no unique light-to-firing gain, delay, sigmoid slope or measurement matrix for the notebook. Millisecond-scale capability should not be treated as a universal actuator time constant. No beta-suppression objective or PIE multiplier design follows from this perspective.''',
followups=r'''\begin{itemize}
\item Boyden et al. (2005), \emph{Millisecond-timescale, genetically targeted optical control of neural activity}: foundational neuronal actuation (ref.~4, PDF pp.~6--7).
\item Gradinaru et al. (2009), \emph{Optical deconstruction of parkinsonian neural circuitry}: circuit-specific Parkinsonian interventions (ref.~19, PDF p.~7).
\end{itemize}'''),

dict(id=17, slug='fenno_2011_optogenetics_development',
title='The Development and Application of Optogenetics',
authors='Fenno, Yizhar and Deisseroth', year='2011', kind='Review', doi='10.1146/annurev-neuro-061010-113817',
relation=r'''What optical stimulation can control, how targeting is achieved, and which actuator dynamics constrain a neural control model.''',
findings=r'''\textbf{Actuation.} Reviews excitatory channelrhodopsins, inhibitory pumps and light-sensitive signalling tools. Genetic and projection targeting allow selective manipulation; opsin kinetics and spectral sensitivity vary substantially across tools (PDF pp.~2--11).

\textbf{Usable insight.} Light input is filtered by expression, delivery and opsin physiology before affecting spikes or circuit activity. High-frequency stimulation fidelity, adaptation and recovery therefore need validation for the selected construct. Electrical or optical measurements are needed to verify the effect; the actuator is not itself a sensor (PDF pp.~7--16).

\textbf{Model relevance.} Helps choose actuator location, sign and bandwidth and motivates adding opsin states when a static gain is inadequate. It does not establish the notebook's monotone memoryless nonlinearity assumptions, numerical delayed coupling coefficients or an LFP observation map. Discussed behavioural interventions are application-specific; this review does not identify beta suppression as a general therapeutic objective.''',
followups=r'''\begin{itemize}
\item Boyden et al. (2005), \emph{Millisecond-timescale, genetically targeted optical control of neural activity}: optical excitation (references, PDF p.~19).
\item Gradinaru et al. (2009), \emph{Optical deconstruction of parkinsonian neural circuitry}: pathway-level intervention (PDF p.~20).
\end{itemize}'''),

dict(id=18, slug='kathe_2022_wireless_spinal_optogenetics',
title='Wireless closed-loop optogenetics across the entire dorsoventral spinal cord in mice',
authors='Kathe et al.', year='2022 (online 2021)', kind='Mouse spinal-circuit device and intervention study', doi='10.1038/s41587-021-01019-x',
relation=r'''Practical closed-loop measurement and control of motor circuits. Demonstrates behavioural and muscle outcomes outside the basal ganglia.''',
findings=r'''\textbf{Measured and controlled.} A stretchable epidural micro-LED implant and wireless headstage combine optical access to targeted spinal pathways with physiological recordings. EMG-based triggering enables stimulation at selected movement phases; experiments assess effects on locomotion and muscle activity (PDF pp.~1--10).

\textbf{Usable insight.} Phase-specific activation or silencing can produce distinct motor effects. The control objective is defined by locomotor function and circuit interrogation, not beta power. Extended Data Fig.~3 separates approximately 11.3~ms signal processing from 0.9~ms stimulus-delivery delay in a bench timing test (PDF p.~20).

\textbf{Model relevance.} EMG and movement measurements are plausible observed/performance outputs for a neuromuscular model, with explicit sensing and processing dynamics. They are not direct measurements of basal-ganglia population rates. The paper provides no STN--GPe parameterization; its hardware timing and actuator gains cannot be transferred unchanged to DBS or another optogenetic preparation.''',
followups=r'''\begin{itemize}
\item Montgomery et al. (2015), \emph{Wirelessly powered, fully internal optogenetics for brain, spinal and peripheral circuits in mice}: wireless actuation (ref.~6, PDF p.~11).
\item Capogrosso et al. (2018), \emph{Configuration of electrical spinal cord stimulation through real-time processing of gait kinematics}: feedback implementation (ref.~40, PDF p.~14).
\end{itemize}'''),

dict(id=19, slug='de_la_crompe_2025_stn_gpe_reassessment',
title='Reevaluating the role of the STN-GPe network in generating beta synchronized oscillatory activity in parkinsonism',
authors='De la Crompe, Deffains, Leblois and Mallet', year='2025', kind="Handbook of Parkinson's Disease Mechanisms, chapter 17", doi='10.1016/B978-0-443-21992-4.00013-0',
relation=r'''Origins of pathological synchronization and which circuit components should be modelled. Critically reassesses a homogeneous STN--GPe pacemaker hypothesis.''',
findings=r'''\textbf{Evidence.} Synthesizes recordings and selective optogenetic perturbations, including distinctions between prototypic and arkypallidal GPe neurons. In the reviewed parkinsonian-rat experiments, GPe inhibition disrupted beta synchronization whereas STN or motor-cortex inhibition did not (PDF pp.~4--8).

\textbf{Usable insight.} Pallidostriatal interactions and population-specific connectivity can explain patterns missed by a two-population loop. Species and preparation matter. Motor deficits can precede exaggerated beta, so the chapter does not equate the origin of synchronization with the sole cause of neurological symptoms (PDF pp.~1, 8--10).

\textbf{Model relevance.} Motivates separating GPe populations and including striatal feedback when the experimental setting requires them. It supplies structural constraints and competing mechanisms, rather than one numerical notebook parameterization. A defensible control objective needs behavioural evidence in addition to a change in beta power.''',
followups=r'''\begin{itemize}
\item De la Crompe et al. (2020), \emph{The globus pallidus orchestrates abnormal network dynamics in a model of Parkinsonism}: causal perturbation evidence (cited in Figs.~17.4--17.5, PDF pp.~7--8).
\item Azizpour Lindi, Mallet and Leblois (2024), \emph{Synaptic Changes in Pallidostriatal Circuits\ldots}: constrained alternative circuit model (ref.~48, PDF p.~12; note~20).
\end{itemize}'''),

dict(id=20, slug='azizpour_lindi_2024_pallidostriatal_synchrony',
title='Synaptic Changes in Pallidostriatal Circuits Observed in the Parkinsonian Model Triggers Abnormal Beta Synchrony with Accurate Spatio-temporal Properties across the Basal Ganglia',
authors='Azizpour Lindi, Mallet and Leblois', year='2024', kind='Experimentally constrained rate and spiking models', doi='10.1523/JNEUROSCI.0419-23.2023',
relation=r'''Mechanisms of beta synchronization and model structure. Tests whether experimentally constrained loops reproduce both frequency and relative spike timing.''',
findings=r'''\textbf{Finding.} The model includes STN, prototypic/arkypallidal GPe, striatal fast-spiking interneurons and D2 medium spiny neurons. Strong STN--GPe or intra-GPe feedback favours gamma; pallidostriatal loops favour lower beta. Combined synaptic changes reproduce parkinsonian beta and phase relationships (PDF pp.~1--5, 8--16).

\textbf{Usable insight.} In model perturbations, GPe inhibition abolishes oscillations whereas STN inhibition does not, matching cited rat experiments. Reproducing phase relationships is an additional model-validation criterion beyond matching a spectral peak. These results explain synchronization, not a demonstrated clinical benefit of suppressing it.

\textbf{Model relevance.} The rate approximation uses delayed, synaptically filtered interactions and threshold-linear activation; synaptic time constants differ by projection. The notebook can represent an augmented rate approximation with extra filter states, but the spiking model is not exactly its memoryless rate equation. Connectivity, membrane, synaptic and delay parameters are tabulated in Methods (PDF pp.~3--6). A new reduction and validated observation/actuator maps are needed.''',
followups=r'''\begin{itemize}
\item De la Crompe et al. (2020), \emph{The globus pallidus orchestrates abnormal network dynamics in a model of parkinsonism}: perturbation constraints (PDF p.~18).
\item Corbit et al. (2016), \emph{Pallidostriatal projections promote beta oscillations in a dopamine-depleted biophysical network model}: related loop hypothesis (PDF p.~18).
\end{itemize}'''),

dict(id=21, slug='ortone_2023_basal_ganglia_loops',
title='Dopamine depletion leads to pathological synchronization of distinct basal ganglia loops in the beta band',
authors='Ortone et al.', year='2023', kind='Spiking-network modelling study', doi='10.1371/journal.pcbi.1010645',
relation=r'''Possible network mechanisms of beta synchronization and the limitations of an isolated STN--GPe model.''',
findings=r'''\textbf{Finding.} Interacting STN--GPe and striatal--GPe loops show beta-range resonances. In simulations, dopamine depletion strengthens the striatal loop and promotes synchronization between loops that are more independent at high dopamine levels (PDF pp.~1--4, Results).

\textbf{Usable insight.} The source of a shared spectral peak can depend on interactions between circuits and dopamine-dependent coupling. Network interventions should therefore be evaluated across mechanisms and operating conditions. The paper establishes a computational explanation of synchronization; it does not demonstrate that minimizing beta improves patients' motor function.

\textbf{Model relevance.} Six populations are included: D1/D2 medium spiny neurons, fast-spiking interneurons, two GPe populations and STN. Individual neurons have adaptation, conductance dynamics and reset events. These equations are not exactly the notebook's memoryless monotone rate model. Tables~2--3 give biophysical parameters and projection delays; they require a justified population reduction before becoming rate-model coefficients (PDF pp.~4--7).''',
followups=r'''\begin{itemize}
\item De la Crompe et al. (2020), \emph{The globus pallidus orchestrates abnormal network dynamics in a model of Parkinsonism}: experimental constraint (ref.~49, PDF p.~28).
\item Corbit et al. (2016), \emph{Pallidostriatal projections promote beta oscillations in a dopamine-depleted biophysical network model}: striatal-loop comparison (ref.~57, PDF pp.~28--29).
\end{itemize}'''),

dict(id=22, slug='koeglsperger_2026_adaptive_dbs_roadblocks',
title="Adaptive Deep Brain Stimulation for Parkinson's Disease: Navigating the Roadblocks to Clinical Implementation",
authors='Koeglsperger et al.', year='2026', kind='Gaps and controversy review', doi='10.1002/mds.70284',
relation=r'''Choosing feedback measurements, clinically meaningful objectives and feasible adaptive control policies. Summarizes practical limitations of biomarker-based DBS.''',
findings=r'''\textbf{Measurements and control.} Reviews LFP beta, gamma, PAC and peripheral measures, alongside single- and dual-threshold stimulation policies. Beta is useful particularly for rigidity/bradykinesia, but is not expressed reliably in every patient and represents other symptoms less well (PDF pp.~2--6).

\textbf{Usable insight.} Thresholds, ramp rates, response latency, artifacts, medication and behavioural state affect controller performance. Stimulation bounds must accommodate clinical benefit and side effects. Reduced stimulation does not automatically imply lower total energy use once sensing and processing are included (PDF pp.~3--9).

\textbf{Objective and model relevance.} Supports symptom-specific clinical outcomes, function and tolerability, with biomarkers as imperfect feedback surrogates. It does not establish indiscriminate beta suppression as the treatment goal. Provides implementation constraints and policy comparisons rather than identified delayed neural equations or an optimal model-based controller. Patient variability motivates uncertainty analysis rather than universal gains.''',
followups=r'''\begin{itemize}
\item Neumann et al. (2023), \emph{Adaptive deep brain stimulation: from experimental evidence toward practical implementation}: translation overview (ref.~14, PDF p.~10).
\item Little and Brown (2012), \emph{What brain signals are suitable for feedback control of deep brain stimulation in Parkinson's disease?}: feedback criteria (ref.~45, PDF p.~11).
\end{itemize}'''),

dict(id=23, slug='nevado_holgado_2010_delayed_stn_gpe',
title='Conditions for the Generation of Beta Oscillations in the Subthalamic Nucleus-Globus Pallidus Network',
authors='Nevado Holgado, Terry and Bogacz', year='2010', kind='Delayed population-rate modelling study', doi='10.1523/JNEUROSCI.0817-10.2010',
relation=r'''A concrete delayed nonlinear model and conditions for oscillation generation. Relevant to the notebook's model class; its mechanistic predictions require separate behavioural validation.''',
findings=r'''\textbf{Model mapping.} With rates $r_S,r_G$ and constant cortical/striatal drives,
\[
\begin{aligned}
\tau_S\dot r_S&=-r_S+F_S(-w_{GS}r_G(t-T_{GS})+w_{CS}\mathrm{Ctx}),\\
\tau_G\dot r_G&=-r_G+F_G(w_{SG}r_S(t-T_{SG})-w_{GG}r_G(t-T_{GG})-w_{XG}\mathrm{Str}).
\end{aligned}
\]
Take $x=r-r^*$, $a_i=-1/\tau_i$, $b^x=0$, and signed nonlinear input rows $(0,-w_{GS})$, $(w_{SG},-w_{GG})$. Set $f_i(v)=[F_i(q_i^*+v)-F_i(q_i^*)]/\tau_i$. The reported sigmoid has $0\leq F_i'\leq1$, giving global slope and sector bounds $[0,1/\tau_i]$ after centring (derived from their Eq.~3).

\textbf{Parameters.} $\tau_S=6$, $\tau_G=14$, $T_{SG}=T_{GS}=6$, $T_{GG}=4$ in ms. With $F_i(q)=M_i/[1+e^{-4q/M_i}(M_i-B_i)/B_i]$, use $(M_S,B_S,M_G,B_G)=(300,17,400,75)$ and $(\mathrm{Ctx},\mathrm{Str})=(27,2)$ in spikes/s. The weight vector $(w_{SG},w_{GS},w_{GG},w_{CS},w_{XG})$ is $(19,1.12,6.60,2.42,15.1)$ for the healthy fit and $(20,10.7,12.3,9.2,139.4)$ for the diseased fit (Tables~1, 3; PDF pp.~2--4). Their pulse experiments use a fitted additive electrode-current term in the STN equation (Eq.~5); no LFP observation map is identified.

\textbf{Interpretation.} Delays, coupling and external drive determine oscillation onset within this model. Predictions about removing beta are model-level results, not proof that beta suppression alone treats symptoms (PDF pp.~5--12).''',
followups=r'''\begin{itemize}
\item Plenz and Kitai (1999), \emph{A basal ganglia pacemaker formed by the subthalamic nucleus and external globus pallidus}: experimental loop hypothesis (PDF p.~13).
\item Terman et al. (2002), \emph{Activity patterns in a model for the subthalamopallidal network of the basal ganglia}: alternative spiking mechanism (PDF p.~13).
\end{itemize}'''),
]

def escape(value):
    return ''.join({'&':r'\&', '%':r'\%', '_':r'\_', '#':r'\#'}.get(c,c) for c in value)

def generate():
    OUT.mkdir(exist_ok=True)
    (OUT/'build').mkdir(exist_ok=True)
    preamble = r'''\documentclass[10pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage[margin=21mm]{geometry}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\setlist[itemize]{leftmargin=*,nosep,topsep=3pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{3em}
\newcommand{\question}[1]{\par\medskip{\normalsize\bfseries #1}\par\smallskip}
\pagestyle{plain}
'''
    (OUT/'notes_preamble.tex').write_text(preamble,encoding='utf-8')
    records=[]
    for note in NOTES:
        item=next(x for x in INVENTORY if x['id']==note['id'])
        name=f"{note['id']:02d}_{note['slug']}"
        note['filename']=name
        source=Path(item['source']).as_posix()
        tex=r'\input{notes_preamble.tex}'+'\n'+r'\begin{document}'+'\n'
        tex+=r'{\Large\bfseries '+escape(note['title'])+r'\par}'+'\n\n'
        tex+=r'\textbf{Paper:} '+escape(note['authors'])+' ('+escape(note['year'])+r').\quad '+escape(note['kind'])+r'.\par'+'\n'
        tex+=r'\href{https://doi.org/'+note['doi']+r'}{DOI: \nolinkurl{'+note['doi']+r'}}\par'+'\n'
        tex+=r'{\footnotesize Page references below use PDF page numbers, including front matter.}'+'\n\n'
        for question,key in [
            ('To which general question does this paper relate?','relation'),
            ('How does it answer the general questions?','findings'),
            ('What papers does it cite that could provide more information?','followups')]:
            tex+=r'\question{'+question+'}\n'+note[key]+'\n\n'
        tex+=r'\end{document}'+'\n'
        (OUT/f'{name}.tex').write_text(tex,encoding='utf-8')
        records.append({'id':note['id'],'title':note['title'],'authors':note['authors'],'year':note['year'],
                        'source':source,'sha256':item['sha256'],'pdf_pages':item['pages'],
                        'notes':f'{name}.tex','compiled':f'build/{name}.pdf','doi':note['doi']})
    (OUT/'sources.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lines=['# Paper notes','',
        'Concise notes for every PDF currently in this workspace\'s `References` folder. Each paper has a standalone LaTeX file and a compiled PDF answering the three questions in `literature_review.tex`.','',
        'Notes are based on the reference PDFs themselves. They do not use the PNAS manuscript or `main.tex` as a source or assume that beta suppression is the clinical objective. Reported findings, modelling predictions and proposed mappings to the notebook model are distinguished. Page citations refer to **PDF pages**, including front matter; cited follow-ups are selected from each paper\'s own references.','',
        'Files 04 and 05 are the published paper and preprint of the same study; retain both notes for the source files but count the experiment once. The collection contains 23 PDFs (22 distinct works). None of these references directly develops the PIE Zames–Falb multiplier parameterization.','',
        '| # | Paper | Notes | Source |','|---|---|---|---|']
    for rec in records:
        name=Path(rec['notes']).stem
        source_link=quote('../../'+rec['source'],safe='/')
        lines.append(f"| {rec['id']:02d} | {rec['authors']} ({rec['year']}): {rec['title']} | [TeX]({rec['notes']}) · [PDF]({rec['compiled']}) | [Original]({source_link}) |")
    lines+=['','Build all notes from this directory:', '', '```powershell', 'python build_notes.py', '```','',
        'Or build one note (run from this directory):','', '```powershell',
        'latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build 01_chikermane_2024_cortical_beta.tex','```','',
        'Open PDFs in `Paper_Notes/build/`; the TeX files share `notes_preamble.tex`. `sources.json` records the exact source paths and SHA-256 hashes for coverage checks.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Created {len(records)} paper notes and index in {OUT}')

if __name__=='__main__':
    generate()
