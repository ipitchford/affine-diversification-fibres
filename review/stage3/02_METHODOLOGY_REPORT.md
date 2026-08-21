# Peer Review Report — Reviewer 1 (Methodology)

## Manuscript information

- **Title:** *Conditional Sharp Partial Identification of Diversification Histories: Affine Measure Geometry, Event Congruence, Certified Extremes and a Confirmatory CRABS Comparison*
- **Manuscript ID:** AFFINE-0.3.0-CANDIDATE
- **Review date:** 21 August 2026
- **Review round:** 1

## Reviewer information

### Reviewer role

Peer Reviewer 1 — Methodology.

### Reviewer identity

Mathematical statistician specialising in partial identification, measure-valued dynamical systems, sharp bounds and optimisation, with experience auditing prospectively specified computational studies.

### Review focus

I assess whether the mathematical statements follow under their stated regularity and conditioning assumptions, whether “sharp” is used correctly, whether the finite benchmark answers its frozen questions, and whether the reported quantitative summaries respect their units of analysis. Literature priority and general journal fit are outside my remit.

## Overall assessment

### Recommendation

- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**
- [ ] Reject

### Confidence score

**4/5 — high confidence.** The identification and optimisation arguments are within my expertise. The precise reconstructed-tree topology convention requires a birth-death process specialist.

### Summary assessment

The paper contains a strong analytic core. The cumulative-loss transformation in Theorem 1, the all-cap pointwise bounds in Theorem 6, the directed-Lipschitz envelopes in Theorem 8 and the factorial endpoint law in Theorem 12 are concise and, within the stated algebraic models, largely convincing. Sharpness is usually handled correctly: attained extrema are separated from unattained suprema, the positive-survival barrier is explicit, and arbitrary curves inside pointwise bands are not declared feasible. The computational controls are unusually extensive.

Major revision is required because the regularity class in Theorem 1 is not stated consistently, the “complete” law in Theorem 4 lacks a fully specified topology/base-measure formula, and the benchmark presentation mixes an observed finite-cloud deficit with a structural censor under the H2 label. H4 is an exact census of frozen queries, but its Wilson interval treats strongly dependent statuses as if they were Bernoulli observations and should remain purely descriptive. Finally, the zero-false-certificate count is a deterministic self-consistency check rather than independent validation. None of these issues necessarily overturns the useful theorem core, but they must be corrected before “exact certification” is an archival claim.

## Strengths

### S1: Sharpness is treated with mathematical discipline

Theorem 6 distinguishes a finite attained upper endpoint from an infinite supremum and explicitly notes when zero survival is an unattained infimum (pp. 5–6). Corollary 9 separately enforces the strict barrier for `c > 1` (p. 7). These are the details most often lost when numerical envelopes are described as exact.

### S2: The finite-constraint result gives short certificates

Theorem 8 reduces feasibility to pairwise directed-Lipschitz inequalities and supplies explicit least and greatest feasible envelopes (pp. 6–8). Corollary 10 produces a minimum compatible cap, and the text correctly warns that an arbitrary path inside the pointwise shading need not satisfy cross-time constraints.

### S3: The sampling theorem is scoped to its actual proposal law

Theorem 12 derives the simplex-volume lower tail only for independent Uniform(0,c) interval turnover draws (pp. 8–9). The next paragraph expressly states that it is not a theorem about CRABS. The accompanying exact order-statistic calculation is an appropriate analytic demonstration of finite-cloud limitations.

### S4: Unfavorable computational outcomes are not discarded

All 1,100 planned stochastic cells are accounted for, the 100 structural censors remain visible, and the failed H4 gate is reported in the abstract, Table 1, limitations and conclusion. The initial H5 environment-selection failure is preserved rather than overwritten.

## Weaknesses

### W1: Theorem 1's regularity class is inconsistent

**Problem:** Theorem 1 claims a bijection involving “continuously differentiable histories” while assuming only continuous positive `lambda_p` and `A` in `C^1` (pp. 2–3). The inverse gives continuous `lambda=lambda_p F/(F-A)` and continuous `mu=A'/(F-A)`, but not necessarily continuously differentiable rate functions unless stronger assumptions are imposed on `lambda_p` and `A`.

**Why it matters:** A bijection is only exact after its domain and codomain have matching regularity. This also affects what is meant by the “smooth fibre.”

**Suggestion:** Define histories as continuous rate pairs with a `C^1` survival path, or strengthen the assumptions enough to obtain the claimed differentiability. State the function spaces once and use them consistently in the theorem, claim ledger and code documentation.

**Severity:** Major but locally repairable.

### W2: Theorem 4 does not yet specify the complete probability object

**Problem:** Equations (19)–(21) are densities for ordered branching times after the ranked topology has been marginalised (pp. 4–5). The subsequent statement says that the topology law is exchangeable and convention-dependent but does not give that law, its state space, base measure or multiplier. The claim ledger, meanwhile, refers to an oriented ranked tree.

**Why it matters:** A normalized topology-marginal density is not by itself a complete law on fully labelled, oriented or ranked reconstructed trees. Different conventions move factorial and orientation factors.

**Suggestion:** Either rename the theorem “topology-marginal fixed-stem branching-time congruence,” or define the precise tree space and supply the conditional topology mass explicitly. Include a derivation showing exactly where the `i` factors, `(n-1)!` and any label/orientation factors enter. Ask an external process specialist to verify this version.

**Severity:** Major and load-bearing.

### W3: Event-side notation and admissible measure classes need tightening

**Problem:** Section 3 defines right-continuous cumulative functions but then uses `u(a+)` and `u(a-)` while time runs backward from the analysis origin (p. 3). The general fibre includes arbitrary positive Radon measures, including singular-continuous components, whereas Theorems 3–4 return to absolutely continuous histories with finitely many events.

**Why it matters:** Readers must know which side of an event is older, which value is right-continuous, and which part of the measure completion has a stochastic-process interpretation.

**Suggestion:** Add a one-line temporal convention at each event and partition the model class into absolutely continuous, finite-atomic and singular-continuous components. State that the process results cover only the first two unless a construction is provided for the third.

**Severity:** Major for clarity; not evidence of a false formula.

### W4: H2 conflates missing output with observed endpoint deficit

**Problem:** H2 is labelled “endpoint incompleteness,” and its 300/300 count combines 240 returned clouds with 60 structurally censored abrupt-signal cells (pp. 9–11). Amendment 004 was created after a Stage-1 nontermination incident, even though it preceded the primary rejection-cell results.

**Why it matters:** A structural censor demonstrates that the frozen workflow cannot return under its rate ceiling; it does not observe how far a returned cloud lies from an endpoint. Calling both events endpoint incompleteness collapses two distinct outcomes.

**Suggestion:** Rename the composite “failure to certify endpoints under the frozen workflow.” Report `240/240` returned clouds above the deficit threshold and `60/60` structurally censored cells as separate primary components. Add a protocol timeline and explicitly describe Amendment 004 as outcome-informed but pre-primary-analysis. Show that the H2 decision is unchanged when censors are excluded; the recorded results appear to allow this.

**Severity:** Major.

### W5: H4 summaries need dependence-aware interpretation and transition directions

**Problem:** The 3,840 query statuses are nested within 240 stochastic cells, five signal sources become four evaluable sources, and sixteen thresholds share each finite cloud. A pooled Wilson interval over queries therefore has no ordinary independent-Bernoulli interpretation. The paper reports only the total number changed, not the transition matrix.

**Why it matters:** The exact 13.85% gate result is valid by protocol, but the interval can be misread as uncertainty about a general population rate. Without directions, readers cannot tell whether certification mostly converted apparently decisive finite-cloud statuses to `UNRESOLVED` or did something else.

**Suggestion:** Retain 532/3,840 as the frozen deterministic decision statistic. Add the full finite-status by certificate-status transition table, cell-level and stratum-level summaries, and either omit the pooled Wilson interval or label it visibly as a non-inferential visualization. If an inferential interval is desired, define the population and use cluster-aware resampling at the independent cell or signal-family level.

**Severity:** Major for interpretation; the H4 fail verdict itself is unaffected.

## Detailed comments

### Research questions and hypotheses

The primary identification question on p. 2 is answerable within a fixed `F` class. H1–H5 are explicit, but H1 is deterministic validation rather than a scientific hypothesis. Consider calling them gates rather than hypotheses throughout.

### Theoretical design

Theorem 6's proof is persuasive for pointwise bounds. Theorem 8's cone constructions appear to establish the generic monotone-Lipschitz result, and Corollary 9 correctly uses the least envelope as an existence witness. Corollary 11 should specify the topology or measurability conditions needed for any integral functional beyond the named examples.

### Benchmark design

The frozen thresholds and retention of H4 failure are strengths. The single `rho=1`, `lambda_ref=lambda_p`, `mu_ref=0` bridge is a bounded design choice, not a general comparator validation. The post-incident amendment did not change the observed 240/240 returned-cloud outcome, which should be made prominent because it removes concern that the H2 decision depends on the censor convention.

### Statistical reporting adequacy

**Rating: Adequate for a prespecified finite benchmark, needs improvement for generalization.** The paper reports exact counts, denominators, frozen thresholds and descriptive intervals. No significance test or power claim is made. However, query-level dependence precludes an inferential reading of the Wilson intervals, and no target population for generalization is defined. The H4 gate is therefore a protocol decision, not an estimate of field-wide utility.

### Results integrity

The H4 failure is completely reported. “Zero false certificates” is checked against the same analytic endpoints that define the certificate; it should be described as an implementation invariant. Independent validation is supplied instead by the separate oracle/LP checks and should not be conflated with this count.

### Reproducibility

Hash manifests and internal replays are strong. Appendix B verifies the sealed stage-two bytes but does not provide a complete command to rerun the CRABS comparison from inputs. A final release needs a clean end-to-end command, resource expectations and an independent reproduction receipt.

### Methodological fallacies detected

- **Composite-outcome conflation:** structural censoring and returned-cloud deficit are combined under one endpoint-incompleteness label.
- **Pseudo-replication risk:** query-level Wilson intervals ignore within-cell dependence, although the paper limits them to descriptive use.
- **Circular validation wording:** zero false certificates is a self-check when judged against the same analytic endpoint definition.
- **No evidence of p-hacking or subgroup rescue:** the failed pooled H4 gate is retained.

## Questions for the authors

1. What exact regularity is intended for `lambda`, `mu`, `lambda_p`, `u` and `A` in Theorem 1?
2. Is Theorem 4 a law for topology-marginal branching times or for a particular fully specified tree representation?
3. What is the 3-by-3 transition matrix between finite-cloud and certificate statuses for H4?
4. Does H2 remain a pass under the returned-cloud-only denominator of 240 cells, and will that become the principal scientific description?

## Minor issues

- State whether `(x_i-x_j)_+` includes equality and define it before Theorem 8.
- Use “supremum” rather than “upper endpoint” whenever the barrier prevents attainment.
- In Theorem 12, state explicitly that `eta <= c Delta` is the lower-tail branch of the Irwin-Hall distribution.
- Report timing precision consistent with the clock and benchmarking setup; five significant digits in `4.68e-5` seconds are unnecessary in prose.

## Dimension scores

| Dimension | Score | Descriptor | Notes |
|---|---:|---|---|
| Originality | 80 | Strong | Distinctive coupling of partial identification and diversification geometry. |
| Methodological rigor | 58 | Weak at publication readiness | Strong algebraic core; theorem-space specification and benchmark semantics require major repair. |
| Evidence sufficiency | 48 | Weak at publication readiness | Large internal audit, but no external theorem review or independent replay. |
| Argument coherence | 78 | Strong | Logical separation of layers is good; H2 terminology obscures one distinction. |
| Writing quality | 76 | Strong | Precise but compact; several conventions need explicit definitions. |
| **Weighted average** | **64.6** | **Major Revision** | Scored against a field-leading methodological venue. |
