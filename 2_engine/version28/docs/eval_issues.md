# LLM Pipeline – Evaluation Issues

This document serves as a **working log for issues, observations, and decisions** related to pipeline evaluation.

Goals:

- document issues in a traceable way,
- analyze root causes,
- record fixes and decisions,
- justify later parameter and model decisions.

This is **not a bug tracker**. It is a technical working log.

---

# Issue 001 — High duplicate rate in `04_problem_generation`

## Status
open

## Date
2026-03-08

## Context

Evaluation via:

`pipeline.eval.evaluate_step_suitability`

Model:

`qwen2.5-72b`

Domain:

`thermodynamics`

Eval mode:

`PIPELINE_EVAL_MODE=1`
`PROBLEMS_PER_CATEGORY=20`

## Observation

Eval run result:

`generated: 60`
`accepted: 3`
`duplicates: 57`
`acceptance_rate: 0.05`
`score: 0.4325`

Interpretation:

95% of generated problems are detected as duplicates.

The eval system rates the step as **not suitable**.

## Affected components

- `pipeline/steps/04_problem_generation.py`
- `pipeline/steps/06_deduplication.py`
- `pipeline/eval/scoring.py`

## Suspected cause

The current `04_problem_generation` implementation uses a very rigid template.

Example:

`"{category} scenario {idx}"`

The problem text is nearly identical:

`Analyze a representative {domain} problem in category {cat} and determine the governing result with a justified solution path.`

This creates structurally identical problems.

The deduplication step correctly flags them as duplicates.

## Assessment

The problem is **primarily in the generation logic**, not in the LLM parameters.

Parameter calibration only makes sense after the step produces enough variety.

## Next steps

### Step 1 — Improve generation logic

`04_problem_generation` should:

- generate multiple problem types,
- use different task formats,
- force different solution paths.

Examples:

- derive
- predict
- compare
- explain
- estimate
- analyze

### Step 2 — Small eval sample

Run a small eval sample:

- categories: 3
- problems_per_category: 5
- total: 15

Goal:

- observe duplicate rate,
- check acceptance rate,
- inspect problem diversity.

### Step 3 — Parameter optimization

Only after diversification succeeds.

Suggested search space:

- `temperature: 0.2 / 0.4 / 0.6`
- `top_p: 0.85 / 0.92 / 0.97`

---

# Issue 002 — Eval sample was too small

## Status
resolved

## Description

Originally, `04_problem_generation` produced only:

`3 problems`

That made the evaluation uninformative.

All parameter profiles had identical scores.

## Resolution

An **eval mode** was introduced.

File:

`pipeline/steps/04_problem_generation.py`

New variables:

- `PIPELINE_EVAL_MODE=1`
- `PROBLEMS_PER_CATEGORY=10`

Example:

```bash
PIPELINE_EVAL_MODE=1 PROBLEMS_PER_CATEGORY=20 python -m pipeline.cli run --domain thermodynamics
```

---

# Open questions

1. Should `04_problem_generation` become fully LLM-based?
2. How should problem diversity be measured?
