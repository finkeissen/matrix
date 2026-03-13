# Step 07_examination_02 — Alternative Check
## Search for Better-Fitting AKU Candidates in Context

**Version:** 2.0.0
**Parent step:** `07_examination` (v1)
**Track:** All tracks
**Deterministic:** No (LLM — adversarial role)
**Upstream:** `07_examination_01_weakness_scan.md` → weakness assessments
**Downstream:** `08_finalization.md` (accept) or `04_hypothesis.md` (reject + retry)

---

## Why This Was Split

Searching for better alternatives requires the LLM to survey the full AKU context and reason comparatively — a different cognitive task from criterion-level weakness assessment. Combining both in one prompt causes the LLM to either miss alternatives or produce shallow weakness analysis.

---

## Single LLM Task

> **Given the current candidate and its weakness assessment, look at all other AKUs in the context. Is any of them a better or equally valid fit? Make a final accept/reject decision.**

---

## Contract

```
update(state, inputs={ candidate, weakness_scan, context_units }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `candidate` | `HypothesisResult` | Yes |
| `weakness_scan` | `WeaknessScanResult` | Yes — output of `07_examination_01` |
| `context_units` | `AKU[]` | Yes — full ranked context from `02_retrieval` |

Only called if `weakness_scan.routing == "proceed_to_alternative_check"`. If `routing == "reject"`, pipeline goes directly to `04_hypothesis` retry.

### Prompt (Full Template)

```
You are a comparative AKU evaluator. Determine if a better candidate exists.

CURRENT CANDIDATE: {candidate_id} — {candidate_title}
WEAKNESS SUMMARY: {weakness_summary}

OTHER AKUs IN CONTEXT:
{other_aku_titles_and_ids}

RULES:
1. For each other AKU, briefly assess: is it a better or equally valid match for the case facts?
2. If a better alternative exists, name it and explain why in one sentence.
3. Make a final decision: "accept" the current candidate or "reject" in favour of an alternative.
4. Flat JSON only.

OUTPUT FORMAT:
{
  "decision": "accept | reject",
  "better_alternatives": [
    { "aku_id": "<id>", "reason": "<one sentence>" }
  ],
  "decision_rationale": "<one sentence>"
}
```

### Output Schema

```json
{
  "candidate_id": "AKU-00123",
  "decision": "accept",
  "better_alternatives": [],
  "decision_rationale": "No other AKU in context satisfies more criteria than AKU-00123 given available facts."
}
```

or if a better alternative is found:

```json
{
  "candidate_id": "AKU-00123",
  "decision": "reject",
  "better_alternatives": [
    {
      "aku_id": "AKU-00125",
      "reason": "AKU-00125 (Pre-diabetes) matches more criteria given borderline glucose value and lacks the separate-day requirement."
    }
  ],
  "decision_rationale": "AKU-00125 is a stronger fit given the ambiguous measurement timing."
}
```

### Combined Examination Result (produced by this step)

This step assembles the final `ExaminationResult` from both sub-steps:

```json
{
  "candidate_id": "AKU-00123",
  "decision": "accept | reject",
  "weak_criteria": [...],
  "better_alternatives": [...],
  "decision_rationale": "string",
  "weakness_scan_id": "WS-00042",
  "examined_at": "2025-06-01T14:20:00Z"
}
```

### Routing

```
decision == "accept"
    → 08_finalization
      (better_alternatives surfaced as informational note, not substituted)

decision == "reject"
    | retry_count < 2   → 04_hypothesis with rejection context
    | retry_count >= 2  → 08_finalization with status: insufficient
```

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `ExaminationResult` | Always |
| `create` | `ReviewQueueEntry` | If decision is `accept` with non-empty `better_alternatives` |

### Report Fields

```json
{
  "status": "accepted | rejected | escalated",
  "decision": "accept",
  "better_alternatives_found": 0,
  "retry_count": 0
}
```

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM returns non-JSON | Retry once; then default to `accept` with warning |
| LLM rejects without naming alternative | Treat as `accept`; log as weak rejection |
| Max retries exceeded | Route to `08_finalization` with `status: insufficient` |

---

## Example

**Weakness scan result:** one `ambiguous` criterion (separate-day timing).

**Context contains:** AKU-00123 (T2DM), AKU-00125 (Pre-diabetes), AKU-00120 (parent concept)

**LLM assessment:**
- AKU-00125: fewer criteria match; lower glucose threshold only
- AKU-00120: parent concept only, not a diagnostic conclusion

**Decision:** `accept` AKU-00123 — no better alternative given current facts. `better_alternatives: []`.

**Passed to finalization:** `weak_criteria` from `07_01` included as `weak_points` in final answer.
