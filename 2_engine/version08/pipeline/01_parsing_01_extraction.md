# Step 01_parsing_01 — Fact Extraction
## Extract Raw Key-Value Facts from User Input

**Version:** 2.0.0
**Parent step:** `01_parsing` (v1)
**Track:** All tracks
**Deterministic:** No (LLM)
**Upstream:** Raw user text
**Downstream:** `01_parsing_02_confidence.md`

---

## Why This Was Split

In v1, `01_parsing` asked the LLM to simultaneously extract facts, assign confidence scores, normalize units, and identify unparsed fragments. For small local LLMs this causes dropped fields and inconsistent JSON. Extraction is now a single, isolated task: produce a flat key-value object from text. Nothing else.

---

## Single LLM Task

> **Extract every explicitly stated fact from the input as a flat key-value object. Do not infer. Do not score. Do not convert units.**

---

## Contract

```
update(state, inputs={ raw_text, session_id }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `raw_text` | string | Yes |
| `session_id` | string | Yes |
| `language` | string | No — ISO 639-1, default: auto-detect |

### Prompt (Full Template)

```
You are a fact extractor. Your only job is to extract explicitly stated facts.

INPUT:
{raw_text}

RULES:
1. Extract only facts explicitly stated. Do not infer or guess.
2. Output a flat JSON object. Keys are snake_case field names. Values are typed (number, boolean, string).
3. If a value has a unit attached, include the unit in the key name (e.g. glucose_mg_dl, not glucose).
4. Do not convert units. Do not add confidence scores. Do not explain.
5. If nothing can be extracted, output: {"extracted": false}

OUTPUT (JSON only, no other text):
```

### Output Schema

```json
{
  "session_id": "sess-00291",
  "raw_text_hash": "sha256:abc123",
  "facts": {
    "fasting_glucose_mg_dl": 148,
    "measurement_count": 2,
    "autoimmune_markers_present": false
  },
  "extracted": true
}
```

**Maximum output fields in `facts{}`: 20. Flat only — no nested objects.**

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `RawFacts` | Always |
| `update` | `RawFacts` | Re-run on same session + same input |

### Report Fields

```json
{
  "status": "ok | warn | error",
  "facts_count": 3,
  "extracted": true,
  "warnings": []
}
```

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Empty or whitespace input | `status: error`; no patches |
| LLM returns `{"extracted": false}` | `status: warn`; proceed with empty facts |
| LLM returns non-JSON | Retry once; then `status: error` |
| Nested objects in output | Strip nesting; flatten; log warning |

---

## Example

**Input:** `"Patient has fasting glucose of 148 mg/dL measured twice, no autoimmune markers."`

**Output `facts`:**
```json
{
  "fasting_glucose_mg_dl": 148,
  "measurement_count": 2,
  "autoimmune_markers_present": false
}
```

No unit conversion. No confidence. No interpretation.
