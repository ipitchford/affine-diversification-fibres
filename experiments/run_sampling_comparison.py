"""Matched finite-sampling benchmark for sharp endpoint recovery."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from affine_diversification.affine_fibre import (
    best_of_n_endpoint_probability,
    endpoint_deficit_cdf,
    required_samples_for_endpoint_tolerance,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
DATA = ROOT / "figure_data"
for path in (OUT, FIG, DATA):
    path.mkdir(exist_ok=True)

TEAL = "#168C8C"
RASPBERRY = "#B23A6F"
OCHRE = "#C58B1B"
VIOLET = "#6750A4"
SLATE = "#415A77"


def main() -> None:
    c = 0.5
    delta = 1.0
    target = 0.95
    ratios = np.geomspace(0.04, 1.0, 60)
    interval_sets = [2, 4, 8, 16]
    colours = [TEAL, OCHRE, VIOLET, RASPBERRY]
    rows: list[dict] = []

    plt.figure(figsize=(8.5, 5.2))
    for m, colour in zip(interval_sets, colours):
        ns = []
        for ratio in ratios:
            eta = ratio * c * delta
            n = required_samples_for_endpoint_tolerance(
                eta,
                target_probability=target,
                intervals=m,
                turnover_cap=c,
                interval_width=delta,
            )
            ns.append(n)
            rows.append({
                "intervals": m,
                "relative_tolerance_eta_over_cdelta": float(ratio),
                "single_draw_probability": endpoint_deficit_cdf(
                    eta, intervals=m, turnover_cap=c, interval_width=delta
                ),
                "samples_for_95pct": n,
            })
        plt.plot(ratios, ns, linewidth=2, color=colour, label=f"{m} intervals")
    plt.yscale("log")
    plt.xscale("log")
    plt.xlabel(r"Endpoint tolerance $\eta/(c\Delta)$")
    plt.ylabel("Independent histories required for 95% hit probability")
    plt.title("Finite random sampling becomes factorially expensive near a sharp endpoint")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "figure5_sampling_endpoint_cost.png", dpi=220)
    plt.close()

    with (DATA / "figure5_sampling_endpoint_cost.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

    # Exact best-of-N CDF and a direct Monte Carlo check for a transparent
    # matched sampler.  This is not a claim about every possible CRABS sampler.
    m = 4
    samples = 100
    deficits = np.linspace(0.0, c * delta * m, 300)
    exact = np.array([
        best_of_n_endpoint_probability(
            d, samples=samples, intervals=m, turnover_cap=c, interval_width=delta
        ) for d in deficits
    ])
    rng = np.random.default_rng(20260806)
    experiments = 30_000
    chunk = 1_000
    minima = np.empty(experiments)
    for start in range(0, experiments, chunk):
        end = min(start + chunk, experiments)
        eps = rng.uniform(0.0, c, size=(end - start, samples, m))
        draw_deficits = delta * np.sum(c - eps, axis=2)
        minima[start:end] = np.min(draw_deficits, axis=1)
    empirical = np.searchsorted(np.sort(minima), deficits, side="right") / experiments

    plt.figure(figsize=(8.5, 5.2))
    plt.plot(deficits, exact, linewidth=2.2, color=VIOLET, label="Exact best-of-100 CDF")
    plt.plot(deficits, empirical, linewidth=1.5, linestyle="--", color=TEAL, label="30,000 Monte Carlo experiments")
    plt.xlabel("Best endpoint deficit among 100 sampled histories")
    plt.ylabel("Cumulative probability")
    plt.title("Matched sampler: exact endpoint law and independent simulation")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "figure6_sampling_best_deficit.png", dpi=220)
    plt.close()

    with (DATA / "figure6_sampling_best_deficit_exact.csv").open("w", newline="") as fh:
        writer = csv.writer(fh); writer.writerow(["deficit", "exact_cdf"])
        writer.writerows(zip(deficits, exact))
    with (DATA / "figure6_sampling_best_deficit_simulated.csv").open("w", newline="") as fh:
        writer = csv.writer(fh); writer.writerow(["deficit", "empirical_cdf"])
        writer.writerows(zip(deficits, empirical))

    summary = {
        "sampler": "independent Uniform(0,c) turnover on an equal pulled-scale grid",
        "scope_warning": "Matched transparent sampler only; actual CRABS was not run in this environment.",
        "turnover_cap": c,
        "interval_width": delta,
        "simulation_intervals": m,
        "histories_per_experiment": samples,
        "simulation_experiments": experiments,
        "maximum_exact_empirical_cdf_gap": float(np.max(np.abs(exact - empirical))),
        "illustrative_required_samples": {
            "m8_eta_over_cdelta_0.2": required_samples_for_endpoint_tolerance(
                0.2 * c * delta, target_probability=0.95, intervals=8,
                turnover_cap=c, interval_width=delta
            ),
            "m16_eta_over_cdelta_0.2": required_samples_for_endpoint_tolerance(
                0.2 * c * delta, target_probability=0.95, intervals=16,
                turnover_cap=c, interval_width=delta
            ),
        },
    }
    (OUT / "sampling_comparison_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
