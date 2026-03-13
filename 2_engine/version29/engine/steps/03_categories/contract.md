# Contract — 03_categories

## Accepted Input
- `domain` (string, required)
- `seed_set` / `seeds` (list[str], from 02_seed_expansion)

## Rejected Input
- generated problems, validation results, or export artifacts

## Operation
Load taxonomy from ingestion layer; fall back to domain-derived defaults.
Categories must be slug-safe strings.

## Output
- `categories` (list[str])
- `category_source` ("ingestion_taxonomy" | "fallback")

## Stop Conditions
- empty category list after processing
- taxonomy file malformed
