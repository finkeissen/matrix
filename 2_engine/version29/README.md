# LLM Pipeline System (English Release)

This package is a cleaned and English-translated version of the uploaded system, based on `version22` and prepared as a deliverable zip.

## What changed in this package

### 1. English-first codebase

The operational code and the evaluation notes were translated to English where German text was still present.

### 2. More robust problem generation

`pipeline/steps/04_problem_generation.py` now:

- uses multiple statement patterns,
- uses explicit evidence requirements,
- validates `PROBLEMS_PER_CATEGORY`,
- creates category-aware problem IDs,
- keeps eval mode deterministic while producing more diverse prompts.

### 3. Consistent difficulty handling

The system now treats `expert` as a valid difficulty level consistently across generation, schema validation, business rules, and quality checks.

### 4. Better ranking

`pipeline/steps/07_ranking.py` now ranks accepted problems with a deterministic score that considers difficulty and statement richness instead of only pushing `hard` items first.

## Suggested next test

```bash
PIPELINE_EVAL_MODE=1 PROBLEMS_PER_CATEGORY=10 python -m pipeline.cli run --domain thermodynamics
```

## Project structure

- `pipeline/` – pipeline runtime
- `ingestion/` – seeds, rules, schemas, and manifests
- `scripts/` – helper scripts
- `tests/` – automated tests
- `docs/` – supporting notes

## Notes

- Runtime cache folders were removed from this release zip.
- Historical run data was removed from this release zip to keep the artifact clean.
