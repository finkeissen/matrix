# Envelope: 06_clarification

**Parent step:** `06_clarification`
**Type:** `llm`
**Model:** `19b`
**Upstream:** `05_validation` → `validation_report` (scope_unclear=true or scope_violations)
**Downstream:** back to `01_scope` with refined input
**Snapshot after:** yes (before re-entry)

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "06_clarification",
  "parent_step": "06_clarification",
  "type": "llm",
  "inputs": {
    "validation_report_hash": "<sha256 of validation_report.json>",
    "scope_hash": "<sha256 of scope.json>",
    "clarification_round": "<integer: 1 or 2>",
    "prior_clarification_hashes": ["<sha256 of prior clarification_request.json, if round > 1>"],
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "clarification_request",
      "path": "runs/<run_id>/artifacts/06_clarification/clarification_request_round_<N>.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 30,
    "priority": "normal",
    "novelty_guard": true,
    "model": "19b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "scope_refinement"
  }
}
```

**Output path includes round number** — preserves all clarification rounds as separate artifacts.

---

## Prompt

```
You are a precise academic knowledge engineer. The scope definition for a subdomain has produced validation issues. Your task is to generate a refined scope that resolves these issues.

This is clarification round <ROUND> of maximum 2 (E-01: scope_clarification_exhausted after round 2).

Input — current scope:
<SCOPE_JSON>

Input — validation report (issues that triggered clarification):
<VALIDATION_REPORT_JSON>

Analyze the scope violations and unclear boundaries identified in the validation report. Produce a refined scope object that resolves these issues.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

The refined scope must have the same structure as the original scope object, with these additions:

{
  "subdomain": <string>,
  "subdomain_id": <string>,
  "parent_domain": <string>,
  "canonical_source": <string>,
  "boundaries": [<string>],
  "exclusions": [<string>],
  "ambiguities": [{ "topic": <string>, "resolution": <string> }],
  "refinement_round": <integer>,
  "changes_made": [
    {
      "field": "boundaries" | "exclusions" | "ambiguities",
      "change": <string: description of what was added, removed, or clarified>
    }
  ]
}
```

---

## Expected Output Schema

```json
{
  "subdomain": "string",
  "subdomain_id": "string",
  "parent_domain": "string",
  "canonical_source": "string",
  "boundaries": ["string"],
  "exclusions": ["string"],
  "ambiguities": [{ "topic": "string", "resolution": "string" }],
  "refinement_round": "integer",
  "changes_made": [
    {
      "field": "string",
      "change": "string"
    }
  ]
}
```

## Re-entry Flow (E-01)

```
Orchestrator checks run_record.clarification_rounds:

  if clarification_rounds < 2:
    increment clarification_rounds
    re-run 01_scope with refined scope as input → new task_id
    pipeline continues from 01_scope forward
    prior scope, categories, normalized_categories, gap_detection → superseded
    all 04a/04b envelopes re-instantiated from new categories

  if clarification_rounds >= 2:
    STOP: scope_clarification_exhausted
```

---

## Content State on Completion
`candidate`

## STOP Conditions
- `clarification_rounds >= 2` before dispatch → orchestrator emits STOP: `scope_clarification_exhausted` (envelope never created)
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- Refined scope missing `boundaries` or `exclusions` → `llm_output_invalid`
