# Export Phase

## Purpose
Move validated knowledge across system boundaries.

Export does not change engine state.

Primary target:
3.commit/

## Promotion Gate
Required:
- provenance complete
- verification recorded
- promotion decision logged

## Outputs
- bundles
- promotion_log.jsonl
- dispute records
- commit metadata

## Rules
- append-only
- never overwrite commit artifacts
- challenges update status, not content

## STOP Conditions
- incomplete provenance
- missing verification
- conflicting promotion

## Claude Role
Claude may:
- propose promotion
- assemble bundles
- create dispute links

Claude may NOT:
- write directly to commit without gate
