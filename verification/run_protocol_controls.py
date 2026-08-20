"""Run pre-execution analytic and semantic controls for the frozen protocol.

This runner generates no confirmatory outcome. All release-critical checks use
explicit exceptions rather than Python assertions, so optimized mode is a
meaningful negative control.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from affine_diversification.affine_fibre import (
    minimum_turnover_cap_for_intervals,
    no_external_point_bounds,
    pulled_scale,
    sharp_envelopes,
)
from verification.crabs_adapter_contract import (
    ProtocolViolation,
    validate_request,
    validate_response,
    vector_hash,
)
from verification.independent_affine_oracle import (
    minimum_turnover_cap,
    point_bounds,
    pulled_scale as oracle_pulled_scale,
    sharp_envelopes as oracle_sharp_envelopes,
)

PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def close(observed: float, expected: float) -> bool:
    if math.isinf(expected):
        return math.isinf(observed) and observed > 0
    return abs(observed - expected) <= 5e-12 * max(1.0, abs(observed), abs(expected))


def analytic_controls() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    tau = [0.0, 1.0, 2.0, 5.0]
    lp = [0.2, 0.2, 0.2, 0.2]
    production_scale = pulled_scale(tau, lp).tolist()
    oracle_scale = [float(value) for value in oracle_pulled_scale(tau, lp)]
    require(all(close(a, b) for a, b in zip(production_scale, oracle_scale)), "pulled-scale oracle mismatch")
    require(close(production_scale[-1], math.e), "constant-signal analytic scale mismatch")
    results.append({"control": "constant_pulled_scale", "status": "PASS"})

    cases = [
        ([1.0, 2.0, 4.0], [0.2, 0.3, 0.1], 1.0, 0.0),
        ([1.0, 1.5, 8.0], [0.05, 0.2, 0.4], 0.5, 0.75),
        ([1.0, 2.0, 100.0], [0.1, 0.1, 0.1], 0.7, 1.0),
        ([1.0, 4.99, 5.0, 6.0], [0.2, 0.2, 0.2, 0.2], 0.8, 1.2),
    ]
    for index, (x, rates, rho, cap) in enumerate(cases):
        production = no_external_point_bounds(x, rates, rho=rho, turnover_cap=cap)
        oracle = point_bounds(x, rates, rho=rho, turnover_cap=cap)
        for observed, target in zip(production.lambda_lower, oracle["lambda_lower"]):
            require(close(float(observed), float(target)), f"lower endpoint mismatch in analytic case {index}")
        for observed, target in zip(production.lambda_supremum, oracle["lambda_supremum"]):
            target_float = float("inf") if target is None else float(target)
            require(close(float(observed), target_float), f"upper endpoint mismatch in analytic case {index}")
        require(production.regime == oracle["regime"], f"regime mismatch in analytic case {index}")
    results.append({"control": "point_bounds_cross_implementation", "cases": len(cases), "status": "PASS"})

    evaluation = np.linspace(1.0, 7.0, 31)
    constraint_x = [1.0, 2.5, 4.0, 7.0]
    lower = [0.2, 0.5, 1.0, 2.0]
    upper = [0.2, 0.7, 1.3, 2.4]
    cap = 0.6
    production_env = sharp_envelopes(evaluation, constraint_x, lower, upper, turnover_cap=cap)
    oracle_env = oracle_sharp_envelopes(evaluation, constraint_x, lower, upper, turnover_cap=cap)
    require(production_env.feasible == oracle_env["feasible"], "envelope feasibility mismatch")
    require(all(close(float(a), float(b)) for a, b in zip(production_env.lower_n, oracle_env["lower_n"])), "lower envelope mismatch")
    require(all(close(float(a), float(b)) for a, b in zip(production_env.upper_n, oracle_env["upper_n"])), "upper envelope mismatch")
    results.append({"control": "constraint_envelopes_cross_implementation", "status": "PASS"})

    infeasible_lower = [0.2, 2.0]
    infeasible_upper = [0.2, 2.0]
    production_bad = sharp_envelopes([1.0, 3.0], [1.0, 3.0], infeasible_lower, infeasible_upper, turnover_cap=0.5)
    oracle_bad = oracle_sharp_envelopes([1.0, 3.0], [1.0, 3.0], infeasible_lower, infeasible_upper, turnover_cap=0.5)
    require(not production_bad.feasible and not oracle_bad["feasible"], "known infeasibility not detected")
    require(production_bad.certificate and oracle_bad["certificate"], "infeasibility witness absent")
    results.append({"control": "known_infeasible_case", "status": "PASS"})

    cap_prod, _ = minimum_turnover_cap_for_intervals(constraint_x, lower, upper)
    cap_oracle, _ = minimum_turnover_cap(constraint_x, lower, upper)
    require(cap_oracle is not None and close(cap_prod, float(cap_oracle)), "minimum-cap oracle mismatch")
    results.append({"control": "minimum_cap_cross_implementation", "status": "PASS"})
    return results


def baseline_records() -> tuple[dict, dict, dict]:
    grid = [0.0, 1.0, 2.0]
    lp = [0.2, 0.2, 0.2]
    pdelta = [0.2, 0.2, 0.2]
    request = {
        "schema_version": "1.0.0",
        "mode": "verify_both",
        "time_grid": grid,
        "equal_grid_declared": True,
        "interpolation": "piecewise_linear",
        "units": {"time": "myr", "rate": "per_myr"},
        "rho": 1.0,
        "pulled_speciation": {"values": lp, "sha256": vector_hash(lp)},
        "pulled_net_diversification": {"values": pdelta, "sha256": vector_hash(pdelta)},
        "reference_model": {"lambda": lp, "mu": [0.0, 0.0, 0.0]},
        "crabs": {"version": "1.2.0.9001", "commit": "f2af9b6c8bb93f5512c2882d2e816060c9e07728"},
        "sampling_ledger": {"requested_samples": 100, "returned_models": 101, "attempts": 125, "accepted": 100, "rejected": 25},
    }
    x = [float(value) for value in oracle_pulled_scale(grid, lp)]
    oracle = point_bounds(x, lp, rho=1.0, turnover_cap=0.5)
    source_hash = hashlib.sha256(b"frozen-adapter-fixture\n").hexdigest()
    expected = {
        "feasible": True,
        "lambda_lower": [float(value) for value in oracle["lambda_lower"]],
        "lambda_upper": [float("inf") if value is None else float(value) for value in oracle["lambda_supremum"]],
        "source_hash": source_hash,
        "max_abs_pdelta": max(abs(value) for value in pdelta),
    }
    response = {
        "schema_version": "1.0.0",
        "feasible": True,
        "lambda_lower": expected["lambda_lower"].copy(),
        "lambda_upper": ["Infinity" if math.isinf(value) else value for value in expected["lambda_upper"]],
        "max_recurrence_residual": 0.0,
        "source_hash": source_hash,
    }
    return request, response, expected


def mutation_controls() -> list[dict[str, object]]:
    mutations = {}

    def register(name: str, mutate) -> None:
        mutations[name] = mutate

    register("swap_endpoints", lambda q, s, e: (q, {**s, "lambda_lower": e["lambda_upper"], "lambda_upper": e["lambda_lower"]}, e))
    register("perturb_endpoint", lambda q, s, e: (q, {**s, "lambda_lower": [s["lambda_lower"][0], s["lambda_lower"][1] + 0.001, s["lambda_lower"][2]]}, e))
    register("flip_feasibility", lambda q, s, e: (q, {**s, "feasible": False}, e))
    register("reverse_grid", lambda q, s, e: ({**q, "time_grid": list(reversed(q["time_grid"]))}, s, e))
    register("unequal_grid_declared_equal", lambda q, s, e: ({**q, "time_grid": [0.0, 1.0, 2.1]}, s, e))
    register("change_units", lambda q, s, e: ({**q, "units": {"time": "years", "rate": "per_year"}}, s, e))
    register("flip_recurrence_sign", lambda q, s, e: (q, {**s, "max_recurrence_residual": 0.25}, e))

    def substitute_pdelta(q: dict, s: dict, e: dict):
        q2 = copy.deepcopy(q)
        values = [0.21, 0.21, 0.21]
        q2["pulled_speciation"] = {"values": values, "sha256": vector_hash(values)}
        return q2, s, e

    register("substitute_pdelta_for_lambda_p", substitute_pdelta)
    register("change_rho_without_conditioning", lambda q, s, e: ({**q, "rho": 0.75}, s, e))

    def miscount_reference(q: dict, s: dict, e: dict):
        q2 = copy.deepcopy(q); q2["sampling_ledger"]["returned_models"] = 100
        return q2, s, e

    register("miscount_retained_reference", miscount_reference)

    def misreport_rejections(q: dict, s: dict, e: dict):
        q2 = copy.deepcopy(q); q2["sampling_ledger"]["rejected"] = 24
        return q2, s, e

    register("misreport_rejections", misreport_rejections)
    register("alter_source_hash", lambda q, s, e: (q, {**s, "source_hash": "0" * 64}, e))

    protocol = json.loads((PROTOCOL_DIR / "PREREGISTRATION.json").read_text())
    declared = protocol["negative_controls"]
    require(set(mutations) == set(declared), "implemented negative controls differ from preregistration")
    results = []
    for name in declared:
        request, response, expected = baseline_records()
        mutated_request, mutated_response, mutated_expected = mutations[name](request, response, expected)
        caught = False
        reason = None
        try:
            validate_request(mutated_request)
            validate_response(mutated_response, mutated_expected)
        except ProtocolViolation as exc:
            caught = True
            reason = str(exc)
        require(caught, f"negative control escaped detection: {name}")
        results.append({"control": name, "status": "PASS", "caught_reason": reason})
    return results


def verify_frozen_assets() -> dict[str, object]:
    required = [
        "PREREGISTRATION.json", "synthetic_signal_specs.json", "synthetic_signals.json",
        "CELL_MANIFEST.jsonl", "CELL_MANIFEST.summary.json", "PROTOCOL.sha256",
        "PROTOCOL_MANIFEST.sha256",
    ]
    missing = [name for name in required if not (PROTOCOL_DIR / name).is_file()]
    require(not missing, f"missing frozen assets: {missing}")
    for line in (PROTOCOL_DIR / "PROTOCOL_MANIFEST.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        observed = hashlib.sha256((PROTOCOL_DIR / name).read_bytes()).hexdigest()
        require(observed == digest, f"protocol manifest mismatch: {name}")
    summary = json.loads((PROTOCOL_DIR / "CELL_MANIFEST.summary.json").read_text())
    require(summary["total_cells"] == 3044, "unexpected total cell count")
    require(summary["confirmatory_outcomes_generated"] is False, "confirmatory outcome flag must be false")
    return {"control": "frozen_asset_manifest", "status": "PASS", "total_cells": summary["total_cells"]}


def main() -> None:
    validate_request(baseline_records()[0])
    validate_response(baseline_records()[1], baseline_records()[2])
    controls = analytic_controls() + mutation_controls() + [verify_frozen_assets()]
    receipt = {
        "schema_version": "1.0.0",
        "status": "PASS",
        "python_optimized": sys.flags.optimize > 0,
        "confirmatory_outcomes_generated": False,
        "controls": controls,
        "control_count": len(controls),
    }
    output = ROOT / "outputs" / ("protocol_controls_optimized.json" if sys.flags.optimize else "protocol_controls_normal.json")
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
