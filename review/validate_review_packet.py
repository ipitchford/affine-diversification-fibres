#!/usr/bin/env python3
"""Read-only consistency checks for the 0.3.0-candidate final-review packet."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "experiments" / "affine_crabs_confirmatory" / "execution"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(actual: float, expected: float, label: str) -> None:
    require(math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-15), f"{label}: {actual} != {expected}")


def main() -> None:
    stage2 = load_json(EXECUTION / "STOCHASTIC_STAGE2_EXECUTION_RECEIPT.json")
    checkpoint = load_json(EXECUTION / "RESEARCH_CHECKPOINT.json")
    h5 = load_json(EXECUTION / "H5_EXECUTION_RECEIPT_002.json")
    claims = load_json(ROOT / "review" / "CLAIM_EVIDENCE_0.3.0-candidate.json")
    alt_text = load_json(ROOT / "figure_data" / "ALT_TEXT.json")
    manuscript = (ROOT / "manuscript.tex").read_text(encoding="utf-8")

    require(stage2["registered_stochastic_cells"] == 1100, "registered stochastic cells")
    require(stage2["complete_result_cells"] == 1100, "complete result cells")
    require(stage2["sample_sidecars"] == 800, "sample sidecars")
    require(
        stage2["status_counts"] == {"CENSORED_STRUCTURAL_NONTERMINATION": 100, "PASS": 1000},
        "status accounting",
    )

    h2 = stage2["hypotheses"]["H2"]
    require((h2["verdict"], h2["successes"], h2["total"]) == ("PASS", 300, 300), "H2 result")
    require(h2["structurally_censored_cells_counted_as_events"] == 60, "H2 censor count")

    h3 = stage2["hypotheses"]["H3"]
    require((h3["verdict"], h3["failures"], h3["eligible_cells"]) == ("PASS", 0, 300), "H3 result")

    h4 = stage2["hypotheses"]["H4"]
    require((h4["verdict"], h4["successes"], h4["total"]) == ("FAIL", 532, 3840), "H4 result")
    close(h4["proportion"], 0.13854166666666667, "H4 proportion")
    require(h4["false_certificates"] == 0, "H4 false certificates")
    sensitivity = h4["discrete_endpoint_sensitivity"]
    require((sensitivity["successes"], sensitivity["total"]) == (182, 3840), "H4 sensitivity")

    require(checkpoint["hypotheses"]["H5"]["verdict"] == "PASS", "checkpoint H5 verdict")
    close(checkpoint["hypotheses"]["H5"]["median_certification_seconds"], 0.00004677049582824111, "H5 median")
    require(h5["status"] == "PASS", "corrected H5 receipt")
    require(h5["clean_environment"]["passed"], "H5 clean environment")
    require(h5["normal_and_optimized_source_tasks"]["passed"], "H5 task modes")
    require(h5["runtime"]["passed"], "H5 runtime")

    with (ROOT / "figure_data" / "figure8_crabs_confirmatory_h4.csv").open(encoding="utf-8", newline="") as handle:
        figure_rows = list(csv.DictReader(handle))
    require(len(figure_rows) == 24, "H4 figure strata")
    require(sum(int(row["changed_queries"]) for row in figure_rows) == 532, "H4 figure successes")
    require(sum(int(row["evaluable_queries"]) for row in figure_rows) == 3840, "H4 figure total")
    require(sum(int(row["false_certificates"]) for row in figure_rows) == 0, "H4 figure false certificates")
    require("figure8_crabs_confirmatory_h4.png" in alt_text, "H4 figure alt text")
    require((ROOT / "figures" / "figure8_crabs_confirmatory_h4.png").is_file(), "H4 figure PNG")

    require(len(claims["claims"]) == 11, "review claim count")
    require({claim["id"] for claim in claims["claims"]} == {f"C{index}" for index in range(1, 12)}, "claim IDs")
    require(all(claim["evidence"] and claim["assurance"] for claim in claims["claims"]), "claim evidence coverage")

    required_manuscript_strings = [
        "Review draft 0.3.0-candidate",
        "1,100-cell benchmark",
        "532 of 3,840",
        "failed H4 utility gate",
        "does not support the stronger claim",
        "not yet archived",
    ]
    for phrase in required_manuscript_strings:
        require(phrase in manuscript, f"missing manuscript phrase: {phrase}")
    require((ROOT / "manuscript.pdf").is_file(), "review PDF")

    print(
        json.dumps(
            {
                "status": "PASS",
                "review_candidate": "0.3.0-candidate",
                "ledger_cells": 1100,
                "h4": {"verdict": "FAIL", "changed_queries": 532, "total_queries": 3840},
                "figure_strata": 24,
                "claims": 11,
                "publication_authorized": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
