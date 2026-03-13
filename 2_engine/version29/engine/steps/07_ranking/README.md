# 07_ranking

## Purpose
Sort deduplicated problems by quality score (difficulty weight × statement length).

## Boundary
Deterministic. No LLM call. Requires deduplicated_problems only.

## Local flow
`deduplicated_problems` → `07_ranking` → `ranked_problems`

## Runtime
```
runs/<run-id>/steps/07_ranking/run/
  input.json   — { "accepted": [...] }
  output.json  — [ { problem }, ... ]  (sorted)
  meta.json    — { "counts": {"ranked": N} }
```
