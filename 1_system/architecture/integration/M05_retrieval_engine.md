# M05 — Retrieval Engine
## Semantic Search, Hierarchical Expansion, and Context Assembly

**Layer:** Retrieval
**Version:** 2.0.0
**Deterministic:** Yes (given fixed embedding model + snapshot)
**Depends on:** M04 (vector index), M02 (knowledge store for hierarchy)
**Used by:** M07 (LLM orchestrator), M06 (validation needs full AKU objects)
**Pipeline steps:** 02_retrieval

---

## Purpose

Reduce the full knowledge base to a **bounded, ranked, structurally enriched context** of AKUs relevant to a given query. The retrieval engine is the gateway between the knowledge layer and the orchestration layer.

Neither the LLM (M07) nor the validation engine (M06) accesses the vector index directly.

---

## Retrieval Pipeline

```
Query (text or structured case facts)
    |
    v
[1] Query Embedding         -- embed using same model as index (M04)
    |
    v
[2] ANN Search              -- approximate nearest neighbor over snapshot index
    |
    v
[3] Metadata Filtering      -- domain, status=active, version constraints
    |
    v
[4] Hierarchical Expansion  -- add ancestor path + direct siblings per match
    |
    v
[5] Ranker                  -- score = a*semantic_similarity + b*structural_depth
    |
    v
[6] Bounded Context         -- enforce hard top-k limit
    |
    v
context_units[]             -- full AKU objects with breadcrumbs and scores
```

---

## Interface

### Input

```json
{
  "query_text": "string (or serialized case facts)",
  "snapshot_id": "SNAP-00189",
  "top_k": 15,
  "domain_filter": ["endocrinology"],
  "status_filter": "active",
  "include_hierarchy": true
}
```

| Parameter | Default | Hard Limit |
|-----------|---------|------------|
| `top_k` | 15 | 30 |
| `domain_filter` | all domains | — |
| `status_filter` | `active` | `deprecated` allowed for replay only |
| `include_hierarchy` | true | — |

### Output — `context_units[]`

```json
[
  {
    "aku_id": "AKU-00123",
    "title": "Type 2 Diabetes Mellitus -- Diagnostic Criteria",
    "rank": 1,
    "score": 0.94,
    "match_source": "direct",
    "breadcrumb": [
      { "id": "AKU-00100", "title": "Metabolic Disorders" },
      { "id": "AKU-00120", "title": "Diabetes Mellitus" },
      { "id": "AKU-00123", "title": "Type 2 Diabetes Mellitus -- Diagnostic Criteria" }
    ],
    "required_criteria": ["..."],
    "exclusion_criteria": ["..."],
    "relations": { "parent": "AKU-00120", "children": [...], "conflicts_with": [...] },
    "metadata": { "domain": "endocrinology", "version": "2.1.0" }
  }
]
```

`match_source` values: `direct` (ANN match), `ancestor` (included via hierarchy), `sibling` (included via sibling expansion).

---

## Hierarchical Expansion

For each directly matched AKU, the expander adds:

1. **All ancestors** (parent, grandparent, ..., root): provides structural context for the matched concept.
2. **Direct siblings** (other children of the same parent): enables the validation engine to check mutual exclusions.

Ancestor path is resolved from M02's relational store, not from the vector index.

Expanded AKUs do not consume top-k slots — they are appended after the ranked list with `match_source: ancestor | sibling`.

---

## Ranking Function

```
score(aku) = alpha * semantic_similarity(query_vector, aku_vector)
           + beta  * structural_relevance(aku, query_domain)
```

Default weights: `alpha = 0.8`, `beta = 0.2`. Configurable per domain in retrieval config.

`structural_relevance` is higher for AKUs that are direct parents or children of other highly-ranked AKUs, rewarding structural centrality.

---

## Domain Boundary Enforcement

The retrieval engine enforces domain isolation by default:

- A query with `domain_filter: ["endocrinology"]` cannot return AKUs from `oncology`.
- Cross-domain retrieval requires `allow_cross_domain: true` explicitly set in params.
- Cross-domain retrieval is logged with a warning in the retrieval report.

---

## Quality Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recall@10 | >= 0.90 | Held-out query test set |
| Precision@10 | >= 0.75 | Held-out query test set |
| MRR (Mean Reciprocal Rank) | >= 0.85 | Held-out query test set |
| Latency p50 | < 80ms | Production monitoring |
| Latency p95 | < 200ms | Production monitoring |
| Latency p99 | < 500ms | Production monitoring |

---

## Retrieval Report

```json
{
  "snapshot_id": "SNAP-00189",
  "embedding_model": "text-embedding-3-large@2024-09",
  "top_k_requested": 15,
  "top_k_returned_direct": 12,
  "top_k_returned_expanded": 5,
  "domains_searched": ["endocrinology"],
  "cross_domain_enabled": false,
  "latency_ms": 142,
  "warnings": []
}
```

---

## Auditability

For full reproducibility, every retrieval run records:

- `snapshot_id`
- `embedding_model` (id + version)
- `top_k`
- `domain_filter`
- `scores[]` for all returned AKUs (direct + expanded)
- `query_vector_hash` (sha256 of the embedded query vector)

Given the same inputs and configuration, retrieval is deterministic.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| No AKUs returned | Return `status: no_results`; route to finalization with `status: no_knowledge` |
| Snapshot not found | Return `status: error`; block pipeline |
| Embedding model unavailable | Return `status: error`; block pipeline |
| Hierarchy expansion fails | Return direct matches only; set `include_hierarchy: false` in report; log warning |
| top_k_returned < top_k_requested | Return available results; set `status: warn` |
| Latency > 1s | Log; proceed; trigger async performance alert |
