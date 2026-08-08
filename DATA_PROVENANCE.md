# Data provenance and licensing

## Upstream source

The mammal sensitivity illustration derives from the public repository:
https://github.com/n8upham/MamDiv-fossil-vs-timetree

That repository states that it contains data and code underlying Upham, Esselstyn and Jetz (2021) and declares GNU General Public License version 3. The present package does not relicense upstream values.

## Upstream objects used

- `PSR_5911species_NDexp_tree1_new.Rda`: one fitted pulled-speciation-rate object.
- `mamDivDyn_ON_pbdb_Mammalia_wPiresEtAl2018_binned1to131_wHiLow.csv`: fossil summary table.
- `scripts/getPulledSpeciation_100trees_forHPC.R`: inspected to establish the fitting grid and analysis origin.

## Included derivatives

- `data/mammalia_tree1_psr.csv` contains the numerical pulled-rate grid and deterministic sampled lineages-through-time curve extracted from one upstream R object. `F_from_dLTT` is computed as `M0/M(tau)`.
- `data/mammalia_fossil_excerpt.csv` contains selected columns and bins from the public fossil summary table; column names are simplified and numerical values retained.
- `data/PSR_tree1.Rda.sha256` records the upstream binary hash used during extraction.

The full upstream R object is not included. The upstream fit was not rerun in this release.

## Inferential boundary

The mammal section is a single-tree, fixed-signal, deterministic sensitivity illustration. The fossil summaries are not treated as validated species-richness observations. No preservation model, stochastic observation model, genus-to-species mapping or simultaneous pulled-signal uncertainty set is supplied. Incompatibility therefore means incompatibility of the mathematical restrictions and all bridge assumptions jointly.

## Verification records

- On 8 August 2026 the upstream R-data SHA-256 was independently fetched and matched `2af4ece2ffb13a0b9c852c906072bc585c97e8291d5c1915bb7178d027b114fc`.
- All 23 packaged pulled-signal rows were compared with the upstream `res_PSR` R object: ages matched exactly; maximum absolute differences were `1.39e-17` for PSR, `2.27e-13` for LTT and `1.14e-13` for F, consistent with decimal serialization.
- All 14 fossil-excerpt rows and seven mapped values per row matched the declared upstream CSV exactly.
- `outputs/mammalia_internal_replay.json` records scoped internal replay.
- `outputs/mammalia_worked_case.json` records the worked values.
- `PROVENANCE.json`, `SOURCES.json` and `LICENSE_MAP.json` record transformations, citations and reuse boundaries.

These checks establish faithful extraction, not correctness of the upstream fit or biological validity of the model bridge.
