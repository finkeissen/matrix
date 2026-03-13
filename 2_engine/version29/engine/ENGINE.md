# Engine Layout

The engine is organized as a sequence of independently executable steps.

Each step has two representations:

1. **Code path** in `pipeline/steps/*.py`
2. **Work package** in `engine/steps/<step>/`

The work package keeps the local contract deliberately small and self-contained:

- `README.md` — purpose, boundary, local flow, runtime layout
- `contract.md` — accepted input, rejected input, operation, output schema, stop conditions
- `run/` — placeholder for step-local run artifacts during manual or scripted work

## Pipeline flow

```
Input → 01_scope → 02_seed_expansion → 03_categories → 04_problem_generation
      → 05_validation → 06_deduplication → 07_ranking → 08_export
```

## Runtime layout

For every pipeline run, the engine writes a step-local runtime envelope:

```
runs/<run-id>/steps/<step>/run/
  input.json    — declared upstream payload
  output.json   — step output artifact
  meta.json     — counts, output_path reference
```

All three files are written by `RunContext.write_step_payload()`.
The manifest records `input_path` and `output_path` per step for resume and audit.

## Step registry

`pipeline/step_registry.py` is the single source of truth for step metadata:
- canonical step name and slug
- module path for dynamic import
- input_label / output_label (declarative data-flow documentation)

## Design principles

- **Information hiding**: each step reads only its declared upstream artifact.
- **No hidden context**: downstream knowledge must not leak into upstream steps.
- **Determinism**: steps 06–08 are LLM-free and produce identical output for identical input.
- **Resumability**: completed steps are skipped on resume; the manifest is the checkpoint.
