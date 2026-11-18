"""Small interfaces for the blocks in the paper's closed-loop diagram."""
from abc import ABC, abstractmethod


class NeuralModel(ABC):
    @abstractmethod
    def prepare(self):
        """Construct the neural network without advancing time."""

    @abstractmethod
    def restore(self):
        """Restore the common warmup state."""

    @abstractmethod
    def advance(self, time_ms):
        """Advance to the next measurement."""

    @abstractmethod
    def close(self):
        """Release the simulator."""


    def network_source(self):
        return ""  # Optional provenance for models assembled from source.

    def warmup_source(self):
        return "", ""

    def run_warmup(self, source):
        raise NotImplementedError("This model does not implement a saved warmup.")


class Sensor(ABC):
    units = ""

    @abstractmethod
    def bind(self, model):
        """Attach to the model's observable signals."""

    @abstractmethod
    def read(self):
        """Return the newly acquired signal samples."""

    @abstractmethod
    def clear(self):
        """Clear consumed recorder buffers."""


    def signals(self):
        return {}


class Biomarker(ABC):
    input_units = ""
    output_units = ""
    history_ms = 0.0

    @abstractmethod
    def update(self, samples):
        """Process acquired samples into one feedback measurement."""


class Controller(ABC):
    measurement_units = "mV"
    command_units = "mA"

    def __init__(self, target):
        self.target = target
        self.measurements, self.errors, self.commands, self.times_s = [], [], [], []

    def remember(self, value, error, command, time_ms):
        self.measurements.append(value)
        self.errors.append(error)
        self.commands.append(command)
        self.times_s.append(time_ms / 1000.0)
        return command

    @abstractmethod
    def update(self, measurement, time_ms):
        """Return the actuator command in command_units."""


class Actuator(ABC):
    command_units = ""

    def validate(self, model):
        """Reject an unsupported model before constructing its network."""

    @abstractmethod
    def bind(self, model, control_times_ms):
        """Connect the stimulation model to the neural model."""

    @abstractmethod
    def apply(self, command, next_control_time_ms):
        """Schedule stimulation over the next controller interval."""

    @abstractmethod
    def signals(self):
        """Return the commanded waveform for the saved results."""
