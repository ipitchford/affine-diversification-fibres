"""Fresh-copy replay orchestrator for the affine-diversification candidate.

The frozen payload is hash-checked before any executable artefact can rewrite
an output. Scientific checks then run in a disposable copy, where regenerated
figures and floating-point serialisations are assessed semantically rather
than incorrectly required to be byte-identical across platforms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> dict[str, Any]:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(cwd)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stdout_tail": completed.stdout.strip().splitlines()[-12:],
    }


def verifier_result(command: list[str], cwd: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(cwd)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    record = {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stdout_tail": completed.stdout.strip().splitlines()[-12:],
    }
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        parsed = None
    return record, parsed


def copy_payload(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", ".venv", "build", "*.egg-info", "__pycache__", "*.pyc"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, help="Optionally write the replay receipt outside the frozen payload")
    args = parser.parse_args()

    python = sys.executable
    preflight_command = [python, "verification/verify_release.py", "--check-only"]
    preflight, preflight_report = verifier_result(preflight_command, ROOT)
    preflight_ok = (
        preflight["exit_code"] == 0
        and preflight_report is not None
        and preflight_report.get("status") == "passed"
    )

    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "recorded_at": datetime.now(UTC).isoformat(),
        "scope": "frozen-payload integrity followed by fresh-copy semantic replay",
        "assurance_boundary": (
            "This is an internal deterministic replay. It is not formal verification, "
            "external specialist review, empirical validation, or an exhaustive novelty audit."
        ),
        "python": sys.version,
        "manifest_sha256": sha256(ROOT / "MANIFEST.sha256"),
        "preflight": {
            **preflight,
            "status": preflight_report.get("status") if preflight_report else "unparseable",
            "checks_passed": preflight_report.get("checks_passed") if preflight_report else None,
            "checks_total": preflight_report.get("checks_total") if preflight_report else None,
        },
        "runs": [],
        "status": "failed",
    }

    if preflight_ok:
        with tempfile.TemporaryDirectory(prefix="affine-diversification-replay-") as temporary:
            scratch = Path(temporary) / "payload"
            copy_payload(ROOT, scratch)

            normal_commands = [
                [python, "-m", "unittest", "affine_diversification.test_affine_fibre", "-v"],
                [python, "affine_diversification/run_mammalia_demo.py"],
                [python, "experiments/run_sampling_comparison.py"],
                [python, "experiments/run_cap_phase_diagram.py"],
                [python, "verification/run_independent_checks.py"],
                [python, "verification/run_negative_controls.py"],
            ]
            optimized_commands = [
                [python, "-O", "-m", "unittest", "affine_diversification.test_affine_fibre", "-v"],
                [python, "-O", "verification/run_independent_checks.py"],
                [python, "-O", "verification/run_negative_controls.py"],
            ]

            for mode, commands in (("normal", normal_commands), ("optimized", optimized_commands)):
                command_records = [run(command, scratch) for command in commands]
                verifier_command = [python]
                if mode == "optimized":
                    verifier_command.append("-O")
                verifier_command.extend(["verification/verify_release.py", "--check-only", "--replay-scratch"])
                verification, report = verifier_result(verifier_command, scratch)
                receipt["runs"].append(
                    {
                        "mode": mode,
                        "commands": command_records,
                        "verification": {
                            **verification,
                            "status": report.get("status") if report else "unparseable",
                            "checks_passed": report.get("checks_passed") if report else None,
                            "checks_total": report.get("checks_total") if report else None,
                        },
                    }
                )

    all_commands_ok = preflight_ok and all(
        all(record["exit_code"] == 0 for record in run_record["commands"])
        and run_record["verification"]["exit_code"] == 0
        and run_record["verification"]["status"] == "passed"
        for run_record in receipt["runs"]
    )
    receipt["status"] = "passed" if all_commands_ok and len(receipt["runs"]) == 2 else "failed"

    encoded = json.dumps(receipt, indent=2) + "\n"
    if args.receipt:
        args.receipt.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
