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
- release manuscript: 23 pages, SHA-256 `4e263ac0c3195a41b10733d6c6e3c6f5c7d328cfe534e0d515d4e7991206a5bf`.

Public GitHub Actions run 32457758437 passed all three Linux jobs on pre-DOI commit `3e50413d9122e90de4b66c25cfdd0602bbdfb484`. The final DOI-bearing commit is rerun before tagging. These producer-controlled public checks are not unaffiliated reproduction.
