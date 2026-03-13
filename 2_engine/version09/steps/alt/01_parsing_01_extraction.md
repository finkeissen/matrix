# Envelope: 01_parsing_01_extraction

**Parent step:** `01_parsing`
**Type:** `llm`
**Deterministic:** No
**Upstream:** raw user input
**Downstream:** `01_parsing_02_confidence`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "01_parsing_01_extraction",
  "parent_step": "01_parsing",
  "type": "llm",
  "inputs": {
    "raw_text_hash": "<sha256 of raw_text>",
    "session_id": "<session_id>"
  },
  "input_snapshot_id": null,
  "expected_outputs": [
    {
      "key": "raw_facts",
      "path": "runs/<run_id>/artifacts/01_parsing_01_extraction/raw_facts.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 30,
    "priority": "normal",
    "novelty_guard": true
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "initial_parse"
  }
}
```

## Output Schema

```json
{
  "session_id": "sess-00291",
  "raw_text_hash": "sha256:...",
  "facts": {
    "fasting_glucose_mg_dl": 148,
    "measurement_count": 2,
    "autoimmune_markers_present": false
  },
  "extracted": true
}
```

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- Input `raw_text` empty → `preflight_input_empty` (caught at preflight)
