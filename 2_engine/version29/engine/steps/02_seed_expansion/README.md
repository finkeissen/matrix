# 02_seed_expansion

## Purpose
Expand the scope into a concrete set of topic seeds.

## Boundary
Requires `scope` + `domain` from upstream only.

## Local flow
`scope + domain` → `02_seed_expansion` → `seed_set`

## Runtime
```
runs/<run-id>/steps/02_seed_expansion/run/
  input.json   — { "domain": "...", "scope": {...} }
  output.json  — { "seeds": [...], "seed_sources": {...} }
  meta.json    — { "counts": {"seeds": N} }
```
