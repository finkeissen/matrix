# run_08_machines_problem_seed

Seeds the Matrix with mechanical engineering problems (automotive + machine design) to test:
- constraint articulation (safety, cost, manufacturability, reliability, environment)
- tradeoff representation without "best design" collapse
- model scope/validity boundaries
- standards and norm conflicts (including temporal updates)
- verification/validation gaps

## Non-goals
- design recommendations
- optimization or ranking of solutions
- authoritative safety or compliance advice

## Files
- manifest.json
- problems.jsonl (150 problems)
- claims.jsonl (empty by design)
- relations.jsonl (empty by design)
- sources.jsonl (empty/minimal by design)

Next steps: select a subset for `3.commit/<date>/` and attach minimal claims + relations only where it improves structural visibility.
