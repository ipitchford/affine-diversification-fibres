# Route A replay receipt

Date: 21 August 2026  
Scope: producer-side Stage 4.5 replay; not independent reproduction

Passed:

- `verification/verify_route_a_candidate.py`;
- 21 tests under normal and optimized Python;
- 720 implementation-diverse envelope endpoints across 180 feasible cases;
- 160,000-replicate finite-event simulation checks;
- five of five semantic negative controls;
- fixed-stem synthetic regeneration and 20,000-replicate coverage sanity check;
- H2/H4 summary regeneration from the unchanged sealed ledger;
- 1,900-entry Stage 2 manifest validation;
- LaTeX/biber PDF rebuild, metadata check and page-by-page visual inspection.

Frozen result identity at this checkpoint:

- H2: 240/240 returned-cloud endpoint deficits plus 60 structural censors;
- H4: 532/3,840 clustered status changes, failed against the 20% gate;
- fixed-stem joint component coverage sanity check: 0.96755 versus nominal lower bound 0.95;
- manuscript: 23 pages, SHA-256 `8fd18c6c0fdcc11af874a1d37da5cddb02d74822f7345b226685ca8436dd77a5`.

Public Linux CI, immutable release identity and public byte readback are recorded separately after they occur. They must not be inferred from this receipt.
