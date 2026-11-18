"""Common execution loop; no device-specific sensing or actuation equations."""
import numpy as np


class ClosedLoop:
    def __init__(self, model, sensor, biomarker, controller, actuator):
        self.model, self.sensor = model, sensor
        self.biomarker, self.controller, self.actuator = biomarker, controller, actuator
        actuator.validate(model)
        if sensor.units != biomarker.input_units:
            raise ValueError("Sensor and biomarker units do not match.")
        if biomarker.output_units != controller.measurement_units:
            raise ValueError("Biomarker and controller measurement units do not match.")
        if controller.command_units != actuator.command_units:
            raise ValueError("Controller command and actuator units do not match.")
        self.control_times_ms = np.arange(
            model.warmup_ms + biomarker.history_ms + controller.period_ms,
            model.stop_ms, controller.period_ms)

    def initialize(self):
        self.model.prepare()
        self.sensor.bind(self.model)
        self.actuator.bind(self.model, self.control_times_ms)
        self.model.restore()

    def run(self, observe=None):
        try:
            self.initialize()
            for i, time_ms in enumerate(self.control_times_ms):
                self.model.advance(time_ms)
                print("Controller Called at t: %f" % self.model.time_ms, flush=True)
                samples = self.sensor.read()
                measurement = self.biomarker.update(samples)
                command = self.controller.update(measurement, self.model.time_ms)
                print("Measurement:", measurement, self.biomarker.output_units, flush=True)
                if observe is not None:
                    observe(self.model.time_ms, measurement, command)
                if i+1 < len(self.control_times_ms):
                    self.actuator.apply(command, self.control_times_ms[i+1])
                self.sensor.clear()
            return self.results()
        finally:
            self.model.close()

    def results(self):
        result = {
            "measurement": np.asarray(self.controller.measurements),
            "error": np.asarray(self.controller.errors),
            "command": np.asarray(self.controller.commands),
            "controller_time_s": np.asarray(self.controller.times_s),
            "target": np.asarray(self.controller.target),
            "sampling_interval_ms": np.asarray(self.model.sampling_interval_ms),
        }
        result.update(self.sensor.signals())
        result.update(self.actuator.signals())
        return result

    def description(self):
        return {
            "model": type(self.model).__name__, "sensor": type(self.sensor).__name__,
            "biomarker": type(self.biomarker).__name__,
            "controller": type(self.controller).__name__,
            "actuator": type(self.actuator).__name__,
            "measurement_units": self.biomarker.output_units,
            "command_units": self.actuator.command_units,
        }
