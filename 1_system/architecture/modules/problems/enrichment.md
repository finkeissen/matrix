# Problems Track: Enrichment Modules (Phase B)

Enrichment produces structured profiles.

## B1) `problems/update_profile_skeleton`
Ensure baseline fields exist; emit review items for missing required fields.

## B2) `problems/update_observables`
Create `Symptom` and `Signal` entities and link them to the problem.

## B3) `problems/update_causes_hypotheses`
Create `CauseHypothesis` entities with qualifiers (confidence/modality/conditions).

## B4) `problems/update_consequences`
Create `Consequence` entities and link via `may_lead_to`.

## B5) `problems/update_constraints`
Create `Constraint` entities and link via `has_constraint`.

## B6) `problems/update_tests`
Create `TestOrCheck` entities; link to hypotheses and/or problems via `verified_by`.

All steps must attach evidence where available or mark evidence_missing explicitly.
