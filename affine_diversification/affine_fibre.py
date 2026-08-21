"""Affine coordinates and certified bounds for birth--death congruence fibres.

The module uses the pulled-scale coordinate ``x = F(tau)``.  In the
absolutely continuous class a history is represented by cumulative loss
``n(x)`` with derivative ``n'(x) = mu/lambda`` almost everywhere.  The
implementation parameterises turnover directly; it never differentiates a
rough fitted curve to recover a cap.

All bounds are conditional on the supplied pulled signal and structural
constraints.  They are not statistical confidence intervals.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, factorial, log, log1p, sqrt
from typing import Optional

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
__version__ = "0.3.0rc2"


def _as_float_1d(values: ArrayLike, name: str) -> FloatArray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains a non-finite value")
    return arr


def _require_strictly_increasing(values: FloatArray, name: str) -> None:
    if values.size > 1 and np.any(np.diff(values) <= 0):
        raise ValueError(f"{name} must be strictly increasing with no duplicates")


def _validate_rho(rho: float) -> None:
    if not np.isfinite(rho) or not (0.0 < rho <= 1.0):
        raise ValueError("rho must lie in (0,1]")


def cumulative_trapezoid(y: ArrayLike, x: ArrayLike) -> FloatArray:
    """Return the cumulative trapezoidal integral, anchored at zero."""
    y_arr = _as_float_1d(y, "y")
    x_arr = _as_float_1d(x, "x")
    if y_arr.size != x_arr.size:
        raise ValueError("x and y must have the same length")
    _require_strictly_increasing(x_arr, "x")
    out = np.zeros_like(x_arr)
    if x_arr.size > 1:
        out[1:] = np.cumsum(0.5 * (y_arr[:-1] + y_arr[1:]) * np.diff(x_arr))
    return out


def pulled_scale(tau: ArrayLike, lambda_p: ArrayLike) -> FloatArray:
    """Compute ``F(tau)=exp(integral_0^tau lambda_p)`` on a grid."""
    tau_arr = _as_float_1d(tau, "tau")
    lp_arr = _as_float_1d(lambda_p, "lambda_p")
    if tau_arr.size != lp_arr.size:
        raise ValueError("tau and lambda_p must have the same length")
    _require_strictly_increasing(tau_arr, "tau")
    if np.any(lp_arr < 0):
        raise ValueError("lambda_p must be non-negative")
    return np.exp(cumulative_trapezoid(lp_arr, tau_arr))


def evaluate_piecewise_linear_pulled_scale(
    tau_grid: ArrayLike,
    lambda_p_grid: ArrayLike,
    tau_eval: ArrayLike,
) -> tuple[FloatArray, FloatArray]:
    """Evaluate a piecewise-linear pulled rate and its exact integrated scale."""
    tg = _as_float_1d(tau_grid, "tau_grid")
    pg = _as_float_1d(lambda_p_grid, "lambda_p_grid")
    te = _as_float_1d(tau_eval, "tau_eval")
    if tg.size != pg.size:
        raise ValueError("tau_grid and lambda_p_grid must have equal length")
    if tg.size < 2:
        raise ValueError("tau_grid must contain at least two points")
    _require_strictly_increasing(tg, "tau_grid")
    if np.any(pg < 0):
        raise ValueError("lambda_p_grid must be non-negative")
    if np.any(te < tg[0]) or np.any(te > tg[-1]):
        raise ValueError("tau_eval lies outside tau_grid")

    cumulative = cumulative_trapezoid(pg, tg)
    values = np.empty_like(te)
    integrals = np.empty_like(te)
    for k, t in enumerate(te):
        j = tg.size - 2 if t == tg[-1] else int(np.searchsorted(tg, t, side="right") - 1)
        j = max(0, min(j, tg.size - 2))
        h = tg[j + 1] - tg[j]
        z = t - tg[j]
        slope = (pg[j + 1] - pg[j]) / h
        values[k] = pg[j] + slope * z
        integrals[k] = cumulative[j] + pg[j] * z + 0.5 * slope * z * z
    return values, np.exp(integrals)


@dataclass(frozen=True)
class EnvelopeResult:
    evaluation_x: FloatArray
    lower_n: FloatArray
    upper_n: FloatArray
    feasible: bool
    certificate: Optional[dict]


@dataclass(frozen=True)
class PointBounds:
    x: FloatArray
    q_infimum: FloatArray
    q_upper: FloatArray
    lambda_lower: FloatArray
    lambda_supremum: FloatArray
    width_factor: FloatArray
    lower_endpoint_attained: NDArray[np.bool_]
    regime: str


@dataclass(frozen=True)
class FixedStemSignalBand:
    """Finite-sample simultaneous band for a fixed-stem pulled scale.

    Coverage is with respect to the exact fixed-stem reconstructed-process law,
    conditional on stem survival.  It does not include tree-dating error,
    smoothing uncertainty, or model misspecification.
    """

    evaluation_ages: FloatArray
    empirical_branching_cdf: FloatArray
    branching_cdf_lower: FloatArray
    branching_cdf_upper: FloatArray
    survival_lower: FloatArray
    survival_upper: FloatArray
    F_lower: FloatArray
    F_upper: FloatArray
    F_plugin: FloatArray
    p_lower: float
    p_upper: float
    p_plugin: float
    dkw_radius: float
    n_tips: int
    alpha: float
    alpha_count: float
    alpha_ages: float


@dataclass(frozen=True)
class TurnoverCapDecision:
    """Robust decision for one deterministic diversity constraint."""

    status: str
    plugin_status: str
    proposed_cap: float
    minimum_cap_lower: float
    minimum_cap_upper: float
    minimum_cap_plugin: float
    F_lower: float
    F_upper: float
    F_plugin: float


def turnover_cap_regime(turnover_cap: float) -> str:
    """Classify the cap as subcritical, critical or supercritical."""
    if not np.isfinite(turnover_cap) or turnover_cap < 0:
        raise ValueError("turnover_cap must be finite and non-negative")
    if turnover_cap < 1.0:
        return "subcritical"
    if turnover_cap == 1.0:
        return "critical"
    return "supercritical"


def critical_pulled_scale(*, rho: float, turnover_cap: float) -> float:
    """Return the supercritical scale where the speciation supremum diverges."""
    _validate_rho(rho)
    regime = turnover_cap_regime(turnover_cap)
    if regime != "supercritical":
        return float("inf")
    return float(1.0 + rho / (turnover_cap - 1.0))


def no_external_point_bounds(
    x: ArrayLike,
    lambda_p: ArrayLike,
    *,
    rho: float,
    turnover_cap: float,
) -> PointBounds:
    """Sharp pointwise bounds under ``0 <= mu/lambda <= turnover_cap``.

    The class has no interior atoms.  For supercritical caps the lower survival
    endpoint can be zero as an unattained infimum; the corresponding speciation
    supremum is infinite whenever the pulled rate is positive.
    """
    x_arr = _as_float_1d(x, "x")
    lp_arr = _as_float_1d(lambda_p, "lambda_p")
    if x_arr.size != lp_arr.size:
        raise ValueError("x and lambda_p must have the same length")
    if np.any(x_arr < 1):
        raise ValueError("x must be at least 1")
    if np.any(lp_arr < 0):
        raise ValueError("lambda_p must be non-negative")
    _validate_rho(rho)
    regime = turnover_cap_regime(turnover_cap)

    raw_lower = rho + (1.0 - turnover_cap) * (x_arr - 1.0)
    scale_tolerance = 32.0 * np.finfo(float).eps * np.maximum(1.0, np.abs(rho) + np.abs((1.0 - turnover_cap) * (x_arr - 1.0)))
    attained = raw_lower > scale_tolerance
    q_inf = np.where(attained, raw_lower, 0.0)
    q_upper = rho + x_arr - 1.0

    numerator = lp_arr * x_arr
    lambda_lower = numerator / q_upper
    lambda_sup = np.empty_like(numerator)
    positive = q_inf > 0
    lambda_sup[positive] = numerator[positive] / q_inf[positive]
    lambda_sup[~positive] = np.where(numerator[~positive] > 0, np.inf, 0.0)
    width = np.divide(
        lambda_sup,
        lambda_lower,
        out=np.ones_like(lambda_sup),
        where=lambda_lower > 0,
    )
    width[(lambda_lower > 0) & np.isinf(lambda_sup)] = np.inf
    return PointBounds(
        x=x_arr,
        q_infimum=q_inf,
        q_upper=q_upper,
        lambda_lower=lambda_lower,
        lambda_supremum=lambda_sup,
        width_factor=width,
        lower_endpoint_attained=attained,
        regime=regime,
    )


def maximum_identification_factor(turnover_cap: float) -> float:
    """Uniform deep-time width: ``1/(1-c)`` for ``c<1``, infinite otherwise."""
    regime = turnover_cap_regime(turnover_cap)
    if regime != "subcritical":
        return float("inf")
    return float(1.0 / (1.0 - turnover_cap))


def cumulative_loss_from_turnover(
    x: ArrayLike,
    interval_turnover: ArrayLike,
    *,
    rho: float,
    turnover_cap: float | None = None,
    require_positive_survival: bool = True,
) -> tuple[FloatArray, FloatArray]:
    """Construct cumulative loss ``n`` and survival scale ``q=x-n`` exactly.

    ``interval_turnover[j]`` applies on ``[x[j],x[j+1]]``.  The full fibre
    trajectory must start at ``x=1`` with ``q(1)=rho``.
    """
    x_arr = _as_float_1d(x, "x")
    eps = _as_float_1d(interval_turnover, "interval_turnover")
    _require_strictly_increasing(x_arr, "x")
    if not np.isclose(x_arr[0], 1.0, atol=1e-12, rtol=0):
        raise ValueError("x must start at 1 for an anchored trajectory")
    if eps.size != x_arr.size - 1:
        raise ValueError("interval_turnover must have length len(x)-1")
    _validate_rho(rho)
    if np.any(eps < 0):
        raise ValueError("turnover must be non-negative")
    if turnover_cap is not None:
        turnover_cap_regime(turnover_cap)
        if np.any(eps > turnover_cap + 1e-12):
            raise ValueError("turnover exceeds turnover_cap")

    q = np.empty_like(x_arr)
    q[0] = rho
    q[1:] = rho + np.cumsum((1.0 - eps) * np.diff(x_arr))
    if require_positive_survival and np.any(q <= 0):
        raise ValueError("turnover trajectory crosses the positive-survival barrier")
    n = x_arr - q
    return n, q


def rates_from_turnover(
    lambda_p: ArrayLike,
    x: ArrayLike,
    q: ArrayLike,
    turnover: ArrayLike,
) -> tuple[FloatArray, FloatArray]:
    """Recover ``lambda`` and ``mu`` from ``q`` and ``epsilon=mu/lambda``."""
    lp = _as_float_1d(lambda_p, "lambda_p")
    x_arr = _as_float_1d(x, "x")
    q_arr = _as_float_1d(q, "q")
    eps = _as_float_1d(turnover, "turnover")
    if not (lp.size == x_arr.size == q_arr.size == eps.size):
        raise ValueError("all inputs must have the same length")
    if np.any(lp < 0) or np.any(x_arr < 1) or np.any(q_arr <= 0) or np.any(eps < 0):
        raise ValueError("rates require lambda_p>=0, x>=1, q>0 and turnover>=0")
    lam = lp * x_arr / q_arr
    return lam, eps * lam


def _validate_constraints(
    constraint_x: ArrayLike,
    lower_n: ArrayLike,
    upper_n: ArrayLike,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    xi = _as_float_1d(constraint_x, "constraint_x")
    lo = _as_float_1d(lower_n, "lower_n")
    hi = _as_float_1d(upper_n, "upper_n")
    if not (xi.size == lo.size == hi.size):
        raise ValueError("constraint arrays must have equal length")
    _require_strictly_increasing(xi, "constraint_x")
    if np.any(xi < 1):
        raise ValueError("constraint_x must be at least 1")
    return xi, lo, hi


def interval_feasibility_certificate(
    constraint_x: ArrayLike,
    lower_n: ArrayLike,
    upper_n: ArrayLike,
    *,
    turnover_cap: float,
    tolerance: float = 1e-12,
) -> Optional[dict]:
    """Return a finite directed-Lipschitz infeasibility witness, or ``None``."""
    xi, lo, hi = _validate_constraints(constraint_x, lower_n, upper_n)
    turnover_cap_regime(turnover_cap)
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    local = np.flatnonzero(lo > hi + tolerance)
    if local.size:
        i = int(local[0])
        return {
            "type": "local_interval",
            "lower_index": i,
            "upper_index": i,
            "lhs": float(lo[i]),
            "rhs": float(hi[i]),
            "excess": float(lo[i] - hi[i]),
        }
    for i in range(xi.size):
        for j in range(xi.size):
            rhs = hi[j] + turnover_cap * max(float(xi[i] - xi[j]), 0.0)
            if lo[i] > rhs + tolerance:
                return {
                    "type": "directed_lipschitz",
                    "lower_index": int(i),
                    "upper_index": int(j),
                    "x_lower": float(xi[i]),
                    "x_upper": float(xi[j]),
                    "lhs": float(lo[i]),
                    "rhs": float(rhs),
                    "excess": float(lo[i] - rhs),
                }
    return None


def positive_survival_certificate(
    constraint_x: ArrayLike,
    lower_n: ArrayLike,
    *,
    tolerance: float = 1e-12,
) -> Optional[dict]:
    """Return a barrier witness when a lower constraint forces ``n(x)>=x``."""
    xi = _as_float_1d(constraint_x, "constraint_x")
    lo = _as_float_1d(lower_n, "lower_n")
    if xi.size != lo.size:
        raise ValueError("constraint_x and lower_n must have equal length")
    _require_strictly_increasing(xi, "constraint_x")
    bad = np.flatnonzero(lo >= xi - tolerance)
    if bad.size:
        i = int(bad[0])
        return {
            "type": "positive_survival_barrier",
            "index": i,
            "x": float(xi[i]),
            "lower_n": float(lo[i]),
            "excess": float(lo[i] - xi[i]),
        }
    return None


def sharp_envelopes(
    evaluation_x: ArrayLike,
    constraint_x: ArrayLike,
    lower_n: ArrayLike,
    upper_n: ArrayLike,
    *,
    turnover_cap: float,
    require_positive_survival: bool = True,
) -> EnvelopeResult:
    """Return the exact least and greatest directed-Lipschitz trajectories."""
    x = _as_float_1d(evaluation_x, "evaluation_x")
    _require_strictly_increasing(x, "evaluation_x")
    if np.any(x < 1):
        raise ValueError("evaluation_x must be at least 1")
    xi, lo, hi = _validate_constraints(constraint_x, lower_n, upper_n)
    turnover_cap_regime(turnover_cap)
    cert = interval_feasibility_certificate(xi, lo, hi, turnover_cap=turnover_cap)
    if cert is None and require_positive_survival:
        cert = positive_survival_certificate(xi, lo)
    lower_terms = lo[:, None] - turnover_cap * np.maximum(xi[:, None] - x[None, :], 0.0)
    upper_terms = hi[:, None] + turnover_cap * np.maximum(x[None, :] - xi[:, None], 0.0)
    lower = np.max(lower_terms, axis=0)
    upper = np.min(upper_terms, axis=0)
    feasible = cert is None and bool(np.all(lower <= upper + 1e-10))
    if require_positive_survival:
        feasible = feasible and bool(np.all(lower < x - 1e-12))
    return EnvelopeResult(x, lower, upper, feasible, cert)


def minimum_turnover_cap_for_intervals(
    constraint_x: ArrayLike,
    lower_n: ArrayLike,
    upper_n: ArrayLike,
    *,
    tolerance: float = 1e-12,
) -> tuple[float, Optional[dict]]:
    """Return the smallest finite directed-Lipschitz cap, or infinity."""
    xi, lo, hi = _validate_constraints(constraint_x, lower_n, upper_n)
    local = np.flatnonzero(lo > hi + tolerance)
    if local.size:
        i = int(local[0])
        return float("inf"), {"type": "local_interval", "lower_index": i, "upper_index": i}
    c_star = 0.0
    active: Optional[dict] = None
    for i in range(xi.size):
        for j in range(xi.size):
            if xi[i] <= xi[j] + tolerance:
                if lo[i] > hi[j] + tolerance:
                    return float("inf"), {
                        "type": "monotonicity",
                        "lower_index": int(i),
                        "upper_index": int(j),
                        "x_lower": float(xi[i]),
                        "x_upper": float(xi[j]),
                        "lhs": float(lo[i]),
                        "rhs": float(hi[j]),
                    }
            else:
                required = max(float(lo[i] - hi[j]), 0.0) / float(xi[i] - xi[j])
                if required > c_star + tolerance:
                    c_star = required
                    active = {
                        "type": "minimum_cap",
                        "lower_index": int(i),
                        "upper_index": int(j),
                        "x_lower": float(xi[i]),
                        "x_upper": float(xi[j]),
                        "required_cap": float(required),
                    }
    return float(c_star), active


def fossil_q_upper(origin_lineages: float, diversity_lower: float) -> float:
    """Translate a model-scale deterministic diversity lower bound to ``q``."""
    if not np.isfinite(origin_lineages) or not np.isfinite(diversity_lower):
        raise ValueError("origin_lineages and diversity_lower must be finite")
    if origin_lineages <= 0 or diversity_lower <= 0:
        raise ValueError("origin_lineages and diversity_lower must be positive")
    return float(origin_lineages / diversity_lower)


def minimum_turnover_cap_from_diversity(
    x: float,
    *,
    rho: float,
    origin_lineages: float,
    diversity_lower: float,
) -> float:
    """Minimum cap compatible with a deterministic model-scale lower bound."""
    if not np.isfinite(x) or x <= 1:
        raise ValueError("x must be finite and exceed 1")
    _validate_rho(rho)
    q_bound = fossil_q_upper(origin_lineages, diversity_lower)
    return float(max(0.0, 1.0 - (q_bound - rho) / (x - 1.0)))


def geometric_probability_interval(n: int, *, alpha: float) -> tuple[float, float]:
    """Equal-tailed exact interval for ``p`` from ``N ~ Geometric(p)``.

    The geometric distribution is supported on ``1, 2, ...``.  The endpoints
    invert ``P_p(N <= n)`` and ``P_p(N >= n)``; discreteness makes coverage
    conservative rather than below the requested ``1-alpha`` level.
    """
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if not np.isfinite(alpha) or not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie in (0,1)")
    tail = 0.5 * float(alpha)
    lower = -np.expm1(np.log1p(-tail) / int(n))
    upper = 1.0 if n == 1 else -np.expm1(log(tail) / (int(n) - 1))
    return float(lower), float(upper)


def fixed_stem_signal_band(
    branching_ages: ArrayLike,
    evaluation_ages: ArrayLike,
    *,
    stem_age: float,
    alpha: float = 0.05,
    alpha_count: float | None = None,
    alpha_ages: float | None = None,
) -> FixedStemSignalBand:
    """Construct an honest simultaneous band for ``F`` under fixed stem age.

    Conditional on stem survival, the positive tip count is geometric with
    ``p=1/F(stem_age)``.  Conditional on that count, the ``N-1`` unordered
    branching ages are iid with CDF

    ``B(t) = (1 - 1/F(t)) / (1 - 1/F(stem_age))``.

    An exact geometric interval and a two-sided DKW--Massart band are combined
    by Bonferroni.  The returned coverage is therefore at least ``1-alpha`` for
    the full evaluated curve whenever the stated process law is correct.
    """
    ages = np.asarray(branching_ages, dtype=float)
    if ages.ndim != 1:
        raise ValueError("branching_ages must be one-dimensional")
    if not np.all(np.isfinite(ages)):
        raise ValueError("branching_ages contains a non-finite value")
    evaluation = _as_float_1d(evaluation_ages, "evaluation_ages")
    _require_strictly_increasing(evaluation, "evaluation_ages")
    if not np.isfinite(stem_age) or stem_age <= 0:
        raise ValueError("stem_age must be finite and positive")
    if np.any(ages <= 0) or np.any(ages >= stem_age):
        raise ValueError("branching ages must lie strictly inside (0, stem_age)")
    if evaluation[0] < 0 or evaluation[-1] > stem_age:
        raise ValueError("evaluation_ages must lie in [0, stem_age]")
    if not np.isfinite(alpha) or not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie in (0,1)")

    if alpha_count is None and alpha_ages is None:
        alpha_count = 0.5 * alpha
        alpha_ages = 0.5 * alpha
    elif alpha_count is None:
        alpha_count = alpha - float(alpha_ages)
    elif alpha_ages is None:
        alpha_ages = alpha - float(alpha_count)
    alpha_count = float(alpha_count)
    alpha_ages = float(alpha_ages)
    if not (0.0 < alpha_count < 1.0) or not (0.0 < alpha_ages < 1.0):
        raise ValueError("alpha_count and alpha_ages must lie in (0,1)")
    if alpha_count + alpha_ages > alpha + 64.0 * np.finfo(float).eps:
        raise ValueError("alpha_count + alpha_ages must not exceed alpha")

    n_tips = int(ages.size + 1)
    p_lower, p_upper = geometric_probability_interval(n_tips, alpha=alpha_count)
    p_plugin = 1.0 / n_tips

    if ages.size:
        sorted_ages = np.sort(ages)
        empirical = np.searchsorted(sorted_ages, evaluation, side="right") / ages.size
        radius = sqrt(log(2.0 / alpha_ages) / (2.0 * ages.size))
        b_lower = np.maximum(0.0, empirical - radius)
        b_upper = np.minimum(1.0, empirical + radius)
    else:
        empirical = np.zeros_like(evaluation)
        radius = 1.0
        b_lower = np.zeros_like(evaluation)
        b_upper = np.ones_like(evaluation)

    at_zero = np.isclose(evaluation, 0.0, atol=1e-12, rtol=0.0)
    at_stem = np.isclose(evaluation, stem_age, atol=1e-12, rtol=0.0)
    empirical[at_zero] = 0.0
    b_lower[at_zero] = 0.0
    b_upper[at_zero] = 0.0
    empirical[at_stem] = 1.0
    b_lower[at_stem] = 1.0
    b_upper[at_stem] = 1.0

    survival_lower = 1.0 - (1.0 - p_lower) * b_upper
    survival_upper = 1.0 - (1.0 - p_upper) * b_lower
    survival_plugin = 1.0 - (1.0 - p_plugin) * empirical
    if np.any(survival_lower <= 0) or np.any(survival_lower > survival_upper):
        raise RuntimeError("internal error while mapping the CDF band to survival")

    return FixedStemSignalBand(
        evaluation_ages=evaluation,
        empirical_branching_cdf=empirical,
        branching_cdf_lower=b_lower,
        branching_cdf_upper=b_upper,
        survival_lower=survival_lower,
        survival_upper=survival_upper,
        F_lower=1.0 / survival_upper,
        F_upper=1.0 / survival_lower,
        F_plugin=1.0 / survival_plugin,
        p_lower=p_lower,
        p_upper=p_upper,
        p_plugin=p_plugin,
        dkw_radius=float(radius),
        n_tips=n_tips,
        alpha=float(alpha),
        alpha_count=alpha_count,
        alpha_ages=alpha_ages,
    )


def turnover_cap_decision_from_signal_band(
    *,
    F_lower: float,
    F_upper: float,
    F_plugin: float,
    rho: float,
    origin_lineages: float,
    diversity_lower: float,
    proposed_cap: float,
    tolerance: float = 1e-12,
) -> TurnoverCapDecision:
    """Propagate a signal band into a three-valued cap decision.

    ``CERTIFIED_INCOMPATIBLE`` means every pulled scale in the supplied band
    violates the proposed cap for the stated deterministic diversity bound.
    ``CERTIFIED_COMPATIBLE`` means the cap is feasible throughout the band.
    Otherwise statistical uncertainty crosses the decision boundary and the
    correct result is ``UNRESOLVED``.
    """
    values = np.asarray([F_lower, F_upper, F_plugin, proposed_cap, tolerance], dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("signal, cap and tolerance inputs must be finite")
    if F_lower <= 1 or F_upper < F_lower or not (F_lower <= F_plugin <= F_upper):
        raise ValueError("require 1 < F_lower <= F_plugin <= F_upper")
    _validate_rho(rho)
    turnover_cap_regime(proposed_cap)
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    q_bound = fossil_q_upper(origin_lineages, diversity_lower)
    offset = q_bound - rho

    def required_cap(x: float) -> float:
        return max(0.0, 1.0 - offset / (x - 1.0))

    cap_at_lower = required_cap(F_lower)
    cap_at_upper = required_cap(F_upper)
    cap_min = min(cap_at_lower, cap_at_upper)
    cap_max = max(cap_at_lower, cap_at_upper)
    cap_plugin = required_cap(F_plugin)

    if proposed_cap < cap_min - tolerance:
        status = "CERTIFIED_INCOMPATIBLE"
    elif proposed_cap >= cap_max - tolerance:
        status = "CERTIFIED_COMPATIBLE"
    else:
        status = "UNRESOLVED"
    plugin_status = (
        "PLUGIN_COMPATIBLE"
        if proposed_cap >= cap_plugin - tolerance
        else "PLUGIN_INCOMPATIBLE"
    )
    return TurnoverCapDecision(
        status=status,
        plugin_status=plugin_status,
        proposed_cap=float(proposed_cap),
        minimum_cap_lower=float(cap_min),
        minimum_cap_upper=float(cap_max),
        minimum_cap_plugin=float(cap_plugin),
        F_lower=float(F_lower),
        F_upper=float(F_upper),
        F_plugin=float(F_plugin),
    )


def mass_extinction_atom(q_before: float, survival_fraction: float) -> float:
    """Return the cumulative-loss atom that produces a survival fraction."""
    if not np.isfinite(q_before) or q_before <= 0:
        raise ValueError("q_before must be finite and positive")
    if not np.isfinite(survival_fraction) or not (0 < survival_fraction <= 1):
        raise ValueError("survival_fraction must lie in (0,1]")
    return float((1.0 - survival_fraction) * q_before)


def survival_from_atom(q_before: float, atom_mass: float) -> float:
    """Recover the survival fraction from a cumulative-loss atom."""
    if not np.isfinite(q_before) or q_before <= 0:
        raise ValueError("q_before must be finite and positive")
    if not np.isfinite(atom_mass) or not (0 <= atom_mass < q_before):
        raise ValueError("atom_mass must lie in [0,q_before)")
    return float(1.0 - atom_mass / q_before)


def q_after_mass_extinction(q_before: float, survival_fraction: float) -> float:
    """Apply the exact event update ``q_after=s*q_before``."""
    return float(q_before - mass_extinction_atom(q_before, survival_fraction))


def descendant_pgf(z: ArrayLike, *, u: float, F: float) -> FloatArray:
    """Zero-inflated geometric probability-generating function."""
    zz = np.asarray(z, dtype=float)
    if not np.all(np.isfinite(zz)):
        raise ValueError("z contains a non-finite value")
    if not (0 <= u <= 1) or F < 1 or not np.isfinite(F):
        raise ValueError("require u in [0,1] and finite F>=1")
    a = 1.0 / F
    return 1.0 - u + u * (a * zz) / (1.0 - (1.0 - a) * zz)


def descendant_probability(k: int, *, u: float, F: float) -> float:
    """Probability of exactly ``k`` sampled descendants from one lineage."""
    if not isinstance(k, (int, np.integer)) or k < 0:
        raise ValueError("k must be a non-negative integer")
    if not (0 <= u <= 1) or F < 1 or not np.isfinite(F):
        raise ValueError("require u in [0,1] and finite F>=1")
    if k == 0:
        return float(1.0 - u)
    return float((u / F) * (1.0 - 1.0 / F) ** (k - 1))


def conditional_descendant_probability(k: int, *, F: float) -> float:
    """Probability of ``k>=1`` descendants conditional on positive survival."""
    if not isinstance(k, (int, np.integer)) or k < 1:
        raise ValueError("k must be a positive integer")
    if F < 1 or not np.isfinite(F):
        raise ValueError("F must be finite and at least 1")
    return float((1.0 / F) * (1.0 - 1.0 / F) ** (k - 1))


def fixed_stem_unconditioned_density(
    lambda_p_nodes: ArrayLike,
    F_nodes: ArrayLike,
    *,
    u_stem: float,
    F_stem: float,
) -> float:
    """Unconditioned density of ordered node ages, topology marginalised."""
    lp = _as_float_1d(lambda_p_nodes, "lambda_p_nodes")
    ff = _as_float_1d(F_nodes, "F_nodes")
    if lp.size != ff.size or np.any(lp < 0) or np.any(ff < 1):
        raise ValueError("node arrays must match with lambda_p>=0 and F>=1")
    if not (0 <= u_stem <= 1) or F_stem < 1:
        raise ValueError("require u_stem in [0,1] and F_stem>=1")
    return float((u_stem / F_stem) * factorial(lp.size) * np.prod(lp / ff))


def fixed_stem_survival_density(
    lambda_p_nodes: ArrayLike,
    F_nodes: ArrayLike,
    *,
    F_stem: float,
) -> float:
    """Density conditional on the stem leaving at least one sampled descendant."""
    lp = _as_float_1d(lambda_p_nodes, "lambda_p_nodes")
    ff = _as_float_1d(F_nodes, "F_nodes")
    if lp.size != ff.size or np.any(lp < 0) or np.any(ff < 1) or F_stem < 1:
        raise ValueError("invalid node or stem inputs")
    return float((factorial(lp.size) / F_stem) * np.prod(lp / ff))


def fixed_stem_count_density(
    lambda_p_nodes: ArrayLike,
    F_nodes: ArrayLike,
    *,
    F_stem: float,
) -> float:
    """Density conditional on the observed positive tip count."""
    lp = _as_float_1d(lambda_p_nodes, "lambda_p_nodes")
    ff = _as_float_1d(F_nodes, "F_nodes")
    if lp.size != ff.size or np.any(lp < 0) or np.any(ff < 1) or F_stem <= 1:
        raise ValueError("invalid node or stem inputs")
    denom = (1.0 - 1.0 / F_stem) ** lp.size
    return float((factorial(lp.size) / denom) * np.prod(lp / ff))


def endpoint_deficit_cdf(
    deficit: float,
    *,
    intervals: int,
    turnover_cap: float,
    interval_width: float,
) -> float:
    """Exact CDF for an equal-grid uniform-turnover endpoint deficit.

    If each interval turnover is independently Uniform(0,c), the deficit from
    the sharp maximal cumulative-loss endpoint is ``delta*sum(c-epsilon_j)``.
    The CDF is the Irwin--Hall CDF after rescaling.
    """
    if intervals < 1 or not isinstance(intervals, (int, np.integer)):
        raise ValueError("intervals must be a positive integer")
    if not np.isfinite(turnover_cap) or turnover_cap <= 0:
        raise ValueError("turnover_cap must be finite and positive")
    if not np.isfinite(interval_width) or interval_width <= 0:
        raise ValueError("interval_width must be finite and positive")
    if not np.isfinite(deficit):
        raise ValueError("deficit must be finite")
    if deficit <= 0:
        return 0.0
    scale = turnover_cap * interval_width
    z = deficit / scale
    if z >= intervals:
        return 1.0
    total = 0.0
    upper = min(int(np.floor(z)), intervals)
    for k in range(upper + 1):
        total += (-1.0) ** k * comb(intervals, k) * (z - k) ** intervals
    value = total / factorial(intervals)
    return float(min(max(value, 0.0), 1.0))


def best_of_n_endpoint_probability(
    deficit_tolerance: float,
    *,
    samples: int,
    intervals: int,
    turnover_cap: float,
    interval_width: float,
) -> float:
    """Probability that at least one of ``samples`` trajectories is near endpoint."""
    if samples < 1 or not isinstance(samples, (int, np.integer)):
        raise ValueError("samples must be a positive integer")
    p = endpoint_deficit_cdf(
        deficit_tolerance,
        intervals=intervals,
        turnover_cap=turnover_cap,
        interval_width=interval_width,
    )
    return float(-np.expm1(samples * log1p(-p))) if p < 1 else 1.0


def required_samples_for_endpoint_tolerance(
    deficit_tolerance: float,
    *,
    target_probability: float,
    intervals: int,
    turnover_cap: float,
    interval_width: float,
) -> int:
    """Smallest sample count giving the requested endpoint-hit probability."""
    if not np.isfinite(target_probability) or not (0 < target_probability < 1):
        raise ValueError("target_probability must lie in (0,1)")
    p = endpoint_deficit_cdf(
        deficit_tolerance,
        intervals=intervals,
        turnover_cap=turnover_cap,
        interval_width=interval_width,
    )
    if p <= 0:
        raise ValueError("the endpoint tolerance has zero probability")
    if p >= 1:
        return 1
    return int(np.ceil(log1p(-target_probability) / log1p(-p)))
