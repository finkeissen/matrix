# Step 03_enrichment_01 — Terminology Mapping
## Map Colloquial Field Names to Ontology-Canonical Names

**Version:** 2.0.0
**Parent step:** `03_enrichment` (v1)
**Track:** All tracks
**Deterministic:** No (LLM)
**Upstream:** `01_parsing_02_confidence.md` → scored `raw_facts`
**Downstream:** `03_enrichment_02_unit_normalization.md`

---

## Why This Was Split

In v1, `03_enrichment` combined terminology mapping, unit conversion, deduplication, ambiguity resolution, and gap detection in one step. For small LLMs this is too many concerns. Terminology mapping is now isolated: given a fact key, find the correct canonical name from the ontology. Nothing else.

---

## Single LLM Task

> **For each fact key in the input, find the matching canonical field name from the provided ontology term list. If no match exists, keep the original key.**

---

## Contract

```
update(state, inputs={ raw_facts, ontology_terms }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `raw_facts` | `RawFacts` (with confidence) | Yes |
| `ontology_terms` | `string[]` | Yes — list of canonical field names from active ontology |

`ontology_terms` is a flat list injected from the ontology package at runtime, e.g.:
```json
["fasting_plasma_glucose_mmol_l", "hba1c_mmol_mol", "ogtt_2h_glucose_mmol_l", "autoimmune_markers_present", ...]
```

### Prompt (Full Template)

```
You are a terminology mapper. Map each input key to the correct canonical term.

CANONICAL TERMS (complete list):
{ontology_terms_list}

INPUT KEYS TO MAP:
{fact_keys_list}

RULES:
1. For each input key, find the single best matching canonical term.
2. If no canonical term matches, output the original key unchanged.
3. Output a flat JSON object: { "input_key": "canonical_key", ... }
4. Do not change values. Do not convert units. Do not explain.

OUTPUT (JSON only):
```

### Output Schema

```json
{
  "session_id": "sess-00291",
  "mappings": {
    "fasting_glucose_mg_dl": "fasting_plasma_glucose_mmol_l",
    "measurement_count": "measurement_count",
    "autoimmune_markers_present": "autoimmune_markers_present"
  },
  "unmapped_keys": []
}
```

`unmapped_keys`: fact keys for which no canonical term was found (original key retained).

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `update` | `RawFacts` | Always — renames keys per mapping |
| `create` | `ReviewQueueEntry` | If `unmapped_keys` non-empty |

### Report Fields

```json
{
  "status": "ok | warn",
  "keys_mapped": 1,
  "keys_unchanged": 2,
  "unmapped_keys": [],
  "warnings": []
}
```

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM maps to a term not in `ontology_terms` | Reject mapping; retain original key; add to `unmapped_keys` |
| LLM returns non-JSON | Retry once; then retain all original keys |
| Ontology terms list empty | `status: error`; block step |

---

## Example

**Input keys:** `["blood sugar", "hba1c_percent", "autoimmune_markers_present"]`

**Ontology terms include:** `fasting_plasma_glucose_mmol_l`, `hba1c_mmol_mol`, `autoimmune_markers_present`

**Output mappings:**
```json
{
  "blood sugar": "fasting_plasma_glucose_mmol_l",
  "hba1c_percent": "hba1c_mmol_mol",
  "autoimmune_markers_present": "autoimmune_markers_present"
}
```

Note: the value `hba1c_percent` is still in % at this point. Unit conversion happens in the next step.
