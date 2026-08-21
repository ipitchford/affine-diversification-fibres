# Peer Review Report — Reviewer 3 (Perspective)

## Manuscript information

- **Title:** *Conditional Sharp Partial Identification of Diversification Histories: Affine Measure Geometry, Event Congruence, Certified Extremes and a Confirmatory CRABS Comparison*
- **Manuscript ID:** AFFINE-0.3.0-CANDIDATE
- **Review date:** 21 August 2026
- **Review round:** 1

## Reviewer information

### Reviewer role

Peer Reviewer 3 — Cross-disciplinary and practical perspective.

### Reviewer identity

Computational macroevolution and research-software specialist familiar with congruence-class exploration, benchmark design, reproducible packaging and method adoption.

### Review focus

As an adjacent-field reviewer, I assess whether a working macroevolutionist can safely use the proposed certificate, whether the CRABS comparison is practically fair, and whether the evidence package is independently reproducible, portable and reusable. I do not adjudicate theorem proofs or conduct a completeness audit of the phylogenetic literature.

## Overall assessment

### Recommendation

- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**
- [ ] Reject

### Confidence score

**4/5 — high confidence.** Reproducible computation and method adoption are within my expertise; I defer on proof validity.

### Summary assessment

The manuscript has the bones of an excellent research object: machine-readable claims, exact hashes, negative controls, an immutable stochastic ledger, disclosed amendments and an intentionally failed utility gate. It also respects CRABS's stated role as an exploration tool and does not present the analytic matched sampler as a CRABS model. These choices substantially reduce the risk of an unfair “exact method beats random software” narrative.

The practical product is nevertheless unfinished. A user currently encounters a historical 0.2.1 README, 0.2.1 container commands, a successor review packet and no single end-to-end command that regenerates the direct comparison. The benchmark covers one `rho=1` bridge, a synthetic-dominant signal set, fixed grids/caps and query thresholds that are convenient for protocolization but not tied to a biological decision. Structural censoring is scientifically interesting for the frozen configuration, yet it is not evidence about all CRABS workflows. Finally, the certificate consumes a fixed pulled signal without an interface for its uncertainty. I therefore see a strong reproducible theorem prototype, not yet a broadly adoptable complement. Major revision should produce a safe user workflow, external replay, cross-platform evidence and rights-cleared successor packaging.

## Strengths

### S1: The evidence chain is inspectable

The manuscript and review packet connect claims to proofs, receipts, source data and manifests. Section 12 lists independent envelope checks, direct simulation, negative controls and clean-container replay (pp. 14–16). This is far more useful than a paper that merely says “code is available.”

### S2: The comparator's role is treated respectfully

Section 6 explicitly limits the factorial law to a matched Uniform sampler and says actual samplers may concentrate differently (pp. 8–9). Section 7 evaluates CRABS directly and the conclusion calls certification a diagnostic, not a replacement (pp. 9–16).

### S3: Incident history is preserved

The nonterminating abrupt cells and the H5 wrong-interpreter incident are not deleted or recoded as ordinary passes. This is good practice for computational accountability.

### S4: Machine-readable results support future extension

The complete ledger, sidecars, stratum-level figure data and alt text should make it possible to add alternative summaries without rerunning the high-cost study or modifying the frozen primary decision.

## Weaknesses

### W1: There is no safe, complete user journey

**Problem:** The paper explains the mathematical pieces but not an operational sequence from an estimated pulled signal to restrictions, feasibility checks, target bounds and a report. Appendix B verifies bytes and invokes historical 0.2.1 tasks rather than a successor pipeline.

**Why it matters:** Broad uptake depends on whether a non-author can make the right choices and interpret the output, not only whether a kernel runs quickly.

**Suggestion:** Add a minimal command-line or notebook workflow with a schema-validated input, explicit units, cap interpretation, event conventions, target definition, uncertainty disclaimer and machine-readable output. Provide a worked `estimate -> condition -> certify -> interpret` example and failure messages for barrier and infeasibility cases.

**Severity:** Major.

### W2: Comparator generality is much narrower than practical CRABS use

**Problem:** The direct comparison uses one exact bridge (`rho=1`, `lambda_ref=lambda_p`, `mu_ref=0`), two grids, three caps, ten replicates and five signals, while abrupt cells are censored under `max.lambda=2` (pp. 9–11).

**Why it matters:** CRABS offers multiple exploration strategies and tuning choices. The benchmark validly characterizes its frozen configuration, but users could mistake the result for a general limitation of CRABS.

**Suggestion:** Put a “tested/not tested” matrix next to Table 1. Include CRABS procedure, version/commit, settings, bridge, signal family and outcome type. State that changing `max.lambda`, proposals or bridges is a new study. Invite CRABS maintainers or unaffiliated users to run a preregistered external extension rather than expanding the frozen claim post hoc.

**Severity:** Major.

### W3: The decision queries are computational rather than biological

**Problem:** H4 uses four domain fractions crossed with four multiples of the signal median. These are reproducible, but the paper does not explain a biological decision that uses those thresholds.

**Why it matters:** A 13.85% status-change fraction is difficult to interpret as utility. A method may be useful for a few high-consequence decisions or unimportant for many artificial thresholds.

**Suggestion:** Keep H4 as the immutable primary result, then add a clearly prospective future-work plan for target-specific decisions chosen by domain users. In the current paper, show the direction and practical meaning of each status transition and avoid equating query count with biological value.

**Severity:** Major.

### W4: Reproducibility stops at internal replay

**Problem:** The container replay was performed by the release-preparing agent, H5 is qualified to one macOS host, and no external party has recreated the CRABS environment and regenerated the ledger. The review package verifies stage-two bytes but does not supply one command for full regeneration.

**Why it matters:** Hashes establish integrity after creation; they do not show that another system can recreate the results. Cross-language Python/R dependencies, long runtimes and the nontermination guard are exactly where independent reproduction is most valuable.

**Suggestion:** Supply an end-to-end replay target, a resource/time budget, deterministic environment lockfiles, Linux and macOS smoke tests, and an independent reproduction receipt. The external replay should begin from a fresh checkout and should compare regenerated summaries and hashes without access to mutable author caches.

**Severity:** Major.

### W5: Successor rights and metadata remain unresolved

**Problem:** The manuscript uses a qualified CRABS empirical signal and redistributes result artefacts, while the release-specific rights review is still open. The root package labels itself 0.2.1 and points to the historical DOI.

**Why it matters:** Reusability requires source-specific license, provenance and version metadata. A scientifically correct package can still be unpublishable if derived data or code terms are unclear.

**Suggestion:** Complete a component-level rights matrix for every CRABS-derived signal/result, separate GPL-covered code from original data and prose, and create a new successor manifest and citation file. Preserve the historical release unchanged.

**Severity:** Major.

## Detailed comments

### Assumption audit

**Explicit assumptions:** A fixed positive pulled signal, homogeneous time-only rates, specified sampling, no interior events under continuous cap results, and a finite turnover cap are clear.

**Implicit assumption:** A user can choose a cap and external constraints without introducing more subjectivity than the certificate resolves. This needs a sensitivity workflow and provenance for every restriction.

**Paradigmatic assumption:** Exact conditional bounds are treated as the key safeguard against finite exploration. In practice, data-model mismatch and uncertainty in the pulled signal may dominate endpoint-sampling error. The software should report all three layers rather than giving exactness visual priority.

### Cross-disciplinary connections

**Parallel research:** Partial-identification inference distinguishes an identified set from a confidence set for that set. Scientific-computing research distinguishes repeatability on the author's system from independent reproducibility.

**Borrowing opportunities:** Use a typed provenance graph for `source signal -> restrictions -> certificate -> decision`, and a set-valued uncertainty layer that unions certificates across a simultaneous signal set.

**Methodological borrowing:** Treat restriction choice like a sensitivity-analysis specification: declare a defensible range, calculate robustness over the range and log which assumption drives infeasibility.

### Practical impact

**Real-world application:** The immediate use is an audit after congruence exploration: a user can check whether a finite cloud supports a claimed endpoint or whether the claim depends on unvisited feasible paths.

**Implementation feasibility:** The exact kernel is fast, but the end-to-end cost includes estimating and serializing the signal, aligning grids/units, choosing restrictions and interpreting event/cap semantics. These steps are not yet productized.

**Stakeholders:** Primary users include CRABS users, developers of alternative congruence samplers, phylogenetic methodologists, palaeobiologists and curators of empirical data. Their input should shape target-specific queries and documentation.

### Broader implications

**Ethical dimension:** “Exact” can create false confidence when conditioning assumptions are hidden. Output must display the fixed-signal and observation-model boundaries as prominently as the numerical endpoints.

**Social impact:** No direct social risk is apparent. The main scholarly risk is asymmetrical comparison that harms trust between method communities; the manuscript largely avoids this but should invite external comparator review.

**Future directions:** Independent CRABS-maintainer review, target-specific preregistered queries, set-valued signal uncertainty, and fossil observation models are the highest-value next steps.

### Cross-disciplinary reading recommendations

1. **Chernozhukov, Hong and Tamer (2007), Econometrica, DOI 10.1111/j.1468-0262.2007.00794.x.** Distinguishes estimation and confidence regions for identified sets from the identified set itself.
2. **Sandve et al. (2013), PLOS Computational Biology, DOI 10.1371/journal.pcbi.1003285.** Practical reproducibility principles for computational analyses.
3. **Wilson et al. (2014), PLOS Biology, DOI 10.1371/journal.pbio.1001745.** Scientific-software practices relevant to testing, automation and maintainability.
4. **Wilkinson et al. (2016), Scientific Data, DOI 10.1038/sdata.2016.18.** FAIR principles for machine-actionable data, provenance and reuse.
5. **Stodden et al. (2016), Science, DOI 10.1126/science.aah6168.** Distinguishes evidence availability from reproducibility of computational methods.

## Questions for the authors

1. What exact command, input schema and interpretation report would a first-time user run on their own pulled-rate curve?
2. Which parts of the H4 transition count represent finite-cloud overconfidence rather than useful new biological decisions?
3. Has any unaffiliated CRABS user or maintainer reviewed the bridge and censor interpretation?
4. Which successor artefacts are redistributable under which licences, and can a fresh Linux host regenerate them?

## Minor issues

- Add explicit CPU, memory and elapsed-time expectations for the full 1,100-cell replay.
- Remove generated `__pycache__` artefacts from any successor publication bundle unless deliberately documented.
- Provide checksums in a machine-readable manifest with algorithm identifiers and relative paths.
- Make figure alt text part of the public landing page, not only a JSON sidecar.

## Dimension scores

| Dimension | Score | Descriptor | Notes |
|---|---:|---|---|
| Originality | 79 | Strong | Exact certification is a valuable adjacent capability. |
| Methodological rigor | 60 | Adequate | Strong internal design; practical workflow and external comparator validation remain incomplete. |
| Evidence sufficiency | 50 | Weak at adoption readiness | Rich internal evidence, no unaffiliated replay or cross-platform verification. |
| Argument coherence | 75 | Strong | The layers are distinguished, but practical utility is not yet tied to a real decision. |
| Writing quality | 76 | Strong | Clear for specialists; operational guidance is dispersed. |
| Significance and impact | 64 | Adequate | Promising diagnostic value, presently narrow and conditional. |
| **Weighted average** | **64.6** | **Major Revision** | Relative to an uptake-oriented methods venue. |
