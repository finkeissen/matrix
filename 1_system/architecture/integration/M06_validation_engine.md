# M06 — Validation Engine
## Deterministic, Non-Bypassable Criteria Checking

**Layer:** Validation
**Version:** 2.0.0
**Deterministic:** Yes (rule engine; no LLM)
**Depends on:** M01 (AKU schema), M02 (knowledge store)
**Used by:** M07 (orchestrator routes candidates here), M08 (multi-agent)
**Pipeline steps:** 05_validation

---

## Purpose

Apply **deterministic rule checks** to every candidate proposed by the LLM. The validation engine is the system's integrity gate — it cannot be bypassed, overridden, or reasoned around by any language model.

A candidate is accepted if and only if it satisfies the formal acceptance condition. All other outcomes produce a structured report used to route the pipeline to clarification, retry, or rejection.

---

## Core Invariant

**The LLM cannot override this module.** A statistically plausible answer that fails validation is rejected. Probability is not a substitute for rule compliance.

---

## Validation Checks

Checks are executed in order. The first failure determines the report outcome for that check category; remaining checks still run to produce a complete report.

### Check 1 — Required Criteria

For each criterion in `aku.required_criteria`:
- Is there a corresponding case fact that satisfies it?
- Does the fact value meet the threshold/condition stated in the criterion?

Any unsatisfied criterion is added to `missing_required`.

### Check 2 — Exclusion Criteria

For each criterion in `aku.exclusion_criteria`:
- Does any case fact match this exclusion?

Any matched exclusion is added to `violated_exclusions`. This is a hard rejection.

### Check 3 — Structural Consistency

- Does the candidate AKU's parent relationship hold with respect to the case facts' domain context?
- Are sibling constraints respected (e.g., if a sibling is a mutual exclusion)?

Any violation is added to `structural_issues`.

### Check 4 — Conflict Check

- Does selecting this AKU trigger any `conflicts_with` relation?
- Cross-reference all AKU IDs in `context_units[]` against the candidate's `conflicts_with` list.

Any triggered conflict is added to `conflicts`.

---

## Acceptance Condition (Formal)

```
Accept(candidate) ⟺
    missing_required     = ∅
  ∧ violated_exclusions  = ∅
  ∧ structural_issues    = ∅
  ∧ conflicts            = ∅
```

All four sets must be empty simultaneously.

---

## Validation Report Schema

```json
{
  "candidate_id": "AKU-00123",
  "kb_snapshot_id": "SNAP-00189",
  "valid": false,
  "matched_required": [
    "fasting_plasma_glucose_mmol_l >= 7.0: satisfied (value=8.2, count=2)",
    "autoimmune_markers_present == false: satisfied"
  ],
  "missing_required": [
    "Second measurement must be on a separate calendar day: not documented in case facts"
  ],
  "violated_exclusions": [],
  "structural_issues": [],
  "conflicts": [],
  "clarification_required": true,
  "notes": [
    "HbA1c path (criterion 2) may independently satisfy requirements if hba1c_mmol_mol >= 48 is confirmed."
  ],
  "evaluated_at": "2025-06-01T14:15:00Z"
}
```

---

## Routing Logic

```
valid == true
    -> forward to M08 (examination)

valid == false
    missing_required != []
        -> route to clarification (06_clarification)
    violated_exclusions != []
        -> hard reject; try next candidate; surface exclusion in output
    conflicts != []
        -> hard reject; surface conflict explanation; try next candidate
    structural_issues != []
        -> reject; log issue; try next candidate
```

When multiple candidates are proposed (M07/M08), validation runs on each independently. The first to satisfy the acceptance condition proceeds. Others are preserved as `alternatives` in finalization.

---

## Multi-Candidate Evaluation

```json
{
  "candidates_evaluated": [
    { "candidate_id": "AKU-00123", "valid": false, "clarification_required": true },
    { "candidate_id": "AKU-00125", "valid": false, "violated_exclusions": ["..."] }
  ],
  "best_candidate": "AKU-00123",
  "routing": "clarification"
}
```

---

## APIs

```
POST /validate
  body: { candidate_id, case_facts, kb_snapshot_id }
  -> ValidationReport

POST /check-conflicts
  body: { candidate_id, context_ids, kb_snapshot_id }
  -> { conflicts[] }

POST /check-structure
  body: { candidate_id, kb_snapshot_id }
  -> { structural_issues[] }

POST /validate-batch
  body: { candidates[], case_facts, kb_snapshot_id }
  -> ValidationReport[]
```

---

## Performance Targets

| Operation | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| Single candidate validation | 10ms | 50ms | 150ms |
| Batch (10 candidates) | 50ms | 150ms | 400ms |

Validation workers are stateless and horizontally scalable.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| KB snapshot mismatch | Reject; error — snapshot must match retrieval run |
| Candidate AKU not in snapshot | Reject; candidate is invalid by definition |
| Case facts missing entirely | Reject with `status: insufficient_input` |
| All candidates rejected (no clarification possible) | Route to finalization with `status: insufficient` |
