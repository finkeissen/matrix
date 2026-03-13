# Ingestion bundle

This bundle applies the agreed ingestion standard directly to the provided files.

## Folder overview

- `archive/imports/`: unchanged source ZIP files
- `imports/`: unpacked source material for traceability
- `rules/`: normalized, reusable rule and case assets
- `seeds/`: normalized seed candidates and reusable pattern lists
- `taxonomy/`: structured families and categories for later domain mappings
- `manifests/`: status, origin, and decision rationale per asset
- `schemas/`: JSON schemas for production assets and manifests
- `trash/`: intentionally non-production or archive-only content

## Decision logic for this conversion

- `contradictions.zip` → adopted as a global rule library and taxonomy
- `cases.zip` → adopted as a case corpus and gate rules
- `meta.zip`, `structural.zip`, `atomic.zip` → adopted as global seed and pattern libraries
- `partials.zip` → kept only as candidate input, not directly approved for production use
- `icd11_enriched_ultra_flat.jsonl.zip` → archived, but not approved for general pipeline usage because it is domain-specific

## Production rule

Only assets with `status: approved` should be reused in production.
Raw data under `archive/` and `imports/` must not be consumed directly by the pipeline.
