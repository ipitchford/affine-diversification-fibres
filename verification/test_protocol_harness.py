from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import shutil

import jsonschema

from verification.run_protocol_controls import analytic_controls, baseline_records, mutation_controls
from verification.crabs_adapter_contract import validate_request, validate_response

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"


class ProtocolHarnessTests(unittest.TestCase):
    def test_independent_oracle_has_no_forbidden_imports(self) -> None:
        path = ROOT / "verification" / "independent_affine_oracle.py"
        tree = ast.parse(path.read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported.isdisjoint({"affine_diversification", "numpy", "scipy"}))

    def test_baseline_adapter_record_passes(self) -> None:
        request, response, expected = baseline_records()
        schema = json.loads((ROOT / "schemas" / "crabs_affine_adapter.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(request)
        validate_request(request)
        validate_response(response, expected)

    def test_all_analytic_controls_pass(self) -> None:
        results = analytic_controls()
        self.assertTrue(results)
        self.assertTrue(all(item["status"] == "PASS" for item in results))

    def test_all_declared_mutations_are_caught(self) -> None:
        protocol = json.loads((PROTOCOL_DIR / "PREREGISTRATION.json").read_text())
        results = mutation_controls()
        self.assertEqual([item["control"] for item in results], protocol["negative_controls"])
        self.assertTrue(all(item["status"] == "PASS" for item in results))

    def test_generator_is_idempotent(self) -> None:
        before = (PROTOCOL_DIR / "PROTOCOL_MANIFEST.sha256").read_bytes()
        subprocess.run(
            [sys.executable, str(PROTOCOL_DIR / "generate_frozen_assets.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(before, (PROTOCOL_DIR / "PROTOCOL_MANIFEST.sha256").read_bytes())

    def test_manifest_cell_ids_and_stochastic_seeds_are_unique(self) -> None:
        cells = [json.loads(line) for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()]
        ids = [cell["cell_id"] for cell in cells]
        seeds = [cell["seed"] for cell in cells if cell["layer"] == "stochastic"]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(seeds), len(set(seeds)))

    def test_r_adapter_emits_cross_language_valid_contract(self) -> None:
        rscript = shutil.which("Rscript")
        if rscript is None:
            self.skipTest("Rscript unavailable")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "request.json"
            subprocess.run(
                [rscript, str(ROOT / "adoption" / "crabs_affine_contract.R"), str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            request = json.loads(output.read_text())
        schema = json.loads((ROOT / "schemas" / "crabs_affine_adapter.schema.json").read_text())
        jsonschema.Draft202012Validator(schema).validate(request)
        validate_request(request)


if __name__ == "__main__":
    unittest.main()
