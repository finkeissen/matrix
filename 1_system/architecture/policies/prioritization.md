# Policies: Prioritization (Navigation Only)

Prioritization is used for *work ordering*, not truth.

Recommended structural scores:
- `upstream_degree` (how many other problems reference this as cause)
- `downstream_degree` (how many consequences depend on it)
- `cross_scope_count` (appears in multiple scopes/components)
- `evidence_density` (how many strong evidence links)
- `review_pressure` (how many constraints failing)

Scores must be reproducible and derived from state structure.
