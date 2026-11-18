"""Local dashboard for the selected DBS-off / PI reproduction. Standard library HTTP."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
import argparse
import ctypes
import json
import math
import mimetypes
import os
import secrets
import subprocess
import sys
import threading
import time
import webbrowser

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from process_control import matching_process, stop as stop_comparison

KINDS = ("warmup", "baseline", "pi")
NAMES = {"warmup": "Network warmup", "baseline": "DBS off", "pi": "PI amplitude"}
DURATION = {"warmup": 6000., "baseline": 32000., "pi": 32000.}
DEFAULTS = {"seed": 3695, "secondorder": 0, "target": 1.0414e-4}


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def tail(path, limit=65536):
    try:
        with path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - limit))
            return f.read().decode("utf-8-sig", errors="replace")
    except OSError:
        return ""


def process_sample(pid):
    """Read a verified local process without WMI or external dependencies."""
    if not matching_process(pid):
        return None
    from ctypes import wintypes as w
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    k.OpenProcess.restype = w.HANDLE
    k.CloseHandle.argtypes = [w.HANDLE]
    k.GetProcessTimes.argtypes = [w.HANDLE] + [ctypes.POINTER(w.FILETIME)] * 4
    class Memory(ctypes.Structure):
        _fields_ = [("cb", w.DWORD), ("PageFaultCount", w.DWORD)] + [
            (name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    p = ctypes.WinDLL("psapi", use_last_error=True)
    p.GetProcessMemoryInfo.argtypes = [w.HANDLE, ctypes.POINTER(Memory), w.DWORD]
    handle = k.OpenProcess(0x1000 | 0x10, False, int(pid))
    if not handle:
        return {"pid": pid, "cpu_seconds": None, "memory_mb": None}
    try:
        times = [w.FILETIME() for _ in range(4)]
        cpu = None
        if k.GetProcessTimes(handle, *(ctypes.byref(x) for x in times)):
            cpu = sum((x.dwHighDateTime << 32) + x.dwLowDateTime for x in times[2:]) / 1e7
        mem = Memory()
        mem.cb = ctypes.sizeof(mem)
        ram = mem.WorkingSetSize / 1048576 if p.GetProcessMemoryInfo(handle, ctypes.byref(mem), mem.cb) else None
        return {"pid": pid, "cpu_seconds": cpu, "memory_mb": ram}
    finally:
        k.CloseHandle(handle)


class Dashboard:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.results = self.root / "results"
        self.python = self.root / "runtime/neuron827/bin/python.exe"
        self.lock = threading.RLock()
        self.cpu_previous = {}
        self.token = secrets.token_urlsafe(32)
        self.analysis = None

    def snapshot(self):
        with self.lock:
            return self._snapshot()

    def _snapshot(self):
        now = time.time()
        campaign = read_json(self.results / "comparison_status.json")
        supervisor = bool(campaign.get("status") == "running" and
                          matching_process(campaign.get("pid", 0)))
        stages, processes, ratios = [], [], []
        work = 0.
        for kind in KINDS:
            state = read_json(self.results / kind / "status.json")
            progress = read_json(self.results / kind / "progress.json")
            phase = state.get("status", "queued")
            sample = process_sample(progress.get("pid", 0)) if phase == "running" else None
            alive = sample is not None
            if phase == "running" and not alive:
                phase = "interrupted"
            completed = phase == "completed"
            raw_ms = float(progress.get("simulation_time_ms", 0) or 0)
            integrated = min(DURATION[kind], max(0., raw_ms - (0 if kind == "warmup" else 6000.)))
            if completed:
                integrated = DURATION[kind]
            work += integrated
            begin = progress.get("started_unix", state.get("started_unix"))
            end = (progress.get("completed_unix") if completed else None)
            elapsed = max(0., (end or (now if alive else progress.get("updated_unix", begin or now))) - (begin or now))
            if integrated > 0 and elapsed > 0 and (alive or completed):
                ratios.append(elapsed / (integrated / 1000))
            if sample:
                key = sample["pid"]
                cpu = sample["cpu_seconds"]
                previous = self.cpu_previous.get(key)
                sample["cpu_one_core_percent"] = (
                    max(0., 100 * (cpu - previous[1]) / (now - previous[0]))
                    if previous and cpu is not None and now > previous[0] else None)
                self.cpu_previous[key] = (now, cpu) if cpu is not None else (now, 0)
                sample["stage"] = kind
                processes.append(sample)
            error = state.get("error", "")
            if phase == "failed" and state.get("exit_code"):
                error += " (exit code " + str(state["exit_code"]) + ")"
            stages.append({
                "kind": kind, "name": NAMES[kind], "status": phase, "alive": alive,
                "phase": progress.get("phase", "") if alive else phase,
                "simulation_time_s": raw_ms / 1000 if raw_ms else None,
                "integrated_s": integrated / 1000, "duration_s": DURATION[kind] / 1000,
                "percent": 100 * integrated / DURATION[kind], "elapsed_s": elapsed,
                "last_update": progress.get("updated_unix"), "pid": progress.get("pid"),
                "error": error, "metrics": read_json(self.results / kind / "metrics.json")
            })
        running = supervisor or bool(processes)
        status = campaign.get("status", "idle")
        if running:
            status = "running"
        elif status == "running":
            status = "interrupted"
        args = dict(DEFAULTS)
        args.update({k: v for k, v in campaign.get("arguments", {}).items() if k in args})
        remaining = (DURATION["warmup"] - stages[0]["integrated_s"] * 1000 +
                     max(DURATION[k] - stages[i]["integrated_s"] * 1000
                         for i, k in enumerate(KINDS) if k != "warmup")) / 1000
        eta = remaining * (sum(ratios) / len(ratios)) if running and ratios else None
        started = campaign.get("started_unix")
        last_work = max((s.get("last_update") or 0 for s in stages), default=0)
        end_time = now if running else campaign.get("completed_unix", last_work or started or now)
        elapsed = max(0., end_time - started) if started else 0
        artifacts = {}
        for name in ("comparison.png", "comparison.svg", "comparison.csv", "comparison.json", "index.html"):
            if (self.results / name).is_file():
                artifacts[name] = "/results/" + name
        return {
            "now": now, "status": status, "running": running, "supervisor_alive": supervisor,
            "stages": stages, "processes": processes, "logical_cpus": os.cpu_count() or 1,
            "percent": 100 * work / sum(DURATION.values()), "elapsed_s": elapsed,
            "eta_s": eta, "settings": args, "artifacts": artifacts,
            "comparison": read_json(self.results / "comparison.json"),
            "error": campaign.get("error", ""),
            "analysis_running": self.analysis is not None and self.analysis.poll() is None
        }

    def series(self):
        result = {}
        for kind in ("baseline", "pi"):
            points = []
            path = self.results / kind / "telemetry.jsonl"
            try:
                # At most 1501 controller samples for this fixed protocol.
                with path.open(encoding="utf-8-sig") as f:
                    for line in f:
                        try:
                            row = json.loads(line)
                            if all(isinstance(row.get(k), (float, int)) and math.isfinite(row[k])
                                   for k in ("time_s", "beta_uv", "amplitude_ma")):
                                points.append(row)
                        except ValueError:
                            continue  # Last line may still be in flight.
                points = points[-1600:]
            except OSError:
                pass
            # Also supports completed cases generated before dashboard telemetry.
            if not points and (self.results / kind / "signals.npz").is_file():
                import numpy as np
                with np.load(self.results / kind / "signals.npz", allow_pickle=False) as z:
                    points = [{"time_s": float(t) - 8, "beta_uv": float(b) * 1000,
                               "amplitude_ma": float(a)}
                              for t, b, a in zip(z["controller_time_s"], z["beta_mv"], z["amplitude_ma"])
                              if all(math.isfinite(float(v)) for v in (t, b, a))]
            result[kind] = points
        return result

    def action(self, name):
        with self.lock:
            snap = self._snapshot()
            if name == "start":
                if snap["running"]:
                    return {"message": "The comparison is already running; attached to its progress."}
                if snap["status"] == "completed":
                    return {"message": "This comparison is complete. Saved results are retained."}
                # Restart/resume this same pair. Never reuse completed stages with other settings.
                settings = snap["settings"]
                if not isinstance(settings["seed"], int) or not 0 <= settings["seed"] <= 2147483647:
                    raise ValueError("Invalid saved seed.")
                if settings["secondorder"] not in (0, 2):
                    raise ValueError("Invalid saved solver setting.")
                if not isinstance(settings["target"], (int, float)) or not math.isfinite(settings["target"]) or settings["target"] <= 0:
                    raise ValueError("Invalid saved target.")
                for kind in KINDS:
                    state = read_json(self.results / kind / "status.json")
                    if state.get("status") == "completed":
                        if state.get("seed") != settings["seed"] or state.get("secondorder") != settings["secondorder"]:
                            raise ValueError("Saved stages use different settings. Keep experiments in separate folders.")
                        if kind == "pi" and state.get("target_mv") != settings["target"]:
                            raise ValueError("Saved PI result uses a different target.")
                self.results.mkdir(exist_ok=True)
                cmd = [str(self.python), "-u", str(self.root / "run_comparison.py")]
                for key, value in settings.items():
                    cmd.extend(["--" + key, str(value)])
                with (self.results / "supervisor.log").open("a", encoding="utf-8") as log:
                    p = subprocess.Popen(cmd, cwd=self.root, stdout=log, stderr=subprocess.STDOUT,
                                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                # Cover the startup window before the child writes its status file.
                pending = {"status": "running", "started_unix": time.time(), "pid": p.pid,
                           "scope": "DBS off versus PI amplitude; no sweeps", "arguments": settings}
                dst = self.results / "comparison_status.json"
                temp = dst.with_suffix(".dashboard.tmp")
                temp.write_text(json.dumps(pending, indent=2), encoding="utf-8")
                temp.replace(dst)
                return {"message": "Comparison started. Completed stages are reused; unfinished stages restart."}
            if name == "stop":
                if not snap["running"]:
                    return {"message": "No comparison process is running."}
                if self.root != ROOT:
                    raise ValueError("Stopping is only supported for this reproduction.")
                stop_comparison()
                return {"message": "Comparison stopped. Saved outputs are retained; unfinished stages restart on resume."}
            if name == "analyse":
                if self.analysis is not None and self.analysis.poll() is None:
                    return {"message": "Analysis is already running."}
                self.results.mkdir(exist_ok=True)
                with (self.results / "analysis.log").open("w", encoding="utf-8") as log:
                    self.analysis = subprocess.Popen(
                        [str(self.python), str(self.root / "analyse_comparison.py")],
                        cwd=self.root, stdout=log, stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                return {"message": "Refreshing the report and any completed comparison plots."}
            raise ValueError("Unknown action.")


class Handler(BaseHTTPRequestHandler):
    server_version = "DBSDashboard/1.0"

    @property
    def app(self):
        return self.server.app

    def local_request(self):
        expected = {"127.0.0.1:" + str(self.server.server_port),
                    "localhost:" + str(self.server.server_port)}
        return self.headers.get("Host") in expected

    def send(self, body, status=200, mime="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, allow_nan=False).encode()
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        if not self.local_request():
            return self.send({"error": "Local dashboard only."}, 403)
        url = urlsplit(self.path)
        try:
            if url.path == "/api/status":
                return self.send(self.app.snapshot())
            if url.path == "/api/session":
                return self.send({"token": self.app.token})
            if url.path == "/api/series":
                return self.send(self.app.series())
            if url.path == "/api/log":
                stage = parse_qs(url.query).get("stage", ["warmup"])[0]
                if stage not in (*KINDS, "supervisor", "analysis"):
                    return self.send({"error": "Unknown log."}, 400)
                path = self.app.results / (stage + ".log") if stage in ("supervisor", "analysis") else self.app.results / stage / "run.log"
                return self.send({"stage": stage, "text": "\n".join(tail(path).splitlines()[-180:])})
            assets = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
            if url.path in assets:
                path = self.app.root / "dashboard" / assets[url.path]
            elif url.path in {
                "/docs/manifest.json", "/tests/results/performance.json", "/tests/results/checks.json",
                "/tests/results/network_100ms.log", "/tests/threadsafe/README.txt",
                "/tests/threadsafe/validation_summary.json",
                "/manifest.json", "/performance.json", "/validation_checks.json",
                "/validation_network_100ms.log", "/threadsafe/README.txt",
                "/threadsafe/validation_summary.json"
            }:
                # Keep old saved report links readable after folder consolidation.
                aliases = {
                    "/manifest.json": "docs/manifest.json",
                    "/performance.json": "tests/results/performance.json",
                    "/validation_checks.json": "tests/results/checks.json",
                    "/validation_network_100ms.log": "tests/results/network_100ms.log",
                    "/threadsafe/README.txt": "tests/threadsafe/README.txt",
                    "/threadsafe/validation_summary.json": "tests/threadsafe/validation_summary.json"
                }
                path = self.app.root / aliases.get(url.path, url.path.lstrip("/"))
            elif url.path.startswith("/results/"):
                name = url.path[len("/results/"):]
                allowed = {"index.html", "progress.html", "comparison.png", "comparison.svg", "comparison.csv", "comparison.json"}
                allowed |= {k + "/" + f for k in KINDS for f in ("signals.npz", "metrics.json", "run.log", "executed_source.py")}
                if name not in allowed:
                    return self.send({"error": "Unknown artifact."}, 404)
                path = self.app.results / name
            else:
                return self.send({"error": "Not found."}, 404)
            if not path.is_file():
                return self.send({"error": "Not available yet."}, 404)
            return self.send(path.read_bytes(), mime=mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        except Exception as exc:
            self.send({"error": str(exc)}, 500)

    def do_POST(self):
        origin = self.headers.get("Origin")
        expected = {"http://127.0.0.1:" + str(self.server.server_port),
                    "http://localhost:" + str(self.server.server_port)}
        if not self.local_request() or (origin is not None and origin not in expected):
            return self.send({"error": "Local dashboard only."}, 403)
        if self.headers.get("X-Dashboard-Token") != self.app.token:
            return self.send({"error": "Refresh the dashboard before using its controls."}, 403)
        if self.headers.get_content_type() != "application/json":
            return self.send({"error": "JSON required."}, 415)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 <= length <= 1024:
                return self.send({"error": "Request too large."}, 413)
            payload = json.loads(self.rfile.read(length) or b"{}")
            if payload != {}:
                raise ValueError("This dashboard runs the selected pair with its saved settings.")
            path = urlsplit(self.path).path
            if path not in ("/api/start", "/api/stop", "/api/analyse"):
                return self.send({"error": "Unknown action."}, 404)
            self.send(self.app.action(path.rsplit("/", 1)[1]))
        except ValueError as exc:
            self.send({"error": str(exc)}, 400)
        except Exception as exc:
            self.send({"error": str(exc)}, 500)

    def log_message(self, fmt, *args):
        if len(args) > 1 and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    address = "http://127.0.0.1:" + str(args.port)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        # A second launcher opens the existing dashboard without spawning another runner.
        from urllib.request import urlopen
        try:
            with urlopen(address + "/api/status", timeout=2) as response:
                existing = json.load(response)
            if "stages" not in existing:
                raise ValueError("Not this dashboard")
        except Exception:
            raise RuntimeError("Port is in use. Choose another with --port.") from None
        if args.open:
            webbrowser.open(address)
        print("Dashboard already running at " + address)
        return
    server.app = Dashboard()
    print("Simulation dashboard: " + address, flush=True)
    print("Closing this server leaves the simulation running.", flush=True)
    if args.open:
        webbrowser.open(address)
    try:
        server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
