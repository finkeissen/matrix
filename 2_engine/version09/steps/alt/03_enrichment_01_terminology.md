# Envelope: 03_enrichment_01_terminology

**Parent step:** `03_enrichment`
**Type:** `llm`
**Upstream:** `01_parsing_02_confidence` → `scored_facts`
**Downstream:** `03_enrichment_02_unit_normalization`

---

## TaskEnvelope

```json
{
  "step": "03_enrichment_01_terminology",
  "parent_step": "03_enrichment",
  "type": "llm",
  "inputs": {
    "scored_facts_hash": "<sha256>",
    "ontology_terms_hash": "<sha256 of active ontology term list>"
  },
  "expected_outputs": [
    {
      "key": "mapped_facts",
      "path": "runs/<run_id>/artifacts/03_enrichment_01_terminology/mapped_facts.json",
      "required": true
    }
  ],
  "policy": { "retries": 1, "timeout_sec": 30, "novelty_guard": true }
}
```

## Output Schema

```json
{
  "mappings": {
    "blood sugar": "fasting_plasma_glucose_mmol_l",
    "hba1c_percent": "hba1c_mmol_mol",
    "autoimmune_markers_present": "autoimmune_markers_present"
  },
  "facts_remapped": {
    "fasting_plasma_glucose_mmol_l": 148,
    "hba1c_mmol_mol": 6.9,
    "autoimmune_markers_present": false
  },
  "unmapped_keys": []
}
```

## STOP Conditions
- Ontology terms list empty → `deterministic_step_error`
- LLM returns non-JSON after retry → `llm_output_invalid`
