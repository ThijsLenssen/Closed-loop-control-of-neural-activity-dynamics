"""Model provenance and paths remain valid after component selection."""
from pathlib import Path
import ast
import hashlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from start_simulation import create_simulation


class ModelLayoutTests(unittest.TestCase):
    def test_manifest_matches_every_model_asset(self):
        manifest = json.loads((ROOT/"docs/manifest.json").read_text(encoding="utf-8-sig"))
        for name, expected in manifest["source_files"].items():
            with self.subTest(asset=name):
                path = ROOT/"model"/name
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_supplied_scripts_reference_existing_input_files(self):
        for path in (ROOT/"model/python").glob("run_CBG_Model_*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            references = [n.value for n in ast.walk(tree)
                          if isinstance(n, ast.Constant) and isinstance(n.value, str)
                          and n.value.startswith("data/")]
            self.assertGreater(len(references), 10, path.name)
            for value in references:
                with self.subTest(script=path.name, input=value):
                    self.assertTrue((ROOT/"model"/value).is_file())

    def test_default_network_and_warmup_sources_compile(self):
        model = create_simulation(ROOT/"model").model
        filename, source = model.warmup_source()
        compile(source, filename, "exec")
        compile(model.network_source(), "network", "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
