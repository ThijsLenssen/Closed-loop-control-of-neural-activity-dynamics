"""Adapter for the paper's supplied conductance-based network construction."""
from pathlib import Path
import numpy as np
from .base import NeuralModel


class CBGModel(NeuralModel):
    def __init__(self, directory, seed=3695, secondorder=0, warmup_ms=6000.0,
                 runtime_ms=32000.0, trial_noise_seed=None):
        self.directory = Path(directory).resolve()
        self.seed, self.secondorder = seed, secondorder
        self.trial_noise_seed = trial_noise_seed
        self.warmup_ms, self.runtime_ms = warmup_ms, runtime_ms
        self.dt = 0.01
        self.sampling_interval_ms = 0.5
        self.stop_ms = warmup_ms + runtime_ms + self.dt
        self.source = ""

    def load_native(self):
        import os
        import sys
        from neuron import h
        os.chdir(self.directory)
        sys.path.insert(0, str(self.directory / "python"))
        self.h = h
        h.CVode().cache_efficient(0)
        h.ParallelContext().nthread(1)
        h.secondorder = self.secondorder
        if not hasattr(h, "is_xtra"):
            h.nrn_load_dll(str(self.directory / "nrnmech.dll"))
        np.random.seed(self.seed)

    def script(self, filename):
        source = (self.directory / "python" / filename).read_text(encoding="utf-8-sig")
        source = source.replace("steady_state_duration = 6000.0",
                                "steady_state_duration = " + repr(self.warmup_ms))
        source = source.replace("simulation_runtime = 32000.0",
                                "simulation_runtime = " + repr(self.runtime_ms))
        return source

    def namespace(self, filename):
        return {"__name__": "__main__", "__file__": str(self.directory/"python"/filename),
                "REPRO_SEED": self.seed}

    def network_source(self):
        filename = "run_CBG_Model_Amplitude_Modulation_Controller.py"
        source = self.script(filename)
        # Keep the original network topology, cells, drives, and recorder setup.
        # Device geometry and feedback operations are supplied by separate components.
        source = source.split("\t# Conductivity and resistivity values")[0]
        begin = source.index("\t# Assign Positions for recording and stimulating electrode")
        end = source.index("\t# Synaptic Connections", begin)
        source = source[:begin] + source[end:]
        return source

    def prepare(self):
        self.load_native()
        filename = "run_CBG_Model_Amplitude_Modulation_Controller.py"
        source = self.network_source()
        self.source = source
        self.scope = self.namespace(filename)
        exec(compile(source, self.scope["__file__"], "exec"), self.scope)
        self.simulator = self.scope["simulator"]
        self.stn = self.scope["STN_Pop"]
        self.cortex = self.scope["Cortical_Pop"]
        self.gpe_clamps = self.scope["GV"].GPe_stimulation_iclamps
        self.population_size = self.scope["Pop_size"]

    @property
    def time_ms(self):
        return float(self.h.t)

    def restore(self):
        if not (self.directory/"steady_state.bin").is_file():
            raise FileNotFoundError("Run the common warmup first.")
        # Preserve the existing trial runner's default native-noise realization.
        if self.trial_noise_seed is not None:
            self.cortex[0]._cell.noise.seed(self.trial_noise_seed)
        self.scope["run_until"](self.warmup_ms + self.dt, run_from_steady_state=True)
        for i in range(self.population_size):
            self.scope["Striatal_Pop"][i].spike_times = self.scope["striatal_spike_times"][i][0]
        print("RESTORED_MS", self.time_ms, flush=True)

    def advance(self, time_ms):
        self.scope["run_until"](time_ms - self.dt)

    def close(self):
        if hasattr(self, "scope") and "end" in self.scope:
            self.scope["end"]()

    def warmup_source(self):
        """Keep the existing warmup/SaveState protocol and its state-file location."""
        filename = "run_CBG_Model_to_SS.py"
        source = self.script(filename).split("\t# Calculate the LFP and biomarkers")[0]
        source = source.replace("\t# Initialise STN LFP list",
            "\tCortical_Pop[0]._cell.noise.seed(REPRO_SEED)\n\t# Initialise STN LFP list")
        replacement = """
\tsimulator.state._update_current_sources(steady_state_duration)
\tsimulator.state._pre_run()
\tsimulator.state.parallel_context.set_maxstep(simulator.state.default_maxstep)
\tsimulator.state.tstop = steady_state_duration
\t_stops = np.arange(100.0, steady_state_duration+0.1, 100.0)
\tif not len(_stops) or _stops[-1] < steady_state_duration:
\t\t_stops = np.append(_stops, steady_state_duration)
\tfor _stop in _stops:
\t\tsimulator.state.parallel_context.psolve(float(_stop))
\t\tprint('WARMUP_MS', float(h.t), flush=True)
\t_sv = h.SaveState()
\t_sv.save()
\t_sf = h.File('steady_state.bin')
\t_sv.fwrite(_sf)
"""
        source = source.replace("\trun_to_steady_state(steady_state_duration)", replacement)
        source += "\n\tprint('WARMUP_COMPLETE', flush=True)\n\tend()\n"
        return filename, source

    def run_warmup(self, source):
        self.load_native()
        namespace = self.namespace("run_CBG_Model_to_SS.py")
        exec(compile(source, namespace["__file__"], "exec"), namespace)
