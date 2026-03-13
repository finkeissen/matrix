# 04_problem_generation

## Purpose
Generate atomic assessment problems per category.

## Boundary
Requires categories list only.

## Local flow
`categories` → `04_problem_generation` → `generated_problems`

## Runtime
```
runs/<run-id>/steps/04_problem_generation/run/
  input.json   — { "domain": "...", "categories": [...] }
  output.json  — [ { problem }, ... ]
  meta.json    — { "counts": {"generated": N} }
```
