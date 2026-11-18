"""CLI, provenance, and output files; system-component choices live in start_simulation.py."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import time
import numpy as np
from process_control import matching_process
from dashboard_telemetry import Observer

ROOT = Path(__file__).resolve().parent


def implementation_hash():
    paths = [ROOT/"start_simulation.py", ROOT/"simulation_runner.py", ROOT/"run_case.py"]
    paths += sorted((ROOT/"components").glob("*.py"))
    # Include the neural equations, compiled mechanisms, and numeric inputs.
    paths += sorted(p for p in (ROOT/"model").rglob("*") if p.is_file()
                    and p.suffix in (".py", ".mod", ".dll", ".txt", ".npy")
                    and "__pycache__" not in p.parts and p.name != "README.txt")
    return hashlib.sha256(b"".join(path.read_bytes() for path in paths)).hexdigest()


def validate_reuse(kind, state):
    """Prevent comparisons that mix results from different component selections."""
    current = implementation_hash()
    if state.get("source_sha256") == current:
        return
    record = ROOT/"tests/results/component_regression.json"
    if record.is_file():
        checked = json.loads(record.read_text(encoding="utf-8-sig"))
        if (checked.get("engine_sha256") == current and
                checked.get("legacy_source_sha256", {}).get(kind) == state.get("source_sha256")):
            return
    raise RuntimeError(
        "Saved results use another component configuration. Keep the existing "
        "results and use start_simulation.py --output for a separate experiment.")


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(path)


def prepare_validation_model():
    target = ROOT / "tests/work/model"
    shutil.copytree(ROOT/"model", target, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.bin"))
    return target


def paper_arrays(result, system):
    """Keep the current report format for the paper's beta/mA experiment only."""
    from components.beta_arv import BetaARV
    if isinstance(system.biomarker, BetaARV) and system.actuator.command_units == "mA":
        result.update(beta_mv=result["measurement"], amplitude_ma=result["command"],
                      target_mv=result["target"])
    return result


def metrics(arrays, period_ms=20.0):
    if "beta_mv" not in arrays:
        return {"controller_samples": len(arrays["measurement"])}
    beta, amplitude = arrays["beta_mv"], arrays["amplitude_ma"]
    target = float(arrays["target_mv"])
    wave, times = arrays["dbs_ma"], arrays["dbs_time_ms"]
    take = times >= float(arrays["controller_time_s"][0]*1000)
    x, t = wave[take], times[take]
    energy = np.sum(np.diff(t)*(x[:-1]**2+x[:-1]*x[1:]+x[1:]**2)/3)
    return {
        "beta_p10_mv": float(np.percentile(beta, 10)),
        "beta_p20_mv": float(np.percentile(beta, 20)),
        "mean_beta_mv": float(beta.mean()), "target_mv": target,
        "mean_positive_error": float(np.maximum((beta-target)/target, 0).mean()),
        "commanded_power_uw": float(np.mean(x**2)*500),
        "linear_play_power_uw": float(500*energy/(t[-1]-t[0])),
        "max_amplitude_rate_ma_s": float(np.max(np.abs(np.diff(amplitude)))/(period_ms/1000)),
        "controller_samples": len(beta), "lfp_samples": len(arrays["lfp_mv"]),
        "control_duration_s": len(beta)*(period_ms/1000)
    }


def run_cli(create_simulation):
    parser = argparse.ArgumentParser(description="Run the components selected in start_simulation.py")
    parser.add_argument("kind", choices=["warmup", "baseline", "pi"])
    parser.add_argument("--seed", type=int, default=3695)
    parser.add_argument("--secondorder", type=int, choices=[0, 2], default=0)
    parser.add_argument("--target", type=float, default=1.0414e-4, help="Target in the selected biomarker units")
    parser.add_argument("--smoke", action="store_true", help="Isolated initialization/restore check")
    parser.add_argument("--output", type=Path, help="Separate results directory for another experiment")
    args = parser.parse_args()
    model_dir = prepare_validation_model() if args.smoke else ROOT/"model"
    results = (args.output.resolve() if args.output else
               ROOT/("tests/work/results" if args.smoke else "results"))
    out = results/args.kind
    old_path = out/"status.json"
    if old_path.exists() and not args.smoke:
        old = json.loads(old_path.read_text(encoding="utf-8-sig"))
        progress = out/"progress.json"
        pid = json.loads(progress.read_text()).get("pid", 0) if progress.exists() else 0
        if old.get("status") == "running" and pid != os.getpid() and matching_process(pid):
            raise RuntimeError("This case is already running.")
        if old.get("status") == "completed" and args.kind != "warmup":
            raise FileExistsError("Saved case is complete; use --output for a separate experiment.")
    system = create_simulation(
        model_dir, args.kind, args.target, args.seed, args.secondorder,
        warmup_ms=10.0 if args.smoke else 6000.0,
        runtime_ms=2200.0 if args.smoke else 32000.0)
    model = system.model
    out.mkdir(parents=True, exist_ok=True)
    code_hash = implementation_hash()
    source = model.warmup_source()[1] if args.kind == "warmup" else model.network_source()
    if source:
        (out/"executed_source.py").write_text(source, encoding="utf-8")
    started = time.time()
    state = {
        "kind": args.kind, "status": "running", "started_unix": started,
        "seed": args.seed, "secondorder": args.secondorder, "source_sha256": code_hash,
        "target_mv": args.target if args.kind == "pi" else None,
        "components": system.description(), "implementation": "modular",
        "protocol": "authors' code (secondorder=0)" if args.secondorder == 0 else
                    "paper-described Crank-Nicolson (secondorder=2)"
    }
    save_json(out/"status.json", state)
    observer = None
    try:
        if args.kind == "warmup":
            model.run_warmup(source)
        elif args.smoke:
            system.initialize()
            print("RESTORE_VALIDATED", model.time_ms, flush=True)
            model.close()
        else:
            from components.beta_arv import BetaARV
            if isinstance(system.biomarker, BetaARV) and system.actuator.command_units == "mA":
                observer = Observer(out/"telemetry.jsonl")
            def observe(time_ms, measurement, command):
                if observer:
                    relative_s = (time_ms-model.warmup_ms-system.biomarker.history_ms)/1000
                    observer(relative_s, float(measurement)*1000, float(command))
            arrays = paper_arrays(system.run(observe), system)
            np.savez_compressed(out/"signals.npz", **arrays)
            save_json(out/"metrics.json", metrics(arrays, system.controller.period_ms))
            print("SIMULATION_COMPLETE", flush=True)
        state.update(status="completed", elapsed_s=time.time()-started)
        save_json(out/"status.json", state)
    except BaseException as exc:
        state.update(status="failed", error=repr(exc), elapsed_s=time.time()-started)
        save_json(out/"status.json", state)
        raise
    finally:
        if observer:
            observer.close()
