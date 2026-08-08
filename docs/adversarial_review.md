# Internal adversarial review of release 0.2.0

## Verdict

The revision removes the principal internal reasons to reject the theorem core. It should remain a candidate because external priority, conditioning and empirical gates are unresolved.

## Attempts to break the mathematics

1. **Affine chart:** forward and inverse substitution recover `lambda_p=lambda*u`; positivity and Radon-Nikodym identities hold.
2. **Event law:** the probability-generating function retains the zero-inflated geometric form after each affine event update. The event changes `u`, not `F`.
3. **Tree density:** the `(n-1)!` ranked-tree factor is necessary; removing it fails normalization and is caught by mutation control M2.
4. **Supercritical cap:** at `c>1`, the lower survival-scale expression reaches zero at `xcrit`; treating the upper rate endpoint as finite is rejected by control M3.
5. **Barrier proof:** necessity follows directly from a lower constraint `L_i >= x_i`; it does not follow merely because every feasible function lies above the least envelope. The manuscript uses the corrected argument.
6. **Finite envelope:** 720 independent linear programmes agree with the closed form to machine precision.
7. **Sampling theorem:** the lower-tail simplex volume and best-of-N order statistic agree with direct simulation.

## Claims deliberately not secured

- Crown or random-origin finite-event likelihood equivalence.
- Posterior equality among likelihood-equivalent histories.
- Confidence coverage for the fixed-signal bands.
- A biological identification of mammalian speciation/extinction from the genus summaries.
- A performance claim against the actual CRABS implementation.
- Exhaustive novelty.

## Residual technical concerns

- The standard oriented-ranked-tree factorisation should receive an external process-theory reading, even though normalization and simulation agree.
- Singular-continuous loss measures are a mathematical completion without an established biological interpretation.
- The cap class remains homogeneous and time-only; lineage/state dependence can alter identifiability.
- Strong external lower bounds can be sensitive to small perturbations in `F`, age and observation mapping; uncertainty propagation is essential before applied use.
