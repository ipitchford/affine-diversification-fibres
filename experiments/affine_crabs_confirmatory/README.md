# Affine–CRABS confirmatory protocol

This directory contains a prospective protocol for testing affine endpoint
certification as a complement to CRABS. It is deliberately separate from the
released Mammalia pilot.

## Current state

`PREREGISTRATION.json` is a locally frozen protocol awaiting explicit
authorization to execute confirmatory cells. Generating manifests, validating
schemas, and running analytic or mutation controls do not generate
confirmatory outcomes.

The protocol has two layers:

1. broad deterministic validation of exact formulas, constraints, grids, caps,
   and sampling fractions; and
2. a smaller stochastic matrix that preserves native CRABS exploration and
   cap-matched comparisons as distinct tasks.

## Pre-execution commands

```bash
python experiments/affine_crabs_confirmatory/generate_frozen_assets.py
python verification/run_protocol_controls.py
python -O verification/run_protocol_controls.py
python -m unittest verification.test_protocol_harness
```

The asset generator refuses to overwrite a frozen manifest with different
bytes. The control runner does not execute CRABS or inspect confirmatory
results.

## Semantic boundary

CRABS `p.delta` and affine pulled speciation `lambda_p` are not interchangeable.
Confirmatory matched comparisons are permitted only for the declared special
bridge with `rho = 1`, `lambda_ref = lambda_p`, and `mu_ref = 0`. Other `rho`
levels are affine-only deterministic validation until a separate derivation is
registered and independently tested.

## Public-claim boundary

These files provide a protocol and harness, not evidence that the hypotheses
are true. The package remains an unrefereed candidate. External theorem review,
confirmatory execution, independent user evaluation, and Evidence Press
publication gates are outstanding.
