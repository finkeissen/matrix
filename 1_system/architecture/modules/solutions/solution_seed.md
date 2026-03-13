# Solutions Track: Seed

## `solutions/update_solution_seed`
Create initial `SolutionApproach` candidates linked to atomic problems.

Inputs:
- atomic problems
- (optional) cause hypotheses, constraints, context

Outputs:
- `SolutionApproach` entities with minimal mechanism statement
- `relation/mitigates` links to problems
- evidence refs where available (or explicit missing markers)
