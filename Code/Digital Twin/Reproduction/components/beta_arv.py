"""Figure 1C: beta bandpass, rectification, and averaging."""
import numpy as np
from scipy import signal
from .base import Biomarker


class BetaARV(Biomarker):
    input_units = output_units = "mV"

    def __init__(self, sampling_interval_ms=0.5, history_ms=2000.0, tail_ms=100.0):
        self.history_ms = history_ms
        self.window_samples = int(history_ms / sampling_interval_ms)
        self.tail_samples = int(tail_ms / sampling_interval_ms)
        nyquist = 0.5 * 1000 / sampling_interval_ms
        self.b, self.a = signal.cheby1(4, 0.5, [21 / nyquist, 29 / nyquist], "band")
        self.history = np.array([], dtype=float)

    def update(self, samples):
        self.history = np.hstack((self.history, samples))
        window = self.history[-self.window_samples:]
        filtered = signal.filtfilt(self.b, self.a, window)
        return np.mean(np.absolute(filtered)[-2*self.tail_samples:-self.tail_samples])
