#!/usr/bin/env python3
"""Generate the review figure and source data for the confirmatory H4 strata."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "experiments" / "affine_crabs_confirmatory" / "execution" / "STOCHASTIC_STAGE2_EXECUTION_RECEIPT.json"
DATA_PATH = ROOT / "figure_data" / "figure8_crabs_confirmatory_h4.csv"
FIGURE_PATH = ROOT / "figures" / "figure8_crabs_confirmatory_h4.png"
SIGNAL_ORDER = ["constant", "crabs_primates_ebd", "high_dynamic_range", "oscillatory"]
SIGNAL_LABELS = {
    "constant": "Constant",
    "crabs_primates_ebd": "CRABS primates EBD",
    "high_dynamic_range": "High dynamic range",
    "oscillatory": "Oscillatory",
}


def parse_key(value: str) -> dict[str, str]:
    fields = {}
    for item in value.split("|"):
        key, content = item.split("=", 1)
        fields[key] = content
    return fields


def main() -> None:
    receipt = json.loads(RECEIPT.read_text())
    h4 = receipt["hypotheses"]["H4"]
    if h4["verdict"] != "FAIL" or h4["successes"] != 532 or h4["total"] != 3840:
        raise RuntimeError("review figure is bound to the sealed 532/3840 H4 result")

    rows = []
    for key, summary in sorted(h4["strata"].items()):
        fields = parse_key(key)
        signal = fields["signal"]
        if signal not in SIGNAL_ORDER:
            raise RuntimeError(f"unexpected evaluable H4 signal: {signal}")
        rows.append(
            {
                "signal_id": signal,
                "grid_knots": int(fields["knots"]),
                "turnover_cap": float(fields["cap"]),
                "changed_queries": int(summary["successes"]),
                "evaluable_queries": int(summary["total"]),
                "changed_fraction": float(summary["proportion"]),
                "wilson_95_lower": float(summary["wilson_95_lower"]),
                "wilson_95_upper": float(summary["wilson_95_upper"]),
                "false_certificates": int(summary["false_certificates"]),
            }
        )
    if len(rows) != 24 or sum(row["evaluable_queries"] for row in rows) != 3840:
        raise RuntimeError("unexpected H4 stratum coverage")

    with DATA_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 180,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    styles = {
        25: {"color": "#0077BB", "marker": "o", "label": "25 knots"},
        100: {"color": "#EE7733", "marker": "s", "label": "100 knots"},
    }
    figure, axes = plt.subplots(2, 2, figsize=(7.1, 5.6), sharex=True, sharey=True)
    for axis, signal in zip(axes.flat, SIGNAL_ORDER, strict=True):
        signal_rows = [row for row in rows if row["signal_id"] == signal]
        for knots, style in styles.items():
            selected = sorted(
                (row for row in signal_rows if row["grid_knots"] == knots),
                key=lambda row: row["turnover_cap"],
            )
            x = [row["turnover_cap"] for row in selected]
            y = [row["changed_fraction"] for row in selected]
            lower = [row["changed_fraction"] - row["wilson_95_lower"] for row in selected]
            upper = [row["wilson_95_upper"] - row["changed_fraction"] for row in selected]
            axis.errorbar(
                x,
                y,
                yerr=[lower, upper],
                color=style["color"],
                marker=style["marker"],
                linewidth=1.2,
                markersize=5,
                capsize=3,
                label=style["label"],
            )
        axis.axhline(0.20, color="#555555", linewidth=1.0, linestyle="--")
        axis.set_title(SIGNAL_LABELS[signal])
        axis.set_xticks([0.25, 0.50, 0.90])
        axis.set_ylim(0.0, 0.42)
        axis.grid(axis="y", color="#dddddd", linewidth=0.5)
    axes[1, 0].set_xlabel("Turnover cap")
    axes[1, 1].set_xlabel("Turnover cap")
    axes[0, 0].set_ylabel("Changed-query fraction")
    axes[1, 0].set_ylabel("Changed-query fraction")
    axes[0, 0].legend(frameon=False, loc="upper left")
    axes[0, 1].text(0.89, 0.205, "20% gate", ha="right", va="bottom", color="#555555", fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURE_PATH)
    print(json.dumps({"rows": len(rows), "data": str(DATA_PATH), "figure": str(FIGURE_PATH)}, indent=2))


if __name__ == "__main__":
    main()
