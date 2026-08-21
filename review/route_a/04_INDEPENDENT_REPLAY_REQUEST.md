# Independent replay request — OUTSTANDING

This file specifies, but does not claim, unaffiliated reproduction.

## Minimum clean replay

On a fresh checkout at the Route A candidate commit:

1. create a clean Python 3.13 environment from `requirements-lock.txt`;
2. run the 21 unit tests under normal and optimized Python;
3. regenerate the fixed-stem synthetic tree, Figure 9 data/PNG and coverage summary;
4. validate the unchanged CRABS Stage 2 manifest and regenerate the H2/H4 revision summaries without modifying result files;
5. run `verification/verify_route_a_candidate.py`;
6. build `manuscript.pdf` from `manuscript.tex` with `latexmk` and `biber`;
7. compare outputs against `ROUTE_A_CANDIDATE_MANIFEST.sha256` where deterministic bytes are promised, and explain platform-dependent figure/PDF differences where byte identity is not promised.

## Resource disclosure

- Sealed CRABS corpus: 1,100 registered result JSON files, 800 sample sidecars and approximately 811 MiB under `execution/results` (about 814 MiB for the full protocol directory on the authoring host).
- The complete stochastic execution spanned approximately 12.5 hours from the amendment freeze to the sealed commit chronology; this is not an instrumented runtime benchmark.
- Quick successor verification does not rerun CRABS; it checks the sealed manifest and derived invariants.
- Authoring host: macOS; qualified Route A Python: `/Users/admin/.venvs/analysis-py313/bin/python`. Linux remains untested.

## Required receipt

Record reviewer/reproducer identity, affiliation or independence basis, platform, CPU/RAM, environment hashes, commands, candidate commit and manifest hash, exact pass/fail results, deviations and conflicts. A replay performed by the preparing agent remains internal repeatability, not independent reproduction.
