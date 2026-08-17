# Matched CRABS comparison: result record

**Status:** primary run completed successfully on 17 August 2026. The preregistered adoption rule fires: use the affine routine as the **conditional endpoint-certification layer** under the matched conventions, while retaining CRABS for construction, visualisation and stochastic exploration of congruent histories.

This closes the software-comparison gate declared in Evidence Press release `v0.2.1-candidate`. It does **not** provide external theorem review, biological validation, posterior coverage or a general ranking of CRABS.

## Prospective protocol

The release specified the desired comparison but did not contain an operational preregistration. The protocol was therefore frozen prospectively in commit [`021537a4ffeeae9c6641f1526a7741dcb36d8491`](https://github.com/ipitchford/affine-diversification-fibres/commit/021537a4ffeeae9c6641f1526a7741dcb36d8491), before the pilot and primary runs.

Frozen conventions:

- Evidence Press target: `v0.2.1-candidate`, DOI `10.5281/zenodo.21851319`.
- Comparator: CRABS commit `f2af9b6c8bb93f5512c2882d2e816060c9e07728`, package version `1.2.0.9001`.
- Signal: released Mammalia pulled-speciation curve, τ=0–70 Ma, 15 knots at 5 Ma intervals, piecewise-linear interpolation.
- Sampling fraction: ρ=1.
- Restriction: `0 ≤ μ/λ ≤ 0.5`.
- External constraints: none.
- Arithmetic: IEEE-754 double precision.
- Primary sample targets: 100, 1,000 and 10,000; 10 fixed seeds.
- Native sampler ceiling: 500,000 proposals per seed.
- Material miss: more than 5% of the CRABS-discrete identified width from either endpoint at any non-zero-width knot in at least 5/10 replicates.
- Native practical failure: any seed incomplete at the proposal ceiling, or median acceptance below 2%.

The comparison scored finite clouds against the **exact endpoints of CRABS' own finite-difference recurrence**. Continuous affine endpoints were reported separately, so finite-grid error was not mislabelled as random-search error.

## Proposals

1. **Cap-aware uniform:** independently draw ε=μ/λ from `Uniform(0,0.5)` at each knot and solve CRABS' discrete congruence recurrence. One hundred paths were instantiated through the CRABS application programming interface for validation; the full 10,000-path computation used the vectorised recurrence.
2. **Native HSMRF with cap rejection:** run CRABS' native horseshoe Markov random field joint sampler and reject histories violating `μ/λ≤0.5`.

## Primary result

| Proposal | Median accepted / attempted | Median acceptance | τ=70 lower deficit | τ=70 upper deficit | Material misses | Median runtime |
|---|---:|---:|---:|---:|---:|---:|
| Cap-aware uniform | 10,000 / 10,000 | 100.00% | 6.9% | 20.0% | 10/10 | 0.006 s |
| Native HSMRF + rejection | 4,384.5 / 500,000 | 0.8769% | 0.5% | 49.5% | 10/10 | 153.19 s |

Every native replicate hit the 500,000-proposal ceiling before reaching 10,000 accepted histories. Accepted counts ranged from 4,299 to 4,499. All 4,956,112 rejected native proposals violated the matched turnover cap; there were no non-finite, negative-rate or sampler-error rejections.

The timing column is descriptive rather than a direct speed ratio: the cap-aware path generator is a vectorised recurrence, whereas the native column times the CRABS sampler itself.

## Exact endpoint conventions at τ=70 Ma

All rates are lineages/Ma.

| Convention | Lower λ | Upper λ | Width |
|---|---:|---:|---:|
| Continuous affine | 0.0778740782 | 0.1552123309 | 0.0773382527 |
| CRABS discrete, 5 Ma grid | 0.0892484780 | 0.1772607511 | 0.0880122731 |

Decision-level witnesses exist for both proposals. For the cap-aware cloud, `λ=0.1100377229` at τ=45 Ma lies within both exact conventions, yet all ten N=10,000 clouds missed it on the upper side. For the native cloud, `λ=0.1849631015` at τ=10 Ma lies within both exact conventions, yet every censored cloud missed it on the upper side.

## Validation and missingness

- Maximum accepted-history CRABS recurrence residual: `3.1919×10⁻16`, versus tolerance `1×10⁻10`.
- No accepted history exceeded the turnover cap; the closest remained `2.7008×10⁻8` below it.
- Exact lower and upper discrete endpoint residuals were below `1.3×10⁻16`.
- Constant ε=0 and ε=0.5 endpoint paths had zero CRABS-object representation error.
- Rejection identities balanced for every seed.
- Saved τ=70 draws reproduced the aggregate cloud boundaries exactly.
- Native N=10,000 targets are censored and explicitly marked incomplete; no seed was replaced.
- The native implementation used each listed base seed plus 1,000,000 to separate its random stream. The preregistration fixed the base seeds but did not state this deterministic offset; the independent audit records the disclosure.

The independent post-run audit returned `audit_status=pass` for all 15 checks.

## Post-preregistration grid sensitivity

CRABS' finite-difference endpoints converge towards the continuous formulas under refinement:

| Step (Ma) | Knots | Max lower error | Max upper error |
|---:|---:|---:|---:|
| 5.00 | 15 | 0.050730 | 0.098532 |
| 2.50 | 29 | 0.038527 | 0.075711 |
| 1.00 | 71 | 0.020381 | 0.040196 |
| 0.50 | 141 | 0.011031 | 0.021776 |
| 0.25 | 281 | 0.005716 | 0.011290 |
| 0.10 | 701 | 0.002333 | 0.004609 |
| 0.05 | 1,401 | 0.001174 | 0.002320 |

The finite-cloud comparison was not rerun at 1,401 knots. Refinement isolates the numerical discretisation issue; the candidate's endpoint-proximity analysis predicts harder undirected search as path dimension grows.

## Reproducibility identity

- Primary workflow run: [`32055272262`](https://github.com/ipitchford/affine-diversification-fibres/actions/runs/32055272262)
- Primary workflow head: `081b96cc6605f4b68950748cdd764fe00ff51630`
- Primary artifact SHA-256: `5bb9301835fa1880e0bf3351887ab07ec49a2293799a8fdcb847257772466dd7`
- Grid-sensitivity run: [`32056209338`](https://github.com/ipitchford/affine-diversification-fibres/actions/runs/32056209338)
- Grid artifact SHA-256: `f238be1e3727997afd4e88d09e5e2aa80089e9fe6a229b32454cb87ee772fe71`
- Runtime: R 4.6.1 on Ubuntu 24.04.4; CRABS 1.2.0.9001.
- Adoption adapter: [`adoption/affine_bounds_adapter.R`](../../adoption/affine_bounds_adapter.R)

GitHub Actions retains the primary artifact until 16 September 2026. The complete adoption bundle supplied with this result includes the raw artifact, all saved draws, independent audit, grid sensitivity, report, adapter and SHA-256 manifest.

## Bounded conclusion

**Observed:** both finite-cloud proposals materially missed a sharp CRABS-discrete endpoint in all ten seeds. The native route also failed the preregistered practicality threshold.

**Prespecified inference:** another group should use the affine routine for conditional endpoint certification under the matched cap-only conventions, and CRABS for exploratory trajectory generation.

**Open:** performance under other signals, caps, grids, constraints, priors and boundary-targeted proposals. Independent specialist review of the affine theorem package remains necessary before treating its certificates as externally validated mathematics.
