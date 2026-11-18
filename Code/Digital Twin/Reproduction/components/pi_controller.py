"""The supplied PI algorithm, including its normalization and anti-windup."""
from .base import Controller


class PIController(Controller):
    def __init__(self, target=1.0414e-4, kp=0.23, ti_s=0.2,
                 period_ms=20.0, minimum=0.0, maximum=3.0):
        super().__init__(target)
        self.kp, self.ti_s = kp, ti_s
        self.period_ms = period_ms
        self.minimum, self.maximum = minimum, maximum
        self.integral = 0.0
        self.last_error = 0.0

    def update(self, measurement, time_ms):
        error = ((measurement - self.target) / self.target
                 if self.target != 0 else measurement - self.target)
        dt = self.period_ms / 1000.0
        self.integral += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        self.last_error = error
        # Retain the arithmetic order of the authors' PID with Td=0.
        try:
            command = self.kp * (error + ((1.0 / self.ti_s) * self.integral)
                                 + (0.0 * derivative))
        except ZeroDivisionError:
            command = self.kp * (error + (0.0 * self.integral) + (0.0 * derivative))
        if command > self.maximum:
            command = self.maximum
            self.integral -= error * dt
        elif command < self.minimum:
            command = self.minimum
            self.integral -= error * dt
        return self.remember(measurement, error, command, time_ms)
