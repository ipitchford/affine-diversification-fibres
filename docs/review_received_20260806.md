# Full review: *Sharp Partial Identification of Diversification Histories: Affine Measure Geometry of Birth–Death Congruence Classes*

**Version reviewed:** Candidate release 0.1.0, dated 6 August 2026
**Review date:** 6 August 2026
**Recommendation:** **Major revisions**
**Confidence:** **High, 0.88**
**Proposed Evidence Press status:** Not ready for release as submitted; credible candidate after the must-fix revisions below.

## 1. Executive assessment

This theorem-led candidate develops an affine cumulative-loss measure coordinate for time-dependent birth–death congruence classes, then uses it to derive sharp pointwise envelopes, finite compatibility certificates and minimum-turnover-cap diagnostics under external constraints. Its strongest feature is the unusually close alignment between mathematics and executable artefacts: the archive checksum and all 38 manifested files verify; the test suite, demo, numerical outputs and four figures reproduce; and independent algebraic checks recover the central fibre parametrisation, atom update, turnover envelopes and interval-feasibility criterion.

I recommend major revisions, with high confidence. I found no fatal arithmetic or theorem-level contradiction in the smooth fibre or sharp-envelope results. The decisive weaknesses are instead at the boundaries of the claimed contribution. The finite-atom reconstructed-tree equivalence rests on a conditioning-dependent likelihood step that is plausible but not yet sufficiently self-contained for such a load-bearing extension. The sharp sets are conditional on a fixed pulled signal, whereas the uncertainty result is only a set-union principle and no simultaneous signal band is supplied. The palaeontological illustration also moves too quickly from a deterministic model-implied lineage trajectory to realised fossil diversity, compounded by genus-to-species and observation-process mismatches. Finally, several constituent ideas have clear prior art, while the exact novelty of the measure geometry and certificates remains supported only by a targeted, non-exhaustive search. After tighter claims, a specialist conditioning audit, clearer empirical semantics and Evidence Press assurance-pack completion, this would be a credible and useful candidate release.

## 2. Scope and evidence limits

### Manuscript type and intended audience

This is principally a **theoretical and computational methods paper** in macroevolutionary phylogenetics, with substantial applied-mathematical content and a deliberately limited mammalian sensitivity illustration. Its likely primary audience is researchers working on diversification-rate inference, birth–death processes, partial identification and palaeodiversity reconstruction. For REF purposes, the closest primary home is **Unit of Assessment 5, Biological Sciences**, with a plausible secondary reading under **Unit of Assessment 10, Mathematical Sciences**.

### Materials inspected

I inspected:

* the thirteen-page PDF manuscript;
* the Markdown and LaTeX sources;
* all source code, tests, demonstration scripts, generated outputs and figures;
* the theorem audit, novelty gate, adversarial review, empirical note, release-status record, README, manifest and licensing metadata;
* the packaged wheel and extracted data;
* the supplied SHA-256 companion file;
* the uploaded REF scoring rubric;
* the current Evidence Press website and release conventions;
* decision-relevant external literature current to 6 August 2026.

The archive SHA-256 was independently computed as:

`2821a0021f0c4e0add93f19d7900e71e99968aeba384260367a042b10fdf6470`

This agrees exactly with the companion checksum. The archive contains 38 manifested payload files, excluding the manifest itself; all 38 hashes verify, with no missing or unmanifested payload files.

### Review standard

I assessed the candidate against:

1. mathematical validity and completeness appropriate to a theorem-led methods output;
2. accurate separation of conditional identification, statistical inference and biological interpretation;
3. computational replayability and claim-to-evidence traceability;
4. originality and positioning against current scholarship;
5. the current Evidence Press model for an explicitly unrefereed candidate release.

I have **not** treated the absence of conventional journal peer review as a defect. Evidence Press explicitly presents releases as pre-journal outputs and distinguishes internal replay from independent reproduction, formal verification and specialist review. It nevertheless states that every released result has complete evidence, mutation and negative controls, an assurance matrix, a pinned environment, an archived DOI and a public repository. ([Evidence Press][1])

### Missing or unavailable material

The following were **not included or not reported**, rather than assumed not to exist:

* the upstream mammal-tree R data object itself; the package includes an extracted derivative and a hash, but I could not independently repeat the original R-side extraction or refit;
* a simultaneous uncertainty set for the pulled signal (F) or (\lambda_p);
* a fossil occurrence, preservation or taxonomic observation model;
* an independent implementation of the central algorithms;
* an external specialist audit of the finite-atom stem-conditioned likelihood argument;
* a matched quantitative comparison with CRABS or the Andréoletti–Morlon exploration method;
* mutation tests and deliberately failing negative controls;
* a lockfile, environment image or fully pinned dependency resolution;
* the final Zenodo deposit, DOI and public GitHub mirror, which would normally be created at release rather than necessarily at candidate stage.

The literature search was targeted rather than systematic. Failure to locate an exact antecedent is therefore evidence in favour of, but not proof of, novelty.

## 3. Contribution and positioning

### Strongest defensible thesis

The strongest claim supportable by the submitted evidence is:

> For a fixed pulled diversification signal, a specified class of homogeneous time-dependent birth–death histories can be represented by a cumulative-loss measure. Within the absolutely continuous, turnover-capped subclass, finite external interval constraints yield explicit sharp envelopes, finite feasibility certificates and a minimum compatible turnover cap. Deterministic survival events can be represented by atoms, subject to the stated stem-conditioning conventions.

This formulation is close to the package’s own conservative “safe claim” and is materially better supported than broader formulations about recovering biological diversification histories.

### Claim-to-evidence map

| Main claim                                                                                                     | Manuscript evidence                   | Review assessment                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Smooth histories with fixed pulled rate are in bijection with admissible cumulative-loss functions or measures | Theorem 1, pp. 2–3                    | **Supported.** Independent substitution recovers the inverse formulas and density identity.                                                                                       |
| Incomplete sampling and deterministic survival events admit a measure-valued completion with atoms             | Proposition 2, p. 3                   | **Algebraically supported.** The jump relation is correct under the manuscript’s convention.                                                                                      |
| Stem-conditioned reconstructed-tree likelihood equivalence persists with finitely many atoms                   | Theorem 3, pp. 3–4                    | **Plausible but not yet sufficiently secured.** The key invariant checks algebraically, but the full conditioning and normalisation argument requires a more explicit derivation. |
| A turnover cap produces sharp bounds on survival and speciation, with a global multiplicative width            | Theorem 4, p. 5                       | **Supported within the stated no-atom class and (0\leq c\leq1).**                                                                                                                 |
| Finite interval constraints have a pairwise feasibility certificate and explicit least/greatest envelopes      | Theorem 5, pp. 5–6; Corollary 6, p. 6 | **Supported.** The necessity, sufficiency and extremal constructions reproduce.                                                                                                   |
| Fossil diversity bounds can constrain or falsify turnover-capped histories                                     | pp. 6–8; Corollary 7                  | **Only conditionally supported.** The affine calculation is valid for the model-defined quantity, but its interpretation as realised biological diversity is not established.     |
| Uncertainty in the pulled signal can be transferred by taking a union over a simultaneous confidence set       | Proposition 8, p. 8                   | **Logically correct but operationally incomplete.** No such confidence set is constructed or validated.                                                                           |
| The mammal example demonstrates empirical biological compatibility or incompatibility                          | pp. 8–11; empirical note              | **Not established.** It is defensible only as a deterministic sensitivity illustration under deliberately strong assumptions.                                                     |

### Originality and significance

The problem is important: extant timetrees can correspond to infinitely many time-dependent speciation and extinction histories, motivating either restrictions, partial identification or additional data. Louca and Pennell established the modern congruence-class formulation; subsequent work has developed diagnostics, sampled alternative histories, demonstrated identifiable restricted classes and shown that richer observations can restore identifiability. ([Nature][2])

Several components of the submission therefore have clear antecedents:

* pulled diversification coordinates and congruence classes;
* integrating-factor transformations;
* exploration of congruent rate trajectories;
* event-aware reconstructed birth–death processes;
* generic monotone/Lipschitz extension and envelope ideas;
* identifiability obtained by restricting function classes or enriching observations.

The likely original contribution is narrower but potentially worthwhile: **the particular cumulative-loss measure representation, its order geometry, and the packaging of turnover-capped external constraints into sharp closed-form envelopes, pairwise infeasibility witnesses and a minimum compatible cap**. I did not locate a publication containing that exact combination. This is a reviewer inference from a targeted search, not a definitive priority finding.

The paper would be significant if it changes practice from drawing arbitrary samples from a congruence class to reporting exact conditional projections and incompatibility certificates. That significance is currently prospective because the paper does not yet demonstrate, against existing software, when its exact solution changes an empirical conclusion or materially improves computation.

## 4. Major comments

### 1. The finite-atom likelihood-equivalence result needs a self-contained conditioning audit

**Classification:** Major

**Issue**

Theorem 3 is the most consequential extension beyond the smooth congruence result, yet its proof depends on reconstructed-tree density and conditioning conventions that are only sketched. The result may be correct, but the present exposition does not make it sufficiently easy to distinguish algebraic invariance from equality of the complete conditioned likelihood.

**Manuscript evidence**

On pp. 3–4, the manuscript derives the generating-function quantities and states that, under stem-survival conditioning, (p_1/u=1/F), so that the reconstructed-tree density depends only on the pulled rate even when finite atoms are present. The conclusion later acknowledges that crown- and origin-conditioned normalisers remain to be audited. The internal release-status document likewise retains an external specialist audit as an open gate.

I independently recovered two supporting identities:

1. between events, the logarithmic derivative of (p_1/u) reduces to (-\lambda_p), giving the claimed (1/F) dependence under the manuscript’s normalisation;
2. at a deterministic survival event, both the one-descendant probability and survival probability receive the same multiplicative survival factor, so their ratio is unchanged.

These checks support the argument but do not by themselves verify every tree-density normaliser, boundary convention or conditioning event.

**Why it matters**

The paper’s measure completion is materially more interesting if atom-bearing histories are genuinely in the same observed-data equivalence class. Conversely, an omitted conditioning factor could invalidate the atom extension while leaving the smooth fibre intact. Stem, crown, origin and fixed-tip-number conditionings are not interchangeable; event placement relative to the stem or root can also affect the normalising probability. Earlier reconstructed-process work treats such conventions explicitly, including bottlenecks, incomplete sampling and mass-extinction events. ([PubMed][3])

**Required revision or decisive test**

Provide a self-contained appendix that:

* defines the orientation of time and all left- and right-limit event conventions;
* states precisely what “stem survival” conditions on;
* derives the full reconstructed-tree density with finitely many atoms, rather than only the invariant factor;
* shows explicitly why conditioning on fixed extant tip count preserves equality;
* separates stem-conditioned results from crown- and origin-conditioned cases;
* either derives those additional cases or excludes them clearly from all general claims.

A useful computational check would compare exact atom formulas against successively narrower smooth-event approximations and against direct stochastic simulation. An external specialist sign-off on this theorem should remain an explicit assurance field rather than being absorbed into a generic “PASS”.

---

### 2. The paper conflates conditional identification geometry with statistical uncertainty in several high-level claims

**Classification:** Major

**Issue**

The sharp results are conditional on an exactly fixed pulled signal (F) or (\lambda_p). Proposition 8 states a valid union construction over a simultaneous confidence set, but the candidate supplies neither a procedure for obtaining that set nor a coverage analysis. Some passages nevertheless read as though the reported bounds were inferential confidence bounds.

**Manuscript evidence**

Theorem 1 and all subsequent geometry fix the pulled signal. Proposition 8 on p. 8 says, in effect, that if the true (F) belongs to a simultaneous set (\mathcal F), then the union of the conditional identified sets has at least the coverage of (\mathcal F). The mammal calculations use one estimated trajectory from one posterior tree and treat it as fixed. The manuscript itself notes that a simultaneous band remains future work.

**Why it matters**

A conditional identified set answers:

> Which rate histories are compatible with this exact pulled signal and these exact restrictions?

It does not answer:

> Which histories remain plausible after accounting for sampling variation, phylogenetic uncertainty, smoothing choices and model misspecification?

The distinction is especially important near feasibility boundaries: small changes in (F), constraint ages or lower bounds can switch a system from feasible to infeasible. A pointwise interval for (F(t)) would also not automatically provide the simultaneous coverage Proposition 8 presupposes.

**Required revision or decisive test**

Choose one of two defensible routes.

1. **Conditional-theory route:** Describe all sharp sets as conditional sensitivity or identification geometry. Retitle or qualify inferential phrases, label the mammal calculation as “plug-in, no coverage claim”, and move Proposition 8 to a short roadmap section.

2. **Inferential route:** Construct a genuinely simultaneous uncertainty set for the pulled trajectory, including phylogenetic or estimation uncertainty, and propagate the entire set through the sharp optimisation. Report the resulting unconditional or partially unconditional coverage target and assumptions.

For an Evidence Press candidate, the first route is sufficient and more proportionate. The present intermediate position is not.

---

### 3. The palaeontological constraint does not yet have a defensible bridge to realised species diversity

**Classification:** Major

**Issue**

The manuscript uses (M=M_0/F) and (N=M/u=M_0/q), then treats fossil-derived counts as lower bounds on (N). The algebra is coherent for a deterministic model-defined trajectory. It is not demonstrated that this trajectory is the realised number of species present at a geological time, or that genus-level fossil summaries are valid hard lower bounds on the same species-level random variable.

**Manuscript evidence**

Sections on palaeontology and the mammal illustration, pp. 6–11, use externally supplied diversity lower bounds to constrain (q) and hence the cumulative-loss function. The empirical note is commendably candid: it records that only one of 100 trees is used; the pulled trajectory is not refitted; the fossil values are genus-level summaries; no preservation, taxonomic or sampling model is supplied; and the time origin is shifted for convenience.

**Why it matters**

A deterministic lineage-through-time quantity under a birth–death model is ordinarily an expectation or model-implied summary across stochastic realisations, not the realised diversity path of a particular clade. Helmstetter et al. explicitly distinguish a deterministic expected lineage-through-time curve from individual stochastic realisations. ([OUP Academic][4])

There are then three separate bridges requiring justification:

1. expected or model-implied lineage count (\rightarrow) realised latent species richness;
2. fossil observations (\rightarrow) latent richness in the presence of incomplete preservation and sampling;
3. genera or higher taxa (\rightarrow) species-scale quantities used by the birth–death model.

Treating each as an exact inequality can make a numerical contradiction look like a falsification of a turnover cap when it is actually incompatibility of the cap **and all bridge assumptions jointly**.

**Required revision or decisive test**

At minimum:

* rename (N) precisely, for example “model-implied deterministic diversity trajectory”, and derive its probabilistic interpretation;
* replace “the fossil data falsify (c)” with “the supplied lower bound is incompatible with (c) under the joint deterministic mapping and taxonomic assumptions”;
* state the scale mismatch in every relevant figure and caption;
* avoid calling genus counts species-diversity lower bounds unless a defensible mapping is provided;
* designate the current mammal section as a synthetic or stylised sensitivity example.

A stronger empirical extension would specify a fossil preservation/detection model and a stochastic relationship between fossil counts and latent richness. That extension is not necessary for an Evidence Press theorem candidate if the biological claims are narrowed accordingly.

---

### 4. The turnover cap is a strong biological restriction and must be made prominent

**Classification:** Major

**Issue**

The most attractive closed-form results assume

[
0\leq\varepsilon(t)=\frac{\mu(t)}{\lambda(t)}\leq c\leq1.
]

Thus (\mu(t)\leq\lambda(t)) at every non-event time: instantaneous net diversification is never negative. The manuscript treats (c) primarily as a regularity cap, but it is also a substantive restriction excluding continuously declining intervals.

**Manuscript evidence**

The assumption enters before Theorem 4 and drives Theorems 4–5 and Corollaries 6–7. The mammal analysis focuses on values such as (c=0.5), (0.94) and (0.95). Interior mass-extinction atoms are discussed separately, but the sharp turnover-capped envelopes are derived for the no-atom continuous class.

**Why it matters**

The factor-of-(1/(1-c)) guarantee is compelling partly because the assumption is strong. It diverges as (c\to1), and the same global bound does not continue beyond (c=1). For (c>1), (q'(x)=1-\varepsilon(x)) can be negative and positivity of (q) is no longer automatic from the anchor alone. A reader could otherwise mistake the theorem for a general result about biologically plausible turnover rather than a sharp theorem for non-negative instantaneous net diversification plus separately represented catastrophic events.

**Required revision or decisive test**

* Put (c\leq1), its biological meaning and the no-continuous-decline implication in the abstract.
* Repeat the restriction in the captions of all turnover-bound figures.
* Distinguish routine extinction turnover from deterministic extinction atoms.
* State exactly which parts of Theorem 5 remain formal Lipschitz statements when (c>1), and which fail because of the positivity barrier.
* Add sensitivity at (c=1) and explain why no finite global multiplicative width remains.
* Discuss whether short negative-net-diversification episodes can be approximated by event atoms and what is lost under that approximation.

An extension to (c>1) would be valuable but is not mandatory. Transparent limitation is mandatory.

---

### 5. The novelty claim needs proposition-level comparison with existing congruence-class methods

**Classification:** Major

**Issue**

The manuscript’s novelty section identifies nearby work but does not yet demonstrate, theorem by theorem, which results are genuinely new rather than reformulations of existing pulled-rate, reconstructed-process or monotone-extension arguments.

**Manuscript evidence**

The novelty gate correctly notes prior collisions for the integrating-factor idea, pulled scale, event concepts and generic Lipschitz constructions. It reports no exact antecedent for the complete measure fibre, sharp constraint envelopes, finite certificate and minimum turnover cap. It also acknowledges that the search was targeted rather than exhaustive and calls for a domain expert.

**Why it matters**

Existing methods already:

* describe congruence classes generated by a common pulled signal;
* construct alternative histories in those classes;
* sample flexible or parsimonious congruent trajectories;
* ask which historical patterns are common across congruent models;
* obtain identifiability under piecewise-constant or piecewise-polynomial restrictions.

CRABS and the Andréoletti–Morlon method are especially close computational comparators, while Legried and Terhorst are close conceptual comparators for restriction-based recovery. ([British Ecological Society Journals][5])

The candidate’s distinction appears to be **exact projection and certification rather than sampling or point identification**, but that distinction should be demonstrated rather than asserted.

**Required revision or decisive test**

Add a comparison table with rows corresponding to each theorem or corollary and columns for:

* Louca–Pennell;
* Helmstetter et al.;
* CRABS;
* Andréoletti–Morlon;
* Kopperud–Magee–Höhna;
* Legried–Terhorst;
* relevant reconstructed-process/event results;
* the present candidate.

For each row, state whether the contribution is antecedent, reformulation, extension, exact sharpening or new synthesis.

Also run a matched example in which:

1. CRABS or another sampling method explores the same congruence class and restrictions;
2. the candidate computes its exact extremal band and certificate;
3. the paper shows what sampling misses, approximates or confirms;
4. computation time and dependence on tuning or sample size are reported.

The paper should avoid claiming novelty for the generic integrating factor or generic Lipschitz envelope separately. The defensible novelty claim is their specific coupling to this birth–death fibre and the resulting closed-form biological compatibility diagnostics.

---

### 6. “Complete identified set” and “all histories” sometimes exceed what the theorems establish

**Classification:** Major

**Issue**

The manuscript characterises a complete functional fibre under stated assumptions and computes sharp pointwise extrema. It does not follow that every curve lying visually inside the pointwise shaded band is feasible, or that arbitrary nonlinear functionals of the history have been sharply bounded.

**Manuscript evidence**

Figure 1 shades the region between least and greatest feasible envelopes. The conclusion refers broadly to “all histories”, “complete identified sets” and replacement of sampled histories by exact answers. Elsewhere, histories are called “equally likely”.

**Why it matters**

Three objects need to be distinguished:

1. the **functional identified set** of cumulative-loss trajectories satisfying monotonicity, slope and interval restrictions;
2. the **pointwise projection** of that set at each time;
3. the feasible range of a particular **nonlinear functional**, such as a maximum rate, integral, event count or time of peak diversification.

Every feasible function lies between the extremal envelopes, but an arbitrary function drawn between the two boundaries need not satisfy the cross-time constraints. Likewise, likelihood equivalence does not imply equal posterior probability: priors and parametrisation can assign different posterior mass along a likelihood ridge.

**Required revision or decisive test**

* Define “identified set” once and distinguish the full trajectory set from its pointwise projection.
* Amend Figure 1’s caption so that the shaded band is not read as a set of freely selectable pointwise values.
* Replace “equally likely” with “likelihood-equivalent under the stated conditioning”.
* Qualify “all histories” by the exact model, regularity, conditioning and event assumptions.
* Say that the current results sharply solve pointwise evaluation and the displayed compatibility problems, not arbitrary target optimisation.
* List classes of other targets for which the least/greatest envelopes do provide immediate extrema, and targets requiring a separate optimisation problem.

---

### 7. The evidence package is internally coherent but does not yet meet Evidence Press’s stated release contract

**Classification:** Major for release readiness; not a defect in the mathematical theorem itself

**Issue**

The candidate includes substantial assurance material, but several items described by Evidence Press as standard for every release are not present or are not represented under the expected machine-readable conventions.

**Manuscript/package evidence**

Positive findings include:

* a correct archive-level checksum;
* a complete file manifest with all hashes verified;
* passing unit tests and demonstration;
* reproducible numerical outputs and figures;
* explicit internal theorem, adversarial, novelty and empirical-limit notes;
* an honest `publication_ready: false` status and named open gates.

However, the package does not include evidence of deliberately mutated negative controls, an independent implementation, a fully pinned environment, or the standard `AI_INDEX`, `STATUS`, `ASSURANCE`, `PROVENANCE` and `SOURCES` artefacts. `verification_report.json` reports “PASS” without making sufficiently prominent that this means internal software replay, not independent mathematical or biological validation. The `CITATION.cff` describes the object as software under MIT, while the package actually contains code under MIT and manuscript/documents under CC BY 4.0. That mixed licence is workable, but the top-level citation metadata does not represent it accurately. Evidence Press currently describes a release architecture containing explicit claim-to-evidence mappings, assurance states, pinned environments, mutation controls and Zenodo/GitHub archival copies. ([Evidence Press][1])

**Why it matters**

The core proposition of Evidence Press is not that internal checks establish truth, but that every assurance boundary is explicit and machine-readable. A broad green “PASS” can undermine that principle if a reader interprets it as specialist verification. Missing negative controls also leave open whether the acceptance tests genuinely fail when the implementation or expected result is deliberately corrupted.

**Required revision or decisive test**

Before release:

* add a claim-to-evidence index mapping every headline claim to theorem, test, output and assurance state;
* provide a complete assurance matrix using `passed`, `partial`, `failed`, `not assessed` and `not applicable`;
* separate “internal replay passed” from “theorem externally reviewed: not assessed” and “empirical bridge validated: not assessed”;
* include at least one deliberately mutated theorem implementation or expected output that the replay correctly rejects;
* add substantive negative and boundary controls;
* supply a pinned lockfile or container recipe and record the interpreter/platform used;
* harmonise `CITATION.cff`, licence files and the intended Evidence Press reuse policy;
* add explicit AI and human-role provenance;
* create the immutable Zenodo deposit, concept/version DOI and public repository mirror at release;
* validate all machine-readable records against the Evidence Press schema.

## 5. Rigour, results and inference

### 5.1 Independent mathematical and computational audit

| Component           | Independent check                                                          | Assessment                                                                 |
| ------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Archive integrity   | Companion checksum; 38 manifest hashes; missing/extra-file comparison      | **Pass**                                                                   |
| Executable replay   | All eight unit tests; demonstration script; output and figure regeneration | **Pass**                                                                   |
| Theorem 1           | Forward and inverse substitutions; positivity conditions; measure density  | **Pass**                                                                   |
| Proposition 2       | Deterministic survival jump and atom interpretation                        | **Pass algebraically**                                                     |
| Theorem 3           | Differential invariant and event-ratio check                               | **Provisional pass; full conditioning audit outstanding**                  |
| Theorem 4           | Integration of (q'=1-\varepsilon) under (0\leq\varepsilon\leq c)           | **Pass**                                                                   |
| Theorem 5           | Pairwise necessity; constructive sufficiency; extremal envelopes           | **Pass**                                                                   |
| Corollary 6         | Minimum compatible cap from maximal positive slope requirement             | **Pass**                                                                   |
| Corollary 7         | Back-propagation of a lower diversity constraint                           | **Pass algebraically, interpretation unresolved**                          |
| Proposition 8       | Set-inclusion/coverage-transfer logic                                      | **Pass as a conditional lemma; no operational band supplied**              |
| Mammal illustration | Numerical replay from packaged extracted data                              | **Pass as computation; not an independently validated empirical analysis** |

### 5.2 Fibre parametrisation

For the smooth class, the manuscript defines survival (u=1-E), the pulled rate (\lambda_p=\lambda u), the integrating factor

[
F(\tau)=\exp!\left(\int_0^\tau \lambda_p(s),ds\right),
]

and cumulative loss

[
A=F(1-u).
]

Substituting the proposed inverse relations,

[
u=\frac{F-A}{F}, \qquad
\lambda=\frac{\lambda_pF}{F-A}, \qquad
\mu=\frac{A'}{F-A},
]

recovers (\lambda_p=\lambda u) and the manuscript’s survival equation. The conditions (A'\geq0) and (A<F) give non-negative extinction and positive survival. The absolutely continuous measure identity

[
\frac{d\nu_{\mathrm{ac}}}{dF}=\frac{\mu}{\lambda}
]

also follows directly. I found no algebraic discrepancy in Theorem 1.

The fibre is correctly described as convex under addition of admissible cumulative-loss measures below the moving barrier, but not as a cone because arbitrary positive scaling can violate (A<F). The pointwise minimum and maximum of admissible cumulative functions retain monotonicity and the barrier, supporting the lattice description.

### 5.3 Atom completion

The Stieltjes formulation and deterministic survival jump are internally consistent. Under a survival fraction (s), the surviving-lineage quantity (q=F-A) changes by the corresponding factor, giving the manuscript’s (q_+=s q_-) convention. The atom then represents a deterministic discontinuity in lineage survival rather than an ordinary integrable extinction hazard.

Two qualifications should be added:

* a singular measure-valued loss process is a mathematical completion of the fibre, not automatically a standard birth–death model with an ordinary instantaneous rate;
* the continuous turnover ratio (\mu/\lambda) is not defined at an atom, so event restrictions and continuous turnover restrictions must remain separate.

### 5.4 Turnover envelopes

With (x=F), (q=F-A) and (\varepsilon=\mu/\lambda), the manuscript obtains

[
\frac{dq}{dx}=1-\varepsilon.
]

Under (0\leq\varepsilon\leq c),

[
1-c\leq q'(x)\leq1.
]

Integrating from the present-day anchor (q(1)=\rho) yields

[
\rho+(1-c)(x-1)
\leq q(x)
\leq \rho+x-1.
]

Because

[
\lambda=\frac{\lambda_pF}{q},
]

the survival and speciation envelopes follow with the appropriate reversed ordering. For (c<1), the ratio of extremal speciation rates is uniformly bounded by (1/(1-c)). The endpoint trajectories correspond to (\varepsilon=0) and (\varepsilon=c), so the bounds are attained. I found this derivation correct.

The theorem should make explicit that “sharp” means sharp over the specified functional class, not sharp over all biologically conceivable histories.

### 5.5 Finite constraint certificate

For interval constraints

[
L_i\leq n(x_i)\leq U_i
]

on a non-decreasing (c)-Lipschitz cumulative loss (n), the manuscript’s pairwise condition

[
L_i\leq U_j+c(x_i-x_j)_+
\quad\text{for all }i,j
]

is necessary: a feasible (n) must satisfy (n(x_i)\leq n(x_j)+c(x_i-x_j)) when (x_i\geq x_j), while monotonicity handles the opposite order.

The least and greatest envelope constructions supply sufficiency. They also produce a finite violating pair when infeasible, which is useful as an interpretable certificate rather than merely a solver failure. I independently recovered the same condition and extremal formulas.

Corollary 6’s minimum cap is correspondingly the largest required positive slope between a lower constraint and an earlier upper constraint, subject to the anchor and admissibility conditions. No inconsistency was found.

### 5.6 Numerical reproduction

The packaged illustration reproduced exactly. Under the package’s shifted time convention, the selected age 58.5 Ma corresponds to (\tau=57.5), with:

[
\lambda_p=0.0438809486,\qquad
F=119.7090495,\qquad
M_0=4790,\qquad
\rho=1.
]

At (c=0.5), the no-fossil speciation interval is:

[
[0.0438809486,;0.0870348440],
]

with multiplicative width (1.9834312), below the theoretical factor of two.

With the lower bound labelled (D=44), the interval becomes:

[
[0.0482525371,;0.0870348440],
]

with width (1.8037361).

The (D=398) and (D=577) constraints are infeasible under (c=0.5). The reproduced minimum compatible caps are:

[
c_{\min}(44)=0.0913613,
]
[
c_{\min}(398)=0.9070402,
]
[
c_{\min}(577)=0.9384920.
]

For (D=577) and (c=0.94), the reproduced interval is:

[
[0.6327662247,;0.6467120786],
]

with width (1.0220395). At (c=0.95), the reported width (1.1969745) also reproduces. The apparently larger width at the looser cap is mathematically possible because the constraint binds differently across the feasible set; the manuscript should explain this explicitly to prevent it being mistaken for an error.

The reported maximum minimum-cap diagnostics across bins also reproduce:

* lineage-through-time: (0.8779657) at 43.5;
* boundary-crossing diversity: (0.9237992) at 48.5;
* sampled-in-bin and range-through diversity: (0.9538579) at 48.5.

I found no disagreement among the manuscript text, generated JSON/CSV outputs and plotted values.

### 5.7 Software assurance

All eight included unit tests pass in a clean copy of the extracted package. The demonstration completes, and all four figures regenerate byte-for-byte identically to the packaged outputs. The 20,000 generated histories satisfy the coded constraints and provide a useful numerical sanity check.

These tests are helpful but comparatively narrow. They do not independently prove the mathematics because the implementation and expected values share the same conceptual source. Particular gaps include:

* only limited randomised linear-programme comparison;
* no property-based testing over large families of feasible and infeasible constraints;
* no mutation tests;
* no independent implementation of the envelope algorithm;
* few tests of duplicate or unsorted ages;
* limited boundary coverage at (c=0), (c=1), (c_{\min}=1) and (c_{\min}>1);
* no adversarial tests of strict positivity of (F-A);
* no chains of multiple deterministic events;
* insufficient input validation in some public functions.

For example, `cumulative_loss_from_turnover` checks non-negativity but does not itself enforce the paper’s upper turnover cap or barrier; the envelope functions do not uniformly validate domain ordering, anchors and barrier conditions; and a computed (c_{\min}>1) is returned without an explicit warning that it lies outside the paper’s restricted class. These are repairable release-engineering issues.

### 5.8 Results and inference

The paper is strongest when it says:

* the likelihood does not identify a unique history;
* a structural restriction defines a conditional fibre;
* external inequalities cut that fibre;
* exact extrema and incompatibility certificates can be calculated.

It is weakest when it moves from that logic to statements about what mammalian diversity “must have been”. The calculations directly establish compatibility or incompatibility among mathematical constraints. Biological conclusions additionally depend on:

* the adequacy of the homogeneous birth–death model;
* correctness of the pulled trajectory;
* the time and sampling convention;
* the interpretation of deterministic lineage quantities;
* fossil preservation and taxonomic mapping;
* absence or treatment of continuous decline and unmodelled extinction events.

The limitations section mentions several of these, but they should be integrated into each result rather than concentrated after the fact.

I found no evidence of p-hacking or selective statistical reporting. The single-tree and selected-age choices could create sensitivity, but the manuscript explicitly treats the example as illustrative. They should therefore be described as analytic choices requiring robustness checks, not as misconduct indicators.

## 6. External literature check

### Search record

**Review date:** 6 August 2026.

**Sources used:** publisher and DOI pages; PubMed and PubMed Central; arXiv and bioRxiv; CRAN and software documentation; official Evidence Press pages; official REF 2029 and REF 2021 guidance; targeted general web search for exact theorem phrases and mathematical formulations.

**Representative search strings:**

* `"pulled speciation rate" affine measure birth death`
* `"birth-death congruence class" sharp bounds turnover`
* `"congruent diversification histories" sampling`
* `"cumulative loss measure" diversification`
* `"time-dependent fossilized birth-death" identifiability`
* `"hidden birth events" identifiability`
* `"mass extinction" reconstructed birth death conditioning`
* exact-title and exact-formula searches for the manuscript’s certificate and minimum-cap claims.

**Inclusion logic:** recent work from approximately 2021–2026 was prioritised, while retaining landmark papers on congruence, reconstructed processes and event sampling. Primary research, original software papers and official guidance were preferred over reviews and derivative summaries.

**Full-text limits:** openly available full text was inspected for Helmstetter et al., Truman et al., the Andréoletti–Morlon repository copy and the 2026 Dieselhorst–Stadler preprint. For several paywalled papers, including parts of the Louca–Pennell, CRABS, Kopperud–Magee–Höhna and older reconstructed-process literature, the review relied on publisher abstracts, metadata and accessible summaries rather than a line-by-line full-text audit. The search was not exhaustive across subscription bibliographic databases or non-English literature.

### Pivotal publications and direct implications

#### Louca and Pennell: the foundational non-identifiability result

Louca and Pennell showed that a given extant timetree likelihood can be consistent with infinitely many time-varying speciation and extinction histories sharing appropriate pulled quantities. The present candidate takes that congruence problem as its starting point rather than overturning it. ([Nature][2])

**Implication:** the basic fibre is not novel. The candidate’s contribution must lie in its coordinate choice, event completion and exact constrained geometry.

#### Helmstetter et al.: interpretation and expected lineage trajectories

Helmstetter et al. clarified pulled-rate concepts, lineage-through-time interpretation and the consequences of congruence. Their treatment is directly relevant to the distinction between deterministic expected trajectories and stochastic realised histories. ([OUP Academic][4])

**Implication:** the manuscript should cite this work in the palaeontological derivation, not only in the general congruence discussion.

#### CRABS and Andréoletti–Morlon: exploration of congruent histories

CRABS provides transformations and summaries across congruent rate scenarios. Andréoletti and Morlon introduced a flexible and parsimonious method for exploring such histories. ([British Ecological Society Journals][5])

**Implication:** the candidate’s “exact envelopes rather than sampled clouds” positioning is plausible, but requires a matched demonstration. It should not imply that previous methods ignored the structure or common features of congruence classes.

#### Kopperud, Magee and Höhna: shared patterns despite non-identifiability

This work argues that rapidly varying or qualitative diversification patterns may remain inferable across congruent models, despite parameter non-identifiability. ([DOI][6])

**Implication:** the manuscript should distinguish exact partial identification of numerical rates from robustness of qualitative historical patterns. The two approaches are complementary rather than mutually exclusive.

#### Legried and Terhorst: identifiability under restricted function classes

Legried and Terhorst established identifiable classes of phylogenetic birth–death models and subsequently studied broader piecewise-polynomial formulations and inference. ([Terhorst lab][7])

**Implication:** imposing restrictions need not only narrow a partial-identification set; sufficiently strong parametric or structural restrictions can restore point identification. The paper should explain why its turnover cap is preferable for the decision problem at hand.

#### Truman et al. and Dieselhorst–Stadler: richer observations restore identifiability

Truman et al. show identifiability for widely used time-dependent fossilised birth–death models under the specified sampling structure. The 2026 Dieselhorst–Stadler preprint argues that information on hidden birth events can restore identifiability even for broad time-dependent models. ([OUP Academic][8])

**Implication:** the candidate should present external fossil constraints as one route among several. Directly modelling fossils or birth-event information may change the problem from partial to point identification rather than merely intersecting the extant-tree fibre.

#### Event-aware reconstructed processes

Lambert and Stadler, and Höhna, developed reconstructed-process treatments involving sampling, bottlenecks, mass extinction and conditioning. ([PubMed][3])

**Implication:** the atom theorem should be positioned as an affine-coordinate reformulation or extension relative to this process literature, with an exact account of what likelihood result is inherited and what is newly proved.

### Overall literature judgement

The literature strongly supports the importance of the problem and the value of reporting what is and is not identified. It also prevents a broad novelty claim for birth–death congruence, pulled coordinates, alternative-history construction or event-aware reconstructed processes.

My targeted searches did **not** locate an exact antecedent combining:

1. a positive cumulative-loss Stieltjes measure as the fibre coordinate;
2. the stated order/lattice geometry;
3. turnover-capped sharp pointwise envelopes;
4. the finite pairwise interval certificate;
5. a closed-form minimum compatible turnover cap;
6. deterministic fossil-like constraints expressed in this coordinate.

That combination is therefore plausibly original. Confidence is moderate rather than high because terminology may differ across probability, optimal transport, viability, monotone regression and population-process literature.

## 7. Minor comments

1. **Title.** “Sharp partial identification” is defensible, but the abstract should say immediately that the principal sets are conditional on a fixed pulled signal. “Conditional sharp partial identification” would be more exact.

2. **Abstract.** State that the global turnover results assume no continuous period with (\mu>\lambda), except for separately represented deterministic events.

3. **Time convention.** The coexistence of geological age, (\tau), and the artificial 1 Ma origin is easy to misread. Add a small timeline diagram or a one-row conversion table.

4. **Notation.** Supply a consolidated table for (E,u,F,A,\nu,q,n,\lambda_p,\varepsilon,c,\rho,M,N). In particular, explain when (A) and (n) are interchangeable.

5. **Left/right limits.** Use one convention consistently for (q_-,q_+), event age and whether the event acts before or after ordinary evolution at that coordinate.

6. **“Equally likely.”** Replace throughout with “equal likelihood under the stated reconstructed-tree model and conditioning”. Posterior equality does not follow.

7. **Figure 1.** State that the shaded region is the pointwise projection between extremal feasible functions, not that every curve contained in the shading is feasible.

8. **Mammal figures.** Put “single-tree plug-in sensitivity; no uncertainty or fossil observation model” directly in each caption.

9. **Figure accessibility.** Add machine-readable tabular data for every plotted series and descriptive alt text. The PDF figures are visually legible, but the inference should not depend on colour alone.

10. **PDF metadata.** Populate title, author/agent attribution, version, licence, DOI placeholder and keywords. The current PDF metadata lacks a title and author.

11. **Source rendering.** Repair the residual Markdown citation placeholders and incomplete rendered phrase noted in the source version, even though the PDF is largely clean.

12. **Theorem audit.** Align theorem numbering and names exactly with the release manuscript so that claim-to-proof links remain stable after editing.

13. **Verification language.** Rename generic `PASS` statuses to scoped phrases such as `internal_software_replay: passed`.

14. **Dependencies.** Replace lower-bound-only dependencies such as `numpy>=2.0` with a tested lock or exact environment record.

15. **Input validation.** Reject or explicitly handle non-increasing (x), duplicate conflicting intervals, non-finite values, invalid anchors, barrier violations and (c_{\min}>1).

16. **Licensing and citation.** Represent the manuscript, data, figures and code as distinct components in `CITATION.cff` or an RO-Crate record rather than describing the whole deposit as MIT-licensed software.

17. **Reference scope.** Add the recent FBD and hidden-birth-event identifiability results to prevent the impression that external information can only narrow, rather than sometimes eliminate, congruence.

18. **Conclusion.** Replace “what replaces rate estimation” with “what complements or bounds rate estimation under non-identifiability”. Restricted and enriched-data models can still support estimation.

## 8. Prioritised revision plan

### Must fix before the claims are publishable

1. **Secure Theorem 3.** Supply the full finite-atom, stem-conditioned likelihood derivation and fixed-tip-count normalisation, with exact event conventions. Keep crown/origin cases out of the claim unless derived.

2. **Separate conditional geometry from inference.** Either provide a simultaneous pulled-signal uncertainty procedure or consistently label all numerical sets as conditional plug-in sensitivity results.

3. **Correct the palaeontological interpretation.** Define (N) probabilistically, distinguish expected/model-implied from realised diversity, remove genus-to-species hard-bound language unless justified, and phrase incompatibility as conditional on all bridge assumptions.

4. **State the turnover restriction prominently.** Explain that (c\leq1) excludes continuous negative net diversification and that the no-atom sharp bounds do not encompass arbitrary extinction histories.

5. **Narrow and substantiate originality.** Add a proposition-level comparison with CRABS, Andréoletti–Morlon, Legried–Terhorst and event-aware reconstructed-process work.

6. **Correct identified-set language.** Distinguish the functional set, pointwise band and target-specific optimisation; replace “equally likely” with “likelihood-equivalent”.

7. **Complete the Evidence Press assurance architecture.** Add scoped status/assurance/provenance/source records, claim-to-evidence mapping, negative and mutation controls, a pinned environment and consistent licensing metadata.

### Should fix to strengthen the paper

1. Run a matched CRABS or alternative-history comparison showing how the exact envelope relates to a finite sampled cloud.

2. Add property-based tests and an independently written reference implementation of the pairwise certificate.

3. Include sensitivity at (c=1), multiple deterministic events and modest perturbations of fossil ages and bounds.

4. Add a clear statement of which numerical results depend on the chosen mammal tree and shifted origin.

5. Report computational complexity for envelope construction, certificate extraction and uncertainty-set unions.

6. Provide tables behind all figures and improve metadata, accessibility and source/PDF consistency.

### Could improve presentation or future work

1. Extend the conditioning audit to crown and origin conditioning.

2. Characterise the fibre for (c>1) with an explicit positivity barrier.

3. Construct simultaneous bands for (F) and propagate them computationally.

4. Introduce a stochastic fossil observation model and taxonomic-scale mapping.

5. Repeat the illustration across the full mammal-tree posterior.

6. Investigate exact bounds for nonlinear targets such as integrated extinction, peak timing and cumulative event loss.

7. Formalise Theorems 1, 4 and 5 in a proof assistant; these appear more tractable than the full stochastic-process likelihood theorem.

## 9. Editorial recommendation

### Recommendation: **Major revisions**

**Confidence:** 0.88.

The smooth affine fibre, turnover envelopes and finite feasibility certificate appear mathematically sound and computationally reproducible. No fatal defect was found in that core. The candidate therefore warrants revision rather than rejection.

It should not be released in its present form because three statements remain capable of materially changing a reader’s conclusion:

1. whether the finite-atom congruence theorem has the claimed full conditioned-likelihood scope;
2. whether the fossil constraints refer to a defensible biological quantity;
3. whether the numerical sets are conditional sensitivity sets or uncertainty-calibrated inferential results.

The current package also falls short of Evidence Press’s own assurance conventions despite being stronger than a typical unsupported preprint.

The following findings would change the decision:

* **Towards rejection or substantial narrowing:** a specialist audit finds an uncancelled atom- or conditioning-dependent factor in Theorem 3; or a clear prior publication contains the same measure representation and sharp certificate.
* **Towards minor revision or release:** the conditioning proof is independently confirmed; the empirical section is explicitly reclassified as stylised conditional sensitivity or supplied with an observation model; the novelty comparison is completed; and the assurance package is brought into conformance with the press’s status contract.

The recommended editorial route is therefore: retain the theorem-led paper, narrow its biological claims, strengthen the load-bearing stochastic-process derivation, and release only after the assurance boundary is machine-readable and unambiguous.

## 10. Provisional REF calibration

REF 2029 retains Unit 5, Biological Sciences, and Unit 10, Mathematical Sciences, within its 34-Unit structure. The present output is best calibrated primarily under Unit 5 because the research question, application and intended intervention concern macroevolutionary inference, although mathematical assessors would be useful. ([REF 2029][9])

As of 6 August 2026, final REF 2029 panel guidance and criteria were still scheduled for publication in autumn 2026. I therefore use the current REF 2029 requirement to recognise rigorous, significant and original research, together with the REF 2021 generic starred definitions and the supplied 12-point high/medium/low rubric. ([REF 2029][10])

| Dimension                  | Provisional rating | Rationale                                                                                                                                                                                                                                                                                   | Confidence |
| -------------------------- | -----------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------: |
| **Originality**            |  **3* Low — 7/12** | The exact combination of cumulative-loss measure geometry, sharp envelopes and finite certificates appears novel from the targeted search. Several ingredients and the general congruence problem are established prior art, and priority has not yet received an external domain audit.    |       0.65 |
| **Significance**           |  **3* Low — 7/12** | Exact conditional bounds and interpretable infeasibility witnesses could improve practice relative to finite sampling of congruent histories. Present significance is limited by the absence of a matched comparison, calibrated uncertainty and a defensible empirical observation bridge. |       0.62 |
| **Rigour**                 |  **3* Low — 7/12** | The central smooth and turnover-capped mathematics reproduces, numerical outputs are consistent and the artefact package is unusually strong. The finite-atom conditioning proof, biological semantics and release-level negative controls remain material gaps.                            |       0.74 |
| **Overall output quality** |  **3* Low — 7/12** | Holistically, the work is at the lower boundary of internationally excellent: it contains a credible, non-trivial theorem contribution with strong executable support, but falls short of 4* because novelty, stochastic-process scope and empirical interpretation are not yet secured.    |       0.66 |

This overall grade is **holistic, not an arithmetic average**. A finding that Theorem 3 is materially incomplete would move the output towards **2* High, 6/12**, unless the claim were cleanly narrowed to the smooth theory. Conversely, a positive specialist audit, a convincing matched-method comparison and corrected empirical framing could support **3* Medium or High**. I see insufficient evidence at present for a world-leading 4* judgement.

This is an **indicative reviewer calibration, not an official REF panel decision**.

## 11. References

### Diversification congruence, identifiability and partial information

Andréoletti, J., & Morlon, H. (2023). Exploring congruent diversification histories with flexibility and parsimony. *Methods in Ecology and Evolution, 14*(12), 2931–2941. [https://doi.org/10.1111/2041-210X.14240](https://doi.org/10.1111/2041-210X.14240)

Dieselhorst, T., & Stadler, T. (2026). *Information on hidden birth events restores identifiability in phylodynamic inference* [Preprint]. arXiv. [https://doi.org/10.48550/arXiv.2604.17926](https://doi.org/10.48550/arXiv.2604.17926)

Helmstetter, A. J., Glémin, S., Käfer, J., Zenil-Ferguson, R., Sauquet, H., de Boer, H., Dagallier, L.-P. M. J., Mazet, N., Reboud, E. L., Couvreur, T. L. P., & Condamine, F. L. (2022). Pulled diversification rates, lineages-through-time plots, and modern macroevolutionary modeling. *Systematic Biology, 71*(3), 758–773. [https://doi.org/10.1093/sysbio/syab083](https://doi.org/10.1093/sysbio/syab083)

Höhna, S., Kopperud, B. T., & Magee, A. F. (2022). CRABS: Congruent rate analyses in birth–death scenarios. *Methods in Ecology and Evolution, 13*(12), 2709–2718. [https://doi.org/10.1111/2041-210X.13997](https://doi.org/10.1111/2041-210X.13997)

Kopperud, B. T., Magee, A. F., & Höhna, S. (2023). Rapidly changing speciation and extinction rates can be inferred in spite of nonidentifiability. *Proceedings of the National Academy of Sciences, 120*(7), e2208851120. [https://doi.org/10.1073/pnas.2208851120](https://doi.org/10.1073/pnas.2208851120)

Legried, B., & Terhorst, J. (2022). A class of identifiable phylogenetic birth–death models. *Proceedings of the National Academy of Sciences, 119*, e2119513119. [https://doi.org/10.1073/pnas.2119513119](https://doi.org/10.1073/pnas.2119513119)

Legried, B., & Terhorst, J. (2023). Identifiability and inference of phylogenetic birth–death models. *Journal of Theoretical Biology, 568*, 111520. [https://doi.org/10.1016/j.jtbi.2023.111520](https://doi.org/10.1016/j.jtbi.2023.111520)

Louca, S., & Pennell, M. W. (2020). Extant timetrees are consistent with a myriad of diversification histories. *Nature, 580*, 502–505. [https://doi.org/10.1038/s41586-020-2176-1](https://doi.org/10.1038/s41586-020-2176-1)

Truman, K., Vaughan, T. G., Gavryushkin, A., & Gavryushkina, A. S. (2025). The fossilized birth–death model is identifiable. *Systematic Biology, 74*(1), 112–123. [https://doi.org/10.1093/sysbio/syae058](https://doi.org/10.1093/sysbio/syae058)

### Reconstructed processes, sampling and extinction events

Höhna, S. (2015). The time-dependent reconstructed evolutionary process with a key-role for mass-extinction events. *Journal of Theoretical Biology, 380*, 321–331. [https://doi.org/10.1016/j.jtbi.2015.06.005](https://doi.org/10.1016/j.jtbi.2015.06.005)

Lambert, A., & Stadler, T. (2013). Birth–death models and coalescent point processes: The shape and probability of reconstructed phylogenies. *Theoretical Population Biology, 90*, 113–128. [https://doi.org/10.1016/j.tpb.2013.10.002](https://doi.org/10.1016/j.tpb.2013.10.002)

### Mammal diversification source

Upham, N. S., Esselstyn, J. A., & Jetz, W. (2021). Molecules and fossils tell distinct yet complementary stories of mammal diversification. *Current Biology, 31*(19), 4195–4206.e3. [https://doi.org/10.1016/j.cub.2021.07.012](https://doi.org/10.1016/j.cub.2021.07.012)

### Evidence Press and research-assessment standards

Evidence Press. (2026). *About this site*. [https://evidence-press.pages.dev/about/](https://evidence-press.pages.dev/about/)

Evidence Press. (2026). *For AI agents and automated research tools*. [https://evidence-press.pages.dev/ai/](https://evidence-press.pages.dev/ai/)

Research Excellence Framework. (2019). *Panel criteria and working methods: REF 2019/02*. [https://2021.ref.ac.uk/publications-and-reports/panel-criteria-and-working-methods-201902/](https://2021.ref.ac.uk/publications-and-reports/panel-criteria-and-working-methods-201902/)

Research Excellence Framework. (2025). *Contributions to Knowledge and Understanding guidance*. [https://2029.ref.ac.uk/guidance/section-4-contributions-to-knowledge-and-understanding-cku-guidance/](https://2029.ref.ac.uk/guidance/section-4-contributions-to-knowledge-and-understanding-cku-guidance/)

Research Excellence Framework. (2026). *Units of assessment*. [https://2029.ref.ac.uk/panels/units-of-assessment/](https://2029.ref.ac.uk/panels/units-of-assessment/)

Research Excellence Framework. (2026, July 30). *REF 2029 launches sector survey on final policy developments*. [https://2029.ref.ac.uk/news/ref-2029-launches-sector-survey-on-final-policy-developments/](https://2029.ref.ac.uk/news/ref-2029-launches-sector-survey-on-final-policy-developments/)

**[END]**

[1]: https://evidence-press.pages.dev/about/ "About this site · Evidence Press"
[2]: https://www.nature.com/articles/s41586-020-2176-1 "https://www.nature.com/articles/s41586-020-2176-1"
[3]: https://pubmed.ncbi.nlm.nih.gov/26073724/ "https://pubmed.ncbi.nlm.nih.gov/26073724/"
[4]: https://academic.oup.com/sysbio/article/71/3/758/6382322?utm_source=chatgpt.com "Pulled Diversification Rates, Lineages-Through-Time Plots ..."
[5]: https://besjournals.onlinelibrary.wiley.com/doi/abs/10.1111/2041-210X.13997?utm_source=chatgpt.com "CRABS: Congruent rate analyses in birth–death scenarios"
[6]: https://doi.org/10.1073/pnas.2208851120?utm_source=chatgpt.com "Rapidly changing speciation and extinction rates can be ..."
[7]: https://jthlab.github.io/publications.html?utm_source=chatgpt.com "Publications"
[8]: https://academic.oup.com/sysbio/article/74/1/112/7831136?utm_source=chatgpt.com "Fossilized Birth–Death Model Is Identifiable | Systematic Biology"
[9]: https://2029.ref.ac.uk/panels/units-of-assessment/ "Units of assessment – REF 2029"
[10]: https://2029.ref.ac.uk/news/ref-2029-launches-sector-survey-on-final-policy-developments/ "REF 2029 launches sector survey on final policy developments – REF 2029"
