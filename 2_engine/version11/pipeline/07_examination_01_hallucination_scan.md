# Envelope: 07_examination_01_hallucination_scan

**Parent step:** `07_examination`
**Type:** `llm`
**Model:** `122b`
**Upstream:** `05_validation` → `validation_report` (valid=true), all `04b_generation_review` outputs
**Downstream:** `07_examination_02_alternative_check`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "07_examination_01_hallucination_scan",
  "parent_step": "07_examination",
  "type": "llm",
  "inputs": {
    "problems_reviewed_hashes": ["<sha256 per category>"],
    "validation_report_hash": "<sha256 of validation_report.json>",
    "scope_hash": "<sha256 of scope.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "hallucination_report",
      "path": "runs/<run_id>/artifacts/07_examination_01_hallucination_scan/hallucination_report.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 90,
    "priority": "normal",
    "novelty_guard": true,
    "model": "122b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "hallucination_risk_assessment"
  }
}
```

---

## Prompt

```
You are a rigorous academic fact-checker. Your task is to scan a set of atomic problems for hallucination risk — cases where a problem statement contains a plausible but potentially incorrect claim, an invented reference, a non-standard term, or a factual error.

Subdomain: Algebra (SD-001, Mathematics)

Input — all reviewed problems (across all categories):
<PROBLEMS_REVIEWED_JSON>

For each problem, assess:
1. Is the problem statement factually correct as stated?
2. Does the canonical_source reference actually exist and cover this topic?
3. Are any technical terms used in a non-standard way?
4. Is the hallucination_risk assigned by the generator appropriate?

Flag any problem where you have doubt. Assign a corrected hallucination_risk if the original is wrong.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain_id": "SD-001",
  "total_problems_scanned": <integer>,
  "flagged_count": <integer>,
  "scan_coverage": "full" | "sampled",
  "flagged": [
    {
      "category": <string>,
      "title": <string: problem title>,
      "issue_type": "factual_error" | "invalid_source" | "non_standard_term" | "risk_underestimated",
      "issue_description": <string: specific issue>,
      "original_hallucination_risk": "low" | "medium" | "high",
      "corrected_hallucination_risk": "low" | "medium" | "high",
      "severity": "low" | "medium" | "high",
      "suggested_fix": <string or null>
    }
  ],
  "overall_quality": "high" | "acceptable" | "low",
  "notes": <string or null>
}
```

## Sampling Strategy

The orchestrator pre-processes input before dispatch:

```
if total_problems <= 60:
    scan_coverage = "full"    → pass all problems to LLM
if total_problems > 60:
    scan_coverage = "sampled" → stratified sample: 6 problems per category,
                                 prioritizing hallucination_risk: "high" and "medium"
                                 from 04b output; random fill for remainder
```

Input token budget with sampling:
```
System prompt + instructions:      ~600 tokens
Scope object:                      ~300 tokens
Problems (≤60 full / sampled):     ~4.000 tokens max
──────────────────────────────────────────────
Total input:                       ~4.900 tokens  ✅ fits in 8k
```

For Algebra (~160 problems across 10 categories): full scan is feasible. For subdomains with 20+ categories, sampling activates automatically.

```json
{
  "subdomain_id": "string",
  "total_problems_scanned": "integer",
  "flagged_count": "integer",
  "scan_coverage": "full | sampled",
  "flagged": [
    {
      "category": "string",
      "title": "string",
      "issue_type": "factual_error | invalid_source | non_standard_term | risk_underestimated",
      "issue_description": "string",
      "original_hallucination_risk": "low | medium | high",
      "corrected_hallucination_risk": "low | medium | high",
      "severity": "low | medium | high",
      "suggested_fix": "string | null"
    }
  ],
  "overall_quality": "high | acceptable | low",
  "notes": "string | null"
}
```

## Routing (post-LLM, deterministic)

```
overall_quality = "high" | "acceptable"   → 07_examination_02_alternative_check
overall_quality = "low"                   → retry 04a/04b for flagged categories (if retries remain)
                                            → 08_finalization status: insufficient (if retries exhausted)
```

Flagged problems with `severity: high` and `corrected_hallucination_risk: high` are carried forward to `08_finalization` and reflected in the final `hallucination_risk` field of each problem.

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- `overall_quality` field missing → `llm_output_invalid`
