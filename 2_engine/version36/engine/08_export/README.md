# 08_export

## Purpose
Write the final ranked problem set to JSONL for downstream ingestion.

## Boundary
Read-only terminal step. No LLM call. Writes to exports/ only.

## Local flow
`ranked_problems` → `08_export` → `export_bundle`

## Runtime
```
runs/<run-id>/steps/08_export/run/
  input.json   — [ { problem }, ... ]
  output.json  — { "exported": N, "ingestion": {...} }
  meta.json    — { "counts": {"exported": N} }
```
