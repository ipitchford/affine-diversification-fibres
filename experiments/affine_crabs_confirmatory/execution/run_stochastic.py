#!/usr/bin/env python3
"""Run registered stochastic cells concurrently and resumably."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_DIR = ROOT / "experiments" / "affine_crabs_confirmatory"
SCRIPT = PROTOCOL_DIR / "execution" / "run_stochastic_cell.R"
RESULT_DIR = PROTOCOL_DIR / "execution" / "results" / "stochastic"
SAMPLE_DIR = PROTOCOL_DIR / "execution" / "results" / "stochastic_samples"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def require_clean_sources() -> None:
    allowed = "experiments/affine_crabs_confirmatory/execution/results/"
    dirty = []
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:].split(" -> ")[-1]
        if not path.startswith(allowed):
            dirty.append(line)
    if dirty:
        raise RuntimeError(f"stochastic execution sources are not clean: {dirty}")


def load_existing(path: Path, cell: dict, commit: str) -> dict | None:
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    if result.get("cell") != cell or result.get("bindings", {}).get("execution_commit") != commit:
        raise RuntimeError(f"existing stochastic result has different bindings: {path}")
    return {
        "cell_id": cell["cell_id"],
        "status": result["status"],
        "explorer": cell["explorer"],
        "accepted": result["sampling"]["accepted"],
        "attempts": result["sampling"]["attempts"],
        "existing": True,
    }


def run_cell(rscript: str, cell: dict, commit: str) -> dict:
    existing = load_existing(RESULT_DIR / f"{cell['cell_id']}.json", cell, commit)
    if existing is not None:
        return existing
    process = subprocess.run(
        [rscript, "--vanilla", str(SCRIPT), str(ROOT), cell["cell_id"], str(RESULT_DIR), str(SAMPLE_DIR)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"cell {cell['cell_id']} failed with exit {process.returncode}:\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    lines = [line for line in process.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--rscript", default="Rscript")
    parser.add_argument("--explorer", action="append", default=[])
    parser.add_argument("--task", action="append", default=[])
    parser.add_argument("--cell-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    require_clean_sources()
    commit = git("rev-parse", "HEAD")
    cells = [json.loads(line) for line in (PROTOCOL_DIR / "CELL_MANIFEST.jsonl").read_text().splitlines()]
    cells = [cell for cell in cells if cell["layer"] == "stochastic"]
    if args.explorer:
        cells = [cell for cell in cells if cell["explorer"] in set(args.explorer)]
    if args.task:
        cells = [cell for cell in cells if cell["task"] in set(args.task)]
    if args.cell_id:
        wanted = set(args.cell_id)
        cells = [cell for cell in cells if cell["cell_id"] in wanted]
        if len(cells) != len(wanted):
            raise RuntimeError("one or more requested ids are not selected registered stochastic cells")
    priority = {"boundary_constructor": 0, "cap_aware_uniform": 1, "crabs_hsmrf": 2, "crabs_gmrf": 3, "crabs_rejection": 4}
    cells.sort(key=lambda cell: (priority[cell["explorer"]], cell["cell_id"]))
    if args.limit is not None:
        cells = cells[: args.limit]

    counts: Counter[str] = Counter()
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_cell, args.rscript, cell, commit): cell for cell in cells}
        for completed, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            cell = futures[future]
            try:
                result = future.result()
                counts[result["status"]] += 1
                counts["existing" if result["existing"] else "written"] += 1
            except Exception as exc:
                counts["orchestrator_error"] += 1
                failures.append({"cell_id": cell["cell_id"], "error": str(exc)})
            if completed % 10 == 0 or completed == len(cells):
                print(json.dumps({"completed": completed, "total": len(cells), "counts": counts}, sort_keys=True), flush=True)
    summary = {
        "selected_cells": len(cells),
        "counts": counts,
        "failures": failures,
        "execution_commit": commit,
    }
    print(json.dumps(summary, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
