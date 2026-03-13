# 01_scope

## Purpose
Define subdomain boundaries for the given domain.

## Boundary
Executable from `domain` alone. Must not rely on any downstream context.

## Local flow
`domain` → `01_scope` → `scope`

## Runtime
```
runs/<run-id>/steps/01_scope/run/
  input.json   — { "domain": "..." }
  output.json  — { "boundaries": [...], "exclusions": [...] }
  meta.json    — { "counts": {...} }
```
