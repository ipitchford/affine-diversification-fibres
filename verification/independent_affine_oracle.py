"""Independent Decimal oracle for the confirmatory affine protocol.

This module intentionally uses only the Python standard library. It neither
imports nor calls the production affine package, NumPy, SciPy, or CRABS. The
formulas are rederived directly from the frozen mathematical specification.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Iterable

PRECISION = 80
ZERO = Decimal(0)
ONE = Decimal(1)


def D(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def vector(values: Iterable[object], name: str) -> list[Decimal]:
    result = [D(value) for value in values]
    if not result:
        raise ValueError(f"{name} must not be empty")
    if any(not value.is_finite() for value in result):
        raise ValueError(f"{name} contains a non-finite value")
    return result


def strictly_increasing(values: list[Decimal], name: str) -> None:
    if any(right <= left for left, right in zip(values, values[1:])):
        raise ValueError(f"{name} must be strictly increasing")


def pulled_scale(tau: Iterable[object], lambda_p: Iterable[object]) -> list[Decimal]:
    t = vector(tau, "tau")
    lp = vector(lambda_p, "lambda_p")
    if len(t) != len(lp):
        raise ValueError("tau and lambda_p lengths differ")
    strictly_increasing(t, "tau")
    if any(value < ZERO for value in lp):
        raise ValueError("lambda_p must be non-negative")
    with localcontext() as ctx:
        ctx.prec = PRECISION
        integral = ZERO
        out = [ONE]
        for index in range(1, len(t)):
            integral += (lp[index - 1] + lp[index]) * (t[index] - t[index - 1]) / D(2)
            out.append(+integral.exp())
        return out


def point_bounds(
    x: Iterable[object],
    lambda_p: Iterable[object],
    *,
    rho: object,
    turnover_cap: object,
) -> dict[str, object]:
    xx = vector(x, "x")
    lp = vector(lambda_p, "lambda_p")
    rr, cap = D(rho), D(turnover_cap)
    if len(xx) != len(lp):
        raise ValueError("x and lambda_p lengths differ")
    if not (ZERO < rr <= ONE) or cap < ZERO:
        raise ValueError("require rho in (0,1] and a non-negative cap")
    if any(value < ONE for value in xx) or any(value < ZERO for value in lp):
        raise ValueError("require x>=1 and lambda_p>=0")

    q_infimum: list[Decimal] = []
    q_upper: list[Decimal] = []
    lambda_lower: list[Decimal] = []
    lambda_supremum: list[Decimal | None] = []
    attained: list[bool] = []
    for scale, pulled in zip(xx, lp):
        raw = rr + (ONE - cap) * (scale - ONE)
        lower_q = max(raw, ZERO)
        upper_q = rr + scale - ONE
        numerator = pulled * scale
        q_infimum.append(lower_q)
        q_upper.append(upper_q)
        lambda_lower.append(numerator / upper_q)
        if lower_q > ZERO:
            lambda_supremum.append(numerator / lower_q)
            attained.append(True)
        else:
            lambda_supremum.append(ZERO if numerator == ZERO else None)
            attained.append(False)
    regime = "subcritical" if cap < ONE else "critical" if cap == ONE else "supercritical"
    return {
        "q_infimum": q_infimum,
        "q_upper": q_upper,
        "lambda_lower": lambda_lower,
        "lambda_supremum": lambda_supremum,
        "lower_endpoint_attained": attained,
        "regime": regime,
    }


def infeasibility_witness(
    constraint_x: Iterable[object],
    lower_n: Iterable[object],
    upper_n: Iterable[object],
    *,
    turnover_cap: object,
) -> dict[str, object] | None:
    x = vector(constraint_x, "constraint_x")
    lower = vector(lower_n, "lower_n")
    upper = vector(upper_n, "upper_n")
    cap = D(turnover_cap)
    if len(x) != len(lower) or len(x) != len(upper):
        raise ValueError("constraint arrays differ in length")
    strictly_increasing(x, "constraint_x")
    if cap < ZERO:
        raise ValueError("turnover_cap must be non-negative")
    for i, (lo, hi) in enumerate(zip(lower, upper)):
        if lo > hi:
            return {"type": "local_interval", "lower_index": i, "upper_index": i, "excess": lo - hi}
    for i, lo in enumerate(lower):
        for j, hi in enumerate(upper):
            directed = max(x[i] - x[j], ZERO)
            rhs = hi + cap * directed
            if lo > rhs:
                return {
                    "type": "directed_lipschitz",
                    "lower_index": i,
                    "upper_index": j,
                    "lhs": lo,
                    "rhs": rhs,
                    "excess": lo - rhs,
                }
    return None


def sharp_envelopes(
    evaluation_x: Iterable[object],
    constraint_x: Iterable[object],
    lower_n: Iterable[object],
    upper_n: Iterable[object],
    *,
    turnover_cap: object,
    require_positive_survival: bool = True,
) -> dict[str, object]:
    evaluate = vector(evaluation_x, "evaluation_x")
    x = vector(constraint_x, "constraint_x")
    lower = vector(lower_n, "lower_n")
    upper = vector(upper_n, "upper_n")
    cap = D(turnover_cap)
    strictly_increasing(evaluate, "evaluation_x")
    strictly_increasing(x, "constraint_x")
    if len(x) != len(lower) or len(x) != len(upper):
        raise ValueError("constraint arrays differ in length")
    witness = infeasibility_witness(x, lower, upper, turnover_cap=cap)
    barrier = next((i for i, (lo, xx) in enumerate(zip(lower, x)) if lo >= xx), None)
    if witness is None and require_positive_survival and barrier is not None:
        witness = {
            "type": "positive_survival_barrier",
            "index": barrier,
            "x": x[barrier],
            "lower_n": lower[barrier],
        }
    least = [max(lo - cap * max(xi - point, ZERO) for xi, lo in zip(x, lower)) for point in evaluate]
    greatest = [min(hi + cap * max(point - xi, ZERO) for xi, hi in zip(x, upper)) for point in evaluate]
    feasible = witness is None and all(lo <= hi for lo, hi in zip(least, greatest))
    if require_positive_survival:
        feasible = feasible and all(lo < point for lo, point in zip(least, evaluate))
    return {"lower_n": least, "upper_n": greatest, "feasible": feasible, "certificate": witness}


def minimum_turnover_cap(
    constraint_x: Iterable[object], lower_n: Iterable[object], upper_n: Iterable[object]
) -> tuple[Decimal | None, dict[str, object] | None]:
    x = vector(constraint_x, "constraint_x")
    lower = vector(lower_n, "lower_n")
    upper = vector(upper_n, "upper_n")
    if len(x) != len(lower) or len(x) != len(upper):
        raise ValueError("constraint arrays differ in length")
    strictly_increasing(x, "constraint_x")
    best = ZERO
    active = None
    for i, lo in enumerate(lower):
        for j, hi in enumerate(upper):
            if x[i] <= x[j]:
                if lo > hi:
                    return None, {"type": "monotonicity", "lower_index": i, "upper_index": j}
            else:
                required = max(lo - hi, ZERO) / (x[i] - x[j])
                if required > best:
                    best = required
                    active = {"type": "minimum_cap", "lower_index": i, "upper_index": j}
    return best, active
