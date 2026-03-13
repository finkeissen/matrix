# 03_categories

## Purpose
Derive problem categories from scope and seed set.

## Boundary
Requires seed_set from upstream only.

## Local flow
`scope + seed_set` → `03_categories` → `categories`

## Runtime
```
runs/<run-id>/steps/03_categories/run/
  input.json   — { "domain": "...", "seeds": [...] }
  output.json  — { "categories": [...], "category_source": "..." }
  meta.json    — { "counts": {"categories": N} }
```
