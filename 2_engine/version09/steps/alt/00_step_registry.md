# Step Registry — All 14 Envelopes

**Version:** 1.0.0
**Reference:** `pipeline_steps_v2/00_overview.md`

---

## Envelope Summary Table

| Step | Type | Retries | Novelty Guard | Snapshot After | Required Outputs |
|------|------|---------|---------------|----------------|-----------------|
| `01_parsing_01_extraction` | llm | 1 | yes | no | `raw_facts` |
| `01_parsing_02_confidence` | llm | 1 | yes | no | `scored_facts` |
| `02_retrieval` | deterministic | 0 | no | no | `context_units` |
| `03_enrichment_01_terminology` | llm | 1 | yes | no | `mapped_facts` |
| `03_enrichment_02_unit_normalization` | deterministic | 0 | no | no | `normalized_facts` |
| `03_enrichment_03_gap_detection` | llm | 1 | yes | **yes** | `gap_detection` |
| `04_hypothesis` | llm | 2 | yes | no | `candidate` |
| `05_validation` | deterministic | 0 | no | **yes** | `validation_report` |
| `06_clarification` | llm | 1 | yes | **yes** | `clarification_request` |
| `07_examination_01_weakness_scan` | llm | 1 | yes | no | `weakness_scan` |
| `07_examination_02_alternative_check` | llm | 1 | yes | no | `examination_result` |
| `08_finalization` | deterministic+llm | 1 | yes | **yes** | `final_answer` |
| `09_commit` | deterministic | 0 | no | **yes** | `commit_record` |

---

## Input/Output Chain

```
raw_text
    │
    ▼ [01_parsing_01]
raw_facts{}
    │
    ▼ [01_parsing_02]
scored_facts{ raw_facts + confidence{} + unparsed_fragments[] }
    │
    ▼ [02_retrieval]
context_units[]
    │
    ▼ [03_enrichment_01]
mapped_facts{ canonical field names }
    │
    ▼ [03_enrichment_02]
normalized_facts{ canonical units }  ◄── deterministic, no LLM
    │
    ▼ [03_enrichment_03]
gap_detection{ covered[], missing[] }
    │
    ▼ [04_hypothesis]
candidate{ aku_id, matched_criteria[], missing_criteria[], uncertainty }
    │
    ▼ [05_validation]
validation_report{ valid, matched_required[], missing_required[], violated_exclusions[] }
    │
    ├─[clarification_required]──► [06_clarification]
    │                              clarification_request{ questions[] }
    │                              └─► back to 01_parsing_01 with augmented input
    ▼
    ▼ [07_examination_01]
weakness_scan{ assessments[], weak_or_ambiguous_count }
    │
    ▼ [07_examination_02]
examination_result{ decision, better_alternatives[], decision_rationale }
    │
    ├─[reject, retry≤2]──► back to 04_hypothesis
    ▼
    ▼ [08_finalization]
final_answer{ status, result{}, audit{} }
    │
    ▼ [09_commit]
commit_record{ patches_accepted, snapshot_after }
```

---

## Scheduling Order

Steps are always dispatched in index order. There is no parallel execution within a single session. The order is:

```
01_01 → 01_02 → 02 → 03_01 → 03_02 → 03_03 → 04 → 05 → [06 →loop] → 07_01 → 07_02 → 08 → 09
```

Retries re-dispatch the same step; downstream steps do not execute until the retry resolves or STOP is emitted.

---

## Retry Context Injection

When `04_hypothesis` is retried after examination rejection, the envelope is re-created with enriched inputs:

```json
{
  "inputs": {
    "normalized_facts_hash": "sha256:...",
    "context_units_hash": "sha256:...",
    "retry_context_hash": "sha256:..."   ← NEW: contains rejection reason
  }
}
```

The new `task_id` differs because inputs differ — this is treated as a new task, not a re-run. The prior `candidate` artifact is marked `superseded` in the manifest.

---

## Clarification Re-entry

When clarification is triggered (`05_validation: clarification_required=true`):

1. `06_clarification` runs → produces `clarification_request`
2. Questions are returned to the user
3. User answers re-enter as new `raw_text` (session continues)
4. `01_parsing_01` runs again with the new text → new `task_id`
5. Pipeline continues from `01_parsing_01` forward
6. Prior `raw_facts`, `scored_facts` etc. are **superseded**

The run directory preserves all prior round artifacts under their original `task_id`.
