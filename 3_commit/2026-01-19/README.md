# Commit 2026-01-19 (consolidated snapshot)

**Status:** first consolidated commit-snapshot  
**Source:** append-only merge of multiple runs executed on 2026-01-19

This directory is a **snapshot** that consolidates artifacts produced by these runs:

- `2.runs/2026-01-19/run_01_position`  
  (Position / Standort)

- `2.runs/2026-01-19/run_02_navigation`  
  (Target + Options)

- `2.runs/2026-01-19/run_03_tradeoffs_norms`  
  (Pros / Cons + Norm constraint)

- `2.runs/2026-01-19/run_04_conflict_supersession`  
  (Contradicting norms + Supersession test)

## What this commit contains

- `problems.jsonl` — problem records (minimal placeholder)
- `claims.jsonl` — claims including roles:
  - position
  - target
  - option
  - pro
  - con
  - norm
- `relations.jsonl` — relations enabling navigation and constraint representation:
  - `has_position`, `has_target`, `has_option`
  - `has_pro`, `has_con`, `constrains`
  - `contradicts`, `supersedes`
- `sources.jsonl` — placeholder source records

## What this commit does NOT do

- no ranking, scoring, optimization, or route selection
- no conflict resolution
- no authority validation or enforcement

## Notes

- This snapshot is **append-only** with respect to upstream runs:
  no run files are modified.
- Records are consolidated by **unique line content**
  (exact duplicates removed).
- Any future revisions should occur via new commits
  (e.g. `2026-01-20`) rather than overwriting.

