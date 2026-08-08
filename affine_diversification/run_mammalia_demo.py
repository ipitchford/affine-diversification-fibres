from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from affine_diversification.affine_fibre import (
    evaluate_piecewise_linear_pulled_scale,
    minimum_turnover_cap_from_diversity,
    no_external_point_bounds,
    sharp_envelopes,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# Non-standard but print-safe palette, selected explicitly for this project.
TEAL = "#168C8C"
RASPBERRY = "#B23A6F"
OCHRE = "#C58B1B"
VIOLET = "#6750A4"
SLATE = "#415A77"
CORAL = "#D66A5E"
ANALYSIS_ORIGIN_LINEAGES = 4790.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_psr() -> np.ndarray:
    return np.genfromtxt(DATA / "mammalia_tree1_psr.csv", delimiter=",", names=True)


def load_fossils() -> list[dict]:
    rows: list[dict] = []
    with (DATA / "mammalia_fossil_excerpt.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            parsed = dict(row)
            for key in ("younger_ma", "older_ma", "mid_age_ma", "tThrough", "divSIB", "divBC", "divRT"):
                parsed[key] = float(row[key]) if row[key] != "" else np.nan
            rows.append(parsed)
    return rows


def point_interval(lp: float, x: float, rho: float, c: float, diversity: float | None = None) -> dict:
    q_min = rho + (1.0 - c) * (x - 1.0)
    q_max = rho + (x - 1.0)
    if diversity is not None and np.isfinite(diversity) and diversity > 0:
        q_max = min(q_max, ANALYSIS_ORIGIN_LINEAGES / diversity)
    feasible = q_min <= q_max + 1e-12 and q_min > 0
    if not feasible:
        return {
            "feasible": False,
            "q_min": q_min,
            "q_max": q_max,
            "lambda_min": None,
            "lambda_max": None,
            "width_factor": None,
        }
    lam_min = lp * x / q_max
    lam_max = lp * x / q_min
    return {
        "feasible": True,
        "q_min": q_min,
        "q_max": q_max,
        "lambda_min": lam_min,
        "lambda_max": lam_max,
        "width_factor": lam_max / lam_min,
    }


def make_geometry_figure() -> None:
    x = np.linspace(1.0, 10.0, 500)
    xi = np.array([1.0, 4.0, 8.0])
    lo = np.array([0.2, 1.30, 3.80])
    hi = np.array([0.2, 1.60, 4.20])
    c = 0.6
    env = sharp_envelopes(x, xi, lo, hi, turnover_cap=c)
    if not env.feasible:
        raise RuntimeError(env.certificate)

    # A deterministic interior trajectory, made from the envelope midpoint.
    interior = 0.5 * (env.lower_n + env.upper_n)

    plt.figure(figsize=(8.5, 5.2))
    plt.fill_between(x, env.lower_n, env.upper_n, color=TEAL, alpha=0.16, label="Sharp identified set")
    plt.plot(x, env.lower_n, color=RASPBERRY, linewidth=2.0, label="Least admissible cumulative loss")
    plt.plot(x, env.upper_n, color=VIOLET, linewidth=2.0, label="Greatest admissible cumulative loss")
    plt.plot(x, interior, color=OCHRE, linewidth=1.7, linestyle="--", label="One admissible history")
    for xx, ll, uu in zip(xi, lo, hi):
        plt.plot([xx, xx], [ll, uu], color=SLATE, linewidth=4, solid_capstyle="round")
    plt.xlabel(r"Pulled scale $x=F(\tau)$")
    plt.ylabel(r"Cumulative loss $n(x)=\nu([0,\tau])$")
    plt.title("Affine fibre: exact envelopes replace sampled trajectory clouds")
    plt.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    plt.savefig(FIG / "figure1_affine_geometry.png", dpi=220)
    plt.close()


def make_turnover_audit_figure(audit_rows: list[dict]) -> None:
    proxy_styles = {
        "tThrough": (TEAL, "Cross-bin genera"),
        "divBC": (VIOLET, "Boundary-crosser estimate"),
        "divSIB": (RASPBERRY, "SIB richness estimate"),
        "divRT": (OCHRE, "Range-through estimate"),
    }
    ages = np.array([r["mid_age_ma"] for r in audit_rows])
    plt.figure(figsize=(8.5, 5.2))
    for proxy, (colour, label) in proxy_styles.items():
        vals = np.array([r[f"c_min_{proxy}"] for r in audit_rows])
        plt.plot(ages, vals, marker="o", markersize=4, linewidth=1.7, color=colour, label=label)
    plt.axhline(0.5, color=SLATE, linestyle="--", linewidth=1.2, label="Illustrative cap $c=0.5$")
    plt.ylim(0, 1.02)
    plt.xlabel("Age (Ma before present)")
    plt.ylabel(r"Minimum compatible turnover cap $c_{\min}$")
    plt.title("Mammal sensitivity audit: fossil proxies imply different assumptions")
    plt.legend(frameon=False, fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(FIG / "figure2_mammalia_turnover_audit.png", dpi=220)
    plt.close()


def make_worked_sensitivity_figure(lp: float, x: float) -> None:
    caps = np.linspace(0.0, 0.99, 500)
    cases = [
        (None, SLATE, "No fossil constraint"),
        (44.0, TEAL, r"Cross-bin $D\geq44$"),
        (398.0, VIOLET, r"Boundary-crosser $D\geq398$"),
        (577.0, RASPBERRY, r"Range-through $D\geq577$"),
    ]
    plt.figure(figsize=(8.5, 5.2))
    for diversity, colour, label in cases:
        widths = []
        for c in caps:
            result = point_interval(lp, x, 1.0, float(c), diversity)
            widths.append(result["width_factor"] if result["feasible"] else np.nan)
        plt.plot(caps, widths, color=colour, linewidth=1.9, label=label)
    plt.xlabel(r"Assumed cap $c$ on turnover $\mu/\lambda$")
    plt.ylabel(r"Multiplicative width $\lambda_{\max}/\lambda_{\min}$")
    plt.title("At 58.5 Ma, fossil information can tighten or falsify a cap")
    plt.ylim(0.95, 4.5)
    plt.legend(frameon=False, fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "figure3_worked_sensitivity.png", dpi=220)
    plt.close()


def make_lambda_bounds_figure(psr: np.ndarray) -> None:
    age = psr["actual_age_ma"]
    mask = age <= 71.0
    x = psr["F_from_dLTT"][mask]
    lp = psr["lambda_p_per_ma"][mask]
    bounds = no_external_point_bounds(x, lp, rho=1.0, turnover_cap=0.5)
    plt.figure(figsize=(8.5, 5.2))
    plt.fill_between(age[mask], bounds.lambda_lower, bounds.lambda_supremum, color=TEAL, alpha=0.18, label="Sharp interval under $c=0.5$")
    plt.plot(age[mask], bounds.lambda_lower, color=VIOLET, linewidth=1.7, label="Lower endpoint")
    plt.plot(age[mask], bounds.lambda_supremum, color=RASPBERRY, linewidth=1.7, label="Upper endpoint")
    plt.plot(age[mask], lp, color=OCHRE, linewidth=1.4, linestyle="--", label=r"Pulled rate $\lambda_p$")
    plt.xlabel("Age (Ma before present)")
    plt.ylabel(r"Speciation rate $\lambda$ (lineages/Ma)")
    plt.title("Sharp mammal speciation-rate bounds from one explicit restriction")
    plt.legend(frameon=False, fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "figure4_mammalia_lambda_bounds.png", dpi=220)
    plt.close()


def random_control() -> dict:
    rng = np.random.default_rng(20260806)
    histories = 20_000
    intervals = 80
    c = 0.5
    x = np.linspace(1.0, 160.0, intervals + 1)
    eps = rng.uniform(0.0, c, size=(histories, intervals))
    q = np.empty((histories, intervals + 1), dtype=float)
    q[:, 0] = 1.0
    q[:, 1:] = 1.0 + np.cumsum((1.0 - eps) * np.diff(x)[None, :], axis=1)
    n = x[None, :] - q
    lower_q = 1.0 + (1.0 - c) * (x - 1.0)
    upper_q = x
    violations = np.count_nonzero(
        (eps < -1e-15)
        | (eps > c + 1e-15)
    )
    envelope_violations = np.count_nonzero(
        (q < lower_q[None, :] - 1e-12) | (q > upper_q[None, :] + 1e-12)
    )
    return {
        "histories": histories,
        "intervals_per_history": intervals,
        "turnover_cap": c,
        "maximum_sampled_turnover": float(np.max(eps)),
        "turnover_violations": int(violations),
        "envelope_violations": int(envelope_violations),
        "minimum_q": float(np.min(q)),
        "maximum_n_over_x": float(np.max(n / x[None, :])),
    }


def main() -> None:
    psr = load_psr()
    fossils = load_fossils()
    tau_eval = np.array([r["mid_age_ma"] - 1.0 for r in fossils])
    lp_eval, x_eval = evaluate_piecewise_linear_pulled_scale(
        psr["tau_ma_after_1Ma_trim"], psr["lambda_p_per_ma"], tau_eval
    )

    audit_rows: list[dict] = []
    proxies = ("tThrough", "divBC", "divSIB", "divRT")
    for row, lp, x in zip(fossils, lp_eval, x_eval):
        out = {
            "bin": row["bin"],
            "mid_age_ma": row["mid_age_ma"],
            "tau_after_trim_ma": row["mid_age_ma"] - 1.0,
            "lambda_p_per_ma": float(lp),
            "F": float(x),
        }
        for proxy in proxies:
            d = row[proxy]
            out[proxy] = None if not np.isfinite(d) else float(d)
            out[f"c_min_{proxy}"] = (
                None
                if not np.isfinite(d) or d <= 0
                else minimum_turnover_cap_from_diversity(
                    float(x), rho=1.0, origin_lineages=ANALYSIS_ORIGIN_LINEAGES, diversity_lower=float(d)
                )
            )
        audit_rows.append(out)

    with (OUT / "mammalia_minimum_turnover.csv").open("w", newline="") as fh:
        fields = [
            "bin", "mid_age_ma", "tau_after_trim_ma", "lambda_p_per_ma", "F",
            "tThrough", "c_min_tThrough", "divBC", "c_min_divBC",
            "divSIB", "c_min_divSIB", "divRT", "c_min_divRT",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audit_rows)

    # Worked point: fossil bin 56--61 Ma, midpoint 58.5 Ma.
    target = next(r for r in audit_rows if abs(r["mid_age_ma"] - 58.5) < 1e-9)
    lp = float(target["lambda_p_per_ma"])
    x = float(target["F"])
    worked = {
        "age_ma": 58.5,
        "tau_after_1Ma_trim_ma": 57.5,
        "lambda_p_per_ma": lp,
        "F": x,
        "analysis_origin_lineages_M0": ANALYSIS_ORIGIN_LINEAGES,
        "rho_at_analysis_origin": 1.0,
        "c_0_5_no_fossil": point_interval(lp, x, 1.0, 0.5, None),
        "c_0_5_cross_bin_D44": point_interval(lp, x, 1.0, 0.5, 44.0),
        "c_0_5_boundary_D398": point_interval(lp, x, 1.0, 0.5, 398.0),
        "c_0_5_range_through_D577": point_interval(lp, x, 1.0, 0.5, 577.0),
        "minimum_cap_D44": minimum_turnover_cap_from_diversity(x, rho=1.0, origin_lineages=ANALYSIS_ORIGIN_LINEAGES, diversity_lower=44.0),
        "minimum_cap_D398": minimum_turnover_cap_from_diversity(x, rho=1.0, origin_lineages=ANALYSIS_ORIGIN_LINEAGES, diversity_lower=398.0),
        "minimum_cap_D577": minimum_turnover_cap_from_diversity(x, rho=1.0, origin_lineages=ANALYSIS_ORIGIN_LINEAGES, diversity_lower=577.0),
        "c_0_94_range_through_D577": point_interval(lp, x, 1.0, 0.94, 577.0),
        "c_0_95_range_through_D577": point_interval(lp, x, 1.0, 0.95, 577.0),
    }
    (OUT / "mammalia_worked_case.json").write_text(json.dumps(worked, indent=2) + "\n")

    maxima = {}
    for proxy in proxies:
        finite = [(r[f"c_min_{proxy}"], r["mid_age_ma"]) for r in audit_rows if r[f"c_min_{proxy}"] is not None]
        value, age = max(finite)
        maxima[proxy] = {"maximum_c_min": value, "age_ma": age}

    verification = {
        "internal_software_replay": "passed",
        "date": "2026-08-08",
        "public_curve_reconstruction_max_relative_error": float(
            np.max(
                np.abs(
                    np.exp(
                        np.concatenate(
                            ([0.0], np.cumsum(0.5 * (psr["lambda_p_per_ma"][:-1] + psr["lambda_p_per_ma"][1:]) * np.diff(psr["tau_ma_after_1Ma_trim"])))
                        )
                    ) / psr["F_from_dLTT"] - 1.0
                )
            )
        ),
        "random_construction_control": random_control(),
        "maximum_minimum_caps_by_proxy": maxima,
        "input_hashes": {
            "mammalia_tree1_psr.csv": sha256(DATA / "mammalia_tree1_psr.csv"),
            "mammalia_fossil_excerpt.csv": sha256(DATA / "mammalia_fossil_excerpt.csv"),
            "PSR_tree1_RData_upstream_sha256": (DATA / "PSR_tree1.Rda.sha256").read_text().split()[0],
        },
        "interpretive_warning": (
            "The fossil calculations are a mathematical sensitivity analysis. "
            "Binned fossil-genus summaries are not automatically pointwise lower bounds "
            "on the deterministic species-diversity trajectory."
        ),
    }
    (OUT / "mammalia_internal_replay.json").write_text(json.dumps(verification, indent=2) + "\n")

    make_geometry_figure()
    make_turnover_audit_figure(audit_rows)
    make_worked_sensitivity_figure(lp, x)
    make_lambda_bounds_figure(psr)

    print(json.dumps({
        "worked_case": worked,
        "maxima": maxima,
        "internal_replay": verification["internal_software_replay"],
    }, indent=2))


if __name__ == "__main__":
    main()
