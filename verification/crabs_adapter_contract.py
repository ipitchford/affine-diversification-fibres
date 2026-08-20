"""Fail-closed semantic validator for CRABS/affine adapter records."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


class ProtocolViolation(ValueError):
    pass


def vector_hash(values: list[float]) -> str:
    payload = (json.dumps(values, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProtocolViolation(message)


def _finite_vector(value: Any, name: str, expected: int | None = None) -> list[float]:
    _require(isinstance(value, list) and len(value) >= 2, f"{name} must be an array of length >=2")
    out = [float(item) for item in value]
    _require(all(math.isfinite(item) for item in out), f"{name} contains non-finite values")
    if expected is not None:
        _require(len(out) == expected, f"{name} length mismatch")
    return out


def validate_request(record: dict[str, Any]) -> None:
    required = {
        "schema_version", "mode", "time_grid", "equal_grid_declared", "interpolation",
        "units", "rho", "pulled_speciation", "crabs", "sampling_ledger",
    }
    _require(set(record) >= required, f"missing request fields: {sorted(required - set(record))}")
    _require(record["schema_version"] == "1.0.0", "unsupported schema version")
    _require(record["mode"] in {"from_pulled_speciation", "from_reference_model", "verify_both"}, "invalid mode")
    grid = _finite_vector(record["time_grid"], "time_grid")
    _require(all(b > a for a, b in zip(grid, grid[1:])), "time grid must be strictly increasing")
    steps = [b - a for a, b in zip(grid, grid[1:])]
    tolerance = 64.0 * math.ulp(max(1.0, max(abs(step) for step in steps)))
    _require(bool(record["equal_grid_declared"]), "equal-grid declaration required")
    _require(max(steps) - min(steps) <= tolerance, "grid is not equal-spaced")
    _require(record["interpolation"] == "piecewise_linear", "unsupported interpolation")
    _require(record["units"] == {"time": "myr", "rate": "per_myr"}, "unit declaration mismatch")
    rho = float(record["rho"])
    _require(math.isfinite(rho) and 0.0 < rho <= 1.0, "rho outside (0,1]")

    pulled = record["pulled_speciation"]
    lp = _finite_vector(pulled.get("values"), "pulled_speciation.values", len(grid))
    _require(all(value >= 0.0 for value in lp), "negative pulled speciation")
    _require(pulled.get("sha256") == vector_hash(lp), "pulled-speciation hash mismatch")
    crabs = record["crabs"]
    _require(crabs.get("commit") == "f2af9b6c8bb93f5512c2882d2e816060c9e07728", "unfrozen CRABS commit")
    _require(crabs.get("version") in {"1.2.0", "1.2.0.9001"}, "unfrozen CRABS version")

    ledger = record["sampling_ledger"]
    requested = int(ledger.get("requested_samples", -1))
    returned = int(ledger.get("returned_models", -1))
    attempts = int(ledger.get("attempts", -1))
    accepted = int(ledger.get("accepted", -1))
    rejected = int(ledger.get("rejected", -1))
    _require(min(requested, returned, attempts, accepted, rejected) >= 0, "negative sampling ledger count")
    _require(returned == requested + 1, "CRABS retained-reference count mismatch")
    _require(attempts == accepted + rejected, "proposal accounting mismatch")
    _require(accepted == requested, "accepted/requested count mismatch")

    if record["mode"] in {"from_reference_model", "verify_both"}:
        _require("reference_model" in record, "reference_model required")
        ref = record["reference_model"]
        ref_lambda = _finite_vector(ref.get("lambda"), "reference_model.lambda", len(grid))
        ref_mu = _finite_vector(ref.get("mu"), "reference_model.mu", len(grid))
        _require(rho == 1.0, "confirmatory CRABS matching is restricted to rho=1")
        _require(all(abs(a - b) <= 5e-12 * max(1.0, abs(a), abs(b)) for a, b in zip(ref_lambda, lp)), "reference lambda does not equal lambda_p bridge")
        _require(all(value == 0.0 for value in ref_mu), "reference mu must be zero for the frozen bridge")
    if record["mode"] == "verify_both":
        _require("pulled_net_diversification" in record, "p.delta required in verify_both mode")
        pdelta = record["pulled_net_diversification"]
        pd = _finite_vector(pdelta.get("values"), "pulled_net_diversification.values", len(grid))
        _require(pdelta.get("sha256") == vector_hash(pd), "p.delta hash mismatch")


def validate_response(record: dict[str, Any], expected: dict[str, Any]) -> None:
    required = {"schema_version", "feasible", "lambda_lower", "lambda_upper", "max_recurrence_residual", "source_hash"}
    _require(set(record) >= required, f"missing response fields: {sorted(required - set(record))}")
    _require(record["schema_version"] == "1.0.0", "unsupported response schema")
    lower = _finite_vector(record["lambda_lower"], "lambda_lower")
    upper_raw = record["lambda_upper"]
    _require(isinstance(upper_raw, list) and len(upper_raw) == len(lower), "lambda_upper length mismatch")
    upper = [float("inf") if item == "Infinity" else float(item) for item in upper_raw]
    _require(all(math.isfinite(item) or item == float("inf") for item in upper), "invalid upper endpoint")
    _require(all(lo <= hi for lo, hi in zip(lower, upper)), "lower endpoint exceeds upper endpoint")
    _require(bool(record["feasible"]) == bool(expected["feasible"]), "feasibility verdict mismatch")
    _require(record["source_hash"] == expected["source_hash"], "source hash mismatch")
    residual = float(record["max_recurrence_residual"])
    scale = max(1.0, float(expected.get("max_abs_pdelta", 1.0)))
    _require(math.isfinite(residual) and residual <= 1e-10 * scale, "recurrence residual exceeds tolerance")

    expected_lower = expected["lambda_lower"]
    expected_upper = expected["lambda_upper"]
    _require(len(lower) == len(expected_lower), "expected endpoint length mismatch")
    for observed, target in zip(lower, expected_lower):
        _require(abs(observed - target) <= 5e-12 * max(1.0, abs(observed), abs(target)), "lower endpoint disagreement")
    for observed, target in zip(upper, expected_upper):
        if math.isinf(target):
            _require(math.isinf(observed) and observed > 0, "upper infinity mismatch")
        else:
            _require(abs(observed - target) <= 5e-12 * max(1.0, abs(observed), abs(target)), "upper endpoint disagreement")
