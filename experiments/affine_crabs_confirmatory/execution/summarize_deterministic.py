#!/usr/bin/env python3
"""Validate and seal the complete deterministic cell ledger."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
RESULT_DIR = PROTOCOL_DIR / "execution" / "results" / "deterministic"
MANIFEST = PROTOCOL_DIR / "execution" / "DETERMINISTIC_RESULT_MANIFEST.sha256"
RECEIPT = PROTOCOL_DIR / "execution" / "DETERMINISTIC_EXECUTION_RECEIPT.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_exact(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different deterministic seal: {path}")
    path.write_bytes(payload)


def numeric(value: object) -> float:
    if value == "+Infinity":
        return math.inf
    if value == "-Infinity":
        return -math.inf
    return float(value)


def main() -> None:
    cells = [json.loads(line) for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()]
    cells = [cell for cell in cells if cell["layer"] == "deterministic"]
    expected_ids = [cell["cell_id"] for cell in cells]
    observed_paths = sorted(RESULT_DIR.glob("*.json"))
    observed_ids = {path.stem for path in observed_paths}
    if observed_ids != set(expected_ids):
        raise RuntimeError(
            f"deterministic result coverage differs: missing={len(set(expected_ids)-observed_ids)} "
            f"extra={len(observed_ids-set(expected_ids))}"
        )

    statuses: Counter[str] = Counter()
    strata: dict[str, Counter[str]] = defaultdict(Counter)
    check_maxima: dict[str, float] = defaultdict(float)
    total_elapsed = 0.0
    bindings = None
    manifest_lines = []
    for cell_id in expected_ids:
        path = RESULT_DIR / f"{cell_id}.json"
        result = json.loads(path.read_text())
        payload_hash = result.pop("result_payload_sha256", None)
        if payload_hash != hashlib.sha256(canonical(result)).hexdigest():
            raise RuntimeError(f"payload hash mismatch: {path}")
        if result["cell"]["cell_id"] != cell_id:
            raise RuntimeError(f"cell id mismatch: {path}")
        if bindings is None:
            bindings = result["bindings"]
        elif bindings != result["bindings"]:
            raise RuntimeError(f"mixed execution bindings: {path}")
        status = result["status"]
        statuses[status] += 1
        strata[f"signal:{result['cell']['signal_id']}"][status] += 1
        strata[f"constraint:{result['cell']['constraint_regime']}"][status] += 1
        strata[f"knots:{result['cell']['grid_knots']}"][status] += 1
        total_elapsed += float(result.get("elapsed_seconds", 0.0))
        for name, check in result.get("oracle_comparisons", {}).items():
            if "max_normalized_difference" in check:
                check_maxima[name] = max(check_maxima[name], numeric(check["max_normalized_difference"]))
        relative = path.relative_to(ROOT).as_posix()
        manifest_lines.append(f"{sha256(path)}  {relative}\n")

    manifest_payload = "".join(manifest_lines).encode()
    write_exact(MANIFEST, manifest_payload)
    receipt = {
        "schema_version": "1.0.0",
        "status": "PASS" if statuses == Counter({"PASS": len(cells)}) else "FAIL",
        "layer": "deterministic",
        "registered_cells": len(cells),
        "result_files": len(observed_paths),
        "status_counts": dict(sorted(statuses.items())),
        "H1_all_cells_pass": statuses == Counter({"PASS": len(cells)}),
        "strata": {key: dict(sorted(value.items())) for key, value in sorted(strata.items())},
        "maximum_normalized_oracle_differences": dict(sorted(check_maxima.items())),
        "summed_cell_elapsed_seconds": total_elapsed,
        "bindings": bindings,
        "result_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "interpretation": "H1 deterministic evidence only; H2-H5 and all publication gates remain unresolved.",
    }
    write_exact(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
