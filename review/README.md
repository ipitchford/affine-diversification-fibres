# Affine diversification fibres 0.3.0-candidate final-review packet

**State:** ready for final expert review; not authorized for publication.

## Authoritative review documents

- `../manuscript.pdf` — rendered 18-page review manuscript
- `../manuscript.tex` — authoritative editable source
- `../docs/final_review_cover_memo_20260821.md` — editorial handoff and reviewer questions
- `../docs/pre_review_integrity_20260821.md` — completed Stage 2.5 integrity audit
- `CLAIM_EVIDENCE_0.3.0-candidate.json` — 11-claim evidence and assurance ledger
- `FINAL_REVIEW_MANIFEST.sha256` — byte-level packet manifest

The root `manuscript.md` belongs to the historical 0.2.1 candidate and is excluded from this review packet. It must not be used as the source for the successor draft.

## New confirmatory evidence

- `../experiments/affine_crabs_confirmatory/execution/RESEARCH_CHECKPOINT.json`
- `../experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_EXECUTION_RECEIPT.json`
- `../experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_MANIFEST.sha256`
- `../experiments/affine_crabs_confirmatory/execution/H5_EXECUTION_RECEIPT.json`
- `../experiments/affine_crabs_confirmatory/execution/H5_EXECUTION_RECEIPT_002.json`
- `../figure_data/figure8_crabs_confirmatory_h4.csv`
- `../figures/figure8_crabs_confirmatory_h4.png`

## Local review checks

Run from the repository root:

```sh
python3 review/validate_review_packet.py
shasum -a 256 -c review/FINAL_REVIEW_MANIFEST.sha256
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
```

The sealed 1,100-cell evidence manifest is independently checked with:

```sh
shasum -a 256 -c --status \
  experiments/affine_crabs_confirmatory/execution/STOCHASTIC_STAGE2_MANIFEST.sha256
```

## Decision boundary

H4 failed: 532 of 3,840 evaluable query statuses changed (13.85%), below the frozen 20% gate, with zero false certificates. H1, H2, H3 and H5 passed within their stated scopes. The permitted headline is therefore “fast exact diagnostic complement,” not “essential” or “must-have complement.”

Do not mint a DOI, alter the historical 0.2.1 archive, deploy, publish or begin outreach from this packet. Those actions require an explicit post-review decision and a separate Evidence Press successor-release workflow.
