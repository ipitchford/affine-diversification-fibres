#!/usr/bin/env python3
"""Execute every registered deterministic cell with an independent oracle."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from affine_diversification.affine_fibre import (  # noqa: E402
    no_external_point_bounds,
    pulled_scale,
    sharp_envelopes,
)
from verification.independent_affine_oracle import (  # noqa: E402
    point_bounds as oracle_point_bounds,
    pulled_scale as oracle_pulled_scale,
    sharp_envelopes as oracle_sharp_envelopes,
)


TOLERANCE = 5e-12
FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)
TURNOVER_PATTERN = (0.2, 0.6, 0.4, 0.8)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def require_clean_execution_sources() -> None:
    allowed_prefix = "experiments/affine_crabs_confirmatory/execution/results/"
    dirty = []
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith(allowed_prefix):
            dirty.append(line)
    if dirty:
        raise RuntimeError(f"execution sources are not clean: {dirty}")


def encode_number(value: float) -> float | str:
    number = float(value)
    if math.isinf(number):
        return "+Infinity" if number > 0 else "-Infinity"
    if math.isnan(number):
        return "NaN"
    return number


def encode_vector(values: Iterable[float]) -> list[float | str]:
    return [encode_number(value) for value in values]


def close(left: float, right: float) -> bool:
    if math.isinf(left) or math.isinf(right):
        return math.isinf(left) and math.isinf(right) and (left > 0) == (right > 0)
    return abs(left - right) <= TOLERANCE * max(1.0, abs(left), abs(right))


def comparison(left: Iterable[float], right: Iterable[float]) -> dict[str, object]:
    pairs = [(float(a), float(b)) for a, b in zip(left, right)]
    mismatches = [index for index, (a, b) in enumerate(pairs) if not close(a, b)]
    normalized = []
    absolute = []
    for a, b in pairs:
        if math.isinf(a) or math.isinf(b):
            if close(a, b):
                continue
            normalized.append(float("inf"))
            absolute.append(float("inf"))
        else:
            absolute.append(abs(a - b))
            normalized.append(abs(a - b) / max(1.0, abs(a), abs(b)))
    return {
        "passed": not mismatches,
        "mismatch_count": len(mismatches),
        "first_mismatch_index": mismatches[0] if mismatches else None,
        "max_abs_difference": encode_number(max(absolute, default=0.0)),
        "max_normalized_difference": encode_number(max(normalized, default=0.0)),
    }


def load_signal(signal_id: str, knots: int, synthetic: dict) -> tuple[list[float], list[float], str]:
    if signal_id == "crabs_primates_ebd":
        path = PROTOCOL_DIR / "execution" / "qualification" / f"crabs_primates_ebd_{knots:03d}.csv"
        receipt = json.loads((PROTOCOL_DIR / "execution" / "qualification" / "PRIMATES_QUALIFICATION_RECEIPT.json").read_text())
        if receipt["status"] != "QUALIFIED_ELIGIBLE":
            raise RuntimeError("primates qualification is not eligible")
        expected = receipt["resampled_grids"][str(knots)]["sha256"]
        if sha256(path) != expected:
            raise RuntimeError("primates grid hash differs from qualification receipt")
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        return [float(row["time"]) for row in rows], [float(row["lambda_p"]) for row in rows], expected
    for signal in synthetic["signals"]:
        if signal["id"] != signal_id:
            continue
        for grid in signal["grids"]:
            if grid["knots"] == knots:
                return list(grid["tau"]), list(grid["lambda_p"]), str(grid["sha256"])
    raise RuntimeError(f"registered signal/grid not found: {signal_id}/{knots}")


def constraint_indices(knots: int) -> list[int]:
    return list(dict.fromkeys(int(math.floor(fraction * (knots - 1) + 0.5)) for fraction in FRACTIONS))


def construct_constraints(x: list[float], rho: float, cap: float, regime: str) -> dict[str, object] | None:
    if regime == "none":
        return None
    indices = constraint_indices(len(x))
    locations = [x[index] for index in indices]
    anchor = 1.0 - rho
    witness = [anchor]
    for index in range(1, len(locations)):
        epsilon = cap * TURNOVER_PATTERN[(index - 1) % len(TURNOVER_PATTERN)]
        witness.append(witness[-1] + epsilon * (locations[index] - locations[index - 1]))
    half_width = 0.02 * max(1.0, x[-1] - 1.0)
    lower = [anchor]
    upper = [anchor]
    for value in witness[1:]:
        lower.append(max(anchor, value - half_width))
        upper.append(value + half_width)
    if regime == "known_infeasible":
        margin = 0.01 * max(1.0, x[-1] - 1.0)
        forced = upper[-2] + cap * (locations[-1] - locations[-2]) + margin
        lower[-1] = forced
        upper[-1] = forced
    return {
        "indices": indices,
        "x": locations,
        "lower_n": lower,
        "upper_n": upper,
        "witness_n": witness,
        "band_half_width": half_width,
    }


def oracle_float(values: Iterable[object | None]) -> list[float]:
    return [float("inf") if value is None else float(value) for value in values]


def execute_cell(cell: dict, synthetic: dict, bindings: dict[str, str]) -> dict[str, object]:
    started = time.perf_counter()
    tau, lambda_p, input_hash = load_signal(cell["signal_id"], int(cell["grid_knots"]), synthetic)
    rho = float(cell["rho"])
    cap = float(cell["turnover_cap"])

    production_x = pulled_scale(tau, lambda_p).tolist()
    independent_x_decimal = oracle_pulled_scale(tau, lambda_p)
    independent_x = [float(value) for value in independent_x_decimal]
    production = no_external_point_bounds(production_x, lambda_p, rho=rho, turnover_cap=cap)
    independent = oracle_point_bounds(independent_x_decimal, lambda_p, rho=rho, turnover_cap=cap)

    checks: dict[str, object] = {
        "pulled_scale": comparison(production_x, independent_x),
        "q_infimum": comparison(production.q_infimum, oracle_float(independent["q_infimum"])),
        "q_upper": comparison(production.q_upper, oracle_float(independent["q_upper"])),
        "lambda_lower": comparison(production.lambda_lower, oracle_float(independent["lambda_lower"])),
        "lambda_supremum": comparison(production.lambda_supremum, oracle_float(independent["lambda_supremum"])),
        "regime": {"passed": production.regime == independent["regime"], "production": production.regime, "oracle": independent["regime"]},
        "attainment": {
            "passed": production.lower_endpoint_attained.tolist() == independent["lower_endpoint_attained"],
            "production": production.lower_endpoint_attained.tolist(),
            "oracle": independent["lower_endpoint_attained"],
        },
    }

    constraints_production = construct_constraints(production_x, rho, cap, cell["constraint_regime"])
    constraints_oracle = construct_constraints(independent_x, rho, cap, cell["constraint_regime"])
    envelope_record: dict[str, object] | None = None
    if constraints_production is not None and constraints_oracle is not None:
        prod_env = sharp_envelopes(
            production_x,
            constraints_production["x"],
            constraints_production["lower_n"],
            constraints_production["upper_n"],
            turnover_cap=cap,
        )
        oracle_env = oracle_sharp_envelopes(
            independent_x,
            constraints_oracle["x"],
            constraints_oracle["lower_n"],
            constraints_oracle["upper_n"],
            turnover_cap=cap,
        )
        expected_feasible = cell["constraint_regime"] == "feasible_intervals"
        prod_certificate = prod_env.certificate["type"] if prod_env.certificate else None
        oracle_certificate = oracle_env["certificate"]["type"] if oracle_env["certificate"] else None
        checks["envelope_lower_n"] = comparison(prod_env.lower_n, oracle_float(oracle_env["lower_n"]))
        checks["envelope_upper_n"] = comparison(prod_env.upper_n, oracle_float(oracle_env["upper_n"]))
        checks["feasibility"] = {
            "passed": prod_env.feasible == oracle_env["feasible"] == expected_feasible,
            "production": prod_env.feasible,
            "oracle": oracle_env["feasible"],
            "expected": expected_feasible,
        }
        checks["certificate_type"] = {
            "passed": prod_certificate == oracle_certificate,
            "production": prod_certificate,
            "oracle": oracle_certificate,
        }
        envelope_record = {
            "feasible": prod_env.feasible,
            "certificate": prod_env.certificate,
            "lower_n": encode_vector(prod_env.lower_n),
            "upper_n": encode_vector(prod_env.upper_n),
            "constraint_indices": constraints_production["indices"],
            "constraint_x": encode_vector(constraints_production["x"]),
            "constraint_lower_n": encode_vector(constraints_production["lower_n"]),
            "constraint_upper_n": encode_vector(constraints_production["upper_n"]),
        }

    all_passed = all(bool(value["passed"]) for value in checks.values())
    result = {
        "schema_version": "1.0.0",
        "status": "PASS" if all_passed else "FAIL",
        "layer": "deterministic",
        "cell": cell,
        "bindings": bindings,
        "input": {
            "signal_grid_sha256": input_hash,
            "time": tau,
            "lambda_p": lambda_p,
            "pulled_scale": encode_vector(production_x),
        },
        "production": {
            "q_infimum": encode_vector(production.q_infimum),
            "q_upper": encode_vector(production.q_upper),
            "lambda_lower": encode_vector(production.lambda_lower),
            "lambda_supremum": encode_vector(production.lambda_supremum),
            "regime": production.regime,
            "lower_endpoint_attained": production.lower_endpoint_attained.tolist(),
            "envelopes": envelope_record,
        },
        "oracle_comparisons": checks,
        "H1_pass": all_passed,
        "elapsed_seconds": time.perf_counter() - started,
    }
    result["result_payload_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def write_once(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError(f"refusing to overwrite different result: {path}")
        return "existing"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)
    return "written"


def validate_existing(path: Path, cell: dict, bindings: dict[str, str]) -> dict:
    result = json.loads(path.read_text())
    if result.get("cell") != cell or result.get("bindings") != bindings:
        raise RuntimeError(f"existing result has different bindings: {path}")
    payload_hash = result.pop("result_payload_sha256", None)
    if payload_hash != hashlib.sha256(canonical_bytes(result)).hexdigest():
        raise RuntimeError(f"existing result payload hash invalid: {path}")
    result["result_payload_sha256"] = payload_hash
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--cell-id", action="append", default=[])
    parser.add_argument("--results-dir", type=Path, default=PROTOCOL_DIR / "execution" / "results" / "deterministic")
    args = parser.parse_args()

    require_clean_execution_sources()
    execution_commit = git("rev-parse", "HEAD")
    bindings = {
        "protocol_sha256": sha256(PROTOCOL_DIR / "PREREGISTRATION.json"),
        "cell_manifest_sha256": sha256(PROTOCOL_DIR / "CELL_MANIFEST.jsonl"),
        "amendment_001_sha256": sha256(PROTOCOL_DIR / "AMENDMENT_001_PRE_EXECUTION.json"),
        "amendment_002_sha256": sha256(PROTOCOL_DIR / "AMENDMENT_002_COMMIT_CORRECTION.json"),
        "primates_qualification_receipt_sha256": sha256(
            PROTOCOL_DIR / "execution" / "qualification" / "PRIMATES_QUALIFICATION_RECEIPT.json"
        ),
        "execution_commit": execution_commit,
    }
    synthetic = json.loads((PROTOCOL_DIR / "synthetic_signals.json").read_text())
    cells = [json.loads(line) for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()]
    cells = [cell for cell in cells if cell["layer"] == "deterministic"]
    if args.cell_id:
        wanted = set(args.cell_id)
        cells = [cell for cell in cells if cell["cell_id"] in wanted]
        if len(cells) != len(wanted):
            raise RuntimeError("one or more requested cell ids are not registered deterministic cells")
    if args.limit is not None:
        cells = cells[: args.limit]

    counts = {"written": 0, "existing": 0, "PASS": 0, "FAIL": 0, "ERROR": 0}
    started = time.perf_counter()
    for index, cell in enumerate(cells, start=1):
        path = args.results_dir / f"{cell['cell_id']}.json"
        if path.exists():
            result = validate_existing(path, cell, bindings)
            counts["existing"] += 1
        else:
            try:
                result = execute_cell(cell, synthetic, bindings)
            except Exception as exc:  # preserve registered cell failures and continue
                result = {
                    "schema_version": "1.0.0",
                    "status": "ERROR",
                    "layer": "deterministic",
                    "cell": cell,
                    "bindings": bindings,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "H1_pass": False,
                }
                result["result_payload_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
            write_once(path, canonical_bytes(result))
            counts["written"] += 1
        counts[result["status"]] += 1
        if index % 100 == 0 or index == len(cells):
            print(json.dumps({"completed": index, "total": len(cells), "counts": counts}, sort_keys=True), flush=True)

    summary = {
        "schema_version": "1.0.0",
        "layer": "deterministic",
        "registered_cells": 1944,
        "selected_cells": len(cells),
        "counts": counts,
        "H1_all_selected_pass": counts["PASS"] == len(cells),
        "bindings": bindings,
        "elapsed_seconds": time.perf_counter() - started,
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
