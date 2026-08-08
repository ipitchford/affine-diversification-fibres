# Independent reviewer checklist

A reviewer should treat every item below as a gate, not a suggestion.

## A. Mathematical representation

- [ ] Re-derive \(u'=\lambda_p(1-u)-\mu u\) under the paper's age convention.
- [ ] Verify \(A=F(1-u)\), \(A'=\mu uF\), and every inverse formula.
- [ ] Check the atom at zero against the chosen present-day sampling convention.
- [ ] Verify that the admissible object is a convex cumulative-order interval, not a cone.
- [ ] Check lattice closure under cumulative minimum and maximum.
- [ ] Decide whether the topology and closure used for endpoint attainment are stated adequately.

## B. Atomic histories and process law

- [ ] Derive the backward equation at a deterministic mass-extinction event.
- [ ] Check the sign and left/right convention in \(q(a)=s q(a^-)\).
- [ ] Prove that a finitely atomic history with fixed pulled signal induces the same reconstructed-tree law under each claimed conditioning convention.
- [ ] Check stem-, crown-, survival- and fixed-tip conditioning separately.
- [ ] Identify any event-specific likelihood factor that is not absorbed by the pulled signal.
- [ ] Decide whether singular-continuous loss should be excluded from the formal model, rather than merely from empirical classes.

## C. Sharp envelopes

- [ ] Prove necessity and sufficiency of every pairwise inequality.
- [ ] Verify that pointwise maxima/minima preserve monotonicity and the slope bound.
- [ ] Confirm simultaneous sharpness, not only pointwise sharpness.
- [ ] Check the formula for the minimum cap and the case \(c_\star>1\).
- [ ] Check strict barrier feasibility and whether a supremum can fail to be attained outside the capped class.
- [ ] Reproduce the independent finite-grid linear-programming comparison.

## D. Biological mapping

- [ ] Confirm the deterministic diversity identity and units.
- [ ] Separate sampled lineages, total species diversity and fossil-genus richness.
- [ ] Reject any hard fossil bound that lacks an observation model or explicit sensitivity label.
- [ ] Check whether mass-extinction ages or survival fractions are externally known or estimated.
- [ ] Test sensitivity to time-varying rather than uniform turnover caps.
- [ ] State which important model extensions lie outside the homogeneous time-dependent fibre.

## E. Statistical uncertainty

- [ ] Construct a simultaneous confidence set for the pulled signal.
- [ ] Verify coverage after union over the nuisance-function confidence set.
- [ ] Incorporate uncertainty in \(\rho\), \(M_0\), fossil constraints and event timing.
- [ ] Distinguish confidence coverage from sensitivity ranges over assumptions.
- [ ] Check regularisation bias and practical identifiability of the pulled-rate estimator.

## F. Prior art

- [ ] Search measure, compensator, hazard, cumulative-incidence and renewal aliases.
- [ ] Search coalescent point-process and splitting-tree literature beyond the cited papers.
- [ ] Search books, theses and non-English sources.
- [ ] Ask domain specialists whether the fibre representation is known under another notation.
- [ ] Confirm that all generic mathematics is credited and no enabling lemma carries the originality claim.

## G. Software and data

- [ ] Run all tests in a clean environment.
- [ ] Verify input hashes and release manifest.
- [ ] Confirm the code never differentiates noisy splines to enforce turnover.
- [ ] Check primal and dual residuals for any future numerical optimisation result.
- [ ] Reproduce every table and figure from the included inputs.
- [ ] Audit upstream licences and transformations.

## Decision codes

- **PASS:** no load-bearing defect found.
- **PASS WITH REVISION:** theorem survives; presentation, scope or empirical mapping requires correction.
- **STOP:** a theorem is false, the process extension fails, or prior art removes the central residual contribution.
