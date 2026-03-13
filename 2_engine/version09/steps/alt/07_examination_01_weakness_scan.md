# Envelope: 07_examination_01_weakness_scan

**Parent step:** `07_examination`
**Type:** `llm`
**Upstream:** `05_validation` → `validation_report` (valid=true), `scored_facts` (confidence scores)
**Downstream:** `07_examination_02_alternative_check` (if no weak criteria) or retry `04_hypothesis` (if weak)

---

## TaskEnvelope

```json
{
  "step": "07_examination_01_weakness_scan",
  "parent_step": "07_examination",
  "type": "llm",
  "inputs": {
    "candidate_hash": "<sha256>",
    "validation_report_hash": "<sha256>",
    "normalized_facts_hash": "<sha256>",
    "confidence_hash": "<sha256 of confidence object from 01_parsing_02>"
  },
  "expected_outputs": [
    {
      "key": "weakness_scan",
      "path": "runs/<run_id>/artifacts/07_examination_01_weakness_scan/weakness_scan.json",
      "required": true
    }
  ],
  "policy": { "retries": 1, "timeout_sec": 45, "novelty_guard": true }
}
```

## Output Schema

```json
{
  "candidate_id": "AKU-00123",
  "assessments": [
    {
      "criterion": "Fasting plasma glucose >= 7.0 mmol/L on two separate occasions",
      "strength": "ambiguous",
      "issue": "Separate-day confirmation not documented."
    },
    {
      "criterion": "autoimmune_markers_present == false",
      "strength": "strong",
      "issue": null
    }
  ],
  "weak_or_ambiguous_count": 1,
  "routing": "proceed_to_alternative_check"
}
```

`routing` field is set by post-LLM logic:
- any `weak` assessment → `routing: reject`
- only `ambiguous` or `strong` → `routing: proceed_to_alternative_check`

## Content State
On `routing: reject`: orchestrator marks candidate as `disputed`.
On `routing: proceed`: candidate remains `verified`; weakness added to review queue.

## STOP Conditions
- `routing: reject` AND `retry_count >= 2` → route to 08 `status: insufficient`
