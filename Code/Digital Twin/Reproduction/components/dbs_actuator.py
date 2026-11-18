"""Monopolar DBS field plus the supplied amplitude-dependent GPe recruitment."""
import math
import numpy as np
from scipy import signal
from .base import Actuator


def pulse_segment(start_ms, stop_ms, dt_ms, amplitude, frequency_hz=130.0,
                  pulse_width_ms=0.06):
    """Retain the source waveform phase, rounding, and next-pulse calculation."""
    times = np.round(np.arange(start_ms, stop_ms, dt_ms), 2)
    elapsed_s = np.arange(0, stop_ms-start_ms, dt_ms) / 1000.0
    period_ms = (1.0 / frequency_hz) * 1000.0
    duty = pulse_width_ms / period_ms
    wave = (1.0 + signal.square(2.0*np.pi*frequency_hz*elapsed_s, duty=duty)) / 2.0
    wave[-1] = 0.0
    last_falling = np.where(np.diff(wave) < 0)[0][-1]
    next_pulse = times[last_falling] + period_ms - pulse_width_ms
    wave *= amplitude
    return wave, times, next_pulse


class DBSActuator(Actuator):
    command_units = "mA"

    def __init__(self, electrode=(0, 0, 250), conductivity_s_m=0.27):
        self.electrode = electrode
        self.conductivity = conductivity_s_m
        self.callbacks = []

    def bind(self, model, control_times_ms):
        from Electrode_Distances import collateral_distances_to_electrode
        from pyNN.parameters import Sequence
        self.model, self.h = model, model.h
        distances = collateral_distances_to_electrode(
            np.array(self.electrode), model.cortex, L=500, nseg=11)
        rho = 1 / (self.conductivity * 1e-2)
        rx = (rho / (4*math.pi)) * (1 / distances) * 0.01
        for i, cell in enumerate(model.cortex):
            cell.collateral_rx = Sequence(rx[i, :].flatten())
        wave, times, _ = pulse_segment(
            model.warmup_ms+10+model.dt, model.stop_ms, model.dt, -1.0)
        wave = np.hstack((np.array([0, 0]), wave))
        self.times = np.hstack((np.array([0, model.warmup_ms+10]), times))
        wave[:] = 0
        self.next_pulse = control_times_ms[0]
        self.wave_vector = self.h.Vector(wave)
        self.time_vector = self.h.Vector(self.times)
        self.wave_vector.play(self.h._ref_is_xtra, self.time_vector, 1)
        self.values = self.wave_vector.as_numpy()
        # One shared GPe waveform; each IClamp retains its individual enable gate.
        self.gpe_vector = self.h.Vector(wave)
        self.gpe_times = self.h.Vector(self.times)
        self.gpe_values = self.gpe_vector.as_numpy()
        for clamp in model.gpe_clamps[:model.population_size]:
            self.gpe_vector.play(clamp._ref_amp, self.gpe_times, 1)
            clamp.dur = 0.0
        path = model.directory / "data/GPe_Stimulation_Order.txt"
        self.order = [int(i) for i in np.loadtxt(path, delimiter=",")]
        self.amplitudes = np.array([0,.25,.5,.75,1,1.25,1.5,1.75,2,2.25,2.5,3,4,5])
        self.entrained = np.array([0,0,0,1,4,8,19,30,43,59,82,100,100,100])

    def apply(self, command, next_control_time_ms):
        if self.next_pulse >= next_control_time_ms:
            return
        pulse_start = self.next_pulse
        wave, times, self.next_pulse = pulse_segment(
            pulse_start, next_control_time_ms, self.model.dt, -command)
        start = np.where(self.times == times[0])[0][0]
        self.values[start:start+len(wave)] = wave
        count = int(np.interp(command, self.amplitudes, self.entrained))
        gpe_wave = wave.copy()
        gpe_wave *= -1
        gpe_wave[gpe_wave > 0] = 100
        self.gpe_values[start:start+len(wave)] = gpe_wave

        def gates(n=count):
            for rank, cell_index in enumerate(self.order):
                self.model.gpe_clamps[cell_index].dur = 1e12 if rank < n else 0.0

        self.callbacks.append(gates)
        gate_time = float(pulse_start) - self.model.dt
        if gate_time <= self.h.t + 1e-9:
            gates()
        else:
            self.h.CVode().event(gate_time, gates)

    def signals(self):
        return {"dbs_ma": np.asarray(self.values), "dbs_time_ms": self.times}
