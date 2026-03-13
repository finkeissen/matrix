# Normalization Phase

## Purpose
Create canonical representation without changing meaning.

Normalization governs:
- IDs
- schemas
- canonical locations
- status timelines
- artifact equivalence links

## Rules
- append-only
- history preserved
- canonical selection recorded
- dedup produces links, not deletions

## Outputs
- canonical artifacts
- index updates
- canonicalization reports
- status transitions

## STOP Conditions
- ambiguous canonical selection
- schema incompatibility
- hash mismatch

## Claude Role
Claude may:
- trigger canonicalization passes
- verify schema compliance
- record status transitions

Claude may NOT:
- discard artifacts
- rewrite history
