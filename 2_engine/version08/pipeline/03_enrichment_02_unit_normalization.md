# Step 03_enrichment_02 — Unit Normalization
## Convert Fact Values to Canonical Units via Rule Table

**Version:** 2.0.0
**Parent step:** `03_enrichment` (v1)
**Track:** All tracks
**Deterministic:** Yes (rule-based; no LLM)
**Upstream:** `03_enrichment_01_terminology.md` → mapped facts
**Downstream:** `03_enrichment_03_gap_detection.md`

---

## Why This Step Has No LLM

Unit conversion is purely arithmetic — applying a known factor to a known field. Involving an LLM introduces unnecessary non-determinism and potential rounding errors. This step is a deterministic lookup + multiply operation driven by a conversion rule table.

---

## Contract

```
update(state, inputs={ mapped_facts, conversion_rules }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `mapped_facts` | key-value object | Yes — output of `03_enrichment_01` |
| `conversion_rules` | `ConversionRule[]` | Yes — injected from ontology package |

### Conversion Rule Schema

```json
[
  {
    "canonical_field": "fasting_plasma_glucose_mmol_l",
    "from_unit_suffix": "_mg_dl",
    "multiply_by": 0.0555,
    "round_to": 2
  },
  {
    "canonical_field": "hba1c_mmol_mol",
    "from_unit_suffix": "_percent",
    "multiply_by": 10.929,
    "round_to": 1
  }
]
```

### Conversion Algorithm

```
for each fact_key in mapped_facts:
    for each rule in conversion_rules:
        if fact_key ends with rule.from_unit_suffix:
            canonical_key = rule.canonical_field
            canonical_value = round(fact_value * rule.multiply_by, rule.round_to)
            record conversion: { from_key, from_value, to_key, to_value, factor }
            replace fact entry
```

### Output Schema

```json
{
  "session_id": "sess-00291",
  "facts_normalized": {
    "fasting_plasma_glucose_mmol_l": 8.21,
    "hba1c_mmol_mol": 52.0,
    "autoimmune_markers_present": false
  },
  "conversions_applied": [
    {
      "from_key": "fasting_glucose_mg_dl",
      "from_value": 148,
      "to_key": "fasting_plasma_glucose_mmol_l",
      "to_value": 8.21,
      "factor": 0.0555
    }
  ],
  "unconverted_fields": []
}
```

`unconverted_fields`: fields where no matching rule was found (value retained as-is).

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `update` | `RawFacts` | If any conversion applied |
| `create` | `ReviewQueueEntry` | If `unconverted_fields` non-empty |

### Report Fields

```json
{
  "status": "ok | warn",
  "conversions_applied_count": 1,
  "unconverted_fields_count": 0,
  "warnings": []
}
```

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| No matching rule for a field | Retain original; add to `unconverted_fields`; warn |
| Rule table empty or not found | `status: error`; block step |
| Arithmetic overflow/underflow | Clamp to field range; log error |

---

## Example

**Input:** `{ "fasting_glucose_mg_dl": 148, "hba1c_percent": 6.9 }`

**Rules applied:**
- `148 mg/dL × 0.0555 = 8.21 mmol/L`
- `6.9% × 10.929 = 52.0 mmol/mol` (HbA1c IFCC conversion)

**Output `facts_normalized`:**
```json
{
  "fasting_plasma_glucose_mmol_l": 8.21,
  "hba1c_mmol_mol": 52.0
}
```
