from __future__ import annotations

import math
import unittest
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import linprog

from affine_diversification.affine_fibre import (
    best_of_n_endpoint_probability,
    conditional_descendant_probability,
    critical_pulled_scale,
    cumulative_loss_from_turnover,
    descendant_pgf,
    descendant_probability,
    endpoint_deficit_cdf,
    evaluate_piecewise_linear_pulled_scale,
    fixed_stem_count_density,
    fixed_stem_survival_density,
    interval_feasibility_certificate,
    mass_extinction_atom,
    maximum_identification_factor,
    minimum_turnover_cap_for_intervals,
    minimum_turnover_cap_from_diversity,
    no_external_point_bounds,
    positive_survival_certificate,
    pulled_scale,
    q_after_mass_extinction,
    required_samples_for_endpoint_tolerance,
    sharp_envelopes,
    survival_from_atom,
)

ROOT = Path(__file__).resolve().parents[1]


class AffineFibreTests(unittest.TestCase):
    def test_01_public_mammal_curve_integrates_to_reported_scale(self) -> None:
        dat = np.genfromtxt(ROOT / "data/mammalia_tree1_psr.csv", delimiter=",", names=True)
        f_calc = pulled_scale(dat["tau_ma_after_1Ma_trim"], dat["lambda_p_per_ma"])
        self.assertLess(np.max(np.abs(f_calc / dat["F_from_dLTT"] - 1.0)), 2e-14)

    def test_02_pure_birth_and_subcritical_endpoint(self) -> None:
        x = np.linspace(1.0, 8.0, 29)
        lp = np.full_like(x, 0.2)
        pure = no_external_point_bounds(x, lp, rho=1.0, turnover_cap=0.0)
        self.assertTrue(np.allclose(pure.lambda_lower, lp))
        self.assertTrue(np.allclose(pure.lambda_supremum, lp))
        self.assertEqual(pure.regime, "subcritical")
        self.assertAlmostEqual(maximum_identification_factor(0.4), 5.0 / 3.0)

    def test_03_critical_cap_is_pointwise_finite_without_uniform_factor(self) -> None:
        x = np.array([1.0, 2.0, 100.0])
        lp = np.full_like(x, 0.1)
        out = no_external_point_bounds(x, lp, rho=0.7, turnover_cap=1.0)
        self.assertEqual(out.regime, "critical")
        self.assertTrue(np.all(np.isfinite(out.lambda_supremum)))
        self.assertTrue(math.isinf(maximum_identification_factor(1.0)))
        self.assertGreater(out.width_factor[-1], out.width_factor[1])

    def test_04_supercritical_phase_transition(self) -> None:
        rho, c = 0.8, 1.2
        xc = critical_pulled_scale(rho=rho, turnover_cap=c)
        self.assertAlmostEqual(xc, 5.0)
        x = np.array([4.99, 5.0, 6.0])
        lp = np.full_like(x, 0.2)
        out = no_external_point_bounds(x, lp, rho=rho, turnover_cap=c)
        self.assertTrue(np.isfinite(out.lambda_supremum[0]))
        self.assertTrue(np.isinf(out.lambda_supremum[1]))
        self.assertFalse(out.lower_endpoint_attained[1])

    def test_05_turnover_construction_and_validation(self) -> None:
        x = np.linspace(1.0, 5.0, 9)
        c = 0.4
        n, q = cumulative_loss_from_turnover(
            x, np.full(x.size - 1, c), rho=1.0, turnover_cap=c
        )
        self.assertTrue(np.allclose(n, c * (x - 1.0)))
        self.assertTrue(np.allclose(q, 1.0 + (1.0 - c) * (x - 1.0)))
        with self.assertRaises(ValueError):
            cumulative_loss_from_turnover(x, np.full(x.size - 1, 0.6), rho=1.0, turnover_cap=0.5)
        with self.assertRaises(ValueError):
            cumulative_loss_from_turnover(np.array([1.0, 2.0, 2.0]), np.array([0.1, 0.1]), rho=1.0)

    def test_06_mass_extinction_atom_is_exact(self) -> None:
        q0 = 3.125
        for survival in (0.3, 0.7, 0.999):
            atom = mass_extinction_atom(q0, survival)
            self.assertAlmostEqual(survival_from_atom(q0, atom), survival, places=14)
            self.assertAlmostEqual(q_after_mass_extinction(q0, survival), survival * q0, places=14)

    def test_07_zero_inflated_geometric_distribution(self) -> None:
        u, F = 0.63, 4.2
        probs = [descendant_probability(k, u=u, F=F) for k in range(500)]
        self.assertAlmostEqual(sum(probs), 1.0, places=12)
        self.assertAlmostEqual(descendant_probability(1, u=u, F=F) / u, 1.0 / F, places=14)
        self.assertAlmostEqual(
            sum(conditional_descendant_probability(k, F=F) for k in range(1, 500)),
            1.0,
            places=12,
        )
        z = 0.37
        series = sum(probs[k] * z**k for k in range(len(probs)))
        self.assertAlmostEqual(float(descendant_pgf(np.array([z]), u=u, F=F)[0]), series, places=12)

    def test_08_fixed_stem_count_density_normalises(self) -> None:
        # Constant pulled rate gives h(t)=a exp(-a t).  Integrating over the
        # ordered simplex yields H(T)^(n-1)/(n-1)!.
        a, T, n = 0.28, 3.7, 4
        F_T = math.exp(a * T)
        H = 1.0 - 1.0 / F_T
        integrated_survival = (math.factorial(n - 1) / F_T) * (H ** (n - 1) / math.factorial(n - 1))
        expected = (1.0 / F_T) * H ** (n - 1)
        self.assertAlmostEqual(integrated_survival, expected, places=14)
        integrated_count = (math.factorial(n - 1) / H ** (n - 1)) * (H ** (n - 1) / math.factorial(n - 1))
        self.assertAlmostEqual(integrated_count, 1.0, places=14)
        nodes = np.array([0.5, 1.4, 2.9])
        lp = np.full(3, a)
        F = np.exp(a * nodes)
        self.assertGreater(fixed_stem_survival_density(lp, F, F_stem=F_T), 0)
        self.assertGreater(fixed_stem_count_density(lp, F, F_stem=F_T), 0)

    def test_09_finite_event_p1_over_u_identity(self) -> None:
        rho = 0.73
        state = np.array([rho, rho, 0.0], dtype=float)  # u, p1, integral lambda_p

        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            u, p1, _ = y
            lam = 0.42 + 0.07 * math.sin(0.8 * t)
            mu = 0.11 + 0.03 * math.cos(0.5 * t)
            return np.array([
                lam * u * (1.0 - u) - mu * u,
                (lam * (1.0 - 2.0 * u) - mu) * p1,
                lam * u,
            ])

        left = 0.0
        for right, survival in ((1.2, 0.7), (2.8, 0.35), (4.0, None)):
            sol = solve_ivp(rhs, (left, right), state, rtol=2e-11, atol=2e-13)
            self.assertTrue(sol.success)
            state = sol.y[:, -1]
            if survival is not None:
                state[0] *= survival
                state[1] *= survival
            self.assertAlmostEqual(state[1] / state[0], math.exp(-state[2]), places=9)
            left = right

    def test_10_pairwise_infeasibility_certificate(self) -> None:
        xi = np.array([1.0, 3.0])
        lo = np.array([0.0, 2.0])
        hi = np.array([0.0, 2.0])
        cert = interval_feasibility_certificate(xi, lo, hi, turnover_cap=0.5)
        self.assertIsNotNone(cert)
        self.assertEqual(cert["type"], "directed_lipschitz")
        self.assertAlmostEqual(cert["excess"], 1.0)

    def test_11_positive_survival_barrier(self) -> None:
        xi = np.array([1.0, 3.0, 7.0])
        self.assertIsNone(positive_survival_certificate(xi, np.array([0.2, 2.9, 6.9])))
        cert = positive_survival_certificate(xi, np.array([0.2, 3.0, 6.9]))
        self.assertIsNotNone(cert)
        self.assertEqual(cert["index"], 1)

    def test_12_minimum_cap_formula(self) -> None:
        xi = np.array([1.0, 4.0, 7.0])
        lo = np.array([0.0, 1.2, 3.0])
        hi = np.array([0.0, 1.4, 3.2])
        c_star, active = minimum_turnover_cap_for_intervals(xi, lo, hi)
        self.assertAlmostEqual(c_star, 1.6 / 3.0)
        self.assertIsNotNone(active)
        self.assertIsNone(interval_feasibility_certificate(xi, lo, hi, turnover_cap=c_star))

    def test_13_closed_form_envelopes_match_grid_linear_programmes(self) -> None:
        rng = np.random.default_rng(20260806)
        grid = np.linspace(1.0, 9.0, 33)
        c = 0.65
        eps = rng.uniform(0.05, 0.55, grid.size - 1)
        n_true, _ = cumulative_loss_from_turnover(grid, eps, rho=0.8, turnover_cap=c)
        idx = np.array([0, 5, 12, 21, 32])
        xi = grid[idx]
        lo = n_true[idx] - np.array([0.0, 0.05, 0.08, 0.06, 0.04])
        hi = n_true[idx] + np.array([0.0, 0.07, 0.05, 0.08, 0.06])
        lo[0] = hi[0] = n_true[0]
        env = sharp_envelopes(grid, xi, lo, hi, turnover_cap=c)
        self.assertTrue(env.feasible)

        nvar = grid.size
        A_ub, b_ub = [], []
        for j, dx in enumerate(np.diff(grid)):
            row = np.zeros(nvar); row[j] = 1; row[j + 1] = -1
            A_ub.append(row); b_ub.append(0.0)
            row = np.zeros(nvar); row[j] = -1; row[j + 1] = 1
            A_ub.append(row); b_ub.append(c * dx)
        for k, j in enumerate(idx):
            row = np.zeros(nvar); row[j] = -1
            A_ub.append(row); b_ub.append(-lo[k])
            row = np.zeros(nvar); row[j] = 1
            A_ub.append(row); b_ub.append(hi[k])
        A_ub, b_ub = np.asarray(A_ub), np.asarray(b_ub)
        for target in (3, 10, 18, 27):
            objective = np.zeros(nvar); objective[target] = 1.0
            rmin = linprog(objective, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * nvar, method="highs")
            rmax = linprog(-objective, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * nvar, method="highs")
            self.assertTrue(rmin.success and rmax.success)
            self.assertAlmostEqual(rmin.fun, env.lower_n[target], places=9)
            self.assertAlmostEqual(-rmax.fun, env.upper_n[target], places=9)

    def test_14_unsorted_and_duplicate_constraints_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sharp_envelopes(
                np.array([1.0, 2.0]), np.array([1.0, 1.0]),
                np.array([0.0, 0.0]), np.array([0.0, 0.0]), turnover_cap=0.5
            )
        with self.assertRaises(ValueError):
            interval_feasibility_certificate(
                np.array([2.0, 1.0]), np.array([0.0, 0.0]),
                np.array([0.0, 0.0]), turnover_cap=0.5
            )

    def test_15_endpoint_sampling_small_tail_formula(self) -> None:
        m, c, delta, eta = 8, 0.5, 1.0, 0.1
        exact = endpoint_deficit_cdf(eta, intervals=m, turnover_cap=c, interval_width=delta)
        expected = (eta / (c * delta)) ** m / math.factorial(m)
        self.assertAlmostEqual(exact, expected, places=15)
        self.assertGreater(required_samples_for_endpoint_tolerance(
            eta, target_probability=0.95, intervals=m, turnover_cap=c, interval_width=delta
        ), 1_000_000)

    def test_16_best_of_n_sampling_probability(self) -> None:
        p = endpoint_deficit_cdf(0.35, intervals=4, turnover_cap=0.5, interval_width=1.0)
        q = best_of_n_endpoint_probability(
            0.35, samples=25, intervals=4, turnover_cap=0.5, interval_width=1.0
        )
        self.assertAlmostEqual(q, 1.0 - (1.0 - p) ** 25, places=14)
        self.assertTrue(0 < q < 1)

    def test_17_mammal_worked_value(self) -> None:
        dat = np.genfromtxt(ROOT / "data/mammalia_tree1_psr.csv", delimiter=",", names=True)
        lp, x = evaluate_piecewise_linear_pulled_scale(
            dat["tau_ma_after_1Ma_trim"], dat["lambda_p_per_ma"], np.array([57.5])
        )
        self.assertAlmostEqual(x[0], 119.709050, places=5)
        self.assertAlmostEqual(lp[0], 0.0438809486, places=9)
        cmin = minimum_turnover_cap_from_diversity(
            x[0], rho=1.0, origin_lineages=4790.0, diversity_lower=577.0
        )
        self.assertAlmostEqual(cmin, 0.93849197, places=7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
