# Problems Track: Quality Module

## `problems/update_problem_quality`

Evaluates constraints and produces:
- `report.json`
- `review_queue.jsonl`
- optional STOP artifacts (policy-defined)

### Phase A constraints
- atomic problems have required identifiers + scope
- candidates have subtype
- split protocol invariants satisfied
- completeness coverage rules satisfied (taxonomy + components)

### Phase B constraints
- each atomic problem has:
  - >=1 Symptom OR review item
  - >=1 CauseHypothesis OR review item
  - >=1 Consequence OR review item
  - >=1 TestOrCheck OR review item
- evidence coverage thresholds (policy-defined)

No auto-fixing; only evaluation and queueing.
