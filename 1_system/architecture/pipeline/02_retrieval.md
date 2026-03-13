# Step 02 — AKU Retrieval
## Fetch Relevant Atomic Knowledge Units

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** Yes (given fixed embedding model + index snapshot)
**Upstream:** `01_parsing.md` → `case_facts`
**Downstream:** `03_enrichment.md`, `04_hypothesis.md`

---

## Purpose

Reduce the reasoning space to a **bounded, ranked set of AKUs** that are semantically and structurally relevant to the parsed case facts. The retrieval layer is the only step that accesses the vector index directly.

Neither the LLM nor the validation engine retrieves AKUs independently — they operate exclusively on the context assembled here.

---

## Contract

```
update(state, inputs={ case_facts }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_facts` | `ParsedFacts` | Yes | Output of Step 01. |
| `kb_snapshot_id` | string | Yes | The knowledge base snapshot to query. Must be pinned per run. |
| `top_k` | int | No | Max AKUs to return. Default: 15. Hard max: 30. |
| `domain_filter` | string[] | No | Restrict retrieval to specific domains. |
| `status_filter` | string | No | Default: `active`. Allows `deprecated` for audit/replay. |

### Retrieval Pipeline (Internal)

```
case_facts (text fields)
    │
    ▼
Embedding Generator          ← domain-tuned model; version pinned per run
    │
    ▼
ANN Vector Search            ← approximate nearest neighbor over KB snapshot
    │
    ▼
Metadata Filter              ← domain, status, version constraints
    │
    ▼
Hierarchical Expander        ← adds ancestor path + direct siblings per matched AKU
    │
    ▼
Ranker                       ← score = α·semantic_similarity + β·structural_depth
    │
    ▼
Bounded Context (top-k)      ← hard cap enforced after ranking
```

### Outputs — `context_units[]`

```json
[
  {
    "aku_id": "AKU-00123",
    "title": "Type 2 Diabetes Mellitus — Diagnostic Criteria",
    "rank": 1,
    "score": 0.94,
    "breadcrumb": ["AKU-00100", "AKU-00120", "AKU-00123"],
    "required_criteria": [...],
    "exclusion_criteria": [...],
    "relations": {...},
    "metadata": { "version": "2.1.0", "domain": "endocrinology" }
  }
]
```

Every returned AKU includes its full ancestor path (`breadcrumb`) for structural context.

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `RetrievalResult` | Every run |

### Report Fields

```json
{
  "status": "ok | warn | no_results",
  "kb_snapshot_id": "SNAP-00189",
  "embedding_model": "text-embedding-3-large@2024-09",
  "top_k_requested": 15,
  "top_k_returned": 12,
  "domains_searched": ["endocrinology"],
  "retrieval_latency_ms": 142,
  "warnings": []
}
```

---

## Retrieval Quality Targets

| Metric | Target |
|--------|--------|
| Recall@10 | ≥ 0.90 |
| Precision@10 | ≥ 0.75 |
| MRR | ≥ 0.85 |
| Latency p95 | < 200ms |

These are evaluated against a curated query test set. Drift below threshold triggers an alert and embedding rebuild.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| No AKUs returned | `status: no_results`; route to `08_finalization` with `status: no_knowledge`. |
| KB snapshot not found | `status: error`; block pipeline. |
| Embedding model unavailable | `status: error`; block pipeline. |
| top_k_returned < top_k_requested | `status: warn`; proceed with available results. |
| Retrieval latency > 1s | `status: warn`; log; proceed. |

---

## Auditability

The following must be recorded in the run record for reproducibility:

- `kb_snapshot_id`
- `embedding_model` (id + version)
- `top_k` value
- `domain_filter` applied
- `status_filter` applied
- `scores[]` for all returned AKUs

Given the same inputs and configuration, retrieval is deterministic.

---

## Example

**Input `case_facts`:**
```json
{ "hba1c_mmol_mol": 52, "prior_diabetes_diagnosis": false }
```

**Top-3 retrieved AKUs:**

| Rank | AKU ID | Title | Score |
|------|--------|-------|-------|
| 1 | AKU-00123 | Type 2 DM — Diagnostic Criteria | 0.94 |
| 2 | AKU-00120 | Diabetes Mellitus — Parent Concept | 0.81 |
| 3 | AKU-00130 | Type 1 DM — Diagnostic Criteria | 0.73 |

AKU-00120 is included via the hierarchical expander (parent of AKU-00123), not direct semantic match.
