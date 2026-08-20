"""Seal the complete pre-execution protocol and harness.

The bundle manifest binds study inputs, the independent oracle, semantic
validator, schema, controls, tests, and normal/optimized receipts. It excludes
confirmatory outcomes because none is authorized at this stage.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_once(path: Path, content: bytes) -> None:
    if path.exists() and path.read_bytes() != content:
        raise RuntimeError(f"refusing to replace a different frozen seal: {path}")
    path.write_bytes(content)


def main() -> None:
    protocol = json.loads((HERE / "PREREGISTRATION.json").read_text())
    require(protocol["status"] == "FROZEN_AWAITING_EXECUTION_AUTHORIZATION", "protocol status is not frozen")
    require(protocol["registration"]["confirmatory_execution_authorized"] is False, "execution flag must remain false")
    require(protocol["registration"]["public_posting_authorized"] is False, "public-posting flag must remain false")

    normal_path = ROOT / "outputs" / "protocol_controls_normal.json"
    optimized_path = ROOT / "outputs" / "protocol_controls_optimized.json"
    for path, optimized in ((normal_path, False), (optimized_path, True)):
        receipt = json.loads(path.read_text())
        require(receipt["status"] == "PASS", f"control receipt did not pass: {path.name}")
        require(receipt["python_optimized"] is optimized, f"optimized-mode mismatch: {path.name}")
        require(receipt["confirmatory_outcomes_generated"] is False, f"outcome contamination: {path.name}")

    manifest_summary = json.loads((HERE / "CELL_MANIFEST.summary.json").read_text())
    require(manifest_summary["total_cells"] == 3044, "cell manifest is incomplete")
    require(manifest_summary["unique_cell_ids"] is True, "cell IDs are not unique")
    require(manifest_summary["unique_stochastic_seeds"] is True, "stochastic seeds are not unique")
    require(manifest_summary["confirmatory_outcomes_generated"] is False, "outcome flag is contaminated")

    prohibited = list(HERE.glob("*RESULT*")) + list(HERE.glob("*OUTCOME*"))
    require(not prohibited, f"confirmatory-looking files present: {[p.name for p in prohibited]}")

    relative_paths = [
        "adoption/crabs_affine_contract.R",
        "experiments/affine_crabs_confirmatory/README.md",
        "experiments/affine_crabs_confirmatory/PREREGISTRATION.json",
        "experiments/affine_crabs_confirmatory/PROTOCOL.sha256",
        "experiments/affine_crabs_confirmatory/PROTOCOL_MANIFEST.sha256",
        "experiments/affine_crabs_confirmatory/CELL_MANIFEST.jsonl",
        "experiments/affine_crabs_confirmatory/CELL_MANIFEST.summary.json",
        "experiments/affine_crabs_confirmatory/synthetic_signal_specs.json",
        "experiments/affine_crabs_confirmatory/synthetic_signals.json",
        "experiments/affine_crabs_confirmatory/generate_frozen_assets.py",
        "experiments/affine_crabs_confirmatory/freeze_protocol.py",
        "schemas/crabs_affine_adapter.schema.json",
        "verification/independent_affine_oracle.py",
        "verification/crabs_adapter_contract.py",
        "verification/run_protocol_controls.py",
        "verification/test_protocol_harness.py",
        "outputs/protocol_controls_normal.json",
        "outputs/protocol_controls_optimized.json"
    ]
    missing = [name for name in relative_paths if not (ROOT / name).is_file()]
    require(not missing, f"missing bundle files: {missing}")
    manifest = "".join(f"{digest(ROOT / name)}  {name}\n" for name in sorted(relative_paths)).encode()
    bundle_manifest_path = HERE / "FROZEN_BUNDLE_MANIFEST.sha256"
    write_once(bundle_manifest_path, manifest)

    git_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    receipt = {
        "schema_version": "1.0.0",
        "status": "FROZEN_AWAITING_EXECUTION_AUTHORIZATION",
        "protocol_date": protocol["protocol_date"],
        "base_git_commit": git_head,
        "bundle_manifest_sha256": digest(bundle_manifest_path),
        "protocol_sha256": digest(HERE / "PREREGISTRATION.json"),
        "cell_manifest_sha256": digest(HERE / "CELL_MANIFEST.jsonl"),
        "normal_controls_sha256": digest(normal_path),
        "optimized_controls_sha256": digest(optimized_path),
        "deterministic_cells": manifest_summary["deterministic_cells"],
        "stochastic_cells": manifest_summary["stochastic_cells"],
        "confirmatory_outcomes_generated": False,
        "public_actions_taken": False,
        "assurance_boundary": "Local protocol and harness integrity only; no confirmatory result, theorem validation, independent reproduction, peer review, or publication."
    }
    receipt_path = HERE / "FREEZE_RECEIPT.json"
    write_once(receipt_path, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
    write_once(HERE / "FREEZE_RECEIPT.sha256", f"{digest(receipt_path)}  FREEZE_RECEIPT.json\n".encode())
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
