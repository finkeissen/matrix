# Ontology Package: Problem (v2)

This package defines how we represent problems in a structured way.
It is a specialization over the substrate and may coexist with alternative future packages.

---

## Entity types
- `ontology.problem/ProblemCandidate`
- `ontology.problem/Problem` (atomic=true)
- `ontology.problem/Symptom`
- `ontology.problem/CauseHypothesis`
- `ontology.problem/Consequence`
- `ontology.problem/Signal`
- `ontology.problem/Constraint`
- `ontology.problem/TestOrCheck`

### Candidate subtypes (required)
`ProblemCandidate.subtype`:
- `observed_issue` (direct observation)
- `inferred_issue` (interpretation from observations)
- `structural_issue` (architecture/process weakness)
- `meta_issue` (problem about problem-handling)

This prevents premature semantic upgrade.

---

## Relations / assertions
- `relation/has_symptom` (Problem → Symptom)
- `relation/has_signal` (Problem → Signal)
- `relation/has_possible_cause` (Problem → CauseHypothesis)
- `relation/may_lead_to` (Problem → Consequence)
- `relation/has_constraint` (Problem → Constraint)
- `relation/verified_by` (CauseHypothesis|Problem → TestOrCheck)

Qualifiers:
- `confidence` (calibrated scale or {low,med,high})
- `modality` (observed|possible|probable)
- `conditions` (when/where)

---

## Atomic problem requirements (minimal)
- `atomic: true`
- single scope (or explicit `unknown`, but not mixed)
- primary symptom class is identifiable
- provenance + evidence refs OR explicit evidence_missing flag
