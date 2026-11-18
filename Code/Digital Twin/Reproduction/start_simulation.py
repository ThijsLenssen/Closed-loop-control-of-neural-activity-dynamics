"""Choose the system components here. The closed-loop execution stays the same."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from components.cbg_model import CBGModel
from components.lfp_sensor import BipolarLFPSensor
from components.beta_arv import BetaARV
from components.pi_controller import PIController
from components.constant_controller import ConstantController
from components.dbs_actuator import DBSActuator
from components.closed_loop import ClosedLoop
# Future extension: from components.optogenetic_actuator import OptogeneticActuator


def create_simulation(model_directory, kind="pi", target=1.0414e-4, seed=3695,
                      secondorder=0, warmup_ms=6000.0, runtime_ms=32000.0,
                      history_ms=2000.0, tail_ms=100.0):
    # Select concrete implementations and their parameters here.
    model = CBGModel(model_directory, seed, secondorder, warmup_ms, runtime_ms)
    sensor = BipolarLFPSensor()
    biomarker = BetaARV(model.sampling_interval_ms, history_ms, tail_ms)
    controller = (ConstantController(command=0.0, target=target) if kind == "baseline"
                  else PIController(target=target, kp=0.23, ti_s=0.2))
    actuator = DBSActuator()
    return ClosedLoop(model, sensor, biomarker, controller, actuator)


if __name__ == "__main__":
    from simulation_runner import run_cli
    run_cli(create_simulation)
