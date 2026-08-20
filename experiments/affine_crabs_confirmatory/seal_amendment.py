#!/usr/bin/env python3
"""Seal the additive pre-execution amendment without modifying the protocol."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AMENDMENT = ROOT / "AMENDMENT_001_PRE_EXECUTION.json"
SEAL = ROOT / "AMENDMENT_001_PRE_EXECUTION.sha256"
RECEIPT = ROOT / "AMENDMENT_001_RECEIPT.json"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite a different sealed file: {path}")
    path.write_bytes(payload)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    amendment = json.loads(AMENDMENT.read_text())
    protocol = ROOT / "PREREGISTRATION.json"
    manifest = ROOT / "CELL_MANIFEST.jsonl"
    protocol_hash = sha256(protocol)
    if amendment["parent_protocol_sha256"] != protocol_hash:
        raise RuntimeError("amendment parent hash does not match PREREGISTRATION.json")
    amendment_hash = sha256(AMENDMENT)
    write_frozen(SEAL, f"{amendment_hash}  {AMENDMENT.name}\n".encode())
    receipt = {
        "schema_version": "1.0.0",
        "status": "SEALED_BEFORE_CONFIRMATORY_OUTCOMES",
        "amendment_id": amendment["amendment_id"],
        "amendment_sha256": amendment_hash,
        "parent_protocol_sha256": protocol_hash,
        "cell_manifest_sha256": sha256(manifest),
        "confirmatory_outcomes_present_at_seal": False,
    }
    write_frozen(RECEIPT, canonical_bytes(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
