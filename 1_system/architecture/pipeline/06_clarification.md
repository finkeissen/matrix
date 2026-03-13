# Step 06 — Clarification Loop
## Generate Targeted Questions for Missing Case Facts

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** No (LLM-based question generation)
**Upstream:** `05_validation.md` → `validation_report` (when `clarification_required: true`)
**Downstream:** `01_parsing.md` (re-entry with user response)

---

## Purpose

When the validation engine identifies **missing required facts**, this step generates precise, answerable clarification questions — one per missing criterion — and returns them to the user. The user's response re-enters the pipeline at Step 01.

This step does not guess, infer, or fill in missing values. It only asks.

---

## Contract

```
update(state, inputs={ validation_report, enriched_context }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `validation_report` | `ValidationReport` | Yes | Output of Step 05, with `clarification_required: true`. |
| `enriched_context` | `EnrichedContext` | Yes | For terminology alignment in question phrasing. |
| `prior_clarifications` | `ClarificationRecord[]` | No | Previous rounds in this session; prevents duplicate questions. |

### Question Generation Rules

The LLM generating clarification questions must:

1. Produce **one question per missing criterion**, no more.
2. Each question must be answerable with **structured data** (numeric value, yes/no, date, selection from defined options).
3. Questions must use **domain-canonical terminology** aligned to AKU criteria fields.
4. Questions must not reveal the candidate AKU ID or internal system structure to the user.
5. If a missing criterion has been asked in a prior round and not answered, flag as `unresolved` rather than re-asking identically.

### Output Schema — `clarification_request`

```json
{
  "session_id": "sess-00291",
  "round": 2,
  "candidate_id": "AKU-00123",
  "questions": [
    {
      "id": "CQ-001",
      "criterion_ref": "measurement_count >= 2 on separate occasions",
      "question": "Was the fasting blood glucose measurement confirmed on a second, separate day?",
      "answer_type": "yes_no",
      "options": null,
      "required": true
    },
    {
      "id": "CQ-002",
      "criterion_ref": "ogtt_2h_glucose_mmol_l",
      "question": "Has a 2-hour oral glucose tolerance test (OGTT) been performed? If yes, what was the result in mmol/L?",
      "answer_type": "numeric_or_na",
      "options": null,
      "required": false
    }
  ],
  "created_at": "2025-06-01T14:10:00Z"
}
```

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `ClarificationRequest` | Always |
| `update` | `SessionRecord` | Increment clarification round counter |

### Report Fields

```json
{
  "status": "ok",
  "questions_generated": 2,
  "round": 2,
  "unresolved_from_prior_round": 0
}
```

---

## Re-entry Flow

```
Step 05 (validation_report.clarification_required = true)
    │
    ▼
Step 06 → ClarificationRequest → User Interface
                                       │
                               User answers question(s)
                                       │
                                       ▼
                              Step 01 (re-parse with
                              original input + new answers)
                                       │
                                       ▼
                              Steps 02–05 re-executed
                              with enriched case facts
```

---

## Clarification Limits

| Limit | Value | Behavior on Breach |
|-------|-------|--------------------|
| Max clarification rounds per session | 3 | Route to finalization with `status: insufficient_facts` |
| Max questions per round | 5 | Prioritize by `required: true`; drop lower-priority questions |
| Max unresolved criteria across rounds | 2 | Route to finalization with partial result + uncertainty flag |

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| No missing criteria in validation report | `status: error`; this step should not have been invoked. |
| All missing criteria already asked (unresolved) | `status: warn`; return summary of unresolved items; route to finalization. |
| Max rounds exceeded | Route to `08_finalization` with `status: insufficient_facts`. |

---

## Example

**Validation report says:**
> `missing_required: ["Second fasting glucose measurement not documented"]`

**Generated question:**
> "Was the fasting blood glucose measurement confirmed on a second, separate day?"
> Answer type: Yes / No / Not yet performed

**User replies:** "Yes, measured again three days later — same result."

**Re-parsed fact added:** `measurement_count: 2`, `measurement_days_apart: 3`

**Validation re-run:** `missing_required: []` → candidate accepted → forward to Step 07.
