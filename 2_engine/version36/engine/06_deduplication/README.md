# 06_deduplication

## Purpose
Three-level deduplication: exact hash, normalized text, semantic similarity.

## Boundary
Requires validated_problems and optional registry/index. No LLM call.

## Local flow
`validated_problems` → `06_deduplication` → `deduplicated_problems`

## Runtime
```
runs/<run-id>/steps/06_deduplication/run/
  input.json   — { "problems": [...] }
  output.json  — { "accepted": [...], "counts": {...} }
  meta.json    — { "counts": {...} }
```
