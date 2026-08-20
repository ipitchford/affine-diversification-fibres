#!/usr/bin/env python3
"""Seal the pre-outcome commit-hash transcription correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORRECTION = ROOT / "AMENDMENT_002_COMMIT_CORRECTION.json"
SEAL = ROOT / "AMENDMENT_002_COMMIT_CORRECTION.sha256"
RECEIPT = ROOT / "AMENDMENT_002_RECEIPT.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different sealed file: {path}")
    path.write_bytes(payload)


def main() -> None:
    correction = json.loads(CORRECTION.read_text())
    amendment_001 = ROOT / "AMENDMENT_001_PRE_EXECUTION.json"
    protocol = ROOT / "PREREGISTRATION.json"
    if correction["parent_amendment_sha256"] != digest(amendment_001):
        raise RuntimeError("correction does not bind to amendment 001")
    if correction["parent_protocol_sha256"] != digest(protocol):
        raise RuntimeError("correction does not bind to the frozen protocol")
    protocol_commit = json.loads(protocol.read_text())["software"]["crabs_development_commit"]
    if correction["correction"]["correct_value_from_parent_protocol_and_source"] != protocol_commit:
        raise RuntimeError("corrected commit does not match the frozen protocol")
    correction_hash = digest(CORRECTION)
    write_frozen(SEAL, f"{correction_hash}  {CORRECTION.name}\n".encode())
    receipt = {
        "schema_version": "1.0.0",
        "status": "SEALED_BEFORE_CONFIRMATORY_OUTCOMES",
        "amendment_id": correction["amendment_id"],
        "correction_sha256": correction_hash,
        "parent_amendment_sha256": digest(amendment_001),
        "parent_protocol_sha256": digest(protocol),
        "confirmatory_outcomes_present_at_seal": False,
    }
    write_frozen(RECEIPT, canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
