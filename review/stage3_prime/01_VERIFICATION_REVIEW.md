# Verification Review Report

## Decision

**Major Revision for journal-style scholarly acceptance.**

**Evidence Press disposition: eligible to proceed as an `unrefereed-candidate` with `PASS_WITH_NOTES`, after the release-boundary corrections in NEW-1 through NEW-3 and a passing Stage 4.5 integrity audit.**

This split is deliberate. The revised manuscript resolves the internal mathematical, statistical and benchmark-presentation defects that motivated Route A. It does not supply the unaffiliated process-theory review or unaffiliated reproduction required for ordinary acceptance. Evidence Press may publish that precise state, but must not represent it as acceptance, independent confirmation or a must-have CRABS complement.

## Revision Response Checklist

### Priority 1 — Required Revisions

| ID | Original review requirement | Author's claim | Response status | Revision location | Verified? | Quality assessment |
|---|---|---|---|---|---|---|
| R1 | Choose one route and enforce one claim hierarchy | Route A organizes the paper around a finite-sample signal-to-decision workflow | FULLY_ADDRESSED | Title, abstract, `Decision problem and contribution`, conclusion | Yes | The central contribution is legible; CRABS and the mammal illustration are explicitly supporting and bounded. |
| R2 | Repair Theorem 1 function spaces and regularity | The map now uses continuous rates and a `C^1` cumulative-loss path | FULLY_ADDRESSED | `Smooth affine fibre`, Theorem 1; `CLAIM_EVIDENCE.json` C2 | Yes | The revised codomain no longer asserts unjustified differentiability of the component rates. |
| R3 | Specify Theorem 4's probability object and obtain process-theory review | The law is narrowed to an explicit topology-marginal disjoint-union space; external review remains unavailable | PARTIALLY_ADDRESSED | `Fixed-stem tip-count and ordered-node-age law`; `03_EXTERNAL_PROCESS_REVIEW_REQUEST.md` | Partial | The statement is now convention-conscious and internally normalised, but the required unaffiliated conditioning review has not occurred. |
| R4 | Clarify event convention, measure subclasses, homogeneity and cap biology | Applicability and cap-interpretation maps added | FULLY_ADDRESSED | Measure-completion, applicability and cap tables | Yes | The exclusions for lineage/state/trait/clade/diversity dependence and pointwise interpretation are prominent. |
| R5 | Separate returned deficits, structural censors and amendment timing | Reports 240/240 returned-cloud deficits plus 60 structural censors and a dated chronology | FULLY_ADDRESSED | Protocol chronology; confirmatory results; H2 summary | Yes | The scientific H2 conclusion no longer depends on calling a censor a deficit. |
| R6 | Add H4 transition/dependence reporting and correct consistency language | Adds full transition matrix, strata and dependence boundary | FULLY_ADDRESSED | H4 table, Figure 8 and two source CSVs | Yes | The 532 changes are reconstructable as 502 withdrawals and 30 reversals; the 20% gate remains failed. |
| R7 | Build the Route A statistical bridge or narrow the paper | Exact count inversion and conditional DKW--Massart band are propagated into a confidence-containing fibre union and three-valued decision | FULLY_ADDRESSED | `Finite-sample fixed-stem uncertainty and robust decisions`, Theorem 14, Figure 9 | Yes | The count interval, conditional empirical-process band, Bonferroni step and monotone map to `F` are internally coherent. Scope exclusions are adequate. |
| R8 | Complete theorem-by-theorem recognition search | Structured search and antecedent classification supplied | FULLY_ADDRESSED | Recognition table; `docs/recognition_search_route_a_20260821.md`; source ledger | Yes | The paper avoids first/unique language and treats the coupling as a provisional synthesis. This remains a structured recognition search, not proof of priority. |
| R9 | Supply coherent successor packaging, rights and replay | Version coherence and a clean successor verifier are supplied; unaffiliated replay and rights sign-off remain open | PARTIALLY_ADDRESSED | README, CFF, status/assurance/licence maps and replay request | Partial | Internal packaging is coherent, but independent reproduction and independent rights review cannot be self-issued. |

### Priority 2 — Suggested Revisions

| ID | Original review requirement | Response status | Notes |
|---|---|---|---|
| S1 | Visual worked decision | FULLY_ADDRESSED | Figure 9 shows both robust incompatibility and a plug-in-compatible result becoming unresolved. |
| S2 | Separate reproducibility, repeatability and integrity | FULLY_ADDRESSED | Assurance records and prose keep the dimensions distinct. |
| S3 | Tested/not-tested CRABS matrix | FULLY_ADDRESSED | The comparison table and limitations bound the comparator. |
| S4 | Simplify main narrative | FULLY_ADDRESSED | Route A is the organizing spine. |
| S5 | Resource/runtime reporting | FULLY_ADDRESSED | The replay request records corpus size and a qualified chronology without presenting it as a benchmark. |
| S6 | Cache hygiene and public alt text | PARTIALLY_ADDRESSED | Candidate caches are excluded and source alt text exists; public-page exposure remains a release-authoring task. |

### Priority 3 — Release polish

No separate Priority 3 scientific item remains. Release metadata, accessibility and component licensing are handled by the Stage 4.5 and Evidence Press gates.

## New issues discovered during revision

| ID | Type | Location | Description and required action |
|---|---|---|---|
| NEW-1 | Reproducibility wording | `Computational assurance`; replay request; response letter | The manuscript says the complete current suite passes in a clean container, while the Route A replay request says Linux is untested. Until a current Linux run exists, narrow the manuscript to the actually recorded environment. If CI later supplies a passing Linux run, record the run URL and scope instead. |
| NEW-2 | Licence map | `LICENSE_MAP.json` and root licences | The default `**` CC0 entry includes original executable code. The Evidence Press successor contract requires original code to be MIT while prose/data remain CC0. Add a code-specific MIT exception and `LICENSE-CODE`; preserve GPL/NOASSERTION exceptions. |
| NEW-3 | Release status semantics | `STATUS.json`, `ASSURANCE.json`, `PUBLICATION_STATE.json` | Replace the pre-review publication block with the split decision: journal acceptance remains blocked, but an explicitly unrefereed Evidence Press candidate may proceed under the user's publication authority and `PASS_WITH_NOTES`. External assurance dimensions must remain `not_assessed` or `partial`. |

## Independent verification performed in this review

- Re-read the author response and every stable manuscript locator for R1--R9.
- Checked the fixed-stem geometric interval, conditional DKW--Massart argument, Bonferroni allocation and monotone transformation to the pulled scale.
- Confirmed the related primary literature supports conditioned reconstructed-process/node-depth factorisation, DKW--Massart concentration and confidence-region logic for set-identified models; this does not replace a specialist audit of the candidate's exact conventions.
- Ran `verification/verify_route_a_candidate.py` successfully in the qualified Python 3.13 environment.
- Ran all 21 unit tests under optimized Python successfully.
- Revalidated all 1,900 entries in the sealed Stage 2 ledger through the integrated verifier.
- Confirmed the frozen results: 240/240 returned-cloud H2 deficits plus 60 structural censors; H4 532/3,840 and failed; 20,000-replicate joint component coverage 0.96755 against nominal 0.95.

## Decision rationale

The scientific revision is no longer in the same state as the first-round Major Revision. Its central inferential gap has been filled for a sharply stated fixed-stem model, its conditional probability object has been narrowed, the negative H4 result controls the CRABS language, and the recognition claims are conservative. No new internal defect was found that invalidates the narrow theorem or frozen computations.

Ordinary acceptance is nevertheless unavailable because R3 and R9 included evidence that must come from outside the preparing workflow. Repeating internal checks cannot satisfy those conditions. For an Evidence Press candidate, the appropriate decision is therefore not to suppress the work, but to publish the exact assurance vector: strong producer-side replay and scoped formal argument, alongside absent independent rerun, absent specialist review, absent editorial peer review and a failed broad-utility gate.

## Residual issues

1. Obtain an unaffiliated reconstructed-process specialist report before upgrading the theorem's external-review dimension.
2. Obtain an unaffiliated clean replay before claiming independent reproduction.
3. Obtain independent rights advice before upgrading the internal component map to externally reviewed rights clearance.
4. Do not use must-have, essential, validated, independently verified, peer-reviewed or journal-accepted language.
