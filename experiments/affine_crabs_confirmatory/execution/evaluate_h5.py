#!/usr/bin/env python3
"""Evaluate the preregistered H5 installation, task, and runtime gate."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import venv
from collections import defaultdict
from pathlib import Path

import numpy as np

from affine_diversification.affine_fibre import no_external_point_bounds, pulled_scale


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
EXECUTION_DIR = PROTOCOL_DIR / "execution"
RESULT_DIR = EXECUTION_DIR / "results" / "stochastic_stage2"
STAGE1_RECEIPT = EXECUTION_DIR / "H5_EXECUTION_RECEIPT.json"
RECEIPT = EXECUTION_DIR / "H5_EXECUTION_RECEIPT_002.json"
REPETITIONS = 31


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_new_or_identical(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different H5 receipt: {path}")
    path.write_bytes(payload)


def run(command: list[str], *, cwd: Path, environment: dict[str, str] | None = None) -> dict:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_sha256": sha256_bytes(completed.stdout),
        "stdout_tail": completed.stdout.decode("utf-8", errors="replace").strip().splitlines()[-8:],
    }


def installed_smoke_source() -> str:
    return """
import numpy as np
from affine_diversification.affine_fibre import (
    interval_feasibility_certificate,
    no_external_point_bounds,
    pulled_scale,
)
tau = np.linspace(0.0, 5.0, 100)
lp = 0.2 + 0.04 * np.sin(tau)
x = pulled_scale(tau, lp)
bounds = no_external_point_bounds(x, lp, rho=1.0, turnover_cap=0.5)
if bounds.regime != 'subcritical':
    raise RuntimeError('unexpected cap regime')
if not np.all(bounds.lambda_lower <= bounds.lambda_supremum):
    raise RuntimeError('invalid endpoint order')
witness = interval_feasibility_certificate(
    np.array([1.0, 3.0]), np.array([0.0, 2.0]), np.array([0.0, 2.0]), turnover_cap=0.5
)
if witness is None or witness['type'] != 'directed_lipschitz':
    raise RuntimeError('expected infeasibility witness was not returned')
print('installed adapter and certification smoke passed')
""".strip()


def clean_environment_tasks() -> dict:
    with tempfile.TemporaryDirectory(prefix="affine-h5-") as temporary:
        temporary_path = Path(temporary)
        environment_path = temporary_path / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=True).create(environment_path)
        python = environment_path / "bin" / "python"
        clean_env = dict(os.environ)
        clean_env.pop("PYTHONPATH", None)
        install = run(
            [str(python), "-m", "pip", "install", "--no-build-isolation", "--no-deps", str(ROOT)],
            cwd=temporary_path,
            environment=clean_env,
        )
        tasks = [install]
        if install["exit_code"] == 0:
            for optimized in (False, True):
                command = [str(python)]
                if optimized:
                    command.append("-O")
                command.extend(["-c", installed_smoke_source()])
                tasks.append(run(command, cwd=temporary_path, environment=clean_env))
        return {
            "isolation": (
                "Fresh virtual environment and local wheel installation without PYTHONPATH; "
                "scientific dependencies are inherited from the qualified host environment."
            ),
            "tasks": tasks,
            "passed": len(tasks) == 3 and all(task["exit_code"] == 0 for task in tasks),
        }


def source_tasks() -> dict:
    source_python = os.environ.get("H5_SOURCE_PYTHON")
    if not source_python:
        raise RuntimeError("H5_SOURCE_PYTHON must name the dependency-qualified interpreter")
    qualification = run(
        [source_python, "-c", "import numpy, scipy; print(numpy.__version__, scipy.__version__)"],
        cwd=ROOT,
        environment=dict(os.environ),
    )
    if qualification["exit_code"] != 0:
        return {"interpreter_qualification": qualification, "tasks": [], "passed": False}
    environment = {**os.environ, "PYTHONPATH": str(ROOT)}
    commands = []
    for optimized in (False, True):
        prefix = [source_python]
        if optimized:
            prefix.append("-O")
        commands.extend(
            [
                prefix + ["-m", "unittest", "affine_diversification.test_affine_fibre", "-v"],
                prefix + ["verification/run_protocol_controls.py"],
                prefix + ["verification/run_negative_controls.py"],
            ]
        )
    tasks = [run(command, cwd=ROOT, environment=environment) for command in commands]
    return {
        "interpreter_qualification": qualification,
        "tasks": tasks,
        "passed": len(tasks) == 6 and all(task["exit_code"] == 0 for task in tasks),
    }


def runtime_assessment() -> dict:
    stage2 = json.loads((EXECUTION_DIR / "STOCHASTIC_STAGE2_EXECUTION_RECEIPT.json").read_text())
    if stage2.get("status") != "SEALED_COMPLETE" or stage2.get("complete_result_cells") != 1100:
        raise RuntimeError("H5 runtime assessment requires the sealed complete Stage-2 ledger")

    grouped: defaultdict[tuple[str, int, float], list[dict]] = defaultdict(list)
    censored = 0
    for path in sorted(RESULT_DIR.glob("*.json")):
        result = json.loads(path.read_text())
        cell = result["cell"]
        if cell["explorer"] != "crabs_rejection":
            continue
        if result["status"] == "CENSORED_STRUCTURAL_NONTERMINATION":
            censored += 1
            continue
        key = (cell["signal_id"], int(cell["grid_knots"]), float(cell["turnover_cap"]))
        grouped[key].append(result)

    pair_records = []
    all_certificate_times = []
    all_exploration_times = []
    for (signal_id, knots, cap), results in sorted(grouped.items()):
        exemplar = results[0]
        tau = np.asarray(exemplar["input"]["time"], dtype=float)
        lambda_p = np.asarray(exemplar["input"]["lambda_p"], dtype=float)
        timings = []
        for _ in range(REPETITIONS):
            started = time.perf_counter()
            scale = pulled_scale(tau, lambda_p)
            bounds = no_external_point_bounds(scale, lambda_p, rho=1.0, turnover_cap=cap)
            if not np.all(bounds.lambda_lower <= bounds.lambda_supremum):
                raise RuntimeError("certification benchmark produced invalid endpoint order")
            timings.append(time.perf_counter() - started)
        certificate_median = statistics.median(timings)
        exploration_times = [float(result["sampling"]["elapsed_seconds"]) for result in results]
        exploration_median = statistics.median(exploration_times)
        threshold = max(2.0, 0.05 * exploration_median)
        pair_records.append(
            {
                "signal_id": signal_id,
                "grid_knots": knots,
                "turnover_cap": cap,
                "paired_cells": len(results),
                "certification_repetitions": REPETITIONS,
                "median_certification_seconds": certificate_median,
                "median_exploration_seconds": exploration_median,
                "allowed_seconds": threshold,
                "passed": certificate_median <= threshold,
            }
        )
        all_certificate_times.extend([certificate_median] * len(results))
        all_exploration_times.extend(exploration_times)

    overall_certificate = statistics.median(all_certificate_times)
    overall_exploration = statistics.median(all_exploration_times)
    overall_threshold = max(2.0, 0.05 * overall_exploration)
    return {
        "rule": "median certification wall time <= max(2 seconds, 0.05*paired exploration wall time)",
        "pairing": "Unique signal/grid/cap certification task paired to noncensored registered CRABS-rejection cells.",
        "paired_cells": len(all_exploration_times),
        "structurally_censored_unpaired_cells": censored,
        "median_certification_seconds": overall_certificate,
        "median_paired_exploration_seconds": overall_exploration,
        "allowed_seconds": overall_threshold,
        "pair_records": pair_records,
        "passed": overall_certificate <= overall_threshold and all(record["passed"] for record in pair_records),
    }


def main() -> None:
    if not STAGE1_RECEIPT.is_file():
        raise RuntimeError("corrected H5 run requires the preserved Stage-1 incident receipt")
    clean = clean_environment_tasks()
    source = source_tasks()
    runtime = runtime_assessment()
    passed = clean["passed"] and source["passed"] and runtime["passed"]
    receipt = {
        "schema_version": "1.0.0",
        "status": "PASS" if passed else "FAIL",
        "hypothesis": "H5",
        "correction": {
            "parent_failed_receipt": STAGE1_RECEIPT.name,
            "parent_failed_receipt_sha256": hashlib.sha256(STAGE1_RECEIPT.read_bytes()).hexdigest(),
            "scope": (
                "Interpreter qualification only: Stage 1 selected a Python without SciPy, so the unit suite "
                "failed during import before executing tests. No scientific result, task, or threshold changed."
            ),
        },
        "python": sys.version,
        "platform": platform.platform(),
        "clean_environment": clean,
        "normal_and_optimized_source_tasks": source,
        "runtime": runtime,
        "assurance_boundary": (
            "This evaluates the frozen H5 software and performance gate on the qualified host. "
            "It is not cross-platform usability evidence or external software review."
        ),
        "public_release_authorized": False,
    }
    write_new_or_identical(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
