# Phase 3 — Reconciliation & Cross-Checking

**Goal:** Ensure internal consistency, remove structural weaknesses, and improve coverage.

**Input:** `problems.jsonl`, `enrichments.jsonl`, `sources.jsonl`, `relations.jsonl`  
**Output:** `relations.jsonl` (expanded), `conflicts.jsonl`, coverage reports

---

## Step 3a — Cross-Problem Deduplication (global)

Identify semantically equivalent problems across subdomains and domains.

Produce `relations` of type:

- `equivalent_to`
- `supersedes` / `superseded_by`
- `duplicate_of`

**Do not delete:** mark with relations only. Original records remain for traceability.

---

## Step 3b — Conflict Detection

Detect contradictions between:

- problem definitions
- assumptions
- constraints
- recommended approaches

For each conflict:

- Write a record to `conflicts.jsonl`
- Link conflict ↔ problem(s) and conflict ↔ sources via `relations`

`conflicts.jsonl` record structure (minimum):
```json
{
  "conflict_id": "...",
  "type": "definition | assumption | constraint | approach",
  "problem_ids": ["...", "..."],
  "source_ids": ["...", "..."],
  "description": "...",
  "run_id": "...",
  "timestamp": "..."
}
```

---

## Step 3c — Coverage & Gap Analysis

Identify:

- Subdomains with too few problems
- Missing standard categories (diagnosis, measurement, decision thresholds, etc.)
- Enrichment fields that are systematically empty or low-quality

Generate targeted follow-up tasks:

- New candidate generation prompts for weak areas → feed back into Phase 1
- Deeper enrichment prompts where detail is thin → feed back into Phase 2

---

## Iterative Loop

Phase 3 does not terminate the pipeline — it feeds back:
```
Phase 3 gap analysis
    → new Phase 1 runs (targeted subdomains)
    → new Phase 2 runs (thin enrichments)
    → new Phase 3 runs (after re-enrichment)
```

Re-run phases with stronger LLMs over time.  
Track all changes via supersession — never overwrite.  
Freeze stable snapshots into `3.commit/YYYY-MM-DD/`.

---

## Multi-Model Validation (optional but powerful)

- Generate with model A
- Validate / dedup / conflict-check with model B
- Use disagreement as a trigger for "needs verification" flag

---

## Output Files

| File | Content |
|---|---|
| `relations.jsonl` | Equivalence, supersession, duplicate links |
| `conflicts.jsonl` | Explicit contradictions with provenance |
| `coverage_report.md` / `.json` | Gap analysis results (optional) |
