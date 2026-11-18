MODEL FILES

python/             Supplied model scripts, neuron classes, and controllers
mechanisms/         NEURON NMODL mechanism sources
data/bursts/        Ten paired cortical burst input schedules
data/connectivity/ Network connection lists
data/geometry/     Neuron positions and electrode distances
data/               Striatal spike times and GPe recruitment order
pynn_patches/       Authors' supplied PyNN source patches

nrnmech.dll         Compiled mechanisms; retained here for NEURON loading
steady_state.bin    Saved warmup; created here and reused by the trials

Run the configured simulation from the parent Reproduction directory with
run_comparison.cmd or start_dashboard.cmd.
The original readme.html describes the authors' flat source distribution.
Current hashes and source changes are in ../docs/manifest.json and
../docs/compatibility.patch. The equations and numerical input values are retained.
