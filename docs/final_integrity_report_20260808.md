# Final integrity report — candidate 0.2.1

**Audit date:** 8 August 2026  
**Decision:** pass for public dissemination as an unrefereed candidate  
**Claim change from 0.2.0:** none

This report closes the release-preparation integrity gate. It does not close the external-specialist, novelty, statistical, empirical or peer-review gates in `STATUS.json`.

## Citation integrity

All 18 bibliography records were checked through publisher, DOI, arXiv or library-catalogue routes. Every citation context in `manuscript.tex` was inspected for correspondence with the cited source. `SOURCES.json` now includes the MacPherson et al. and Anderson--Nash antecedents and the publisher's correction to Truman et al.; that correction restores omitted supplementary data and does not report a substantive correction to the cited identifiability result.

Result: source identity and contextual support passed. This is not an independent validation of the candidate's deductions or an exhaustive priority search.

## Upstream-data integrity

The declared `n8upham/MamDiv-fossil-vs-timetree` source repository, its GPL-3.0 declaration and the named upstream objects were inspected. The fetched R-data SHA-256 matched the packaged record exactly. All 23 pulled-signal rows were compared with the upstream R object: ages matched exactly and the maximum numerical differences were at decimal-serialization scale. All 14 fossil-excerpt rows and seven mapped values per row matched the upstream CSV exactly.

Result: faithful extraction passed. The upstream fit was not rerun, and the biological observation bridge remains unassessed.

## Claim and replay integrity

- `C1`--`C7` retain the same statements and limitations as 0.2.0.
- Seventeen deterministic unit tests pass.
- Independent checks cover 720 linear-program endpoints across 180 random cases and a 160,000-replicate finite-event branching simulation.
- Five deliberately broken or infeasible controls are detected.
- Full regeneration and semantic verification pass under normal Python and `python -O` in a disposable copy.
- The same workflow passes in a clean container pinned to the Python 3.13.5 base-image digest recorded in `environment.json`.

The original 0.2.0 harness installed the project into `/work` and then treated its own build products as unauthorized files; it also required generated floating-point serializations and PNGs to be byte-identical across platforms. Candidate 0.2.1 instead hash-checks the frozen payload first and regenerates outputs only in a scratch copy, where scientific checks are semantic. The replay receipt binds the frozen manifest; the containing Git tag, release archive and archive SHA-256 bind the receipt itself.

## AI-research failure-mode audit

1. **Implementation bug:** mitigated by the independent envelope implementation, LP comparisons, stochastic simulation, boundary tests and negative controls. External code review remains absent.
2. **Hallucinated citation or result:** no unsupported or nonexistent citation found; all source identities and contexts were checked.
3. **Shortcut substituted for the required result:** no evidence found. Outputs were traced to the stated scripts and restrictions; the actual CRABS comparison remains explicitly unperformed.
4. **Bug narrated as insight:** no such narrative step is used. The sampling theorem is analytically stated and checked against its deliberately transparent sampler.
5. **Methodology fabricated after seeing outputs:** no evidence found in the supplied review/revision chain; the release preserves the review, response, audit and generated outputs. This is a provenance check, not a complete transcript audit.
6. **Manuscript/code mismatch:** entry points, configurations, sample sizes, constraints and output paths were cross-checked; no material mismatch found.
7. **Frame lock:** the supplied major review materially narrowed the empirical and conditioning claims. Remaining alternative frames are retained as open gates rather than declared resolved.

## Remaining trust boundary

Theorem 4's fixed-stem conditioning conventions have not been audited by an external stochastic-process specialist. The novelty search is targeted, not systematic. There is no proof-assistant formalization, independent external replay, simultaneous pulled-signal uncertainty procedure, validated fossil observation model or matched CRABS run. Accordingly the release state remains `candidate`, and a successful verifier must not be reported as peer review, formal verification, empirical validation or theorem certification.
