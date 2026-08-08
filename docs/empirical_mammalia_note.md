# Mammal illustration: exact scope

The mammal section is a **single-tree, fixed-pulled-signal, deterministic sensitivity calculation**.

## Source and transformation

- Upstream source: Upham, Esselstyn and Jetz (2021) public data/code repository.
- One pulled-speciation R object was extracted upstream; this release contains a CSV derivative and the reported upstream object hash, not the original R object.
- The original workflow sliced the first 1 Ma from the tree. The release uses `tau = actual age - 1 Ma` and `M0 = 4,790` lineages at that artificial origin.

## What reproduces

At actual age 58.5 Ma:

- `lambda_p = 0.0438809485961 Myr^-1`;
- `F = 119.709049534`;
- under `c=0.5`, the no-external-bound interval is `[0.04388095, 0.08703484]`;
- the illustrative `D=44` mapping narrows it to `[0.04825254, 0.08703484]`;
- the illustrative `D=398` and `D=577` mappings require minimum caps `0.90704015` and `0.93849197`.

## What does not follow

The binned values are genus-level fossil summaries. They are not automatically hard lower bounds on a realised species trajectory. No model connects:

1. the deterministic model quantity to one realised historical richness path;
2. fossil preservation and collection to latent richness;
3. genera to species.

Accordingly, every incompatibility statement is conditional on the cap and all three bridges. The figures and manuscript captions repeat this boundary.
