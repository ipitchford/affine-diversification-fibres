#!/usr/bin/env python3
"""Seal the interrupted first stochastic run and its nontermination witness."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
RESULT_DIR = PROTOCOL_DIR / "execution" / "results" / "stochastic"
SAMPLE_DIR = PROTOCOL_DIR / "execution" / "results" / "stochastic_samples"
MANIFEST = PROTOCOL_DIR / "execution" / "STOCHASTIC_STAGE1_MANIFEST.sha256"
RECEIPT = PROTOCOL_DIR / "execution" / "STOCHASTIC_STAGE1_INCIDENT.json"
CRABS_SOURCE = Path(
    "/Users/admin/Documents/Codex/2026-08-20/n-the-0processed-folder-there-is/work/crabs-source/R/sample.rates.R"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_exact(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different Stage-1 seal: {path}")
    path.write_bytes(payload)


def main() -> None:
    cells = [json.loads(line) for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()]
    stochastic = [cell for cell in cells if cell["layer"] == "stochastic"]
    by_id = {cell["cell_id"]: cell for cell in stochastic}
    result_paths = sorted(RESULT_DIR.glob("*.json"))
    status_counts: Counter[str] = Counter()
    explorer_counts: Counter[str] = Counter()
    bindings = None
    manifest_lines: list[str] = []
    for path in result_paths:
        result = json.loads(path.read_text())
        cell_id = result["cell"]["cell_id"]
        if cell_id not in by_id or result["cell"] != by_id[cell_id]:
            raise RuntimeError(f"unregistered or altered Stage-1 cell: {path}")
        if bindings is None:
            bindings = result["bindings"]
        elif bindings != result["bindings"]:
            raise RuntimeError(f"mixed Stage-1 execution bindings: {path}")
        status_counts[result["status"]] += 1
        explorer_counts[result["cell"]["explorer"]] += 1
        sidecar = result["sampling"].get("decision_value_sidecar")
        if sidecar is not None:
            sidecar_path = PROTOCOL_DIR / sidecar["path"]
            if not sidecar_path.is_file() or sha256(sidecar_path) != sidecar["sha256"]:
                raise RuntimeError(f"missing or changed Stage-1 sidecar: {sidecar_path}")
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")
    for path in sorted(SAMPLE_DIR.glob("*.csv")):
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")

    completed_ids = {path.stem for path in result_paths}
    missing = [cell for cell in stochastic if cell["cell_id"] not in completed_ids]
    affected = [
        cell for cell in stochastic
        if cell["signal_id"] == "abrupt_change" and cell["explorer"] in {"crabs_hsmrf", "crabs_gmrf", "crabs_rejection"}
    ]
    witnesses = {}
    for knots in (25, 100):
        candidates = [
            json.loads(path.read_text()) for path in result_paths
            if json.loads(path.read_text())["cell"]["explorer"] == "boundary_constructor"
            and json.loads(path.read_text())["cell"]["signal_id"] == "abrupt_change"
            and json.loads(path.read_text())["cell"]["grid_knots"] == knots
        ]
        maxima = {max(item["exact_endpoints"]["discrete_lower"]) for item in candidates}
        if len(maxima) != 1:
            raise RuntimeError(f"non-unique abrupt lower-path witness for knots={knots}")
        witnesses[str(knots)] = {
            "maximum_required_zero_extinction_lambda": maxima.pop(),
            "frozen_crabs_max_lambda": 2.0,
            "strictly_exceeds_bound": True,
        }
    if not all(item["maximum_required_zero_extinction_lambda"] > 2 for item in witnesses.values()):
        raise RuntimeError("nontermination witness does not exceed the frozen CRABS bound")

    manifest_payload = "".join(manifest_lines).encode()
    write_exact(MANIFEST, manifest_payload)
    receipt = {
        "schema_version": "1.0.0",
        "status": "INTERRUPTED_STRUCTURAL_NONTERMINATION",
        "registered_stochastic_cells": len(stochastic),
        "completed_result_files": len(result_paths),
        "sample_sidecar_files": len(list(SAMPLE_DIR.glob("*.csv"))),
        "missing_cells": len(missing),
        "status_counts": dict(sorted(status_counts.items())),
        "completed_by_explorer": dict(sorted(explorer_counts.items())),
        "bindings": bindings,
        "affected_registered_cells": {
            "count": len(affected),
            "native_unconstrained": sum(cell["task"] == "native_unconstrained" for cell in affected),
            "cap_matched_rejection": sum(cell["explorer"] == "crabs_rejection" for cell in affected),
            "cell_ids": [cell["cell_id"] for cell in affected],
        },
        "proof": {
            "crabs_source_file": "R/sample.rates.R",
            "crabs_source_sha256": sha256(CRABS_SOURCE),
            "source_behavior": "sample.basic.models.joint repeats while !in_bounds; it forces lambda_i to lambda_min and rejects the trajectory whenever lambda_i exceeds max.lambda.",
            "witnesses": witnesses,
            "conclusion": "For the abrupt-change signal, even the minimum admissible lambda exceeds frozen max.lambda=2, so the CRABS internal loop cannot return and the outer proposal ceiling is unreachable.",
        },
        "interruption": "The parent and workers were interrupted after the deterministic impossibility was established; already-written atomic results and sidecars were retained.",
        "stage1_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "publication_authorized": False,
    }
    write_exact(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
