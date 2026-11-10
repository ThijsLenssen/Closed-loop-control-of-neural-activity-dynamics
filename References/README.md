# References

Papers are grouped by stimulation modality, with shared modeling and control methods in a separate folder.

```text
References/
  optogenetics/
    actuators/
    sensors/
    applications/
  deep brain stimulation/
  modeling and control/
    modeling/
      basal ganglia/
    control/
    control objectives/
    Neural Control Engineering/
  parkinsons/
```

- **[optogenetics](optogenetics/)**: optical stimulation and recording, opsin kinetics, devices, reviews, and experimental applications. The `applications` folder contains the parvalbumin/gamma-rhythm study.
- **[deep brain stimulation](deep%20brain%20stimulation/)**: DBS mechanisms, clinical applications, adaptive stimulation, and associated electrophysiological biomarkers. Includes the Koeglsperger adaptive DBS review previously filed under Parkinson's disease.
- **[modeling and control](modeling%20and%20control/)**: approaches useful across stimulation modalities. `modeling` contains the control-oriented dynamical-model review and state-space modeling paper; `basal ganglia` contains the Azizpour Lindi, Ortone, and Nevado Holgado network models. `control` contains optimal spike-timing control, decoder design and adaptation, microcircuit feedback, state-space optimal feedback, and phase control. `control objectives` contains the general neural-synchrony review. The complete *Neural Control Engineering* collection is kept together with its scripts and manifests.
- **[parkinsons](parkinsons/)**: disease and circuit background, currently the review reassessing the STN-GPe explanation of beta oscillations.

Some papers in the shared control folder demonstrate their methods using optogenetics. Their placement reflects the reusable control approach; sensor and actuator models still depend on the chosen modality.

Original PDF filenames are preserved. The paper-note index and source register are in [Paper Notes](../Literature_Review/Paper_Notes/README.md).
