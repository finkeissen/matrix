# Envelope: 02_retrieval

**Type:** `deterministic`
**Upstream:** `01_parsing_02_confidence` → `scored_facts`
**Downstream:** `03_enrichment_01_terminology`, `04_hypothesis`

---

## TaskEnvelope

```json
{
  "step": "02_retrieval",
  "parent_step": "02_retrieval",
  "type": "deterministic",
  "inputs": {
    "scored_facts_hash": "<sha256>",
    "kb_snapshot_id": "SNAP-00189",
    "top_k": 15,
    "domain_filter": ["endocrinology"]
  },
  "input_snapshot_id": "SNAP-00189",
  "expected_outputs": [
    {
      "key": "context_units",
      "path": "runs/<run_id>/artifacts/02_retrieval/context_units.json",
      "required": true
    }
  ],
  "policy": { "retries": 0, "timeout_sec": 5000, "novelty_guard": false }
}
```

## Output Schema

```json
{
  "kb_snapshot_id": "SNAP-00189",
  "embedding_model": "text-embedding-3-large@2024-09",
  "top_k_returned": 12,
  "units": [
    {
      "aku_id": "AKU-00123",
      "rank": 1,
      "score": 0.94,
      "breadcrumb": ["AKU-00100", "AKU-00120", "AKU-00123"],
      "required_criteria": ["..."],
      "exclusion_criteria": ["..."]
    }
  ]
}
```

## Content State on Completion
`candidate`

## Special Routing
- `top_k_returned == 0` → STOP: route to `08_finalization` with `status: no_knowledge`

## STOP Conditions
- KB snapshot not found → `preflight_snapshot_missing`
- Embedding model unavailable → `deterministic_step_error`
