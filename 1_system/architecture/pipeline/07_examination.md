# Step 07 — Adversarial Examination
## Stress-Test the Validated Candidate

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** No (LLM-based; adversarial role)
**Upstream:** `05_validation.md` -> `validation_report` (valid candidate only)
**Downstream:** `08_finalization.md` (accepted) or `04_hypothesis.md` (rejected, retry)

---

## Purpose

Apply **adversarial scrutiny** to a candidate that has passed deterministic validation. The examiner's role is to find reasons to reject, not to confirm. This reduces single-pass confirmation bias and catches cases where criteria were technically satisfied but weakly supported.

The examiner is a separate LLM invocation with an explicitly adversarial system prompt. It has no knowledge of the generator's confidence or rationale beyond what is in the validation report.

---

## Contract

```
update(state, inputs={ candidate, validation_report, enriched_context }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `candidate` | `HypothesisResult` | Yes | Output of Step 04. |
| `validation_report` | `ValidationReport` | Yes | Output of Step 05 (must have `valid: true`). |
| `enriched_context` | `EnrichedContext` | Yes | Output of Step 03. |
| `retry_count` | int | No | Current retry iteration (0, 1, or 2). |

### Examiner Prompt Pattern

```
You are a strict criteria examiner. Your role is adversarial -- find reasons to reject.

You have been given:
- Candidate: {candidate_id}
- Matched criteria: {matched_criteria}
- Validation report: {validation_report}
- Available AKU context: {context_units}

Your tasks:
1. Identify any criterion marked as "matched" that is weakly or ambiguously supported
   by the case facts. Weak support: value is at boundary, measurement method is unclear,
   or supporting evidence is indirect.
2. Identify any alternative AKU in the context that may be an equal or better fit.
3. Check whether any matched criterion relies on a case fact with confidence < 0.75.
4. If you find grounds for rejection, state them explicitly with criterion references.
5. If you find no grounds for rejection, explicitly confirm acceptance.

Do not be lenient. If in doubt, reject and request stronger mapping or alternative.
```

### Output Schema

```json
{
  "candidate_id": "AKU-00123",
  "decision": "accept | reject",
  "weak_criteria": [
    {
      "criterion": "measurement_count >= 2 on separate occasions",
      "issue": "Case facts confirm count=2 but do not specify separate calendar days.",
      "severity": "medium"
    }
  ],
  "better_alternatives": [],
  "low_confidence_facts_used": [],
  "decision_rationale": "Accept with medium confidence. Flag measurement_days_apart for documentation."
}
```

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `ExaminationResult` | Always |
| `create` | `ReviewQueueEntry` | If `weak_criteria` non-empty and decision is `accept` |

---

## Retry Logic

```
decision == "accept"           -> forward to 08_finalization
decision == "reject"
    | retry_count < 2          -> return to 04_hypothesis with rejection context
    | retry_count >= 2         -> forward to 08_finalization with status: insufficient
```

## Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| `low` | Minor ambiguity | Accept; note in output |
| `medium` | Ambiguity could affect edge cases | Accept; add review queue entry |
| `high` | Ambiguity materially undermines match | Reject; return to hypothesis |

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Malformed examiner output | Retry once; then escalate to review queue |
| Better alternative identified | Accept current; surface alternative in finalization |
| Max retries exceeded | Forward to finalization with `status: insufficient` |
