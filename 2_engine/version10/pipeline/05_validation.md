# Envelope: 05_validation

**Parent step:** `05_validation`
**Type:** `deterministic` + LLM (atomicity check only)
**Model:** `35b` (LLM part only)
**Upstream:** all `04b_generation_review` outputs (merged), `01_scope` → `scope`
**Downstream:** `06_clarification` (if scope_unclear) or `07_examination_01_hallucination_scan` (if valid)
**Snapshot after:** yes

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "05_validation",
  "parent_step": "05_validation",
  "type": "llm",
  "inputs": {
    "problems_reviewed_hashes": ["<sha256 per category>"],
    "scope_hash": "<sha256 of scope.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "validation_report",
      "path": "runs/<run_id>/artifacts/05_validation/validation_report.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 0,
    "timeout_sec": 30,
    "priority": "normal",
    "novelty_guard": false,
    "model": "35b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "validate_generated_problems"
  }
}
```

---

## What This Step Does

Two-phase validation:

**Phase 1 — Deterministic checks (no LLM):**
- Schema compliance: every problem has all required fields, correct types, valid enum values
- Duplicate detection: exact and near-exact title matches across all categories
- Scope compliance: problem statement does not reference topics listed in `scope.exclusions`
- Count sanity: total problem count > 0

**Phase 2 — LLM atomicity check (35b):**
- Sample up to 20 problems (stratified across categories and difficulty levels)
- Check: is each sampled problem truly atomic (cannot be split further)?
- Check: is the problem self-contained given its `requires_context` flag?
- Result feeds into `atomicity_failures[]` — does not block pipeline unless failure rate > 20%

---

## Output Schema

```json
{
  "subdomain_id": "SD-001",
  "total_problems": "integer",
  "valid": "boolean",
  "schema_errors": [
    {
      "category": "string",
      "problem_title": "string",
      "field": "string",
      "issue": "string"
    }
  ],
  "duplicates": [
    {
      "title_a": "string",
      "title_b": "string",
      "category_a": "string",
      "category_b": "string",
      "similarity": "exact | near_exact"
    }
  ],
  "scope_violations": [
    {
      "problem_title": "string",
      "violation": "string"
    }
  ],
  "atomicity_failures": [
    {
      "problem_title": "string",
      "issue": "string",
      "severity": "low | medium | high"
    }
  ],
  "atomicity_sample_size": "integer",
  "atomicity_failure_rate": "float (0.0–1.0)",
  "scope_unclear": "boolean",
  "notes": "string | null"
}
```

## Routing (deterministic)

```
valid=true AND scope_unclear=false          → 07_examination_01_hallucination_scan
valid=true AND scope_unclear=true           → 06_clarification (max 2 rounds, E-01)
valid=false AND schema_errors only          → retry 04a/04b for affected categories
valid=false AND atomicity_failure_rate>0.20 → retry 04a/04b for affected categories
valid=false AND scope_violations            → 06_clarification
all retries exhausted                       → 08_finalization status: insufficient
```

---

## Content State Transitions
- All `problems_reviewed` artifacts: `candidate` → `verified` if `valid=true`
- On retry: prior `problems_reviewed` artifacts → `superseded`

## STOP Conditions
- Input hashes unresolvable → `deterministic_step_error`
- KB snapshot mismatch → `deterministic_step_error`
