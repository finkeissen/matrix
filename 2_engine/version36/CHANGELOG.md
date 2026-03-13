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

## v33.0.0 — 00_atomic_problem_curation and 01_atomic_problem_merge fully integrated

### Added — Steps
- `00_atomic_problem_curation`: refactored from CLI-only to `run(ctx, step_input, config, prompt_loader)`
  - Accepts `domain`, `subdomains_file`, `provider`, `provider_config`, `curation_params`
  - Returns `{"data": {...}, "counts": {...}}` — no intermediate/ write
  - CLI wrapper preserved as thin `main()` around `run()`
- `01_atomic_problem_merge`: refactored from CLI-only to `run(ctx, step_input, config, prompt_loader)`
  - Accepts `domain`, `input_files` (from 00 output_files), `output_dir`, `records_per_file`
  - Returns `{"data": {...}, "counts": {...}}` — no intermediate/ write
  - CLI wrapper preserved as thin `main()` around `run()`

### Added — Registry (step_registry.py)
- `00_atomic_problem_curation`: `subdomains_file+domain → candidate_batches`
- `01_atomic_problem_merge`: `candidate_batches → ap_store`
- Registry now has 10 steps total

### Added — step_chain.py
- `_input_00_atomic_problem_curation`: reads curation config from `ctx.manifest.model_config["curation"]`
- `_input_01_atomic_problem_merge`: reads `output_files` from 00's step-local output.json

### Added — engine/steps/
- `engine/steps/00_atomic_problem_curation/README.md` + `contract.md`
- `engine/steps/01_atomic_problem_merge/README.md` + `contract.md`
  Both include: Accepted Input (with schema), Forbidden Context, Operation, Output Schema, Invariants, Stop Conditions

### Versioning
- `pipeline_version` bumped to `33.0.0`

## v34.0.0 — Full E2E integration: 00→01_merge→01_scope→...→08

### Fixed — 00→01 data contract gap
- `01_atomic_problem_merge.load_records()`: no longer silently discards records missing `problem_group`
- `problem_group` is now derived from `subdomain` when absent — closes the 00→01 contract gap
- Updated `engine/steps/01_atomic_problem_merge/contract.md` to document this bridge

### Changed — Orchestrator
- Added `PRE_PIPELINE_STEPS = ['00_atomic_problem_curation', '01_atomic_problem_merge']`
- Added `MAIN_PIPELINE_STEPS = ['01_scope', ..., '08_export']`  (was ALL_STEPS)
- `ALL_STEPS` now aliases `MAIN_PIPELINE_STEPS` for backward compat
- `Orchestrator.run()` gains `include_pre_pipeline: bool = False` param
  - `include_pre_pipeline=True` → runs all 10 steps in order
  - default → main pipeline only (unchanged behavior)

### Tested — E2E
Full pipeline 00→01_merge→01_scope→02→03→04→05→06→07→08:
- 00: 3 subdomains → 6 candidates, all with `candidate_id`
- 01_merge: 6 records merged (inserted=6, problem_group derived from subdomain)
- 01_scope→08_export: 3 problems generated, validated, deduped, ranked, exported to JSONL
- All 10 steps: no `output_path` in returns, no `intermediate/` writes
- `PRE_PIPELINE_STEPS + MAIN_PIPELINE_STEPS = 10 steps`, sequence verified

### Versioning
- `pipeline_version` bumped to `34.0.0`
