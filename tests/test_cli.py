"""Exercise the public CLI without reading any patient or legacy data."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from src.evaluate_synthetic import main

class CliTests(unittest.TestCase):
    def test_seed_and_json_stdout(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--seed", "7"]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["seed"], 7)
        self.assertEqual(report["test_rows"], 100)

    def test_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            main(["--output", str(path)])
            original = path.read_bytes()
            self.assertEqual(json.loads(original)["seed"], 42)
            with self.assertRaises(FileExistsError):
                main(["--seed", "7", "--output", str(path)])
            self.assertEqual(path.read_bytes(), original)

    def test_negative_seed_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                main(["--seed", "-1"])
        self.assertEqual(error.exception.code, 2)
