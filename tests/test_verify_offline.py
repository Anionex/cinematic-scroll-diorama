"""Run with: python -m unittest discover -s tests -v (Playwright required)."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "verify_offline", Path(__file__).resolve().parents[1] / "scripts/verify_offline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Deliberately contains no 3D scene: runtime success must not imply visual success.
FIXTURE = """<!doctype html><meta charset="utf-8"><title>Runtime fixture</title>
<style>body{margin:0}section{height:200vh}canvas{position:fixed;pointer-events:none}</style>
<canvas></canvas><main>
<section class="chapter">Cover</section>
<section class="chapter"><figure class="memory-photo"><img
src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8'%3E%3Crect width='8' height='8' fill='red'/%3E%3C/svg%3E"></figure></section>
<section class="chapter">Ending</section></main>"""


class OfflineReportTests(unittest.TestCase):
    def test_runtime_only_success_then_failure_replaces_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "fixture.html"
            source.write_text(FIXTURE, encoding="utf-8")
            result = module.verify(source, {"width": 800, "height": 600}, 0.4)
            self.assertEqual(result["status"], "runtime_passed")
            self.assertEqual(result["acceptance"], "pending")
            self.assertIn("world_coordinates", result["unverified"])
            self.assertIn("miniature_geometry", result["unverified"])
            self.assertEqual(result["chapter_progress"], 0.4)
            self.assertEqual(len(result["screenshots"]), 3)
            for image in result["screenshots"]:
                self.assertTrue(Path(image).is_file())
            source.write_text(FIXTURE.replace("<canvas></canvas>", ""), encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "Missing 3D canvas"):
                module.verify(source, {"width": 800, "height": 600})
            report = json.loads((Path(directory) / "fixture-review/result.json").read_text())
            self.assertEqual(report["status"], "runtime_failed")
            self.assertEqual(report["acceptance"], "not_passed")
            self.assertFalse(list(Path(directory).glob(".album-offline-*")))

    def test_invalid_progress_is_recorded_without_browser(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "fixture.html"
            source.write_text(FIXTURE, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "between 0 and 1"):
                module.verify(source, {"width": 800, "height": 600}, 1.1)
            report = json.loads((Path(directory) / "fixture-review/result.json").read_text())
            self.assertEqual(report["status"], "runtime_failed")

    def test_missing_input_replaces_old_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "fixture.html"
            output = Path(directory) / "fixture-review"
            output.mkdir()
            report = output / "result.json"
            report.write_text('{"status":"runtime_passed"}', encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                module.verify(source, {"width": 800, "height": 600})
            self.assertEqual(json.loads(report.read_text())["status"], "runtime_failed")


if __name__ == "__main__":
    unittest.main()
