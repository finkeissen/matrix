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
