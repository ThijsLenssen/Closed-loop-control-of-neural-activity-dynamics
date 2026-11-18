MODULAR DBS SIMULATION

Choose components in start_simulation.py, in create_simulation():
  model       Neural dynamics                     CBGModel
  sensor      Signal acquisition                  BipolarLFPSensor
  biomarker   Signal processing                   BetaARV
  controller  Feedback law                        PIController / ConstantController
  actuator    Stimulus delivery                   DBSActuator

Each component inherits its interface from components/base.py.
The common loop is components/closed_loop.py: read -> process -> update -> apply.
Sensor and actuator choices are independent. Add another implementation in its
own file and select it in create_simulation(); the common loop stays unchanged.
OptogeneticActuator is an explicit extension point. An opsin/photocurrent model,
light-delivery model, and target-cell expression are needed before it can run.

Commands from this directory:
  .\start_dashboard.cmd       Open http://127.0.0.1:8765
  .\run_comparison.cmd        Run/resume the DBS-off versus PI pair
  .\stop_comparison.cmd       Stop this comparison
  .\analyse_comparison.cmd    Refresh saved plots and metrics

Run the selected components into separate results:
  runtime\neuron827\bin\python.exe start_simulation.py pi --output results\my_experiment
This reuses the model's warmup. Changes to neural mechanisms require a new
warmup in a separate model/experiment copy. --output separates results only.
Cached comparison stages are checked against the selected implementation.

Folders:
  components/  Parent interfaces and concrete component implementations
  model/       Supplied neural source, inputs, mechanisms, and warmup checkpoint
  dashboard/   Browser interface
  results/     Logs, signals, plots, metrics, and component metadata
  tests/       Validation scripts and compact check summaries
  docs/        Protocol, provenance, package versions, and compatibility patch
  runtime/     Bundled Python/NEURON dependencies

start_simulation.py selects the system; simulation_runner.py handles files/CLI.
run_case.py keeps the existing comparison/dashboard commands compatible.
Defaults: one seed, one burst pattern, 6 s warmup and 30 s evaluation.
Scientific details and limitations: docs/protocol.txt.
