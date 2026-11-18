"""Extension point: the supplied paper/model does not include an opsin model."""
from .base import Actuator


class OptogeneticActuator(Actuator):
    command_units = "mW/mm^2"

    def validate(self, model):
        raise NotImplementedError(
            "Optogenetics needs an opsin/photocurrent model, light delivery, and "
            "target-cell expression. Implement this actuator and extend the neural "
            "model before selecting it; the DBS model supplies none of these.")

    def bind(self, model, control_times_ms):
        self.validate(model)

    def apply(self, command, next_control_time_ms):
        raise NotImplementedError("Implement light delivery and photocurrent coupling.")

    def signals(self):
        return {}
