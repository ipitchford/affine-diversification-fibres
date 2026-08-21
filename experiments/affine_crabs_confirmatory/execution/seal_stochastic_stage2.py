#!/usr/bin/env python3
"""Validate, analyse, and seal the complete Stage-2 stochastic ledger."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
EXECUTION_DIR = PROTOCOL_DIR / "execution"
RESULT_DIR = EXECUTION_DIR / "results" / "stochastic_stage2"
SAMPLE_DIR = EXECUTION_DIR / "results" / "stochastic_samples_stage2"
MANIFEST = EXECUTION_DIR / "STOCHASTIC_STAGE2_MANIFEST.sha256"
RECEIPT = EXECUTION_DIR / "STOCHASTIC_STAGE2_EXECUTION_RECEIPT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_new_or_identical(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different complete-ledger artefact: {path}")
    path.write_bytes(payload)


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, float | int]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive denominator")
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half_width = z * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total)) / denominator
    return {
        "successes": successes,
        "total": total,
        "proportion": proportion,
        "wilson_95_lower": max(0.0, centre - half_width),
        "wilson_95_upper": min(1.0, centre + half_width),
    }


def stratum_key(cell: dict) -> str:
    return (
        f"signal={cell['signal_id']}|knots={cell['grid_knots']}|"
        f"cap={cell.get('turnover_cap', 'NA')}"
    )


def main() -> None:
    registered = [
        json.loads(line)
        for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()
        if line.strip()
    ]
    stochastic = [cell for cell in registered if cell["layer"] == "stochastic"]
    by_id = {cell["cell_id"]: cell for cell in stochastic}
    if len(stochastic) != 1100 or len(by_id) != 1100:
        raise RuntimeError("frozen stochastic registration is not exactly 1100 unique cells")

    result_paths = sorted(RESULT_DIR.glob("*.json"))
    observed_ids = {path.stem for path in result_paths}
    missing = sorted(set(by_id) - observed_ids)
    extra = sorted(observed_ids - set(by_id))
    if missing or extra or len(result_paths) != len(stochastic):
        raise RuntimeError(f"incomplete Stage-2 ledger: missing={len(missing)} extra={len(extra)}")

    protocol = json.loads((PROTOCOL_DIR / "PREREGISTRATION.json").read_text())
    expected_bindings = {
        "protocol_sha256": sha256(PROTOCOL_DIR / "PREREGISTRATION.json"),
        "cell_manifest_sha256": sha256(PROTOCOL_DIR / "CELL_MANIFEST.jsonl"),
        "amendment_001_sha256": sha256(PROTOCOL_DIR / "AMENDMENT_001_PRE_EXECUTION.json"),
        "amendment_002_sha256": sha256(PROTOCOL_DIR / "AMENDMENT_002_COMMIT_CORRECTION.json"),
        "amendment_003_sha256": sha256(PROTOCOL_DIR / "AMENDMENT_003_STOCHASTIC_METRICS.json"),
        "amendment_004_sha256": sha256(PROTOCOL_DIR / "AMENDMENT_004_NONTERMINATION_REPAIR.json"),
        "primates_qualification_receipt_sha256": sha256(EXECUTION_DIR / "qualification" / "PRIMATES_QUALIFICATION_RECEIPT.json"),
        "deterministic_execution_receipt_sha256": sha256(EXECUTION_DIR / "DETERMINISTIC_EXECUTION_RECEIPT.json"),
        "stochastic_stage1_incident_sha256": sha256(EXECUTION_DIR / "STOCHASTIC_STAGE1_INCIDENT.json"),
        "execution_commit": "549683e00f9b2dfa0d80ce159f5ccf7ebebd4aec",
    }

    statuses: Counter[str] = Counter()
    explorers: Counter[str] = Counter()
    explorer_elapsed: defaultdict[str, list[float]] = defaultdict(list)
    referenced_sidecars: set[Path] = set()
    manifest_lines: list[str] = []
    h2_events = 0
    h2_strata: defaultdict[str, list[int]] = defaultdict(list)
    h3_failures = 0
    h4_changed = 0
    h4_false = 0
    h4_queries = 0
    h4_discrete_changed = 0
    h4_strata: defaultdict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    censored_rejection = 0

    for path in result_paths:
        result = json.loads(path.read_text())
        cell = result.get("cell")
        if cell != by_id[path.stem]:
            raise RuntimeError(f"altered or mismatched Stage-2 cell record: {path}")
        if result.get("bindings") != expected_bindings:
            raise RuntimeError(f"unexpected Stage-2 bindings: {path}")
        if result.get("integrity_pass") is not True:
            raise RuntimeError(f"Stage-2 integrity failure: {path}")
        status = result["status"]
        explorer = cell["explorer"]
        statuses[status] += 1
        explorers[explorer] += 1
        elapsed = result["sampling"].get("elapsed_seconds")
        if isinstance(elapsed, (int, float)) and math.isfinite(elapsed):
            explorer_elapsed[explorer].append(float(elapsed))

        metrics = result["confirmatory_metrics"]
        if explorer == "crabs_rejection":
            event = metrics.get("H2_deficit_event")
            if not isinstance(event, bool):
                raise RuntimeError(f"missing Boolean H2 event: {path}")
            h2_events += int(event)
            h2_strata[stratum_key(cell)].append(int(event))
            queries = metrics.get("H4_queries")
            if not isinstance(queries, list):
                raise RuntimeError(f"missing H4 query list: {path}")
            if status == "CENSORED_STRUCTURAL_NONTERMINATION":
                censored_rejection += 1
                if queries:
                    raise RuntimeError(f"structurally censored cell emitted H4 queries: {path}")
            for query in queries:
                changed = bool(query["changed"])
                false = bool(query["false_certificate"])
                discrete_changed = query["finite_cloud_status"] != query["discrete_endpoint_status"]
                h4_queries += 1
                h4_changed += int(changed)
                h4_false += int(false)
                h4_discrete_changed += int(discrete_changed)
                stratum = h4_strata[stratum_key(cell)]
                stratum[0] += int(changed)
                stratum[1] += 1
                stratum[2] += int(false)
            if metrics.get("H4_changed_query_count") != sum(bool(q["changed"]) for q in queries):
                raise RuntimeError(f"inconsistent H4 changed count: {path}")
            if metrics.get("H4_false_certificate_count") != sum(bool(q["false_certificate"]) for q in queries):
                raise RuntimeError(f"inconsistent H4 false-certificate count: {path}")
        elif explorer == "boundary_constructor" and metrics.get("H3_boundary_pass") is not True:
            h3_failures += 1

        sidecar = result["sampling"].get("decision_value_sidecar")
        if sidecar is not None:
            sidecar_path = PROTOCOL_DIR / sidecar["path"]
            if not sidecar_path.is_file() or sha256(sidecar_path) != sidecar["sha256"]:
                raise RuntimeError(f"missing or changed Stage-2 sidecar: {sidecar_path}")
            referenced_sidecars.add(sidecar_path.resolve())
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")

    expected_explorers = {
        "boundary_constructor": 300,
        "cap_aware_uniform": 300,
        "crabs_gmrf": 100,
        "crabs_hsmrf": 100,
        "crabs_rejection": 300,
    }
    if dict(sorted(explorers.items())) != expected_explorers:
        raise RuntimeError(f"unexpected explorer coverage: {dict(explorers)}")

    observed_sidecars = {path.resolve() for path in SAMPLE_DIR.glob("*.csv")}
    if observed_sidecars != referenced_sidecars:
        raise RuntimeError(
            f"Stage-2 sidecar coverage mismatch: unreferenced={len(observed_sidecars-referenced_sidecars)} "
            f"missing={len(referenced_sidecars-observed_sidecars)}"
        )
    for path in sorted(SAMPLE_DIR.glob("*.csv")):
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")

    h2 = wilson(h2_events, explorers["crabs_rejection"])
    h2["threshold"] = protocol["thresholds"]["incremental_utility_minimum_fraction"]
    h2["verdict"] = "PASS" if h2["proportion"] >= h2["threshold"] else "FAIL"
    h2["structurally_censored_cells_counted_as_events"] = censored_rejection
    h2["strata"] = {
        key: wilson(sum(values), len(values)) for key, values in sorted(h2_strata.items())
    }

    h4 = wilson(h4_changed, h4_queries)
    h4["threshold"] = protocol["thresholds"]["incremental_utility_minimum_fraction"]
    h4["false_certificates"] = h4_false
    h4["false_certificate_maximum"] = protocol["thresholds"]["false_certificate_maximum_count"]
    h4["censored_cells_excluded_from_queries"] = censored_rejection
    h4["discrete_endpoint_sensitivity"] = wilson(h4_discrete_changed, h4_queries)
    h4["verdict"] = (
        "PASS"
        if h4["proportion"] >= h4["threshold"] and h4_false <= h4["false_certificate_maximum"]
        else "FAIL"
    )
    h4["strata"] = {
        key: {**wilson(values[0], values[1]), "false_certificates": values[2]}
        for key, values in sorted(h4_strata.items())
        if values[1] > 0
    }

    elapsed_summary = {
        explorer: {
            "cells": len(values),
            "median_seconds": statistics.median(values),
            "sum_seconds": sum(values),
            "maximum_seconds": max(values),
        }
        for explorer, values in sorted(explorer_elapsed.items())
    }
    manifest_payload = "".join(manifest_lines).encode()
    write_new_or_identical(MANIFEST, manifest_payload)

    deterministic = json.loads((EXECUTION_DIR / "DETERMINISTIC_EXECUTION_RECEIPT.json").read_text())
    receipt = {
        "schema_version": "1.0.0",
        "status": "SEALED_COMPLETE",
        "registered_stochastic_cells": len(stochastic),
        "complete_result_cells": len(result_paths),
        "sample_sidecars": len(observed_sidecars),
        "status_counts": dict(sorted(statuses.items())),
        "completed_by_explorer": dict(sorted(explorers.items())),
        "bindings": expected_bindings,
        "hypotheses": {
            "H1": {
                "verdict": "PASS" if deterministic.get("H1_all_cells_pass") is True else "FAIL",
                "registered_cells": deterministic.get("registered_cells"),
            },
            "H2": h2,
            "H3": {
                "eligible_cells": explorers["boundary_constructor"],
                "failures": h3_failures,
                "verdict": "PASS" if h3_failures == 0 else "FAIL",
            },
            "H4": h4,
            "H5": {"verdict": "PENDING_SEPARATE_CLEAN_ENVIRONMENT_AND_RUNTIME_ASSESSMENT"},
        },
        "elapsed_seconds_by_explorer": elapsed_summary,
        "stage2_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "interpretation": (
            "This receipt reports complete registered computational evidence. It is not external theorem review, "
            "peer review, community acceptance, or publication authorization."
        ),
        "public_release_authorized": False,
    }
    write_new_or_identical(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
