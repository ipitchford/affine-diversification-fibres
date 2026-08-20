#!/usr/bin/env python3
"""Seal stochastic metric definitions before any stochastic cell outcome."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AMENDMENT = ROOT / "AMENDMENT_003_STOCHASTIC_METRICS.json"
SEAL = ROOT / "AMENDMENT_003_STOCHASTIC_METRICS.sha256"
RECEIPT = ROOT / "AMENDMENT_003_RECEIPT.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different sealed file: {path}")
    path.write_bytes(payload)


def main() -> None:
    amendment = json.loads(AMENDMENT.read_text())
    protocol = ROOT / "PREREGISTRATION.json"
    correction = ROOT / "AMENDMENT_002_COMMIT_CORRECTION.json"
    deterministic = ROOT / "execution" / "DETERMINISTIC_EXECUTION_RECEIPT.json"
    expected = {
        "parent_protocol_sha256": digest(protocol),
        "parent_amendment_002_sha256": digest(correction),
        "deterministic_execution_receipt_sha256": digest(deterministic),
    }
    for field, value in expected.items():
        if amendment[field] != value:
            raise RuntimeError(f"stochastic amendment binding mismatch: {field}")
    amendment_hash = digest(AMENDMENT)
    write_frozen(SEAL, f"{amendment_hash}  {AMENDMENT.name}\n".encode())
    receipt = {
        "schema_version": "1.0.0",
        "status": "SEALED_BEFORE_STOCHASTIC_OUTCOMES",
        "amendment_id": amendment["amendment_id"],
        "amendment_sha256": amendment_hash,
        **expected,
        "stochastic_outcomes_present_at_seal": False,
    }
    write_frozen(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
