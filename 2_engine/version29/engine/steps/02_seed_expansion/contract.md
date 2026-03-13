# Contract — 02_seed_expansion

## Accepted Input
- `domain` (string, required)
- `scope` (object from 01_scope, optional — falls back to domain string)

## Rejected Input
- categories, problems, or any artifact from steps 03–08

## Operation
Merge LLM-generated seeds with curated ingestion seeds.
Deduplicate preserving insertion order.

## Output
- `seeds` (list[str])
- `seed_sources` (object: generated / curated / final counts)

## Stop Conditions
- `domain` missing
- seed list empty after dedup
