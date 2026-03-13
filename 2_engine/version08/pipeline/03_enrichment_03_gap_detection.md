# Step 03_enrichment_03 — Gap Detection
## Identify AKU Criteria Fields Missing from Case Facts

**Version:** 2.0.0
**Parent step:** `03_enrichment` (v1)
**Track:** All tracks
**Deterministic:** No (LLM — semantic matching of criteria to facts)
**Upstream:** `03_enrichment_02_unit_normalization.md` → `facts_normalized`
**Downstream:** `04_hypothesis.md`

---

## Why This Was Split

Gap detection requires understanding whether a natural-language criterion string maps to any available case fact. This is a semantic matching task — different from terminology mapping (exact key matching) and unit conversion (arithmetic). Isolating it gives the LLM a single, well-scoped job.

---

## Single LLM Task

> **For each AKU criterion in the context, determine whether the normalized case facts contain a value that could satisfy it. List criteria that have no matching fact.**

---

## Contract

```
update(state, inputs={ facts_normalized, context_units }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `facts_normalized` | key-value object | Yes — output of `03_enrichment_02` |
| `context_units` | `AKU[]` | Yes — output of `02_retrieval` |

### Prompt (Full Template)

```
You are a gap detector. Identify which AKU criteria cannot be evaluated because the required fact is missing.

AVAILABLE FACTS (keys only):
{fact_keys_list}

AKU CRITERIA TO CHECK:
{criteria_list_with_aku_ids}

RULES:
1. For each criterion, decide: is there a fact key that could supply the required value?
2. If yes: mark as "covered".
3. If no: mark as "missing" and name the fact field that would be needed.
4. Output flat JSON only. No explanation.

OUTPUT FORMAT:
{
  "covered": ["<criterion_string>", ...],
  "missing": [
    { "criterion": "<criterion_string>", "aku_id": "<id>", "needed_field": "<field_name>" },
    ...
  ]
}
```

### Output Schema

```json
{
  "session_id": "sess-00291",
  "covered": [
    "Fasting plasma glucose >= 7.0 mmol/L on two separate occasions",
    "autoimmune_markers_present == false"
  ],
  "missing": [
    {
      "criterion": "2-hour plasma glucose >= 11.1 mmol/L during OGTT",
      "aku_id": "AKU-00123",
      "needed_field": "ogtt_2h_glucose_mmol_l"
    }
  ]
}
```

This `missing[]` list is passed directly to `05_validation` as a pre-computed hint, reducing the validation engine's work and improving clarification question quality in `06_clarification`.

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `update` | `EnrichedContext` | Always — adds gap list |

### Report Fields

```json
{
  "status": "ok | warn",
  "criteria_covered": 2,
  "criteria_missing": 1,
  "warnings": []
}
```

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM marks criterion as covered incorrectly | Validation engine (05) will catch it deterministically |
| LLM returns non-JSON | Retry once; then proceed with empty gap list |
| No criteria in context | `status: warn`; proceed with empty gap list |

---

## Note on LLM Errors Here

This step's output is a **hint**, not a gate. If the LLM incorrectly classifies a gap, the deterministic validation engine in Step 05 will surface the actual missing criteria. The gap list accelerates validation and improves clarification questions — it does not replace validation.

---

## Example

**Available fact keys:** `["fasting_plasma_glucose_mmol_l", "hba1c_mmol_mol", "autoimmune_markers_present"]`

**AKU-00123 criteria:**
1. `Fasting plasma glucose >= 7.0 mmol/L` → `fasting_plasma_glucose_mmol_l` present → **covered**
2. `HbA1c >= 48 mmol/mol` → `hba1c_mmol_mol` present → **covered**
3. `2-hour OGTT >= 11.1 mmol/L` → no matching key → **missing**, needed: `ogtt_2h_glucose_mmol_l`
