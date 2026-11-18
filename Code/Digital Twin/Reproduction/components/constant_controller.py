"""Constant command; zero reproduces the DBS-off comparison."""
from .base import Controller


class ConstantController(Controller):
    def __init__(self, command=0.0, target=1.0414e-4, period_ms=20.0,
                 minimum=0.0, maximum=3.0):
        super().__init__(target)
        self.command, self.period_ms = command, period_ms
        self.minimum, self.maximum = minimum, maximum

    def update(self, measurement, time_ms):
        error = ((measurement - self.target) / self.target
                 if self.target != 0 else measurement - self.target)
        command = min(self.maximum, max(self.minimum, self.command))
        return self.remember(measurement, error, command, time_ms)
