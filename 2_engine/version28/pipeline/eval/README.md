# `pipeline.eval`

This package is **explicitly intended to live outside the production pipeline**.

## Goals

1. **Check step suitability**  
   Determine which pipeline steps a loaded LLM can handle reliably.

2. **Calibrate parameters**  
   Test multiple parameter combinations for suitable steps and identify the best option based on run metrics and downstream success.

## Important architectural decision

These scripts do **not** belong in `tests/` because they:

- can be slow,
- may call external LLMs,
- are not deterministic,
- are experimental by design.

`tests/` should contain only fast, deterministic checks.

## Assumptions

The scripts launch the pipeline **as a separate subprocess** through a configurable command template, for example:

```bash
python -m pipeline.cli run --domain {domain}
```

The scripts also set environment variables such as:

- `LLM_TEMPERATURE`
- `LLM_TOP_P`
- `LLM_MAX_TOKENS`
- `LLM_EVAL_STEP`

If your pipeline or LLM client expects different names, adjust the mapping in the adapter or invocation layer.

## Typical workflow

### 1. Check suitability

```bash
python -m pipeline.eval.evaluate_step_suitability --domain thermodynamics --model qwen2.5-72b --steps 01_scope 02_seed_expansion 03_categories 04_problem_generation --run-cmd "python -m pipeline.cli run --domain {domain}"
```

### 2. Calibrate parameters

```bash
python -m pipeline.eval.calibrate_llm_params --domain thermodynamics --model qwen2.5-72b --step 04_problem_generation --run-cmd "python -m pipeline.cli run --domain {domain}"
```

## Output

The scripts write reports to:

- `pipeline/eval/reports/`

They can also update profiles in:

- `pipeline/eval/profiles/calibrated_profiles.json`

## Limits

This version is intentionally **an external eval runner**, not a deep integration into the production pipeline.
It can:

- launch runs,
- evaluate runs,
- produce recommendations.

It cannot guarantee that step-specific parameters are actually applied unless the production LLM integration already consumes those variables.
