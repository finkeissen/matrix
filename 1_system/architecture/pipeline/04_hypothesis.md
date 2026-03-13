# Step 04 — Hypothesis Generation
## Propose Candidate AKU(s) with Criteria Mapping

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** No (LLM-based)
**Upstream:** `03_enrichment.md` → `enriched_context`
**Downstream:** `05_validation.md`

---

## Purpose

The LLM proposes one or more **candidate AKU IDs** as the best match for the case facts, together with an explicit mapping of which criteria are satisfied, which are missing, and which are potentially violated.

This step produces a hypothesis — it does not validate, decide, or explain to the end user. All of those responsibilities belong to downstream steps.

---

## Contract

```
update(state, inputs={ enriched_context }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enriched_context` | `EnrichedContext` | Yes | Output of Step 03. |
| `max_candidates` | int | No | Maximum candidates to propose. Default: 3. |
| `model_id` | string | Yes | LLM model ID. Must be pinned per run. |
| `temperature` | float | No | Default: 0.0 for maximum determinism. |

### Prompt Constraints

Every prompt sent to the LLM at this step must include:

```
CONSTRAINTS:
1. Use only the AKUs provided in the context. Do not introduce external knowledge.
2. Cite the AKU ID for every claim you make.
3. List matched criteria and missing criteria separately and explicitly.
4. Do not validate — propose candidates only. Validation happens downstream.
5. If no AKU in the context is a plausible match, respond with status: NO_MATCH.
6. Express uncertainty as a structured field, not as hedging language.
```

### Output Schema — `candidate`

```json
{
  "candidate_id": "AKU-00123",
  "rank": 1,
  "aku_title": "Type 2 Diabetes Mellitus — Diagnostic Criteria",
  "matched_criteria": [
    "Fasting plasma glucose >= 7.0 mmol/L: satisfied (8.2 mmol/L, confirmed twice)",
    "No autoimmune markers: satisfied"
  ],
  "missing_criteria": [
    "OGTT 2-hour glucose: not available in case facts"
  ],
  "potentially_violated": [],
  "uncertainty": {
    "level": "low",
    "reason": "Two primary criteria satisfied; one optional criterion unavailable."
  },
  "rationale": "Case facts directly satisfy the fasting glucose and absence-of-autoimmune criteria. HbA1c value (52 mmol/mol) also meets threshold independently."
}
```

Multiple candidates are returned as a ranked list (`rank: 1, 2, 3`).

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `HypothesisResult` | Always |

The raw LLM output is stored in the run record verbatim (model ID, temperature, seed, full response) to enable deterministic replay.

### Report Fields

```json
{
  "status": "ok | warn | no_match",
  "candidates_proposed": 2,
  "model_id": "claude-sonnet-4-20250514",
  "temperature": 0.0,
  "prompt_tokens": 1840,
  "completion_tokens": 412,
  "warnings": []
}
```

---

## NO_MATCH Behavior

If the LLM returns `status: NO_MATCH`:

- No candidate patches are created.
- Pipeline routes to `08_finalization` with `status: no_knowledge`.
- The retrieval result and run record are preserved for audit.

---

## Retry Context

If this step is re-entered after a failed examination (Step 07), the prompt must include:

```json
{
  "retry_context": {
    "prior_candidate_id": "AKU-00123",
    "rejection_reason": "Examiner flagged weak support for criterion: measurement_count >= 2.",
    "instruction": "Propose an alternative candidate or strengthen the mapping for the flagged criterion."
  }
}
```

Maximum retries: 2. After 2 failed attempts, route to finalization with `status: insufficient`.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM returns malformed JSON | `status: error`; retry once; then block. |
| LLM returns NO_MATCH | `status: no_match`; route to finalization. |
| LLM cites AKU ID not in context | `status: warn`; strip invalid citation; add to review queue. |
| Max retries exceeded | `status: error`; route to finalization with `status: insufficient`. |

---

## Example

**Input facts:** `fasting_plasma_glucose_mmol_l: 8.2`, `measurement_count: 2`, `autoimmune_markers_present: false`

**Proposed candidates:**

| Rank | Candidate | Matched | Missing | Uncertainty |
|------|-----------|---------|---------|-------------|
| 1 | AKU-00123 (T2DM) | 3/4 criteria | OGTT result | low |
| 2 | AKU-00125 (Pre-diabetes) | 2/3 criteria | HbA1c repeat | medium |
