# Step 05 — Deterministic Validation
## Rule-Based Criteria Checking

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** Yes (rule engine; no LLM)
**Upstream:** `04_hypothesis.md` → `candidate`, `enriched_context`
**Downstream:** `06_clarification.md` (if missing facts) or `07_examination.md` (if valid)

---

## Purpose

Apply **deterministic, non-bypassable rule checks** to each candidate proposed in Step 04. The validation engine does not use language models. Its output is a structured report that either accepts, rejects, or requests clarification for each candidate.

The LLM cannot override this step. A candidate is only forwarded to examination if `validation_report.valid == true`.

---

## Contract

```
update(state, inputs={ candidate, enriched_context }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `candidate` | `HypothesisResult` | Yes | Output of Step 04 (one candidate per validation call). |
| `enriched_context` | `EnrichedContext` | Yes | Output of Step 03. |
| `kb_snapshot_id` | string | Yes | Must match snapshot used in Steps 02–04. |

### Validation Checks (Executed in Order)

| # | Check | Failure Action |
|---|-------|---------------|
| 1 | **Required criteria** | Are all `required_criteria` of the target AKU satisfied by normalized case facts? | List unsatisfied in `missing_required`. |
| 2 | **Exclusion criteria** | Do any case facts match `exclusion_criteria`? | List violated in `violated_exclusions`; reject candidate. |
| 3 | **Structural consistency** | Are parent/child/sibling constraints respected? | List issues in `structural_issues`. |
| 4 | **Conflict check** | Does selecting this AKU trigger any `conflicts_with` relations? | List in `conflicts`; reject candidate. |

### Validation Output Contract

```json
{
  "candidate_id": "AKU-00123",
  "valid": false,
  "matched_required": [
    "fasting_plasma_glucose_mmol_l >= 7.0: satisfied (8.2)",
    "measurement_count >= 2: satisfied (2)",
    "autoimmune_markers_present == false: satisfied"
  ],
  "missing_required": [
    "Second confirmation on separate calendar day not documented."
  ],
  "violated_exclusions": [],
  "structural_issues": [],
  "conflicts": [],
  "notes": [
    "HbA1c value (52 mmol/mol) independently meets threshold. If fasting glucose gap cannot be resolved, HbA1c path alone may be sufficient per AKU-00123 criteria variant B."
  ],
  "clarification_required": true
}
```

### Routing Logic

```
valid == true                     → forward to 07_examination
valid == false
  ├── missing_required != []      → route to 06_clarification
  ├── violated_exclusions != []   → reject candidate; try next candidate or finalize
  └── conflicts != []             → reject candidate; surface conflict; try next candidate
```

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `ValidationReport` | Always (one per candidate) |

### Report Fields

```json
{
  "status": "ok | clarification_required | rejected",
  "candidates_evaluated": 2,
  "candidates_valid": 1,
  "candidates_rejected": 1,
  "clarification_triggered": true
}
```

---

## Acceptance Condition (Formal)

```
Accept(candidate) ⟺
    missing_required = ∅
  ∧ violated_exclusions = ∅
  ∧ structural_issues = ∅
  ∧ conflicts = ∅
```

All four conditions must hold simultaneously.

---

## Multiple Candidates

When Step 04 proposes multiple candidates, this step validates each independently. The first candidate to satisfy the acceptance condition is forwarded to examination. Remaining candidates are preserved as `alternatives` in the finalization step.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| KB snapshot mismatch | `status: error`; block step. Snapshot must match retrieval run. |
| AKU not found in snapshot | `status: error`; candidate invalid by definition. |
| All candidates rejected | Route to `08_finalization` with `status: insufficient`. |
| All candidates require clarification | Route to `06_clarification` for the highest-ranked candidate. |
