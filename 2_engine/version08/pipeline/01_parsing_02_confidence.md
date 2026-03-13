# Step 01_parsing_02 — Confidence Scoring
## Score Extraction Confidence per Field and Flag Unparsed Fragments

**Version:** 2.0.0
**Parent step:** `01_parsing` (v1)
**Track:** All tracks
**Deterministic:** No (LLM)
**Upstream:** `01_parsing_01_extraction.md` → `raw_facts`
**Downstream:** `02_retrieval.md`

---

## Why This Was Split

Confidence scoring requires the LLM to reason about each extracted field independently — assessing whether the source text clearly supports the value, or whether the extraction was ambiguous. Combining this with extraction in a single prompt causes both tasks to degrade: values get incorrectly scored and scores get attached to the wrong fields.

---

## Single LLM Task

> **For each extracted fact, assign a confidence score based on how clearly the source text supports it. List any input fragments that could not be mapped to any fact.**

---

## Contract

```
update(state, inputs={ raw_facts, raw_text }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `raw_facts` | `RawFacts` | Yes — output of `01_parsing_01` |
| `raw_text` | string | Yes — original text for reference |

### Prompt (Full Template)

```
You are a confidence scorer. You have been given extracted facts and the original text.

ORIGINAL TEXT:
{raw_text}

EXTRACTED FACTS:
{facts_json}

RULES:
1. For each fact key, assign a confidence score from 0.0 to 1.0.
   - 1.0 = explicitly and unambiguously stated in the text
   - 0.7-0.9 = stated but with minor ambiguity (relative date, approximate value)
   - 0.4-0.6 = implied or partially stated
   - < 0.4 = weak inference; likely should not have been extracted
2. List any text fragments that were not captured in any fact as "unparsed_fragments".
3. Output flat JSON only. No explanation.

OUTPUT FORMAT:
{
  "confidence": { "<key>": <score>, ... },
  "unparsed_fragments": ["<fragment>", ...]
}
```

### Output Schema

```json
{
  "session_id": "sess-00291",
  "confidence": {
    "fasting_glucose_mg_dl": 0.98,
    "measurement_count": 0.85,
    "autoimmune_markers_present": 0.91
  },
  "unparsed_fragments": [
    "last Tuesday"
  ],
  "low_confidence_fields": ["measurement_count"]
}
```

`low_confidence_fields` is computed post-LLM: any field with score < 0.70.

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `update` | `RawFacts` | Always — adds confidence + unparsed_fragments |
| `create` | `ReviewQueueEntry` | If any field confidence < 0.50 |

### Report Fields

```json
{
  "status": "ok | warn",
  "fields_scored": 3,
  "low_confidence_count": 1,
  "unparsed_fragments_count": 1,
  "warnings": []
}
```

---

## Downstream Use of Confidence

| Score Range | Used By |
|-------------|---------|
| < 0.50 | Review queue; flagged in final output |
| 0.50–0.74 | `07_examination_01` checks for weak criteria relying on these |
| ≥ 0.75 | Treated as reliable by validation engine |

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM returns scores outside 0.0–1.0 | Clamp to range; log warning |
| LLM omits a field present in `raw_facts` | Assign default score 0.5; log warning |
| LLM returns non-JSON | Retry once; then assign 0.5 to all fields |

---

## Example

**Input facts:** `{ "fasting_glucose_mg_dl": 148, "measurement_count": 2 }`
**Input text:** `"glucose of 148 mg/dL measured twice last Tuesday"`

**Output:**
```json
{
  "confidence": {
    "fasting_glucose_mg_dl": 0.98,
    "measurement_count": 0.85
  },
  "unparsed_fragments": ["last Tuesday"]
}
```

`measurement_count` scores 0.85 because "twice" is slightly informal — not a precise lab count. `last Tuesday` is flagged as unparsed since it has no corresponding fact field.
