Thread-safe mechanism variants — validated on NEURON 8.2.7+

SynNoiseTS.mod replaces the shared normrand/set_seed generator with a
private Random123 stream per mechanism. Bind it with bind_noise() and
retain the returned h.Random object for the whole simulation.
No Random object may be shared between worker threads.

Important: NEURON normrand(mean,variance) takes a variance. The legacy
parameter named "std" is passed as that variance, so the new mechanism
uses sqrt(std)*standard_normal. It preserves the noise distribution but
changes the realization relative to the original global RNG.

xtra_ts.mod replaces the shared GLOBAL stimulation value with a RANGE
stimulus value. The im/ex POINTER targets must belong to the same cell.
threadsafe_support.play_stimulus() attaches Vector.play to an owning
point process on each cell, so playback follows that cell's worker.

Validation: validate_threads.py ran 12 passive cells for 100 ms at
0.01 ms with 1, 2, and 4 real worker threads. Currents, membrane voltages,
and stimulation traces were bit-for-bit identical. Noise variance was
0.2000207 nA^2 against an expected 0.2; maximum pairwise correlation
was 0.02299. See validation_summary.json (including per-thread statistics).

Use fixed-step record(ref) when recording at every integration step.
The explicit timed record(ref, dt) path in this legacy runtime produced
incorrect secondary-thread recordings even with owner arguments, and
was rejected by the cross-thread checks.

These components DO NOT remove NEURON's full-network restriction:
extracellular() is unsupported with multiple threads in this backend.
require_supported_full_network_threads() rejects that configuration
before a native solver call. The original paper model remains intact.
The reproduction runner continues to use one thread per independent
process. Its DBS-off and PI processes can run concurrently.

Integrating the opt-in variants into a compatible model requires:
  * SynNoiseTS instead of SynNoise; bind a unique stream for every cell
    with a noise source, including cortex, interneurons and thalamus.
  * xtra_ts instead of xtra, and updated local im/ex pointer bindings.
  * play_stimulus() instead of writing h._ref_is_xtra.
  * A solver/model formulation supporting the desired parallel mode.
Do not force THREADSAFE on legacy code or enable cache reordering.

To repeat the isolated validation, from this directory use:
  ..\..\runtime\neuron827\bin\python.exe validate_threads.py --threads 1
  ..\..\runtime\neuron827\bin\python.exe validate_threads.py --threads 2
  ..\..\runtime\neuron827\bin\python.exe validate_threads.py --threads 4

The precompiled Windows DLL is included. Recompile
against another NEURON version before loading it into that version.

