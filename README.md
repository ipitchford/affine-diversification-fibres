# Conditional sharp partial identification of diversification histories

**Candidate release:** 0.2.1, 8 August 2026  
**DOI:** [10.5281/zenodo.21851319](https://doi.org/10.5281/zenodo.21851319)  
**Publication state:** ready for public candidate dissemination; unrefereed and not externally verified  
**Primary object:** theorem-led methods paper with executable assurance artefacts

## Safe claim

For a fixed pulled speciation signal, a stated class of homogeneous time-dependent birth-death histories admits a cumulative-loss measure coordinate. In the absolutely continuous turnover-capped subclass, finite interval constraints have explicit sharp pointwise envelopes, finite infeasibility certificates, a positive-survival test and a minimum compatible turnover cap. Finitely many independent deterministic survival events preserve the complete reconstructed-tree law under the paper's fixed-stem conditioning conventions.

The release does **not** claim statistical confidence coverage, a validated fossil observation model, crown-conditioned event equivalence, an exhaustive novelty search or external specialist verification.

## What changed in 0.2.1

The mathematical claims are unchanged from 0.2.0. This patch release hardens citation coverage, upstream-data provenance, licensing and replay. It also fixes the release harness so regeneration occurs in a disposable copy rather than changing the frozen evidence package.

## Major changes in 0.2.0

- Completed the finite-event descendant-count and fixed-stem likelihood derivation, including normalization under stem-survival and fixed-tip-count conditioning.
- Extended turnover caps from `0 <= c <= 1` to every finite `c >= 0`; proved the phase transition at `c=1` and the supercritical divergence scale.
- Added the exact positive-survival barrier for finite constraints and corrected the identified-set language.
- Added a factorial endpoint-sampling theorem and a matched simulation, quantifying why finite random trajectory clouds do not certify endpoints.
- Reclassified the mammal analysis as single-tree plug-in deterministic sensitivity; no palaeobiological inference is claimed.
- Added scoped assurance, provenance, sources, licences, negative controls, an independent reference implementation and a release verifier.

See `docs/response_to_major_review.md` and `docs/revision_assessment.md`.

## Reproduce

```bash
make verify
make verify-package
docker build -f Containerfile -t affine-diversification-fibres:0.2.1 .
docker run --rm affine-diversification-fibres:0.2.1
```

`make verify` regenerates and checks results in a disposable scratch copy under normal and optimized Python. `make verify-package` checks the immutable package hashes and shipped evidence. A successful replay establishes internal computational consistency only; it is not external theorem verification or peer review.

## Release map

- `manuscript.pdf`, `.tex`, `.md`: paper and sources.
- `affine_diversification/`: reference Python implementation and 17 tests.
- `experiments/`: matched finite-sampling benchmark and turnover-cap phase diagram.
- `verification/`: independent envelope implementation, simulation, negative controls and release verifier.
- `REPLAY_RECEIPT.json`: machine-readable record of normal and optimized scratch replay.
- `outputs/`: machine-readable replay and validation reports.
- `figure_data/`: the data and alt text behind all seven figures.
- `CLAIM_EVIDENCE.json`, `ASSURANCE.json`, `STATUS.json`: claim-level assurance boundary.
- `PROVENANCE.json`, `SOURCES.json`, `LICENSE_MAP.json`: provenance, source and reuse metadata.
- `docs/final_integrity_report_20260808.md`: publication-gate citation, data, replay and failure-mode audit.

## Open gates

1. External specialist audit of Theorem 4 and its conditioning conventions.
2. Recognition search across adjacent mathematical and non-English literatures.
3. Simultaneous uncertainty set for the pulled signal and robust set propagation.
4. Fossil preservation, observation and taxonomic-scale model.
5. Actual matched CRABS comparison under identical restrictions.
6. Crown and random-origin conditioning extensions.
7. Independent environment recreation and replay by an unaffiliated party.

## Licensing

All original content in this release is dedicated to the public domain under CC0-1.0. Source-derived mammal data retain their upstream terms, and the user-supplied review remains `NOASSERTION`; see `LICENSE`, `LICENSE_MAP.json` and `DATA_PROVENANCE.md`.
