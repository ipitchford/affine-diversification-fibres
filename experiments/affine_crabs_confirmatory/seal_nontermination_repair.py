#!/usr/bin/env python3
"""Seal the post-incident, pre-Stage-2 nontermination repair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AMENDMENT = ROOT / "AMENDMENT_004_NONTERMINATION_REPAIR.json"
SEAL = ROOT / "AMENDMENT_004_NONTERMINATION_REPAIR.sha256"
RECEIPT = ROOT / "AMENDMENT_004_RECEIPT.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different repair seal: {path}")
    path.write_bytes(payload)


def main() -> None:
    amendment = json.loads(AMENDMENT.read_text())
    expected = {
        "parent_protocol_sha256": digest(ROOT / "PREREGISTRATION.json"),
        "parent_amendment_003_sha256": digest(ROOT / "AMENDMENT_003_STOCHASTIC_METRICS.json"),
        "stage1_incident_sha256": digest(ROOT / "execution" / "STOCHASTIC_STAGE1_INCIDENT.json"),
    }
    for field, value in expected.items():
        if amendment[field] != value:
            raise RuntimeError(f"repair binding mismatch: {field}")
    amendment_hash = digest(AMENDMENT)
    write_frozen(SEAL, f"{amendment_hash}  {AMENDMENT.name}\n".encode())
    receipt = {
        "schema_version": "1.0.0",
        "status": "SEALED_BEFORE_STAGE2",
        "amendment_id": amendment["amendment_id"],
        "amendment_sha256": amendment_hash,
        **expected,
        "stage2_outcomes_present_at_seal": False,
    }
    write_frozen(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
