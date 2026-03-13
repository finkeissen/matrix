# Acquisition Phase

## Purpose
Acquire inputs for runs without mutating source material.

Inputs may originate from:
- 2.work/
- previous runs
- external ingestion
- worlds / foundation references

Acquisition produces normalized intake artifacts but does not generate knowledge.

## Rules
- Source inputs are read-only
- Provenance must be recorded
- Every acquisition step creates a decision record
- RAM staging is allowed but canonical materialization required

## Outputs
- normalized_inputs/
- acquisition_log.jsonl
- provenance records

## STOP Conditions
- missing required inputs
- ambiguous provenance
- normalization failure
- RAM unavailable

## Claude Role
Claude may:
- select inputs
- define minimal normalization
- verify completeness

Claude may NOT:
- reinterpret content
- deduplicate
- promote artifacts
