# Changelog

## version23_en

- translated remaining German operational docs and script comments to English
- improved deterministic problem generation diversity
- added environment validation for `PROBLEMS_PER_CATEGORY`
- made `expert` difficulty valid across validation layers
- improved deterministic ranking quality
- removed caches and historical run data from the release package

## v29.0.0 — Step-oriented Engine with `engine/steps/` work packages

### Added
- `pipeline/step_registry.py` — `StepSpec` dataclass + `STEP_SPECS` tuple, `STEP_MAP`, `get_step_spec()`, `all_step_names()`
- `RunContext.step_dir()`, `.step_run_dir()`, `.step_input_path()`, `.step_output_path()`, `.step_meta_path()`
- `RunContext.write_step_payload()` — writes `input.json`, `output.json`, `meta.json` per step
- `RunContext.read_step_payload()` — reads step-local artifact back as dict
- `engine/steps/<step>/README.md` and `contract.md` for all 8 steps (01–08)
- `engine/ENGINE.md` — authoritative engine layout documentation

### Changed
- `Orchestrator._run_step_with_retry()` now writes `input.json` before execution and `output.json` + `meta.json` after
- `RunContext.start_step()` defaults `input_path` to `step_input_path(step_name)` if not provided
- `RunManifest.pipeline_version` bumped to `29.0.0`

### Unchanged
- All `pipeline/steps/*.py` step implementations — backward compatible
- `intermediate/` layout — still written by individual steps for legacy path continuity
- All validation, health, observability, and eval modules

## v30.0.0 — Step-native: explicit step chain and concrete contracts

### Added
- `pipeline/step_chain.py` — `build_step_input(ctx, step_name, domain)` with one
  `_input_<step>` assembler per step. Each assembler reads only from its declared
  upstream `output.json`. Fallback to `intermediate/` for legacy compatibility.
- `_read_step_output()` helper: resolves step-local output.json → legacy intermediate/ fallback

### Changed
- `Orchestrator._run_step_with_retry()`: replaces generic `{domain, step}` payload
  with `build_step_input()` — every `input.json` now contains the fachlich correct
  upstream data per contract
- All 8 `engine/steps/<step>/contract.md` rewritten with:
  - concrete JSON input/output schemas with field tables
  - Forbidden Context section (explicit list of what must NOT be read)
  - Invariants (checkable postconditions)
  - Stop Conditions table (FAIL / WARN / FALLBACK per case)
  - Example Input / Output
- `engine/ENGINE.md` updated to document step_chain, assembler pattern, and audit trail
- `pipeline_version` bumped to `30.0.0`

### Unchanged
- All `pipeline/steps/*.py` implementations — fully backward compatible
- `intermediate/` layout — still written by individual steps
- All validation, health, observability, and eval modules

## v31.0.0 — Contract-driven step execution

### Changed — Steps (all 8)
- All `run()` functions changed from `run(ctx, domain, config, prompt_loader)`
  to `run(ctx, step_input, config, prompt_loader)`
- Each step reads its declared contract input from `step_input` dict
- Steps no longer read from `ctx.intermediate_dir()` directly as primary source;
  the orchestrator assembles the input via `step_chain.build_step_input()` first
- `06_deduplication`, `07_ranking`, `08_export`: now raise `ValueError` on empty input
  instead of silently producing empty output
- `07_ranking`: annotates each problem with `_rank_score` for full traceability

### Changed — Orchestrator
- `_run_step_with_retry()`: passes `step_input` (not `domain`) to `run()`
- `_load_step()`: resolves module path via `get_step_spec(step_name).module_path`
  instead of raw `f"pipeline.steps.{step_name}"` string interpolation
  — step_registry is now the single source of truth for module location

### Changed — step_chain
- `_read_step_output()` legacy fallback now emits `DeprecationWarning`
  instead of silently reading from `intermediate/`
  — new runs use only the canonical `steps/<step>/run/output.json` path

### Changed — Versioning
- `pipeline_version` bumped to `31.0.0`

## v32.0.0 — Clean output separation: steps return data, orchestrator writes artifacts

### Changed — Steps (01–08)
- All steps **no longer write to `intermediate/`** or any filesystem path
- All steps **no longer return `output_path`** in their result dict
- Steps return only `{"data": ..., "counts": {...}}` — pure computation
- `05_validation` and `06_deduplication` retain `rejected/` diagnostic writes
  (these are side-channel diagnostics, not primary step output)
- `08_export` retains `exports/atomic_problems.jsonl` write
  (this is the canonical pipeline deliverable, not a step artifact)

### Changed — Orchestrator
- Sole writer of `steps/<step>/run/input.json`, `output.json`, `meta.json`
- `meta.json` no longer contains `output_path` (was a legacy field from old intermediate writes)
- Comment updated: "orchestrator is sole writer of artifacts"

### Invariant now enforced (tested)
- No step writes to `intermediate/` — assertion verified in integration test
- No step returns `output_path` — assertion verified in integration test
- Full chain 01→08 produces correct `exports/atomic_problems.jsonl`

### Versioning
- `pipeline_version` bumped to `32.0.0`
