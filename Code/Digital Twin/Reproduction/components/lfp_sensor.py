"""Bipolar STN LFP acquisition from the paper's two recording contacts."""
import math
import numpy as np
from .base import Sensor


class BipolarLFPSensor(Sensor):
    units = "mV"

    def __init__(self, contact_1=(0, -1500, 250), contact_2=(0, 1500, 250),
                 conductivity_s_m=0.27):
        self.contact_1, self.contact_2 = contact_1, contact_2
        self.conductivity = conductivity_s_m
        self.lfp = np.array([], dtype=float)
        self.ampa = np.array([], dtype=float)
        self.gabaa = np.array([], dtype=float)
        self.time_ms = np.array([], dtype=float)
        self.time_cursor = 0

    def bind(self, model):
        from Electrode_Distances import distances_to_electrode
        self.population = model.stn
        self.distance_1 = distances_to_electrode(np.array(self.contact_1), self.population)
        self.distance_2 = distances_to_electrode(np.array(self.contact_2), self.population)

    def potential(self, currents, distance):
        # nA and micrometres -> mV; preserve the source expression's arithmetic.
        return ((1 / (4 * math.pi * self.conductivity))
                * np.sum((1 / (distance * 1e-6)) * currents.transpose(), axis=0) * 1e-6)

    def bipolar(self, currents):
        return self.potential(currents, self.distance_1) - self.potential(currents, self.distance_2)

    def read(self):
        ampa = np.array(self.population.get_data("AMPA.i").segments[0].analogsignals[0])
        gabaa = np.array(self.population.get_data("GABAa.i").segments[0].analogsignals[0])
        values = self.bipolar(ampa + gabaa)
        self.lfp = np.hstack((self.lfp, values))
        self.ampa = np.hstack((self.ampa, self.bipolar(ampa)))
        self.gabaa = np.hstack((self.gabaa, self.bipolar(gabaa)))
        # Preserve the legacy recorder's duplicated chunk-endpoint convention.
        times = self.population[0]._cell.record_times.as_numpy()
        new_times = times[self.time_cursor:].copy()
        self.time_cursor = len(times)
        if len(new_times) < len(values):
            new_times = np.pad(new_times, (0, len(values)-len(new_times)), mode="edge")
        self.time_ms = np.hstack((self.time_ms, new_times[-len(values):]))
        return values

    def clear(self):
        self.population.get_data("soma(0.5).v", clear=True)

    def signals(self):
        return {"lfp_mv": self.lfp, "lfp_time_ms": self.time_ms,
                "lfp_ampa_mv": self.ampa, "lfp_gabaa_mv": self.gabaa}
