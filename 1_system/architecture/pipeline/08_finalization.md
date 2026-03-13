# Step 08 — Finalization & Output
## Assemble Structured Result and Audit Trace

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** Yes (assembly only; no LLM reasoning)
**Upstream:** `07_examination.md` (normal path) or any step (failure/exit paths)
**Downstream:** `09_commit.md`

---

## Purpose

Consolidate all prior step outputs into a single **structured, transparent result** that is returned to the user and logged for audit. This step generates the user-facing explanation (one LLM call), assembles the audit trace, and determines the final status code.

The finalizer does not re-evaluate candidates or modify validation results. It assembles and explains only.

---

## Contract

```
update(state, inputs={ all_prior_outputs }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_facts` | `ParsedFacts` (normalized) | Yes | From Step 03. |
| `context_units` | `AKU[]` | Yes | From Step 02. |
| `candidate` | `HypothesisResult` | Conditional | Present if a candidate was produced. |
| `validation_report` | `ValidationReport` | Conditional | Present if validation was run. |
| `examination_result` | `ExaminationResult` | Conditional | Present if examination was run. |
| `clarification_records` | `ClarificationRecord[]` | No | All clarification rounds, if any. |
| `pipeline_status` | string | Yes | Routing outcome from prior steps. |

### Status Codes

| Status | Meaning |
|--------|---------|
| `validated` | Candidate accepted by both validation and examination. |
| `clarification_required` | Missing facts; clarification questions returned to user. |
| `insufficient` | Max retries exceeded; no valid candidate produced. |
| `insufficient_facts` | Max clarification rounds exceeded; facts incomplete. |
| `no_knowledge` | No relevant AKU found in retrieval. |
| `no_match` | AKUs found but none matched the case facts. |
| `error` | Pipeline error; see `error_details`. |

### Output Schema — Final Answer

```json
{
  "session_id": "sess-00291",
  "status": "validated",
  "result": {
    "aku_id": "AKU-00123",
    "aku_title": "Type 2 Diabetes Mellitus -- Diagnostic Criteria",
    "confidence": "high",
    "explanation": "The available clinical data satisfies the diagnostic criteria for Type 2 Diabetes Mellitus. Fasting plasma glucose was confirmed at 8.2 mmol/L on two occasions (threshold: 7.0 mmol/L), and HbA1c independently meets the diagnostic threshold at 52 mmol/mol. No exclusion criteria were triggered.",
    "weak_points": [
      "Measurement interval between the two fasting glucose tests was not explicitly documented."
    ],
    "alternatives": []
  },
  "audit": {
    "kb_version": "2.1.0",
    "kb_snapshot_id": "SNAP-00189",
    "aku_ids_used": ["AKU-00100", "AKU-00120", "AKU-00123", "AKU-00130"],
    "retrieval_config": {
      "top_k": 15,
      "domain_filter": ["endocrinology"],
      "embedding_model": "text-embedding-3-large@2024-09"
    },
    "validation_report_id": "VAL-00289",
    "examination_result_id": "EX-00147",
    "clarification_rounds": 1,
    "system_version": "2.0.0",
    "timestamp": "2025-06-01T14:22:00Z",
    "trace_id": "TRACE-20250601-00291"
  }
}
```

### Explanation Generation (LLM)

One LLM call is made at this step to generate the `explanation` field only. Constraints:

1. Explain in plain language suitable for the end user (domain-appropriate, not system-internal).
2. Reference the matched criteria by name, not by system IDs.
3. Do not introduce new claims beyond what the validation report contains.
4. If `weak_points` exist, mention them transparently without alarming language.
5. Do not expose AKU IDs, internal scores, or pipeline structure in the explanation.

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `FinalAnswer` | Always |
| `create` | `AuditTrace` | Always |
| `create` | `ReviewQueueEntry` | If `weak_points` non-empty or status is `insufficient` |

---

## Audit Trace

Every finalized answer produces an immutable audit trace that enables full replay:

```
TRACE-20250601-00291
  |-- run_ids: [RUN-001, RUN-002, ..., RUN-008]
  |-- kb_snapshot_id: SNAP-00189
  |-- input_hash: sha256(normalized_case_facts)
  |-- retrieval_config: { top_k, filters, model }
  |-- patch_ids: [...]
  |-- system_version: 2.0.0
```

Given this trace and the KB snapshot, the result is fully reproducible.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Explanation LLM call fails | Return result without explanation; log error; do not block delivery. |
| Audit trace write fails | Block delivery; retry; alert. Audit integrity is mandatory. |
| Missing required input fields | Return `status: error` with field list. |
