# Peer Review Report — Reviewer 2 (Domain)

## Manuscript information

- **Title:** *Conditional Sharp Partial Identification of Diversification Histories: Affine Measure Geometry, Event Congruence, Certified Extremes and a Confirmatory CRABS Comparison*
- **Manuscript ID:** AFFINE-0.3.0-CANDIDATE
- **Review date:** 21 August 2026
- **Review round:** 1

## Reviewer information

### Reviewer role

Peer Reviewer 2 — Domain.

### Reviewer identity

Stochastic phylogenetics specialist working on reconstructed birth-death processes, extant sampling, mass-extinction events and diversification-model identifiability.

### Review focus

I assess whether the process interpretation, conditioning conventions and biological terminology are accurate; whether the paper is positioned fairly within macroevolutionary scholarship; and whether the claimed contribution is genuinely useful to diversification researchers. I leave numerical benchmark mechanics and generic optimisation proofs to other reviewers.

## Overall assessment

### Recommendation

- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**
- [ ] Reject

### Confidence score

**5/5 — very high confidence** for the birth-death and systematic-biology issues addressed here.

### Summary assessment

This manuscript offers a potentially important bridge between the congruence-class debate and the language of conditional partial identification. Its central domain contribution is not that extant timetrees suddenly identify speciation and extinction, but that scientifically explicit restrictions can be translated into complete conditional feasible sets, extrema and incompatibility witnesses. That is a constructive and appropriately modest response to nonidentifiability. The manuscript also deserves credit for distinguishing extant-tree geometry from fossil observation and for retaining the failed CRABS utility gate.

The domain case is not yet publication-ready. Most importantly, the fixed-stem result is presented as a complete reconstructed-tree law without a fully explicit tree convention, even though the history of this literature shows that survival, stem, crown, origin-time, tip-count, labelling and sampling conventions change normalizing factors. Second, the biological status of the turnover cap is underdeveloped: `mu/lambda <= c` is a strong history-wide restriction, not merely a benign regularizer. Third, the paper's 18-reference positioning is too thin for a priority-sensitive synthesis spanning reconstructed processes, sampling symmetries, congruence methods and partial identification. Finally, the mammal example is correctly labelled non-inferential, but it cannot yet motivate applied biological conclusions. I recommend major revision with external process-theory review.

## Strengths

### S1: Correctly treats nonidentifiability as a model property

The introduction (pp. 1–2) does not imply that more tips or more computation alone identify `lambda(t)` and `mu(t)`. It instead asks what is sharp after conditioning on a pulled signal and explicit restrictions. That is a productive way to engage the Louca–Pennell result.

### S2: Conditioning limits are disclosed

Remark 5 explicitly excludes crown conditioning, random-origin priors and other normalizers (p. 5). This is important because equivalence claims in reconstructed birth-death models are highly sensitive to which tree event is conditioned upon.

### S3: Deterministic events are separated from continuous turnover

Section 3 represents an event as independent survival thinning and states that its atom is not a point value of continuous `mu/lambda` (p. 3). This prevents a mass-extinction event from being confused with an arbitrarily large continuous extinction rate.

### S4: The fossil boundary is unusually honest

Sections 8–9 distinguish the deterministic model quantity `N_det` from realised species richness and list the latent-process, preservation and taxonomic bridges required for fossil use (pp. 12–13). The mammal calculation is not advertised as an extinction estimate.

## Weaknesses

### W1: The fixed-stem theorem needs a convention-complete derivation

**Problem:** Theorem 4 supplies a topology-marginal ordered-time density and then asserts that the conditional ranked-topology law is exchangeable and rate-independent (pp. 4–5). The exact topology convention remains verbal.

**Why it matters:** Reconstructed-process formulae differ under stem versus crown age, survival versus fixed `n`, labelled versus unlabelled trees, and ranked versus oriented representations. The manuscript's phrase “complete fixed-stem reconstructed-tree law” invites readers to apply more than has been written down.

**Suggestion:** Define the sampled tree space explicitly and state each density/mass with respect to its base measure. Reconcile the result with Nee, May and Harvey (1994), Gernhard (2008), Stadler (2010), Lambert and Stadler (2013), Höhna (2015), and the incomplete-sampling symmetries of Stadler and Steel (2019). Add an external review statement from a specialist who did not develop the candidate.

**Severity:** Major and load-bearing.

### W2: The turnover cap lacks adequate biological interpretation

**Problem:** The paper derives elegant phase behavior for `0 <= mu/lambda <= c` (pp. 5–6), but offers little guidance for why a systematist should select `c=0.25`, `0.5`, `0.9`, `1` or a supercritical value. The restriction is imposed at every non-event time.

**Why it matters:** For `c<=1`, the class excludes all continuous intervals of negative net diversification. That can rule out biologically plausible histories during environmental deterioration or diffuse extinction episodes. For `c>1`, a pointwise ceiling still has a strong interpretation and the possible divergence after `x_crit` may limit practical use.

**Suggestion:** Add a biological assumptions table: each cap regime, what it permits, what it excludes, how events interact with it, and which conclusions are sensitivity analyses rather than estimates. Prefer reporting results over a range of scientifically justified caps to implying that one value is natural.

**Severity:** Major.

### W3: “Homogeneous” needs prominence as an applicability boundary

**Problem:** The model is homogeneous across contemporaneous lineages and varies only with time, but this condition is easy to lose behind the broad phrase “diversification histories.” Lineage-, state-, trait- and diversity-dependent processes are not represented by the one-dimensional fibre.

**Why it matters:** Much modern macroevolution concerns heterogeneity across clades and traits. Readers may otherwise infer that the identified-set geometry applies to all birth-death diversification models.

**Suggestion:** Put “homogeneous time-varying” in the abstract's first contribution sentence and add a boxed applicability boundary contrasting time-only homogeneous models with state-dependent and lineage-heterogeneous models.

**Severity:** Major for scope calibration.

### W4: Literature integration is too sparse for the priority claim

**Problem:** Section 11 acknowledges that the priority search was targeted, but the paper makes a coupled-package novelty claim while citing only eighteen sources (pp. 14 and 17–18). Several foundational conditioning and incomplete-sampling papers and an important current field synthesis are absent.

**Why it matters:** The coordinate may be recognizable under inverse-tail, reconstructed-process, survival-analysis or birth-death transformation notation. Without a theorem-by-theorem recognition table, novelty can be overestimated even when no intentional overclaim occurs.

**Suggestion:** Conduct the planned systematic recognition search and add a result-level table classifying each component as antecedent, reformulation, extension or new synthesis. At minimum incorporate the specific sources listed below.

**Severity:** Major.

### W5: The mammal section does not yet support field adoption

**Problem:** Section 9 fixes one upstream curve, shifts the analysis origin to 1 Ma and tries three fossil-genus summaries under an unvalidated mapping (pp. 12–13).

**Why it matters:** These calculations illustrate algebra but do not show whether the certificate improves a defensible mammal-diversification inference. The incompatibility can arise from the cap, the fixed signal, the latent richness approximation, preservation, taxonomy or time alignment.

**Suggestion:** Retain the example only as a worked sensitivity check unless an observation model and signal uncertainty are added. Give the multiple possible causes of incompatibility equal visual prominence and avoid implying that a minimum cap diagnoses mammalian turnover.

**Severity:** Major for applied claims; minor for the theorem paper.

## Detailed comments

### Literature review

**Coverage:** The core 2020–2026 identifiability and congruence literature is represented, but the historical conditioning lineage is incomplete. The paper should also engage the contemporary shift toward explicit hypotheses and uncertainty rather than treating the debate as only exploration versus certification.

**Integration quality:** Table 2 is useful but compresses heterogeneous approaches into broad columns. “Identifiable restricted or enriched models” includes conceptually different strategies—functional restriction, fossil sampling, hidden-event information and model-specific identifiability—that deserve separate lines.

**Research gap:** The narrow gap is plausible: a coupled conditional-measure representation with cap bounds, finite certificates and a sampling law. It is not yet established by a systematic priority search.

### Theoretical framework

The partial-identification framing is appropriate. Its domain value is that assumptions become restrictions whose consequences can be reported as sets and falsified jointly. The framework should more clearly distinguish a biological hypothesis class from a computational convenience class.

### Academic argument quality

The statement that finite events preserve the conditional positive descendant-count law is plausible under independent contemporaneous thinning, but the event must be independent across lineages and not state- or diversity-dependent. These qualifiers should follow the theorem statement, not only appear indirectly in the proof.

The phrase “the pulled speciation rate is identified by the reconstructed extant-timetree likelihood” (p. 2) should be expressed carefully: the likelihood depends on the pulled quantity, but finite-data estimation of a time-varying function remains a separate problem, and present-day sampling can participate in parameter transformations.

### Contribution to the field

If the theorem package survives external review, its chief contribution is a vocabulary and exact calculus for conditional sensitivity analysis. It should not be pitched as recovering the true diversification history. The failed H4 result makes “diagnostic complement” a defensible description, provided the particular comparator scope is always attached.

### Missing key references

1. **Nee, May and Harvey (1994), “The reconstructed evolutionary process,” Philosophical Transactions of the Royal Society B, DOI 10.1098/rstb.1994.0068.** Foundational reconstructed-process and descendant-count context.
2. **Gernhard (2008), “The conditioned reconstructed process,” Journal of Theoretical Biology, DOI 10.1016/j.jtbi.2008.04.005.** Directly relevant to fixed-tip-count conditioning and tree-shape/speciation-time factorization.
3. **Stadler (2010), “Sampling-through-time in birth-death trees,” Journal of Theoretical Biology, DOI 10.1016/j.jtbi.2010.09.010.** Clarifies sampling and conditioning conventions in birth-death tree densities.
4. **Stadler and Steel (2019), “Swapping Birth and Death: Symmetries and Transformations in Phylodynamic Models,” Systematic Biology, DOI 10.1093/sysbio/syz039.** Relevant to incomplete-sampling transformations and the admissibility of transformed rates.
5. **Morlon, Robin and Hartig (2022), “Studying speciation and extinction dynamics from phylogenies: addressing identifiability issues,” Trends in Ecology & Evolution, DOI 10.1016/j.tree.2022.02.004.** Places congruence, hypotheses and regularisation in the wider methodological debate.
6. **Title, Henao-Díaz, Zenil-Ferguson and Vasconcelos (2026), “An Evolving View of Lineage Diversification,” Systematic Biology, DOI 10.1093/sysbio/syaf086.** Current field-level synthesis emphasizing uncertainty, hypothesis-driven work and biological evidence.

## Questions for the authors

1. Precisely which topology, labelling and orientation convention is used in the “complete” law, and where is its probability mass stated?
2. What biological knowledge would justify a uniform turnover cap over the entire time interval rather than a time-varying or probabilistic restriction?
3. Which parts of the affine representation survive lineage or state dependence, if any?
4. Is the mammal example intended to motivate a future observation model, or is it part of the current evidential case?

## Minor issues

- Define “analysis origin” before using “present” in any figure caption; the mammal origin is 1 Ma, not today.
- Avoid alternating “survival event,” “deterministic event” and “mass-extinction event” unless their equivalence and independence assumptions are explicit.
- Explain whether the sampling atom at zero is part of the same event convention as interior thinning or merely a coordinate representation.
- In Table 2, replace “No” with more nuanced entries where a prior method answers a different question rather than lacking a capability.

## Dimension scores

| Dimension | Score | Descriptor | Notes |
|---|---:|---|---|
| Originality | 76 | Strong | The coupled synthesis appears distinctive; exhaustive priority remains open. |
| Methodological rigor | 57 | Weak at publication readiness | Process-theoretic state space and biological restriction class need clarification. |
| Evidence sufficiency | 47 | Weak at publication readiness | Strong internal evidence, sparse external recognition and no observation-aware empirical validation. |
| Argument coherence | 76 | Strong | Conditional logic is clear; the biological adoption story remains incomplete. |
| Writing quality | 75 | Strong | Precise but dense, with scope qualifiers too dispersed. |
| Literature integration | 58 | Significant gaps | Several foundational and current synthesis sources are missing. |
| **Weighted average** | **62.3** | **Major Revision** | Relative to a leading systematic-biology venue. |
