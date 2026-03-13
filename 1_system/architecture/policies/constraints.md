# Policies: Constraints Catalogue

This file lists constraint families and their purpose.
Each constraint set should be versioned and referenced by quality modules.

## Global families
- integrity: required fields, valid references, no silent deletes
- provenance: runs/producer metadata present
- scope: scopes not mixed where disallowed
- evidence: evidence refs required or explicit missing markers
- conflict: detect contradictory assertions (flag, do not resolve silently)

## Track-specific families
- problems.inventory: completeness + atomization invariants
- problems.profile: profile completeness (symptoms/causes/consequences/tests)
- solutions.profile: mechanism/tradeoff/precondition/verification required
