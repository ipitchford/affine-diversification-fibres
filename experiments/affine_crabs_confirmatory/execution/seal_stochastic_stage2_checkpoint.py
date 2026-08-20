#!/usr/bin/env python3
"""Validate and seal the compute-hard-stop Stage-2 checkpoint."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
RESULT_DIR = PROTOCOL_DIR / "execution" / "results" / "stochastic_stage2"
SAMPLE_DIR = PROTOCOL_DIR / "execution" / "results" / "stochastic_samples_stage2"
MANIFEST = PROTOCOL_DIR / "execution" / "STOCHASTIC_STAGE2_CHECKPOINT_MANIFEST.sha256"
RECEIPT = PROTOCOL_DIR / "execution" / "STOCHASTIC_STAGE2_CHECKPOINT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_exact(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different Stage-2 checkpoint: {path}")
    path.write_bytes(payload)


def main() -> None:
    cells = [json.loads(line) for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()]
    stochastic = [cell for cell in cells if cell["layer"] == "stochastic"]
    by_id = {cell["cell_id"]: cell for cell in stochastic}
    result_paths = sorted(RESULT_DIR.glob("*.json"))
    observed_ids = {path.stem for path in result_paths}
    if not observed_ids <= set(by_id):
        raise RuntimeError("Stage-2 results include an unregistered cell id")

    statuses: Counter[str] = Counter()
    explorers: Counter[str] = Counter()
    rejection_statuses: Counter[str] = Counter()
    h2_events = 0
    h3_failures = 0
    h4_changed = 0
    h4_queries = 0
    h4_false = 0
    bindings = None
    referenced_sidecars: set[Path] = set()
    manifest_lines: list[str] = []
    for path in result_paths:
        result = json.loads(path.read_text())
        cell = result["cell"]
        if cell != by_id[path.stem]:
            raise RuntimeError(f"altered Stage-2 cell record: {path}")
        if bindings is None:
            bindings = result["bindings"]
        elif bindings != result["bindings"]:
            raise RuntimeError(f"mixed Stage-2 bindings: {path}")
        if not result["integrity_pass"]:
            raise RuntimeError(f"Stage-2 integrity failure cannot be hidden in checkpoint: {path}")
        statuses[result["status"]] += 1
        explorers[cell["explorer"]] += 1
        if cell["explorer"] == "crabs_rejection":
            rejection_statuses[result["status"]] += 1
            h2_events += int(bool(result["confirmatory_metrics"]["H2_deficit_event"]))
            h4_changed += int(result["confirmatory_metrics"]["H4_changed_query_count"])
            h4_false += int(result["confirmatory_metrics"]["H4_false_certificate_count"])
            h4_queries += len(result["confirmatory_metrics"]["H4_queries"])
        if cell["explorer"] == "boundary_constructor" and not result["confirmatory_metrics"]["H3_boundary_pass"]:
            h3_failures += 1
        sidecar = result["sampling"].get("decision_value_sidecar")
        if sidecar is not None:
            sidecar_path = PROTOCOL_DIR / sidecar["path"]
            if not sidecar_path.is_file() or sha256(sidecar_path) != sidecar["sha256"]:
                raise RuntimeError(f"missing or changed Stage-2 sidecar: {sidecar_path}")
            referenced_sidecars.add(sidecar_path.resolve())
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")

    observed_sidecars = {path.resolve() for path in SAMPLE_DIR.glob("*.csv")}
    if observed_sidecars != referenced_sidecars:
        raise RuntimeError(
            f"Stage-2 sidecar coverage mismatch: unreferenced={len(observed_sidecars-referenced_sidecars)} "
            f"missing={len(referenced_sidecars-observed_sidecars)}"
        )
    for path in sorted(SAMPLE_DIR.glob("*.csv")):
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")

    missing = [cell for cell in stochastic if cell["cell_id"] not in observed_ids]
    missing_strata: Counter[str] = Counter()
    for cell in missing:
        missing_strata[
            f"{cell['explorer']}|{cell['signal_id']}|knots={cell['grid_knots']}|cap={cell.get('turnover_cap', 'NA')}"
        ] += 1
    manifest_payload = "".join(manifest_lines).encode()
    write_exact(MANIFEST, manifest_payload)

    boundary_complete = explorers["boundary_constructor"] == 300
    rejection_complete = explorers["crabs_rejection"] == 300
    h2_locked_support = h2_events >= 60  # 20% of the frozen 300-cell denominator
    receipt = {
        "schema_version": "1.0.0",
        "status": "COMPUTE_HARD_STOP_RESUMABLE",
        "registered_stochastic_cells": len(stochastic),
        "complete_result_cells": len(result_paths),
        "pending_cells": len(missing),
        "sample_sidecars": len(observed_sidecars),
        "status_counts": dict(sorted(statuses.items())),
        "completed_by_explorer": dict(sorted(explorers.items())),
        "rejection_status_counts": dict(sorted(rejection_statuses.items())),
        "missing_strata": dict(sorted(missing_strata.items())),
        "pending_cell_ids": [cell["cell_id"] for cell in missing],
        "bindings": bindings,
        "hypothesis_checkpoint": {
            "H1": "PASS on all 1944 deterministic cells",
            "H2": {
                "final_verdict_authorized": False,
                "observed_events": h2_events,
                "frozen_denominator": 300,
                "support_is_mathematically_locked_under_amendment_003": h2_locked_support,
                "reason_verdict_withheld": "Complete registered rejection ledger is still required for final reporting and stratification."
            },
            "H3": {
                "final_verdict_authorized": boundary_complete,
                "eligible_cells": 300,
                "completed_cells": explorers["boundary_constructor"],
                "failures": h3_failures,
                "verdict": "PASS" if boundary_complete and h3_failures == 0 else "WITHHELD"
            },
            "H4": {
                "final_verdict_authorized": rejection_complete,
                "evaluable_queries_so_far": h4_queries,
                "changed_queries_so_far": h4_changed,
                "false_certificates_so_far": h4_false,
                "verdict": "WITHHELD"
            },
            "H5": "NOT YET ASSESSED"
        },
        "stage2_complete": False,
        "analysis_gate": "H2/H4 final analysis and publication interpretation prohibited until all 1100 Stage-2 cells are present.",
        "resume_command": "env R_LIBS=<isolated-lib>:<base-lib> python3 experiments/affine_crabs_confirmatory/execution/run_stochastic.py --rscript <framework-Rscript> --workers 8 --explorer crabs_rejection",
        "checkpoint_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "public_release_authorized": False,
    }
    write_exact(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
