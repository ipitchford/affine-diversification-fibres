# Review packets

## Current packet: Route A revision

The authoritative re-review packet is `review/route_a/` and describes candidate `0.3.0rc2` / `0.3.0-candidate-r2`.

- `../manuscript.pdf` — 23-page rendered revision.
- `../manuscript.tex` — mathematical source of truth.
- `../manuscript.md` — accessible text companion; TeX/PDF controls numbering.
- `route_a/01_RESPONSE_TO_REVIEWERS.md` — R1–R9 and S1–S6 response.
- `route_a/02_CHANGE_LOG.md` — stable revised locators.
- `route_a/06_STAGE4_CHECKPOINT.md` — mandatory Stage 3′ stopping boundary.
- `../outputs/route_a_candidate_verification.json` — passing internal integrated verification.

Run from the repository root with the qualified environment:

```sh
PYTHONPATH=. /Users/admin/.venvs/analysis-py313/bin/python verification/verify_route_a_candidate.py
shasum -a 256 -c review/route_a/ROUTE_A_CANDIDATE_MANIFEST.sha256
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
```

## Preserved first-round packet

The files directly under `review/` and `review/stage3/` record the first-round 0.3.0-candidate packet and its Stage 3 review. `FINAL_REVIEW_MANIFEST.sha256` binds the first-round bytes from commit `a16c8af6f192fb62c656dc641ad69c8abda1f305`; it is not expected to validate revised root files. It is intentionally not rewritten.

## Decision boundary

H4 remains failed at 532/3,840 clustered status changes. External process review, unaffiliated full replay, Linux execution and independent rights review remain outstanding. Do not mint a DOI, deploy, publish or begin release outreach from this packet. The next step is mandatory Stage 3′ re-review.
