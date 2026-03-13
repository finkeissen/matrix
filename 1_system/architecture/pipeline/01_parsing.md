# Step 01 — Semantic Parsing
## Extract Structured Case Facts from User Input

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** No (LLM-based)
**Upstream:** User input (raw text)
**Downstream:** `02_retrieval.md`

---

## Purpose

Transform unstructured or semi-structured user input into a normalized, machine-readable set of **case facts** that can be matched against AKU criteria.

The parser does not reason, classify, or retrieve — it only extracts and normalizes.

---

## Contract

```
update(state, inputs={ raw_text }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `raw_text` | string | Yes | The user's original input, unmodified. |
| `session_id` | string | Yes | Links this run to a conversation or request context. |
| `language` | string | No | ISO 639-1 code. Default: auto-detect. |

### Outputs — `case_facts`

```json
{
  "session_id": "sess-00291",
  "raw_text": "Patient has fasting glucose of 8.2 mmol/L measured twice, no autoimmune markers.",
  "facts": {
    "fasting_glucose_mmol_l": 8.2,
    "measurement_count": 2,
    "autoimmune_markers_present": false
  },
  "confidence": {
    "fasting_glucose_mmol_l": 0.98,
    "measurement_count": 0.85,
    "autoimmune_markers_present": 0.91
  },
  "unparsed_fragments": [],
  "language_detected": "en",
  "parsed_at": "2025-06-01T14:00:00Z"
}
```

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `ParsedFacts` | Always (new parse) |
| `update` | `ParsedFacts` | Re-run on same session |

### Report Fields

```json
{
  "status": "ok | warn | error",
  "facts_extracted": 3,
  "low_confidence_fields": [],
  "unparsed_fragments": [],
  "warnings": []
}
```

---

## Prompt Constraints

The LLM invoked at this step must:

1. Extract only facts explicitly stated in the input. No inference.
2. Express each fact as a typed key-value pair.
3. Assign a confidence score (0.0–1.0) per extracted field.
4. List any input fragments it could not parse as `unparsed_fragments`.
5. Normalize units (e.g., mg/dL → mmol/L) and record the conversion.

**Prohibited:** The parser must not propose candidates, apply rules, or reference AKU IDs.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Input is empty or whitespace | `status: error`; do not produce patches. |
| No facts extractable | `status: warn`; produce empty `facts: {}`; proceed to retrieval with empty context. |
| Low confidence on all fields (< 0.5) | `status: warn`; include `review_queue` entry. |
| Language not supported | `status: error`; return structured error with detected language code. |

---

## Re-entry Behavior

Re-running this step on the same `session_id` and `raw_text` produces an `update` patch (not a duplicate `create`). Fingerprint is computed over `(session_id, sha256(raw_text))`.

---

## Example

**Input:**
> "The patient's HbA1c came back at 52 mmol/mol last Tuesday. No prior diabetes diagnosis."

**Output `facts`:**
```json
{
  "hba1c_mmol_mol": 52,
  "prior_diabetes_diagnosis": false,
  "measurement_recency": "recent"
}
```
**Confidence:** `hba1c_mmol_mol: 0.99`, `prior_diabetes_diagnosis: 0.88`, `measurement_recency: 0.60`

`measurement_recency` is flagged as low-precision (relative date) and added to `unparsed_fragments` for potential clarification.
