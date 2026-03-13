# Production Phase

## Purpose
Produce knowledge artifacts from normalized inputs.

Artifacts include:
- atomic problems
- dossiers
- relations
- sources
- intermediate reasoning artifacts

Production is exploratory but bounded by TaskEnvelope contracts.

## Rules
- TaskEnvelope immutable
- Expected outputs must exist canonically
- Intermediate artifacts must be persisted
- No promotion decisions here

## Outputs
- artifacts/claims/
- artifacts/problems/
- artifacts/relations/
- artifacts/intermediate/

## STOP Conditions
- missing expected outputs
- envelope violation
- repeated zero-novelty loops
- manifest mismatch

## Claude Role
Claude may:
- dispatch deterministic production tasks
- verify outputs
- trigger snapshot

Claude may NOT:
- change schema
- bypass verification

