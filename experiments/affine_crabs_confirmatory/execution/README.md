# Confirmatory execution harness

This directory implements the frozen protocol plus
`AMENDMENT_001_PRE_EXECUTION.json`. It is deliberately separate from the
released Mammalia pilot.

The execution order is fail-closed:

1. run `qualify_environment_and_primates.R` against the exact CRABS source
   commit and the isolated R library;
2. validate the generated qualification receipt and hashes;
3. run deterministic registered cells;
4. run resumable stochastic registered cells; and
5. aggregate only complete or explicitly censored cell records.

Files under `qualification/` are derived from a GPL-3 upstream component.
Their presence in an internal execution branch is not authorization to publish
or redistribute them.
