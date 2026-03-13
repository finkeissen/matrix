# Problems Track: Identity & Dedup (v2)

## Principle
Never merge silently. Identity is expressed as relations and explicit deprecations.

## Outputs
- `relation/same_as` (exact duplicates)
- `relation/similar_to` (near duplicates; review)
- `relation/supersedes` (improved formulation)
- `deprecate` op only with replacement pointer

## Canonical selection
Default: earliest stable ID remains canonical unless policy chooses otherwise.
