# Envelope: 01_parsing_02_confidence

**Parent step:** `01_parsing`
**Type:** `llm`
**Upstream:** `01_parsing_01_extraction` → `raw_facts`
**Downstream:** `02_retrieval`

---

## TaskEnvelope

```json
{
  "step": "01_parsing_02_confidence",
  "parent_step": "01_parsing",
  "type": "llm",
  "inputs": {
    "raw_facts_hash": "<sha256 of raw_facts.json>",
    "raw_text_hash": "<sha256 of raw_text>"
  },
  "expected_outputs": [
    {
      "key": "scored_facts",
      "path": "runs/<run_id>/artifacts/01_parsing_02_confidence/scored_facts.json",
      "required": true
    }
  ],
  "policy": { "retries": 1, "timeout_sec": 30, "novelty_guard": true }
}
```

## Output Schema

```json
{
  "session_id": "sess-00291",
  "facts": { "...": "...inherited from raw_facts" },
  "confidence": {
    "fasting_glucose_mg_dl": 0.98,
    "measurement_count": 0.85,
    "autoimmune_markers_present": 0.91
  },
  "unparsed_fragments": ["last Tuesday"],
  "low_confidence_fields": ["measurement_count"]
}
```

`low_confidence_fields` computed post-LLM: any field with score < 0.70.

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns scores outside 0.0–1.0 → clamp + warn (no STOP)
- LLM returns non-JSON after retry → `llm_output_invalid`
