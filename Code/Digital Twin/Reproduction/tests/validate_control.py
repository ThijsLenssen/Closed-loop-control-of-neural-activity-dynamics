"""Short component wiring check, isolated from the full comparison."""
from pathlib import Path
import argparse
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulation_runner import prepare_validation_model, paper_arrays
from start_simulation import create_simulation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["baseline", "pi"])
    args = parser.parse_args()
    model_dir = prepare_validation_model()
    target = 1e-12 if args.kind == "pi" else 1.0414e-4
    system = create_simulation(model_dir, args.kind, target=target,
                               warmup_ms=10.0, runtime_ms=60.0,
                               history_ms=20.0, tail_ms=2.0)
    started = time.perf_counter()
    arrays = paper_arrays(system.run(), system)
    out = ROOT/"tests/work/results"/args.kind
    out.mkdir(exist_ok=True, parents=True)
    np.savez_compressed(out/"smoke_signals.npz", **arrays)
    check = {
        "kind": args.kind, "wall_s": time.perf_counter()-started,
        "controller_samples": len(arrays["beta_mv"]),
        "amplitude_ma": arrays["amplitude_ma"].tolist(),
        "lfp_samples": len(arrays["lfp_mv"]),
        "lfp_time_samples": len(arrays["lfp_time_ms"]),
        "finite_lfp": bool(np.isfinite(arrays["lfp_mv"]).all()),
        "enabled_GPe_cells": sum(c.dur > 0 for c in system.model.gpe_clamps[:100]),
        "validation_target_mv": target,
        "scope": "10 ms warmup + 60 ms simulation; 20 ms history for software validation only"
    }
    assert check["controller_samples"] == 2, check
    assert check["lfp_samples"] == check["lfp_time_samples"], check
    assert check["finite_lfp"] and np.isfinite(arrays["beta_mv"]).all(), check
    if args.kind == "pi":
        assert max(check["amplitude_ma"]) > 0 and check["enabled_GPe_cells"] > 0, check
    (out/"control_check.json").write_text(json.dumps(check, indent=2), encoding="utf-8")
    print("CONTROL_CHECK", json.dumps(check), flush=True)


if __name__ == "__main__":
    main()
