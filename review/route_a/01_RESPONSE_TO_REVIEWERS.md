# Response to Stage 3 reviewers

We thank the editorial and specialist panels. We selected Route A and reorganized the paper around an honest finite-sample fixed-stem signal-to-decision workflow. The negative H4 result is unchanged. Historical 0.2.1 receipts are preserved.

## Required revisions

### R1 — single route and claim hierarchy — RESOLVED

The title, abstract, opening question, contribution paragraph, methods comparison, limitations and conclusion now state one principal contribution: simultaneous uncertainty for `F` propagated to conditional affine decisions. The CRABS benchmark, affine theorems and mammal material are supporting, bounded or illustrative. Essential-complement wording is explicitly prohibited.

Locators: manuscript title and abstract; `Decision problem and contribution`; `Position relative to existing methods`; `Conclusion`; `STATUS.json` exclusions.

### R2 — Theorem 1 regularity — RESOLVED

Theorem 1 now maps histories with continuous rates and a `C^1` survival/cumulative-loss path, rather than claiming continuously differentiable rate functions. The inverse formulas land in the stated spaces. The code and claim ledger use the same versioned object.

Locators: `Smooth affine fibre`, Theorem 1; `CLAIM_EVIDENCE.json` C2.

### R3 — Theorem 4 probability object and external review — UNRESOLVABLE

The mathematical wording is repaired: the theorem defines stem/survival/count conditioning and the disjoint-union sample space with counting times Lebesgue measure; it is expressly topology-marginal and makes no complete labelled/oriented/ranked topology claim. Internal normalization and simulation checks remain. Written unaffiliated process-theory review cannot be self-issued and is still a publication blocker.

Locators: `Fixed-stem tip-count and ordered-node-age law`, Theorem 4 and following scope paragraph; `03_EXTERNAL_PROCESS_REVIEW_REQUEST.md`; `STATUS.json` G1.

### R4 — event convention, model classes and cap biology — RESOLVED

The revision states which event side is younger/older, separates absolutely continuous, finite-atomic and singular-continuous measure subclasses, and maps each to process results. A dedicated applicability table excludes lineage/state/trait/clade/diversity-dependent processes. A cap-interpretation table explains that `c<=1` excludes continuously negative net diversification and that event survival is not a pointwise turnover value.

Locators: `Measure completion and finite survival events`; model-class table; `Turnover caps and the phase transition at c=1`; cap-interpretation table; `Limitations and research programme`.

### R5 — H2 and amendment narrative — RESOLVED

The scientific endpoint result is now 240/240 returned clouds above threshold. The 60 abrupt cells are reported separately as structural censors. The frozen 300/300 composite is called workflow failure, never 300 observed deficits. The chronology records that Amendment 004 followed the nontermination incident but preceded every primary rejection/H4 result.

Locators: abstract; `Nontermination incident and complete accounting`; chronology table; `Confirmatory results`; `outputs/crabs_h2_h4_revision_summary.json`.

### R6 — H4 transitions, dependence and consistency wording — RESOLVED

The paper adds the full 3-by-3 transition table, reports 502 withdrawals to unresolved and 30 below-to-above reversals, states the 16-query within-cell dependence, gives cell and stratum summaries, and labels Wilson displays descriptive. “Zero false certificates” is replaced by an analytic-endpoint implementation consistency invariant.

Locators: `Confirmatory results`; H4 transition table and Figure 8 caption; `figure_data/crabs_h4_status_transitions.csv`; `figure_data/crabs_h4_transition_strata.csv`.

### R7 — Route A statistical/biological bridge — RESOLVED

The revision constructs exact tail-inverted count bounds and a conditional DKW--Massart node-age band, maps them monotonically into a simultaneous `F` band, unions conditional fibres only over valid pulled scales, and gives a three-valued target decision. The frozen synthetic example shows one robust incompatibility and one plug-in-compatible result that becomes unresolved. It is not presented as empirical validation.

Locators: `Finite-sample fixed-stem uncertainty and robust decisions`, Theorem 14, Figure 9; `experiments/run_fixed_stem_uncertainty.py`; `outputs/fixed_stem_uncertainty.json`.

### R8 — recognition and literature — RESOLVED

A structured theorem-by-theorem recognition search now covers reconstructed processes, coalescent point processes, partial identification, DKW bands, optimal recovery/Lipschitz interpolation and product integration. Each component is classified as antecedent, reformulation, extension or provisional new synthesis. Residual specialist, non-English, thesis and non-indexed uncertainty is explicit; no exhaustive-priority claim is made.

Locators: manuscript antecedent table in `Position relative to existing methods`; `docs/recognition_search_route_a_20260821.md`; `docs/prior_art_ledger.csv`; `SOURCES_ROUTE_A.json`.

### R9 — replayable, rights-cleared, version-coherent successor — DELIBERATE_LIMITATION

The successor README, CFF, package version, status, assurance, claim ledger, source supplement, alt text, replay commands and additive candidate verifier now tell one `0.3.0rc2` story. The previous DOI is labelled historical; old manifests and receipts were not rewritten. Internal qualified-macOS replay is supplied. Unaffiliated replay, Linux execution and independent rights sign-off remain open and block publication preparation.

Locators: `README.md`; `CITATION.cff`; `STATUS.json`; `ASSURANCE.json`; `LICENSE_MAP.json`; `04_INDEPENDENT_REPLAY_REQUEST.md`; `05_RIGHTS_REVIEW_CHECKLIST.md`.

## Suggested revisions

### S1 — visual worked decision — RESOLVED

Figure 9 traces a frozen 22-tip synthetic tree through the `F` band to a certified-incompatible stem decision and an unresolved interior decision.

### S2 — assurance terminology — RESOLVED

The manuscript and `ASSURANCE.json` distinguish integrity, internal replay, numerical checks, proof and independent reproduction. Hash agreement is not described as theorem validation.

### S3 — tested/not-tested CRABS matrix — RESOLVED

The manuscript's comparator scope table specifies the one `rho=1` bridge, five signals, grids, caps, query families, and excluded claims. H4 is reported as failed.

### S4 — simplify main narrative — RESOLVED

Route A is the organizing spine. The mammal section is explicitly a plug-in sensitivity illustration; dense assurance and reproduction detail is placed near the end.

### S5 — resource/runtime reporting — RESOLVED

The replay request records the 1,100 registered cells, 800 sample sidecars, approximately 811 MiB of result files, qualified host/environment and the approximately 12.5-hour observed commit-to-seal span. That span is operational chronology, not a separately instrumented wall-clock benchmark.

### S6 — cache hygiene and alt text — RESOLVED

Generated caches and LaTeX auxiliaries are excluded from the sealed successor packet. Figure 9 alt text is in `figure_data/ALT_TEXT.json`; every plotted figure retains source data.

## Remaining blockers submitted to Stage 3′

1. Unaffiliated process-theory review of Theorem 4.
2. Unaffiliated full replay and Linux/cross-platform execution.
3. Independent component-rights review.
4. Editorial evaluation of whether the wide but honest fixed-stem band is sufficient for the intended venue.
