# Verification Phase

## Purpose
Evaluate structural and semantic consistency of produced artifacts.

Verification establishes status:
candidate → verified → disputed → superseded

## Activities
- dedup detection
- conflict detection
- admissibility checks
- matrix alignment
- integrity validation

## Outputs
- artifacts/alignment/
- verification_reports/
- conflict_logs/
- novelty_reports/

## STOP Conditions
- invariant violation
- manifest drift
- unresolved structural conflict
- corrupted provenance

## Claude Role
Claude may:
- schedule verification tasks
- compare artifacts
- record anomalies

Claude may NOT:
- suppress problems
- silently resolve conflicts
