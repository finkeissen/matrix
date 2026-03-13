# 05_validation

## Purpose
Validate generated problems against schema, business rules, content checks, and quality gates.

## Boundary
Requires generated_problems list only.

## Local flow
`generated_problems` → `05_validation` → `validated_problems`

## Runtime
```
runs/<run-id>/steps/05_validation/run/
  input.json   — [ { problem }, ... ]
  output.json  — { "problems": [...], "rejected": [...] }
  meta.json    — { "counts": {"accepted": N, "rejected": N} }
```
