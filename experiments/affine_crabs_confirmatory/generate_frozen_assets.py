"""Generate outcome-blind protocol inputs and the complete cell manifest.

This script never imports the production affine implementation and never runs
CRABS. It is safe to execute before confirmatory authorization.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
R_INT_MAX = 2_147_483_646


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite frozen file with different bytes: {path}")
    path.write_bytes(payload)


def signal_value(signal_id: str, z: float) -> float:
    if signal_id == "constant":
        return 0.2
    if signal_id == "monotone_increasing":
        return 0.05 + 0.30 * z
    if signal_id == "monotone_decreasing":
        return 0.35 - 0.30 * z
    if signal_id == "unimodal":
        return 0.05 + 0.35 * math.exp(-((z - 0.5) / 0.18) ** 2)
    if signal_id == "abrupt_change":
        return 0.08 if z < 0.5 else 0.33
    if signal_id == "oscillatory":
        return 0.20 + 0.12 * math.sin(4.0 * math.pi * z)
    if signal_id == "near_zero_positive":
        return 0.005 + 0.15 * z * z
    if signal_id == "high_dynamic_range":
        return 0.01 * math.exp(math.log(50.0) * z)
    raise ValueError(f"unknown synthetic signal: {signal_id}")


def derived_seed(cell_without_seed: dict) -> int:
    digest = hashlib.sha256(canonical_bytes(cell_without_seed)).hexdigest()
    return int(digest[:8], 16) % R_INT_MAX + 1


def build_signals(spec: dict, grids: list[int]) -> dict:
    output: dict[str, object] = {
        "schema_version": "1.0.0",
        "domain_tau": spec["domain_tau"],
        "interpolation": "piecewise_linear",
        "signals": [],
    }
    for family in spec["families"]:
        grids_out = []
        for knots in grids:
            tau = [5.0 * i / (knots - 1) for i in range(knots)]
            values = [signal_value(family["id"], t / 5.0) for t in tau]
            grid = {"knots": knots, "tau": tau, "lambda_p": values}
            grid["sha256"] = hashlib.sha256(canonical_bytes(grid)).hexdigest()
            grids_out.append(grid)
        output["signals"].append({"id": family["id"], "grids": grids_out})
    return output


def build_cells(protocol: dict) -> list[dict]:
    cells: list[dict] = []
    det = protocol["deterministic_validation"]
    for signal in det["signal_ids"]:
        for rho in det["rho_levels"]:
            for cap in det["turnover_cap_levels"]:
                for knots in det["grid_knot_counts"]:
                    for constraint in det["constraint_regimes"]:
                        cell = {
                            "layer": "deterministic",
                            "signal_id": signal,
                            "rho": rho,
                            "turnover_cap": cap,
                            "grid_knots": knots,
                            "constraint_regime": constraint,
                            "crabs_matched": rho == 1.0,
                        }
                        cell["cell_id"] = hashlib.sha256(canonical_bytes(cell)).hexdigest()[:20]
                        cells.append(cell)

    stochastic = protocol["stochastic_benchmark"]
    for signal in stochastic["signal_ids"]:
        for knots in stochastic["grid_knot_counts"]:
            for replicate in range(1, stochastic["replicates"] + 1):
                for explorer in stochastic["native_unconstrained"]["explorers"]:
                    cell = {
                        "layer": "stochastic",
                        "task": "native_unconstrained",
                        "signal_id": signal,
                        "grid_knots": knots,
                        "replicate": replicate,
                        "explorer": explorer,
                        "accepted_cloud_prefixes": stochastic["accepted_cloud_prefixes"],
                    }
                    cell["seed"] = derived_seed(cell)
                    cell["cell_id"] = hashlib.sha256(canonical_bytes(cell)).hexdigest()[:20]
                    cells.append(cell)
                for cap in stochastic["cap_matched"]["turnover_cap_levels"]:
                    for explorer in stochastic["cap_matched"]["explorers"]:
                        cell = {
                            "layer": "stochastic",
                            "task": "cap_matched",
                            "signal_id": signal,
                            "rho": 1.0,
                            "turnover_cap": cap,
                            "grid_knots": knots,
                            "replicate": replicate,
                            "explorer": explorer,
                            "accepted_cloud_prefixes": stochastic["accepted_cloud_prefixes"],
                            "proposal_ceiling": stochastic["proposal_ceiling"]["resolved_value"],
                        }
                        cell["seed"] = derived_seed(cell)
                        cell["cell_id"] = hashlib.sha256(canonical_bytes(cell)).hexdigest()[:20]
                        cells.append(cell)
    return cells


def main() -> None:
    protocol_path = ROOT / "PREREGISTRATION.json"
    spec_path = ROOT / "synthetic_signal_specs.json"
    protocol = json.loads(protocol_path.read_text())
    specs = json.loads(spec_path.read_text())
    signals = build_signals(specs, protocol["deterministic_validation"]["grid_knot_counts"])
    cells = build_cells(protocol)

    deterministic = sum(c["layer"] == "deterministic" for c in cells)
    stochastic = sum(c["layer"] == "stochastic" for c in cells)
    native = sum(c.get("task") == "native_unconstrained" for c in cells)
    matched = sum(c.get("task") == "cap_matched" for c in cells)
    expected = (
        protocol["deterministic_validation"]["planned_cells"],
        protocol["stochastic_benchmark"]["total_planned_cells"],
        protocol["stochastic_benchmark"]["native_unconstrained"]["planned_cells"],
        protocol["stochastic_benchmark"]["cap_matched"]["planned_cells"],
    )
    observed = deterministic, stochastic, native, matched
    if observed != expected:
        raise RuntimeError(f"cell-count mismatch: observed={observed}, expected={expected}")
    ids = [c["cell_id"] for c in cells]
    if len(ids) != len(set(ids)):
        raise RuntimeError("cell_id collision")
    stochastic_seeds = [c["seed"] for c in cells if c["layer"] == "stochastic"]
    if len(stochastic_seeds) != len(set(stochastic_seeds)):
        raise RuntimeError("derived stochastic seed collision")

    write_frozen(ROOT / "synthetic_signals.json", canonical_bytes(signals))
    manifest_bytes = b"".join(canonical_bytes(cell) for cell in cells)
    write_frozen(ROOT / "CELL_MANIFEST.jsonl", manifest_bytes)
    summary = {
        "schema_version": "1.0.0",
        "deterministic_cells": deterministic,
        "stochastic_cells": stochastic,
        "native_unconstrained_cells": native,
        "cap_matched_cells": matched,
        "total_cells": len(cells),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "unique_cell_ids": True,
        "unique_stochastic_seeds": True,
        "confirmatory_outcomes_generated": False,
    }
    write_frozen(ROOT / "CELL_MANIFEST.summary.json", canonical_bytes(summary))

    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    write_frozen(ROOT / "PROTOCOL.sha256", f"{protocol_hash}  PREREGISTRATION.json\n".encode())
    names = [
        "PREREGISTRATION.json",
        "synthetic_signal_specs.json",
        "synthetic_signals.json",
        "CELL_MANIFEST.jsonl",
        "CELL_MANIFEST.summary.json",
        "PROTOCOL.sha256",
    ]
    lines = []
    for name in names:
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}\n")
    write_frozen(ROOT / "PROTOCOL_MANIFEST.sha256", "".join(lines).encode())
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
