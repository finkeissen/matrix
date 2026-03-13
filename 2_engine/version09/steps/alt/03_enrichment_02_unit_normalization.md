# Envelope: 03_enrichment_02_unit_normalization

**Parent step:** `03_enrichment`
**Type:** `deterministic`
**Upstream:** `03_enrichment_01_terminology` → `mapped_facts`
**Downstream:** `03_enrichment_03_gap_detection`

---

## TaskEnvelope

```json
{
  "step": "03_enrichment_02_unit_normalization",
  "parent_step": "03_enrichment",
  "type": "deterministic",
  "inputs": {
    "mapped_facts_hash": "<sha256>",
    "conversion_rules_hash": "<sha256 of rule table>"
  },
  "expected_outputs": [
    {
      "key": "normalized_facts",
      "path": "runs/<run_id>/artifacts/03_enrichment_02_unit_normalization/normalized_facts.json",
      "required": true
    }
  ],
  "policy": { "retries": 0, "timeout_sec": 5, "novelty_guard": false }
}
```

## Output Schema

```json
{
  "facts_normalized": {
    "fasting_plasma_glucose_mmol_l": 8.21,
    "hba1c_mmol_mol": 52.0,
    "autoimmune_markers_present": false
  },
  "conversions_applied": [
    { "from_key": "fasting_glucose_mg_dl", "from_value": 148,
      "to_key": "fasting_plasma_glucose_mmol_l", "to_value": 8.21, "factor": 0.0555 }
  ],
  "unconverted_fields": []
}
```

## STOP Conditions
- Conversion rule table missing → `deterministic_step_error`
