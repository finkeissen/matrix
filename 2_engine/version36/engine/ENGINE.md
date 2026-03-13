# Engine Layout — v36

The engine is organized as a sequence of independently executable steps.

Each step has three representations that form a coherent unit:

1. **Work package** in `engine/<step>/` — contract, docs, run placeholder
2. **Code** in `pipeline/<steps>/<step>.py` — executable implementation
3. **Step registry** in `pipeline/step_registry.py` — canonical metadata

## Pipeline flow

```
domain
  → 01_scope        → scope
  → 02_seed_expansion → seed_set
  → 03_categories   → categories
  → 04_problem_generation → generated_problems
  → 05_validation   → validated_problems
  → 06_deduplication → deduplicated_problems
  → 07_ranking      → ranked_problems
  → 08_export       → export_bundle
```

## Runtime layout per step

```
runs/<run-id>/steps/<step>/run/
  input.json    — exact declared upstream payload (built by step_chain.py)
  output.json   — step output artifact (written after step.run())
  meta.json     — counts, output_path reference, provenance
```

## Step chain — explicit data handoff

`pipeline/step_chain.py` contains one `_input_<step>` assembler per step.
Each assembler reads **only** from the output.json of its declared upstream step.
No assembler may access the output of a step that comes after it.

The orchestrator calls `build_step_input(ctx, step_name, domain)` before
executing each step. The result is written to `input.json` and passed to
the step's `run()` function as its declared contract input.

## Step registry

`pipeline/step_registry.py` is the single source of truth for:
- canonical step name + slug
- module path for dynamic import
- `input_label` / `output_label` (declarative data-flow documentation)

## Work package structure

```
engine/steps/<step>/
  README.md     — purpose, boundary, local flow, runtime paths
  contract.md   — accepted input (with schema), forbidden context,
                  operation, output schema, invariants, stop conditions,
                  example input/output
  run/          — placeholder; populated at runtime
```

## Design principles

- **Information hiding**: each step reads only its declared upstream artifact
- **No hidden context**: downstream knowledge must not leak upstream
- **Determinism**: steps 06–08 are LLM-free; identical input → identical output
- **Resumability**: completed steps are skipped; manifest.json is the checkpoint
- **Traceability**: input.json + output.json + meta.json form a complete audit trail per step
