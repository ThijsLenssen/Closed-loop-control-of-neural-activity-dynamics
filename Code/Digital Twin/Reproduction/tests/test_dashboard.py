"""Dashboard tests use temporary results and mocked process controls; no solver is launched."""
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch, Mock
import importlib.util
import json
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import dashboard_server as ds
from dashboard_telemetry import Observer


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/"results").mkdir()
        self.app = ds.Dashboard(self.root)
        self.match = patch.object(ds, "matching_process", return_value=False)
        self.sample = patch.object(ds, "process_sample", return_value=None)
        self.match.start()
        self.sample.start()

    def tearDown(self):
        self.sample.stop()
        self.match.stop()
        self.temp.cleanup()

    def write(self, path, obj):
        p = self.root/"results"/path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(obj), encoding="utf-8")

    def stage(self, kind, **kwargs):
        obj = {"kind": kind, "seed": 3695, "secondorder": 0, "status": "running", "started_unix": time.time()-100}
        obj.update(kwargs)
        self.write(kind+"/status.json", obj)

    def test_empty_is_idle_and_zero(self):
        snap = self.app.snapshot()
        self.assertEqual(snap["status"], "idle")
        self.assertFalse(snap["running"])
        self.assertEqual(snap["percent"], 0)
        self.assertIsNone(snap["eta_s"])

    def test_dead_runner_is_interrupted(self):
        self.write("comparison_status.json", {"status": "running", "pid": 99})
        self.stage("warmup")
        self.write("warmup/progress.json", {"pid": 100, "simulation_time_ms": 600})
        snap = self.app.snapshot()
        self.assertEqual(snap["status"], "interrupted")
        self.assertEqual(snap["stages"][0]["status"], "interrupted")
        self.assertAlmostEqual(snap["percent"], 600/70000*100)

    def test_trial_progress_excludes_restored_warmup(self):
        self.stage("warmup", status="completed")
        self.stage("baseline")
        self.write("baseline/progress.json", {"pid": 10, "simulation_time_ms": 8000})
        snap = self.app.snapshot()
        self.assertEqual(snap["stages"][0]["percent"], 100)
        self.assertEqual(snap["stages"][1]["integrated_s"], 2)
        self.assertEqual(snap["stages"][1]["duration_s"], 32)
        self.assertAlmostEqual(snap["percent"], 8000/70000*100)

    def test_stopped_elapsed_does_not_count_idle_time(self):
        self.write("comparison_status.json", {"status":"stopped", "started_unix":100, "completed_unix":200})
        self.assertEqual(self.app.snapshot()["elapsed_s"], 100)

    def test_cpu_is_measured_as_delta(self):
        self.stage("warmup")
        self.write("warmup/progress.json", {"pid": 10})
        with patch.object(ds, "process_sample", side_effect=[
            {"pid":10,"cpu_seconds":5.,"memory_mb":100.},
            {"pid":10,"cpu_seconds":7.,"memory_mb":101.}
        ]), patch.object(ds.time, "time", side_effect=[10., 12.]):
            a, b = self.app.snapshot(), self.app.snapshot()
        self.assertIsNone(a["processes"][0]["cpu_one_core_percent"])
        self.assertEqual(b["processes"][0]["cpu_one_core_percent"], 100.)

    def test_start_attaches_without_duplicate_process(self):
        with patch.object(ds, "matching_process", return_value=True), patch.object(ds.subprocess, "Popen") as spawn:
            self.write("comparison_status.json", {"status":"running", "pid":100})
            result = self.app.action("start")
        spawn.assert_not_called()
        self.assertIn("already running", result["message"])

    def test_start_passes_only_selected_protocol(self):
        with patch.object(ds.subprocess, "Popen", return_value=Mock(pid=123)) as spawn:
            self.app.action("start")
        command = spawn.call_args.args[0]
        self.assertEqual(command[-6:], ["--seed", "3695", "--secondorder", "0", "--target", "0.00010414"])
        self.assertNotIn("shell", spawn.call_args.kwargs)
        saved = ds.read_json(self.root/"results/comparison_status.json")
        self.assertEqual(saved["pid"], 123)

    def test_mismatched_completed_seed_is_rejected(self):
        self.stage("warmup", status="completed", seed=123)
        with patch.object(ds.subprocess, "Popen") as spawn:
            with self.assertRaisesRegex(ValueError, "different settings"):
                self.app.action("start")
        spawn.assert_not_called()

    def test_completed_comparison_is_not_relaunched(self):
        self.write("comparison_status.json", {"status":"completed"})
        with patch.object(ds.subprocess, "Popen") as spawn:
            self.app.action("start")
        spawn.assert_not_called()

    def test_telemetry_is_real_and_tolerates_incomplete_line(self):
        p = self.root/"results/pi/telemetry.jsonl"
        p.parent.mkdir()
        observer = Observer(p)
        observer(.02, .12, 1.3)
        observer(.04, float("nan"), 0)
        observer.close()
        with p.open("a") as f:
            f.write('{"time_s":0.04,')
        data = self.app.series()
        self.assertEqual(data["baseline"], [])
        self.assertEqual(data["pi"], [{"time_s":.02,"beta_uv":.12,"amplitude_ma":1.3}])


    def test_stop_covers_child_import_startup_window(self):
        import process_control
        self.write("comparison_status.json", {"status":"running", "pid":100})
        self.write("baseline/progress.json", {"phase":"starting", "pid":200})
        with patch.object(process_control, "ROOT", self.root), patch.object(
                process_control, "terminate_matching", return_value=True) as terminate:
            process_control.stop()
        self.assertEqual([call.args[0] for call in terminate.call_args_list], [100, 200])
        self.assertEqual(ds.read_json(self.root/"results/comparison_status.json")["status"], "stopped")

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(ValueError):
            self.app.action("anything")


class RunCoordinatorTests(unittest.TestCase):
    def test_dashboard_pending_pid_can_enter_its_own_runner(self):
        import run_comparison as runner
        with patch.object(runner.os, "getpid", return_value=123), patch.object(
                runner, "matching_process", return_value=True):
            self.assertFalse(runner.another_comparison_running(
                {"status": "running", "pid": 123}))

    def test_another_live_runner_still_prevents_a_duplicate(self):
        import run_comparison as runner
        with patch.object(runner.os, "getpid", return_value=123), patch.object(
                runner, "matching_process", return_value=True):
            self.assertTrue(runner.another_comparison_running(
                {"status": "running", "pid": 456}))

    def test_dead_pending_runner_does_not_block_a_restart(self):
        import run_comparison as runner
        with patch.object(runner.os, "getpid", return_value=123), patch.object(
                runner, "matching_process", return_value=False):
            self.assertFalse(runner.another_comparison_running(
                {"status": "running", "pid": 456}))


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = ds.Dashboard()
        cls.app.snapshot = Mock(return_value={"stages":[],"status":"test"})
        cls.app.action = Mock(return_value={"message":"test only"})
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ds.Handler)
        cls.server.app = cls.app
        cls.url = "http://127.0.0.1:" + str(cls.server.server_port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, data=None, headers=None):
        req = Request(self.url+path, data=data, headers=headers or {})
        try:
            with urlopen(req, timeout=3) as r:
                return r.status, r.read(), r.headers
        except HTTPError as r:
            return r.code, r.read(), r.headers

    def test_read_status(self):
        code, body, _ = self.request("/api/status")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["status"], "test")

    def test_controls_require_session_token(self):
        before = self.app.action.call_count
        code, _, _ = self.request("/api/stop", b"{}", {"Content-Type":"application/json"})
        self.assertEqual(code, 403)
        self.assertEqual(self.app.action.call_count, before)

    def test_cross_origin_control_is_rejected(self):
        before = self.app.action.call_count
        code, _, _ = self.request("/api/start", b"{}", {
            "Content-Type":"application/json", "X-Dashboard-Token":self.app.token, "Origin":"https://example.com"})
        self.assertEqual(code, 403)
        self.assertEqual(self.app.action.call_count, before)

    def test_valid_control_calls_mock_only(self):
        code, _, _ = self.request("/api/start", b"{}", {
            "Content-Type":"application/json", "X-Dashboard-Token":self.app.token})
        self.assertEqual(code, 200)
        self.app.action.assert_called_with("start")

    def test_request_cannot_change_settings(self):
        code, _, _ = self.request("/api/start", b'{"seed":1}', {
            "Content-Type":"application/json", "X-Dashboard-Token":self.app.token})
        self.assertEqual(code, 400)

    def test_path_traversal_is_rejected(self):
        self.assertEqual(self.request("/results/../run_comparison.py")[0], 404)
        self.assertEqual(self.request("/results/%2e%2e/run_comparison.py")[0], 404)

    def test_nonlocal_host_is_rejected(self):
        self.assertEqual(self.request("/api/status", headers={"Host":"example.com"})[0], 403)

    def test_frontend_is_served_offline(self):
        for path in ("/", "/app.js", "/style.css"):
            code, body, headers = self.request(path)
            self.assertEqual(code, 200)
            self.assertGreater(len(body), 1000)
            self.assertIn("default-src 'self'", headers["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
