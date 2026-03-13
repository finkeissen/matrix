# Problems Track: Schemas (recommended)

These shapes map to the substrate and can be adapted to existing JSONL formats.

## ProblemCandidate
- type: `ontology.problem/ProblemCandidate`
- required: `subtype`, `label`, `description`, `scope`, `evidence_refs`

## Problem (atomic)
- type: `ontology.problem/Problem`
- required: `problem_id`, `atomic=true`, `label`, `description`, `scope`, `status`, provenance

## Common profile entities
- Symptom / CauseHypothesis / Consequence / Signal / Constraint / TestOrCheck
- required: `label`, `scope`, provenance
- CauseHypothesis should include `qualifiers.confidence` and `qualifiers.modality`
