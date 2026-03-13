# M09 — Audit & Transparency Layer
## Decision Logging, Reproducibility, and Trace Replay

**Layer:** Governance
**Version:** 2.0.0
**Deterministic:** Yes
**Depends on:** All modules (receives outputs)
**Used by:** All pipeline steps (write); operators, auditors (read)
**Pipeline steps:** 08_finalization, 09_commit

---

## Purpose

Ensure that every system decision is **logged, attributable, and reproducible**. This module provides the infrastructure that makes the system auditable by regulators, reviewers, and developers — and enables full replay of any past decision from its inputs.

Transparency is not optional. An answer without an audit trace is not a valid system output.

---

## Core Invariant

A result is **reproducible** if and only if:

```
same KB snapshot version
  + same case facts (normalized)
  + same retrieval configuration (top-k, filters, embedding model)
  + same system version
= same output
```

For non-deterministic steps (LLM), reproducibility is achieved by replaying the recorded raw response, not by re-invoking the model.

---

## What Is Logged

Every pipeline run logs, at minimum:

| Log Entry | Content | When |
|-----------|---------|------|
| **Run record** | Module ID, version, params, input hash, output hash, timestamps | Every module invocation |
| **Patch log** | All proposed patches (accepted + rejected) with reasons | Every commit gate pass |
| **Retrieval log** | Snapshot ID, embedding model, top-k, scores, query hash | Every retrieval run |
| **Validation log** | Candidate ID, full validation report, acceptance condition result | Every validation run |
| **LLM invocation log** | Model ID, temperature, prompt hash, raw response, token counts | Every LLM call |
| **Audit trace** | Aggregated decision record linking all above logs via `trace_id` | Every finalized answer |

---

## Audit Trace Schema

```json
{
  "trace_id": "TRACE-20250601-00291",
  "session_id": "sess-00291",
  "status": "validated | insufficient | no_knowledge | ...",
  "result_aku_id": "AKU-00123",
  "kb_snapshot_id": "SNAP-00189",
  "kb_version": "2.1.0",
  "system_version": "2.0.0",
  "run_ids": [
    "RUN-001-parsing",
    "RUN-002-retrieval",
    "RUN-003-enrichment",
    "RUN-004-hypothesis",
    "RUN-005-validation",
    "RUN-006-examination",
    "RUN-007-finalization",
    "RUN-008-commit"
  ],
  "aku_ids_used": ["AKU-00100", "AKU-00120", "AKU-00123", "AKU-00130"],
  "retrieval_config": {
    "top_k": 15,
    "domain_filter": ["endocrinology"],
    "embedding_model": "text-embedding-3-large@2024-09"
  },
  "validation_report_id": "VAL-00289",
  "examination_result_id": "EX-00147",
  "clarification_rounds": 1,
  "input_hash": "sha256:abc123...",
  "output_hash": "sha256:def456...",
  "created_at": "2025-06-01T14:22:00Z"
}
```

---

## Trace Replay

Any audit trace can be replayed to reproduce the original result:

```
POST /traces/{trace_id}/replay
```

Replay process:
1. Fetch the KB snapshot referenced in the trace.
2. Reconstruct the retrieval context using the logged config.
3. Replay all LLM invocations using stored raw responses (no re-invocation).
4. Re-run the validation engine against the stored case facts.
5. Compare the reproduced result to the original `output_hash`.

A replay is successful if `reproduced_output_hash == original_output_hash`.

---

## Audit Interface

```
POST /traces                    body: { trace }           -> trace_id
GET  /traces/{id}               ->  full AuditTrace
GET  /traces/{id}/replay        ->  replay result + hash comparison
GET  /traces/{id}/runs          ->  all run records in this trace
GET  /traces/{id}/patches       ->  all patches proposed in this trace
GET  /traces/search?session_id=...&from=...&to=...  ->  trace list
```

---

## Mandatory Output Fields

Every answer returned to the user or API caller must include:

| Field | Description |
|-------|-------------|
| `kb_version` | KB snapshot version used |
| `aku_ids_used` | All AKU IDs referenced in the decision |
| `retrieval_config` | top-k, filters, embedding model |
| `validation_report` | Full structured validation output |
| `timestamp` | ISO 8601 UTC |
| `system_version` | Orchestration system version |
| `trace_id` | Link to full audit trace |

An answer missing any of these fields must not be returned to the caller — it is treated as an incomplete output.

---

## Audit Log Properties

The audit log must be:

- **Append-only:** no deletions, no in-place edits.
- **Tamper-evident:** each entry is hash-chained or stored in an immutable log service.
- **Separate from operational DB:** stored independently to prevent accidental or deliberate modification.
- **Retained indefinitely** for regulatory domains; minimum 7 years in most regulated contexts.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Audit trace write fails | Block answer delivery; retry with backoff; alert after 3 failures. Do not return answer without trace. |
| Replay hash mismatch | Flag trace as non-reproducible; open investigation ticket; do not suppress the original result. |
| Log storage unavailable | Block all pipeline runs; alert immediately. The system must not operate without audit capability. |
