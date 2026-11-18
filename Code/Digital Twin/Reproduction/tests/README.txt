VALIDATION

Run these commands from the Reproduction directory:
  runtime\neuron827\bin\python.exe tests\test_dashboard.py
  runtime\neuron827\bin\python.exe tests\test_components.py
  runtime\neuron827\bin\python.exe tests\test_model_layout.py
  runtime\neuron827\bin\python.exe tests\validate_gate.py

The dashboard tests use temporary files and mocked start/stop controls.
results/checks.json retains the previous short full-network check summary.
results/performance.json and network_100ms.log retain the benchmark evidence.
These are software checks, not completed paper-comparison results.

Optional short network checks:
  runtime\neuron827\bin\python.exe run_case.py warmup --smoke
  runtime\neuron827\bin\python.exe tests\validate_control.py baseline
  runtime\neuron827\bin\python.exe tests\validate_control.py pi
Disposable model copies and outputs are generated on demand in work/.
The short checks use altered time windows solely to verify software behavior.

threadsafe/ contains opt-in mechanism variants and their component validation.
They are not substituted into the active full-network comparison.

results/component_regression.json records the short stimulated-network comparison
against the pre-refactor runner. It is not a full-length paper result.
