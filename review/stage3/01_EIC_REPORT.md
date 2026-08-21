# Peer Review Report — Editor-in-Chief

## Manuscript information

- **Title:** *Conditional Sharp Partial Identification of Diversification Histories: Affine Measure Geometry, Event Congruence, Certified Extremes and a Confirmatory CRABS Comparison*
- **Manuscript ID:** AFFINE-0.3.0-CANDIDATE
- **Review date:** 21 August 2026
- **Review round:** 1

## Reviewer information

### Reviewer role

Editor-in-Chief.

### Reviewer identity

Senior editor in systematic biology with expertise in theoretical macroevolution and phylogenetic methods, applying a field-leading specialist-journal standard.

### Review focus

I assess whether the paper makes a sufficiently clear, original and consequential contribution for systematic biologists, whether the headline is supported by the actual result hierarchy, and whether the paper is mature enough to enter an archival publishing workflow. I do not adjudicate the detailed proofs.

## Overall assessment

### Recommendation

- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**
- [ ] Reject

### Confidence score

**4/5 — high confidence.** The editorial and macroevolutionary questions are within my expertise; the measure-theoretic proofs require a separate specialist.

### Summary assessment

The manuscript recasts a fixed-pulled-signal birth-death congruence class as a conditional identified set and uses a cumulative-loss measure to obtain sharp projections, feasibility certificates and endpoint constructions. It also reports a commendably transparent 1,100-cell comparison with CRABS in which H4, the prespecified decision-utility gate, fails. The paper's strongest editorial qualities are its unusually explicit assurance boundary (p. 1), its retention of an unfavorable primary result (pp. 10–12), and a potentially valuable conceptual separation among exact geometry, finite exploration and statistical inference (pp. 13–16).

The present article is nevertheless not ready for a field-leading archival release. The biological problem solved is not yet demonstrated end to end: the pulled signal is treated as fixed, its simultaneous uncertainty procedure is absent, and the fossil calculation is explicitly only a plug-in sensitivity illustration. The theorem and software contributions also compete for attention, while the broadest event-congruence statement still awaits an external specialist audit. I recommend major revision rather than rejection because the conditional theorem package appears substantial, the negative benchmark result is honestly reported, and the core can be repositioned into a rigorous methods contribution.

## Strengths

### S1: Unusually disciplined claim calibration

The abstract and assurance boundary state that H4 failed and explicitly prohibit “must-have” or essential-complement language (p. 1). The conclusion again reports 13.85% rather than rescuing the claim through favorable strata (p. 16). This is exemplary editorial conduct for a mixed-result methods paper.

### S2: A coherent conceptual object

The decision problem on pp. 1–2 is memorable: a congruence class is treated as a functional identified set for which analysts should ask for the complete feasible set, sharp target extrema and infeasibility witnesses. That framing gives the mathematics a recognisable role beyond another curve generator.

### S3: Strong internal assurance architecture

The paper distinguishes proofs, numerical controls, the sealed benchmark, external review and publication status (pp. 14–16). The complete 1,100-cell accounting, preserved nontermination incident and additive H5 correction are stronger transparency signals than are typical for theoretical-computational submissions.

### S4: Negative results add credibility

Table 1 and Figure 5 make the failed H4 gate visible. The paper does not use H2, H3, fast execution or favorable subgroups to overwrite the negative primary utility decision. This makes the benchmark scientifically useful even though it does not support the desired headline.

## Weaknesses

### W1: The end-to-end biological contribution remains incomplete

**Problem:** The paper solves the geometry conditional on a supplied pulled-scale trajectory, but Section 10 supplies only a set-inclusion architecture and explicitly does not construct a simultaneous uncertainty set. Section 9 supplies no observation model for the fossil quantities (pp. 12–13).

**Why it matters:** A Systematic Biology reader cannot yet take an estimated timetree signal through uncertainty propagation to a biologically interpretable decision. Without that bridge, the contribution is chiefly mathematical, despite a biologically ambitious title and framing.

**Suggestion:** Either add one complete uncertainty-aware worked analysis with an honest simultaneous set for the pulled signal and a clearly delimited target decision, or reposition the article as a theorem paper and make the statistical and palaeobiological steps explicit future modules rather than near-term applications.

**Severity:** Major.

### W2: The contribution hierarchy is overloaded

**Problem:** The title and abstract ask readers to absorb affine measure geometry, finite events, turnover phase transitions, finite certificates, a sampling theorem, CRABS benchmarking and a mammal illustration in eighteen pages.

**Why it matters:** The field-level message becomes less clear: is the paper primarily a new representation theorem, a certification method, a critique of finite congruence exploration or a CRABS companion?

**Suggestion:** Make “conditional sharp certification of a fixed-signal congruence class” the single principal contribution. Present the finite-event theorem as its process-theoretic foundation and the CRABS study as a bounded stress test. Consider moving the mammal illustration or derivational material to a supplement.

**Severity:** Major.

### W3: The broadest theorem headline outruns its review status

**Problem:** The subtitle includes “Event Congruence,” and Theorem 4 is described as the complete fixed-stem reconstructed-tree law (pp. 4–5), yet the assurance boundary and limitations acknowledge that specialist review of its topology and conditioning conventions remains open (pp. 1 and 16).

**Why it matters:** This is a load-bearing claim for readers of reconstructed-process theory. Internal normalization and simulation are valuable but cannot substitute for specialist examination of the probability space and normalizers.

**Suggestion:** Before archival release, obtain an independent stochastic-process review. In the manuscript, make clear whether the proved formula is topology-marginal or a density for a fully specified oriented/ranked topology, and state the base measure and topology factor explicitly.

**Severity:** Major.

### W4: The benchmark's practical meaning needs a more reader-centered explanation

**Problem:** H2 passes under a deficit-or-censor composite while H4 fails on 3,840 non-abrupt queries (pp. 9–12). A reader must work hard to understand why every H2 cell can count as an event while only 13.85% of decision statuses change.

**Why it matters:** Without an explicit decision example, “systematic endpoint incompleteness” can sound more consequential than the failed utility gate permits.

**Suggestion:** Add a one-page worked decision example showing a finite cloud, the sharp interval, the resulting status transition and a case in which no decision changes. Report returned-cloud and structural-censor results separately before giving the frozen composite.

**Severity:** Major.

### W5: The release-facing material is not yet a coherent successor

**Problem:** Appendix B still invokes a `0.2.1` container tag, and the root README remains the 0.2.1 release document with the direct CRABS comparison listed as open. The candidate packet correctly separates the historical DOI, but a final reader can encounter conflicting version narratives.

**Why it matters:** Version ambiguity damages trust in an evidence-led publication even when the manuscript bytes are correct.

**Suggestion:** In the revision stage, create a clean successor README, complete replay instructions and new immutable release manifest without altering historical 0.2.1 receipts.

**Severity:** Major for release readiness; minor for theorem correctness.

## Detailed comments

### Title and abstract

The title is accurate but too dense. The abstract is impressive in its candor, although “all 300 primary cells” should immediately distinguish 240 returned clouds from 60 structural censors. “Zero false certificates” should be labelled a certificate self-consistency check if it is evaluated against the same analytic endpoints used to generate the certificate.

### Introduction

The partial-identification question is clear and should become the organising spine. Add a short audience-level example before introducing the five contributions.

### Results and discussion

The failed H4 result deserves interpretive priority over the visually striking 300/300 H2 result. Explain the direction of the 532 status changes and the consequences for an analyst. The paper should also distinguish utility for avoiding overconfident finite-cloud statements from utility for changing substantive biological decisions.

### Conclusion

The conclusion is appropriately narrow. It should state the recommended present use in one sentence: for example, as a conditional diagnostic after a pulled signal and restrictions have been supplied, not as an inferential pipeline.

### Journal fit

The topic is in scope for Systematic Biology, but that venue would require clearer biological significance, stronger process-theoretic validation and a more complete link to uncertainty in an estimated pulled signal. Methods in Ecology and Evolution would additionally require a polished, adoptable user workflow. Theoretical Population Biology is a natural destination if the paper remains primarily theorem-led.

## Questions for the authors

1. What single decision should a systematic biologist make differently after using the certificate, and can the manuscript trace that decision from timetree input through signal uncertainty?
2. Is the intended principal article a theorem paper or an adoptable software method? Which secondary components can move to supplementary material?
3. Will an external process specialist sign off on Theorem 4's exact conditioning and topology conventions before release?
4. Can the successor package be replayed from one documented command without relying on historical 0.2.1 instructions?

## Minor issues

- Replace “Anonymous agentic research candidate” with the authorship/provenance form required by the Evidence Press protocol and provide a responsibility statement.
- Give the H4 status-change directions, not only their total.
- Explain in the Figure 5 caption that the displayed Wilson intervals are not independent-query inferential intervals.
- Consider shortening “Conditional Sharp Partial Identification” to “Sharp Conditional Identification” only if that does not change the intended statistical terminology.

## Dimension scores

| Dimension | Score | Descriptor | Notes |
|---|---:|---|---|
| Originality | 80 | Strong | Distinctive coupled representation and certification package; priority remains incompletely searched. |
| Methodological rigor | 54 | Weak at target-journal readiness | Strong internal controls, but a load-bearing theorem and end-to-end inferential path remain externally unvalidated. |
| Evidence sufficiency | 48 | Weak at target-journal readiness | Extensive internal evidence; limited external validation and no uncertainty-aware empirical demonstration. |
| Argument coherence | 78 | Strong | Clear central logic, but too many co-equal contributions. |
| Writing quality | 76 | Strong | Precise and candid, although dense for a broad systematic-biology audience. |
| **Weighted average** | **64.6** | **Major Revision** | Ordinal score relative to a field-leading specialist venue. |
