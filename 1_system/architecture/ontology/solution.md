# Ontology Package: Solution (v1)

Represents solution approaches as structured artifacts.
Does not assume correctness; attaches evidence and verification criteria.

## Entity types
- `ontology.solution/SolutionApproach`
- `ontology.solution/Tradeoff`
- `ontology.solution/Precondition`
- `ontology.solution/Verification`
- `ontology.solution/ImplementationStep`
- `ontology.solution/RollbackPlan`

## Relations
- `relation/mitigates` (SolutionApproach → Problem)
- `relation/has_tradeoff` (SolutionApproach → Tradeoff)
- `relation/has_precondition` (SolutionApproach → Precondition)
- `relation/verified_by` (SolutionApproach → Verification)
- `relation/has_step` (SolutionApproach → ImplementationStep)
- `relation/has_rollback` (SolutionApproach → RollbackPlan)
