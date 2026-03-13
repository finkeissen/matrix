# Step 03 — Entity Enrichment
## Normalize, Deduplicate, and Enrich Retrieved Entities

**Version:** 1.0.0
**Track:** Problems Track, Solutions Track
**Deterministic:** No (LLM-assisted normalization)
**Upstream:** `02_retrieval.md` → `context_units[]`
**Downstream:** `04_hypothesis.md`

---

## Purpose

Before hypothesis generation, the retrieved AKU context is **normalized and enriched**: units of measure are standardized, terminology is aligned to the domain ontology, and potential duplicates within the context window are flagged. This step does not add new AKUs — it cleans and consolidates what retrieval returned.

Enrichment also resolves **surface-level ambiguities** in case facts that would otherwise cause incorrect criteria matching downstream (e.g., "blood sugar" → `fasting_plasma_glucose_mmol_l`).

---

## Contract

```
update(state, inputs={ case_facts, context_units }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_facts` | `ParsedFacts` | Yes | Output of Step 01. |
| `context_units` | `AKU[]` | Yes | Output of Step 02. |
| `ontology_package` | string | No | Ontology to use for terminology normalization. Default: active package. |

### Enrichment Operations

| Operation | Description |
|-----------|-------------|
| **Unit normalization** | Convert all fact values to canonical units declared in the ontology (e.g., mg/dL → mmol/L). Record conversion factor. |
| **Terminology alignment** | Map colloquial terms in case facts to ontology-canonical field names. |
| **Deduplication** | Identify AKUs in context that are structurally equivalent or near-duplicate. Flag for review if confidence < threshold. |
| **Ambiguity resolution** | For case facts with low parse confidence, attempt to resolve against AKU criteria terminology. |
| **Gap detection** | Identify criteria fields in retrieved AKUs for which no corresponding case fact exists. Pre-populate `missing_fields[]` for Step 05. |

### Outputs — `enriched_context`

```json
{
  "case_facts_normalized": {
    "fasting_plasma_glucose_mmol_l": 8.2,
    "hba1c_mmol_mol": 52,
    "measurement_count": 2,
    "autoimmune_markers_present": false
  },
  "unit_conversions_applied": [
    { "field": "hba1c_mmol_mol", "from": "%" , "to": "mmol/mol", "factor": 10.929 }
  ],
  "context_units_enriched": [...],
  "duplicate_flags": [],
  "missing_fields_preview": [
    "ogtt_2h_glucose_mmol_l"
  ]
}
```

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `update` | `ParsedFacts` | If normalization changes any field value |
| `create` | `EnrichmentResult` | Always |
| `create` | `ReviewQueueEntry` | If deduplication confidence < 0.80 |

### Report Fields

```json
{
  "status": "ok | warn",
  "normalizations_applied": 1,
  "terminology_mappings": 2,
  "duplicates_flagged": 0,
  "missing_fields_count": 1,
  "warnings": []
}
```

---

## Deduplication Threshold

| Confidence | Action |
|------------|--------|
| ≥ 0.95 | Auto-merge duplicate AKUs in context |
| 0.80–0.94 | Flag; proceed with both; add review queue entry |
| < 0.80 | Keep both; add high-priority review queue entry |

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| No normalization rules for detected unit | `status: warn`; retain original value; flag field. |
| Ontology package not found | `status: error`; block step. |
| All case facts already canonical | `status: ok`; no patches produced; proceed. |

---

## Re-entry Behavior

Fingerprint is computed over `(session_id, sha256(case_facts), sha256(context_unit_ids))`. Re-running with unchanged inputs produces no new patches.

---

## Example

**Input fact:** `"blood sugar": "148 mg/dL"`
**Terminology mapping:** `"blood sugar"` → `fasting_plasma_glucose_mmol_l`
**Unit conversion:** 148 mg/dL × 0.0555 = `8.2 mmol/L`
**Output:** `"fasting_plasma_glucose_mmol_l": 8.2` with `conversion_recorded: true`
