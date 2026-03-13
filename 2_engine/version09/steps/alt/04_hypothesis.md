# Envelope: 04_hypothesis

**Type:** `llm`
**Upstream:** `03_enrichment_03` → `gap_detection`, `normalized_facts`, `context_units`
**Downstream:** `05_validation`

---

## TaskEnvelope

```json
{
  "step": "04_hypothesis",
  "parent_step": "04_hypothesis",
  "type": "llm",
  "inputs": {
    "normalized_facts_hash": "<sha256>",
    "context_units_hash": "<sha256>",
    "gap_detection_hash": "<sha256>",
    "retry_context_hash": null
  },
  "expected_outputs": [
    {
      "key": "candidate",
      "path": "runs/<run_id>/artifacts/04_hypothesis/candidate.json",
      "required": true
    }
  ],
  "policy": { "retries": 2, "timeout_sec": 60, "novelty_guard": true }
}
```

**On retry after examination rejection**, `retry_context_hash` is non-null (points to a
`retry_context.json` artifact containing rejection reason). This changes `task_id` — treated
as a new task, not a re-run. Prior `candidate` marked `superseded`.

## Output Schema

```json
{
  "candidates": [
    {
      "candidate_id": "AKU-00123",
      "rank": 1,
      "matched_criteria": ["Fasting plasma glucose >= 7.0: satisfied (8.21 mmol/L, ×2)"],
      "missing_criteria": ["OGTT 2-hour glucose: not available"],
      "potentially_violated": [],
      "uncertainty_level": "low",
      "uncertainty_reason": "Two primary criteria satisfied; one optional unavailable.",
      "rationale": "Case facts directly satisfy fasting glucose and absence-of-autoimmune criteria."
    }
  ]
}
```

**Flat schema** — `uncertainty` is two top-level fields (`uncertainty_level`, `uncertainty_reason`), not a nested object. Maximizes reliability with small LLMs.

## Content State on Completion
`candidate`

## STOP Conditions
- `NO_MATCH` returned by LLM → route to `08_finalization` with `status: no_match` (not a STOP)
- Malformed JSON after 2 retries → `llm_output_invalid`
- Retry with unchanged inputs → `no_novelty_on_retry`
- `dispatch_count > policy.retries + 1` → `loop_limit_exceeded`
