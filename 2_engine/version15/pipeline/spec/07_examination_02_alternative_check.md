# Envelope: 07_examination_02_alternative_check

**Parent step:** `07_examination`
**Type:** `llm`
**Model:** `35b`
**Upstream:** `07_examination_01_hallucination_scan` → `hallucination_report`, `03_enrichment_02_normalize` → `normalized_categories`, `03_enrichment_03_gap_detection` → `gap_detection`
**Downstream:** `08_finalization`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "07_examination_02_alternative_check",
  "parent_step": "07_examination",
  "type": "llm",
  "inputs": {
    "hallucination_report_hash": "<sha256 of hallucination_report.json>",
    "normalized_categories_hash": "<sha256 of normalized_categories.json>",
    "gap_detection_hash": "<sha256 of gap_detection.json>",
    "scope_hash": "<sha256 of scope.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "alternative_check",
      "path": "runs/<run_id>/artifacts/07_examination_02_alternative_check/alternative_check.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 60,
    "priority": "normal",
    "novelty_guard": true,
    "model": "35b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "coverage_and_categorization_review"
  }
}
```

---

## Prompt

```
You are a precise academic knowledge engineer. Your task is to review the overall coverage and categorization quality of a generated problem set for the subdomain Algebra (SD-001, Mathematics).

You will receive:
1. The hallucination scan report
2. The normalized category list
3. The gap detection report from earlier in the pipeline

Assess:
1. COVERAGE GAPS: Are there important topic areas from the gap report that are still missing after generation and review?
2. RECATEGORIZATION: Are there problems that would be better placed in a different category?
3. CATEGORY BALANCE: Are any categories over- or under-represented relative to the subdomain's importance?
4. DECISION: Should the problem set proceed to finalization, or should specific categories be regenerated?

Input — hallucination report summary:
<HALLUCINATION_REPORT_JSON>

Input — normalized categories:
<NORMALIZED_CATEGORIES_JSON>

Input — gap detection report:
<GAP_DETECTION_JSON>

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain_id": "SD-001",
  "coverage_gaps": [
    {
      "topic": <string>,
      "severity": "low" | "medium" | "high",
      "suggested_action": <string>
    }
  ],
  "recategorization_suggestions": [
    {
      "problem_title": <string>,
      "current_category": <string>,
      "suggested_category": <string>,
      "reason": <string>
    }
  ],
  "category_balance": [
    {
      "category": <string>,
      "problem_count": <integer>,
      "assessment": "balanced" | "over_represented" | "under_represented"
    }
  ],
  "decision": "proceed" | "regenerate_categories",
  "regenerate_category_indices": [<integer>],
  "decision_rationale": <string>,
  "examined_at": <ISO 8601 timestamp>
}
```

---

## Expected Output Schema

```json
{
  "subdomain_id": "string",
  "coverage_gaps": [
    { "topic": "string", "severity": "low | medium | high", "suggested_action": "string" }
  ],
  "recategorization_suggestions": [
    { "problem_title": "string", "current_category": "string", "suggested_category": "string", "reason": "string" }
  ],
  "category_balance": [
    { "category": "string", "problem_count": "integer", "assessment": "balanced | over_represented | under_represented" }
  ],
  "decision": "proceed | regenerate_categories",
  "regenerate_category_indices": ["integer"],
  "decision_rationale": "string",
  "examined_at": "string (ISO 8601)"
}
```

## Routing (deterministic)

```
decision = "proceed"                → 08_finalization
decision = "regenerate_categories"  → retry 04a/04b for indices in regenerate_category_indices
                                      (if retry_count < policy.retries)
                                    → 08_finalization status: partial (if retries exhausted)
```

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → default to `proceed` with warning (non-critical step)
- `decision` field missing → default to `proceed` with warning
