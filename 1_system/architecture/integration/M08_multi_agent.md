# M08 — Multi-Agent Self-Correction
## Adversarial Verification and Bias Reduction

**Layer:** Orchestration
**Version:** 2.0.0
**Deterministic:** No (LLM-based; adversarial role)
**Depends on:** M06 (validation), M07 (orchestrator)
**Used by:** Pipeline after M06 produces `valid: true`
**Pipeline steps:** 04_hypothesis (generator), 07_examination (examiner)

---

## Purpose

Reduce single-pass confirmation bias by separating **hypothesis generation** from **hypothesis examination** into distinct agents with opposing roles. The generator proposes; the examiner challenges.

This module implements the "adversarial verification" level of the maturity model (Level 4).

---

## Motivation

A single LLM pass is subject to self-confirmation bias: the model tends to construct a justification for its first candidate rather than rigorously testing it. Multi-agent separation enforces an adversarial check by ensuring the examiner has no access to the generator's confidence or internal reasoning — only the hypothesis and the validation report.

---

## Agent Roles

| Agent | Role | Stance | May See |
|-------|------|--------|---------|
| **Generator (A)** | Propose candidate AKU(s) with criteria mapping | Constructive | `case_facts`, `context_units[]` |
| **Rule Engine** | Deterministic validation (M06) | Neutral / strict | `candidate`, `case_facts`, KB snapshot |
| **Examiner (B)** | Stress-test the validated candidate | Adversarial | `candidate`, `validation_report` (not generator's reasoning) |
| **Finalizer** | Consolidate result + uncertainty + alternatives | Neutral | All prior outputs |

The Examiner does **not** receive the Generator's confidence scores or rationale. It starts from the validation report only.

---

## Correction Loop

```
Generator (M07/Role 3)
    |
    v
Rule Engine (M06)
    |
    +--> [invalid] --> Clarification (06) or Rejection
    |
    +--> [valid]
         |
         v
    Examiner (M07/adversarial prompt)
         |
         +--> [accept] --> Finalizer (08_finalization)
         |
         +--> [reject] --> Generator retry (with rejection context)
                              |
                         [retry_count < 2]
                              |
                         retry loop
                              |
                         [retry_count >= 2]
                              |
                         Finalizer with status: insufficient
```

Maximum correction iterations: **2**. After 2 failed examinations, the pipeline does not loop indefinitely — it finalizes with the best available candidate and flags the uncertainty.

---

## Examiner Prompt (Full Pattern)

```
You are a strict criteria examiner. Your role is adversarial -- find reasons to reject.

You have been given:
- Candidate AKU: {candidate_id} -- {candidate_title}
- Matched criteria (from validation): {matched_required}
- Validation report: {validation_report_summary}
- Available AKU context: {context_units_titles_and_ids}

Your tasks:
1. Identify any matched criterion that is weakly or ambiguously supported by the case facts.
   Weak support means: value is at boundary, measurement method is unclear,
   measurement timing is ambiguous, or supporting evidence is indirect.
2. Check whether any matched criterion relies on a case fact with confidence < 0.75.
3. Identify any alternative AKU in the context that may be an equal or better fit.
4. If you find grounds for rejection, state them explicitly with criterion references.
5. If you find no grounds for rejection, explicitly confirm acceptance with reasoning.

Do not be lenient. If in doubt, reject and request a stronger mapping.
```

---

## Examiner Output Schema

```json
{
  "candidate_id": "AKU-00123",
  "decision": "accept | reject",
  "weak_criteria": [
    {
      "criterion": "string",
      "issue": "string",
      "severity": "low | medium | high"
    }
  ],
  "better_alternatives": [
    {
      "aku_id": "AKU-00125",
      "reason": "string"
    }
  ],
  "low_confidence_facts_used": ["field_name"],
  "decision_rationale": "string"
}
```

---

## Severity-Based Routing

| Severity | Decision | Action |
|----------|----------|--------|
| All `low` | Accept | Include weak criteria in finalization output |
| Any `medium` | Accept | Add review queue entry; surface in output |
| Any `high` | Reject | Return to Generator with rejection context |
| No weak criteria | Accept | Full confidence |

---

## Retry Context Injection

When the Examiner rejects, the Generator receives:

```json
{
  "retry_context": {
    "retry_count": 1,
    "prior_candidate_id": "AKU-00123",
    "rejection_reason": "Criterion 'measurement on separate calendar day' weakly supported",
    "flagged_criterion": "measurement_count >= 2 on separate occasions",
    "instruction": "Propose an alternative candidate or provide a stronger mapping for the flagged criterion."
  }
}
```

---

## Alternative Surfacing

If the Examiner identifies a `better_alternative`, it is:
- **Not** automatically substituted for the current candidate.
- Passed to the Finalizer as an `alternatives[]` entry in the output.
- Surfaced to the user as a note: "An alternative interpretation was identified."

This preserves transparency — the system does not silently switch candidates.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Examiner returns malformed output | Retry once; then escalate to review queue; proceed with `status: unexamined` |
| Examiner rejects on `low` severity only | Override to accept; log override |
| Max retries exceeded | Finalize with best candidate + `status: insufficient` |
| Generator returns `NO_MATCH` on retry | Finalize with `status: no_match` |
