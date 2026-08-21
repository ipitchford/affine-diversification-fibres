# Finite-sample signal uncertainty and affine diversification fibres

**Successor candidate:** `0.3.0rc2` / `0.3.0-candidate-r2`, 21 August 2026

**Workflow state:** Stage 3′ completed; approved only for an explicitly unrefereed Evidence Press candidate under `PASS_WITH_NOTES`

**Previous immutable candidate:** [0.2.1, DOI 10.5281/zenodo.21851319](https://doi.org/10.5281/zenodo.21851319)

This Route A successor gives a finite-sample signal-to-decision workflow for one exact fixed-stem reconstructed tree under a homogeneous time-varying birth-death model. It constructs an honest simultaneous band for the pulled scale `F`, propagates that band through an affine conditional identified set, and reports three-valued turnover-cap decisions: certified incompatible, compatible throughout the band, or unresolved.

The separate frozen CRABS comparison is supporting evidence, not the principal claim. All 240 returned primary rejection clouds missed at least one sharp endpoint beyond the frozen tolerance, with 60 additional structural censors. Exact certification changed 532/3,840 clustered decision-query statuses (13.854%), so the prespecified H4 utility gate failed. The candidate must not be described as a “must-have” or essential complement to CRABS.

## Assurance boundary

- Internal mathematical, numerical, ledger and qualified-host checks have passed within their recorded scope.
- The simultaneous band covers exact node-age sampling variation under the stated fixed-stem, stem-survival model only.
- It does not cover topology or dating error, model misspecification, lineage heterogeneity, fossil observation, or uncertainty in external biological constraints.
- External process-theory review, unaffiliated full replay, cross-platform replay and independent rights review remain outstanding. They are visible assurance gaps, not implied passes.
- No DOI has been assigned to this successor, and the 0.2.1 DOI must not be used for it.

## Qualified local replay

Use the recorded analysis environment; the bare host Python may not contain SciPy.

```bash
PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=/tmp/affine-mpl-cache \
  /Users/admin/.venvs/analysis-py313/bin/python -m unittest \
  affine_diversification.test_affine_fibre -v

PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=/tmp/affine-mpl-cache \
  /Users/admin/.venvs/analysis-py313/bin/python experiments/run_fixed_stem_uncertainty.py

PYTHONPATH=. /Users/admin/.venvs/analysis-py313/bin/python \
  experiments/affine_crabs_confirmatory/summarize_h2_h4.py

PYTHONPATH=. /Users/admin/.venvs/analysis-py313/bin/python \
  verification/verify_route_a_candidate.py
```

The full 1,100-cell CRABS computation is not rerun by the quick verifier; it validates the unchanged sealed ledger and the derived H2/H4 summaries. Resource expectations and the independent-replay request are recorded under `review/route_a/`.

## Principal files

- `manuscript.pdf` — rendered review paper; `manuscript.tex` controls equations and numbering.
- `manuscript.md` — accessible text companion regenerated from the TeX source.
- `review/route_a/01_RESPONSE_TO_REVIEWERS.md` — point-by-point R1–R9 and S1–S6 response.
- `review/route_a/06_STAGE4_CHECKPOINT.md` — stop/go boundary for Stage 3′ re-review.
- `docs/recognition_search_route_a_20260821.md` — structured recognition search and residual limitations.
- `SOURCES.json` and `review/route_a/SOURCES_ROUTE_A.json` — inherited and Route A source registries.
- `MANIFEST.sha256` and `REPLAY_RECEIPT.json` — historical 0.2.1 records, intentionally not rewritten.

## Publication state

This repository is an unrefereed successor candidate. Stage 3′ retained Major Revision for journal-style acceptance but authorized Evidence Press candidate publication with notes. Public release remains conditional on the Stage 4.5 integrity report, immutable GitHub/Zenodo identity and Evidence Press readback. No public surface may call the work peer reviewed, independently reproduced, formally verified, biologically validated or a must-have CRABS complement.
