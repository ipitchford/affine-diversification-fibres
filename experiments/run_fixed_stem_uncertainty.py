"""Route A finite-sample signal band and target-specific decision example.

This is a frozen synthetic method demonstration.  It is not an analysis of the
mammal data and it does not cover phylogenetic dating error or model
misspecification.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from affine_diversification.affine_fibre import (
    fixed_stem_signal_band,
    geometric_probability_interval,
    turnover_cap_decision_from_signal_band,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
FIGURE_DATA = ROOT / "figure_data"
FIGURES = ROOT / "figures"

TREE_SEED = 20260821
COVERAGE_SEED = 20260822
PULLED_RATE = 0.08
STEM_AGE = 50.0
ALPHA = 0.05
COVERAGE_REPLICATES = 20_000

# A normalized deterministic constraint M0 / D = 2, with rho = 1.
RHO = 1.0
ORIGIN_LINEAGES = 2.0
DIVERSITY_LOWER = 1.0
STEM_PROPOSED_CAP = 0.70
INTERIOR_AGE = 20.0
INTERIOR_PROPOSED_CAP = 0.80

TEAL = "#168C8C"
RASPBERRY = "#B23A6F"
OCHRE = "#C58B1B"
VIOLET = "#6750A4"
SLATE = "#415A77"


def true_branching_cdf(ages: np.ndarray, p: float) -> np.ndarray:
    return (1.0 - np.exp(-PULLED_RATE * ages)) / (1.0 - p)


def inverse_branching_cdf(uniforms: np.ndarray, p: float) -> np.ndarray:
    return -np.log(1.0 - uniforms * (1.0 - p)) / PULLED_RATE


def required_cap(x: np.ndarray) -> np.ndarray:
    offset = ORIGIN_LINEAGES / DIVERSITY_LOWER - RHO
    out = np.zeros_like(x)
    beyond_present = x > 1.0
    out[beyond_present] = np.maximum(
        0.0, 1.0 - offset / (x[beyond_present] - 1.0)
    )
    return out


def simulate_coverage(p: float) -> dict[str, float | int]:
    """Numerical check of the two component events and their intersection."""
    rng = np.random.default_rng(COVERAGE_SEED)
    count_covered = 0
    age_covered = 0
    joint_covered = 0
    tip_sum = 0
    for _ in range(COVERAGE_REPLICATES):
        n_tips = int(rng.geometric(p))
        tip_sum += n_tips
        p_lower, p_upper = geometric_probability_interval(
            n_tips, alpha=ALPHA / 2.0
        )
        count_ok = p_lower <= p <= p_upper

        m = n_tips - 1
        if m == 0:
            age_ok = True
        else:
            uniforms = np.sort(rng.uniform(size=m))
            indices = np.arange(1, m + 1, dtype=float)
            d_plus = np.max(indices / m - uniforms)
            d_minus = np.max(uniforms - (indices - 1.0) / m)
            radius = math.sqrt(math.log(2.0 / (ALPHA / 2.0)) / (2.0 * m))
            age_ok = max(float(d_plus), float(d_minus)) <= radius

        count_covered += int(count_ok)
        age_covered += int(age_ok)
        joint_covered += int(count_ok and age_ok)

    return {
        "replicates": COVERAGE_REPLICATES,
        "seed": COVERAGE_SEED,
        "mean_tip_count": tip_sum / COVERAGE_REPLICATES,
        "count_interval_coverage": count_covered / COVERAGE_REPLICATES,
        "branching_cdf_band_coverage": age_covered / COVERAGE_REPLICATES,
        "joint_component_coverage": joint_covered / COVERAGE_REPLICATES,
        "nominal_joint_lower_bound": 1.0 - ALPHA,
        "role": "Monte Carlo sanity check; not the proof of coverage",
    }


def main() -> None:
    for directory in (DATA, OUTPUTS, FIGURE_DATA, FIGURES):
        directory.mkdir(exist_ok=True)

    p_true = math.exp(-PULLED_RATE * STEM_AGE)
    rng = np.random.default_rng(TREE_SEED)
    n_tips = int(rng.geometric(p_true))
    uniforms = rng.uniform(size=n_tips - 1)
    branching_ages = np.sort(inverse_branching_cdf(uniforms, p_true))
    evaluation = np.linspace(0.0, STEM_AGE, 201)
    band = fixed_stem_signal_band(
        branching_ages, evaluation, stem_age=STEM_AGE, alpha=ALPHA
    )
    F_true = np.exp(PULLED_RATE * evaluation)

    stem_index = evaluation.size - 1
    interior_index = int(np.argmin(np.abs(evaluation - INTERIOR_AGE)))
    stem_decision = turnover_cap_decision_from_signal_band(
        F_lower=float(band.F_lower[stem_index]),
        F_upper=float(band.F_upper[stem_index]),
        F_plugin=float(band.F_plugin[stem_index]),
        rho=RHO,
        origin_lineages=ORIGIN_LINEAGES,
        diversity_lower=DIVERSITY_LOWER,
        proposed_cap=STEM_PROPOSED_CAP,
    )
    interior_decision = turnover_cap_decision_from_signal_band(
        F_lower=float(band.F_lower[interior_index]),
        F_upper=float(band.F_upper[interior_index]),
        F_plugin=float(band.F_plugin[interior_index]),
        rho=RHO,
        origin_lineages=ORIGIN_LINEAGES,
        diversity_lower=DIVERSITY_LOWER,
        proposed_cap=INTERIOR_PROPOSED_CAP,
    )

    if stem_decision.status != "CERTIFIED_INCOMPATIBLE":
        raise RuntimeError("the frozen primary target no longer has the registered status")
    if not (
        interior_decision.status == "UNRESOLVED"
        and interior_decision.plugin_status == "PLUGIN_COMPATIBLE"
    ):
        raise RuntimeError("the frozen caution target no longer has the registered status")

    with (DATA / "synthetic_fixed_stem_tree.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["node_index", "branching_age"])
        for index, age in enumerate(branching_ages, start=1):
            writer.writerow([index, f"{age:.17g}"])

    cap_lower = required_cap(band.F_lower)
    cap_plugin = required_cap(band.F_plugin)
    cap_upper = required_cap(band.F_upper)
    with (FIGURE_DATA / "figure9_fixed_stem_uncertainty.csv").open(
        "w", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "age",
                "F_true",
                "F_lower_95",
                "F_plugin",
                "F_upper_95",
                "minimum_cap_lower",
                "minimum_cap_plugin",
                "minimum_cap_upper",
            ]
        )
        for row in zip(
            evaluation,
            F_true,
            band.F_lower,
            band.F_plugin,
            band.F_upper,
            cap_lower,
            cap_plugin,
            cap_upper,
        ):
            writer.writerow([f"{float(value):.17g}" for value in row])

    coverage = simulate_coverage(p_true)
    result = {
        "schema_version": "1.0",
        "scope": "synthetic fixed-stem method demonstration",
        "assurance_boundary": (
            "Finite-sample coverage is conditional on the exact fixed-stem, "
            "stem-survival, homogeneous time-varying reconstructed-process law. "
            "It excludes dating error, smoothing, model misspecification and any "
            "fossil observation process."
        ),
        "model": {
            "pulled_rate": PULLED_RATE,
            "stem_age": STEM_AGE,
            "F_stem_true": math.exp(PULLED_RATE * STEM_AGE),
            "p_true": p_true,
        },
        "observed_tree": {
            "seed": TREE_SEED,
            "n_tips": n_tips,
            "n_branching_ages": int(branching_ages.size),
            "minimum_branching_age": float(branching_ages.min()),
            "maximum_branching_age": float(branching_ages.max()),
        },
        "confidence_band": {
            "confidence_level": 1.0 - ALPHA,
            "alpha_count": band.alpha_count,
            "alpha_ages": band.alpha_ages,
            "p_interval": [band.p_lower, band.p_upper],
            "F_stem_interval": [
                float(band.F_lower[stem_index]),
                float(band.F_upper[stem_index]),
            ],
            "F_stem_plugin": float(band.F_plugin[stem_index]),
            "dkw_radius": band.dkw_radius,
        },
        "primary_target": {
            "age": STEM_AGE,
            "rho": RHO,
            "origin_lineages": ORIGIN_LINEAGES,
            "diversity_lower": DIVERSITY_LOWER,
            "proposed_cap": STEM_PROPOSED_CAP,
            **stem_decision.__dict__,
        },
        "caution_target": {
            "age": INTERIOR_AGE,
            "rho": RHO,
            "origin_lineages": ORIGIN_LINEAGES,
            "diversity_lower": DIVERSITY_LOWER,
            "proposed_cap": INTERIOR_PROPOSED_CAP,
            **interior_decision.__dict__,
        },
        "coverage_sanity_check": coverage,
    }
    (OUTPUTS / "fixed_stem_uncertainty.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7))
    ax = axes[0]
    ax.fill_between(
        evaluation,
        band.F_lower,
        band.F_upper,
        color=TEAL,
        alpha=0.18,
        label="95% simultaneous band",
    )
    ax.plot(evaluation, F_true, color=SLATE, linewidth=2.0, label="Generating F (audit only)")
    ax.step(
        evaluation,
        band.F_plugin,
        where="post",
        color=OCHRE,
        linewidth=1.7,
        label="Plug-in F",
    )
    ax.set_yscale("log")
    ax.set_xlabel("Age from present")
    ax.set_ylabel("Pulled scale F")
    ax.set_title("A. Honest fixed-stem signal uncertainty")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    ax.fill_between(
        evaluation,
        cap_lower,
        cap_upper,
        color=VIOLET,
        alpha=0.17,
        label="Minimum-cap range from F band",
    )
    ax.step(
        evaluation,
        cap_plugin,
        where="post",
        color=RASPBERRY,
        linewidth=1.7,
        label="Plug-in minimum cap",
    )
    ax.scatter(
        [STEM_AGE],
        [STEM_PROPOSED_CAP],
        color=SLATE,
        marker="X",
        s=70,
        zorder=4,
        label="Primary: incompatible",
    )
    ax.scatter(
        [INTERIOR_AGE],
        [INTERIOR_PROPOSED_CAP],
        color=OCHRE,
        marker="D",
        s=48,
        zorder=4,
        label="Caution: unresolved",
    )
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Age from present")
    ax.set_ylabel("Minimum compatible turnover cap")
    ax.set_title("B. Propagated three-valued decisions")
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle("Synthetic method demonstration; not empirical validation", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure9_fixed_stem_uncertainty.png", dpi=220)
    plt.close(fig)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
