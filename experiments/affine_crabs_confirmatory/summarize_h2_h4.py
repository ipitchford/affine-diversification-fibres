"""Create dependence-aware H2/H4 summaries from the sealed Stage-2 ledger."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments/affine_crabs_confirmatory/execution/results/stochastic_stage2"
OUTPUT = ROOT / "outputs/crabs_h2_h4_revision_summary.json"
TRANSITIONS = ROOT / "figure_data/crabs_h4_status_transitions.csv"
STRATA = ROOT / "figure_data/crabs_h4_transition_strata.csv"

STATUSES = ("BELOW", "UNRESOLVED", "ABOVE")


def main() -> None:
    files = sorted(RESULTS.glob("*.json"))
    if len(files) != 1100:
        raise RuntimeError(f"expected 1100 sealed Stage-2 results, found {len(files)}")

    h2_returned = 0
    h2_returned_events = 0
    h2_censors = 0
    transitions: Counter[tuple[str, str]] = Counter()
    stratum_transitions: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    changes_per_cell: Counter[int] = Counter()
    false_certificates = 0
    evaluable_cells = 0

    for path in files:
        record = json.loads(path.read_text(encoding="utf-8"))
        cell = record["cell"]
        if cell["explorer"] != "crabs_rejection":
            continue
        if record["status"] == "CENSORED_STRUCTURAL_NONTERMINATION":
            h2_censors += 1
            continue
        if record["status"] != "PASS":
            raise RuntimeError(f"unexpected primary explorer status in {path.name}")

        h2_returned += 1
        h2_returned_events += int(record["confirmatory_metrics"]["H2_deficit_event"])
        queries = record["confirmatory_metrics"]["H4_queries"]
        if len(queries) != 16:
            raise RuntimeError(f"expected 16 H4 queries in {path.name}")
        evaluable_cells += 1
        cell_changes = 0
        key = (
            f"signal={cell['signal_id']}|knots={cell['grid_knots']}|"
            f"cap={cell['turnover_cap']}"
        )
        for query in queries:
            source = query["finite_cloud_status"]
            target = query["continuous_certificate_status"]
            if source not in STATUSES or target not in STATUSES:
                raise RuntimeError(f"unexpected H4 status in {path.name}")
            transitions[(source, target)] += 1
            stratum_transitions[key][(source, target)] += 1
            cell_changes += int(source != target)
            false_certificates += int(query["false_certificate"])
        changes_per_cell[cell_changes] += 1

    changed = sum(count for (source, target), count in transitions.items() if source != target)
    total_queries = sum(transitions.values())
    if (h2_returned, h2_returned_events, h2_censors) != (240, 240, 60):
        raise RuntimeError("H2 decomposition no longer matches the sealed ledger")
    if (evaluable_cells, total_queries, changed, false_certificates) != (240, 3840, 532, 0):
        raise RuntimeError("H4 totals no longer match the sealed ledger")

    TRANSITIONS.parent.mkdir(exist_ok=True)
    with TRANSITIONS.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["finite_cloud_status", "continuous_certificate_status", "queries"])
        for source in STATUSES:
            for target in STATUSES:
                writer.writerow([source, target, transitions[(source, target)]])

    with STRATA.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "stratum",
                "finite_cloud_status",
                "continuous_certificate_status",
                "queries",
            ]
        )
        for stratum in sorted(stratum_transitions):
            for source in STATUSES:
                for target in STATUSES:
                    writer.writerow(
                        [stratum, source, target, stratum_transitions[stratum][(source, target)]]
                    )

    result = {
        "schema_version": "1.0",
        "source": "sealed Stage-2 ledger; historical result bytes unchanged",
        "H2": {
            "returned_clouds": h2_returned,
            "returned_cloud_deficit_events": h2_returned_events,
            "returned_cloud_deficit_fraction": h2_returned_events / h2_returned,
            "structural_censors": h2_censors,
            "registered_composite_events": h2_returned_events + h2_censors,
            "registered_primary_cells": h2_returned + h2_censors,
            "interpretation": (
                "The returned-cloud endpoint result is 240/240 and does not depend "
                "on counting the 60 structural censors as registered workflow events."
            ),
        },
        "H4": {
            "evaluable_cells": evaluable_cells,
            "queries_per_cell": 16,
            "evaluable_queries": total_queries,
            "changed_queries": changed,
            "changed_fraction": changed / total_queries,
            "false_certificates": false_certificates,
            "transition_matrix": {
                source: {target: transitions[(source, target)] for target in STATUSES}
                for source in STATUSES
            },
            "changed_queries_per_cell_distribution": {
                str(value): changes_per_cell[value] for value in sorted(changes_per_cell)
            },
            "dependence_boundary": (
                "The 16 queries within each cell share one sampled cloud and exact "
                "endpoint calculation. Query rows are therefore clustered and the "
                "pooled fraction is the frozen descriptive gate statistic, not an "
                "independent-query population estimate."
            ),
            "zero_false_certificate_boundary": (
                "Zero is an implementation-consistency invariant against the frozen "
                "analytic endpoints, not independent validation of theorem truth."
            ),
        },
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
