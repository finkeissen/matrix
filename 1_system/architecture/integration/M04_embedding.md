# M04 — Embedding & Vector Index
## Represent AKUs as Searchable Vectors

**Layer:** Retrieval
**Version:** 2.0.0
**Deterministic:** Yes (given fixed model + snapshot)
**Depends on:** M01 (schema), M02 (knowledge store)
**Used by:** M05 (retrieval engine)
**Pipeline steps:** Background job (on KB update); pinned at query time via `snapshot_id`

---

## Purpose

Transform every active AKU in a knowledge snapshot into a **dense vector representation** that enables semantic similarity search. The embedding index is rebuilt or incrementally updated whenever a new KB snapshot is published.

The embedding layer is invisible to query-time callers — they interact only with M05.

---

## Embedding Chunk Construction

Each AKU is embedded as a **single rich text chunk** that combines all semantically relevant fields. Embedding isolated fields is explicitly prohibited (see `grounded_intelligence_architecture_v2.md §18`, anti-pattern: "Isolated field embedding").

### Chunk Template

```
{title}
Definition: {definition}
Required criteria: {required_criteria joined with " | "}
Exclusion criteria: {exclusion_criteria joined with " | "}
Domain: {metadata.domain}
Ancestor path: {breadcrumb titles joined with " > "}
```

### Example Chunk

```
Type 2 Diabetes Mellitus -- Diagnostic Criteria
Definition: A metabolic disorder characterized by chronic hyperglycemia resulting from insulin resistance.
Required criteria: Fasting plasma glucose >= 7.0 mmol/L on two separate occasions | OR HbA1c >= 48 mmol/mol confirmed | OR 2-hour plasma glucose >= 11.1 mmol/L during OGTT
Exclusion criteria: Confirmed autoimmune beta-cell destruction | Secondary diabetes due to exocrine pancreatic pathology
Domain: endocrinology
Ancestor path: Metabolic Disorders > Diabetes Mellitus > Type 2 Diabetes Mellitus
```

The `ancestor path` is resolved from the relational store (M02) at embedding time.

---

## Embedding Model Requirements

| Requirement | Specification |
|-------------|--------------|
| Model type | Dense text embedding (not sparse/BM25) |
| Domain tuning | Domain-tuned model preferred for regulated domains |
| Version pinning | Model ID and version must be pinned per KB snapshot |
| Max token length | Chunk must fit within model's token limit; truncate at `exclusion_criteria` if necessary (log truncations) |
| Dimensionality | 768–3072 dimensions depending on model |

The model version used for a snapshot is recorded in the snapshot metadata and must be used for all queries against that snapshot.

---

## Vector Index

### Technology Options

| Option | Recommended Use Case |
|--------|---------------------|
| pgvector (PostgreSQL) | Small-medium KB (< 100k AKUs); integrated with relational store |
| Qdrant | Medium-large KB; dedicated vector service; supports payload filtering |
| Weaviate | Large KB; native hybrid search (dense + sparse); GraphQL API |

### Index Metadata (Stored Per Vector)

Each vector is stored with the following payload for metadata filtering:

```json
{
  "aku_id": "AKU-00123",
  "domain": "endocrinology",
  "status": "active",
  "kb_version": "2.1.0",
  "snapshot_id": "SNAP-00189",
  "parent_id": "AKU-00100",
  "has_children": true,
  "has_conflicts": true
}
```

---

## Index Build Process

### Full Rebuild (MAJOR version bump)

```
1. Fetch all active AKUs from new snapshot (M02)
2. Resolve ancestor paths for all AKUs (M02 relational queries)
3. Construct rich embedding chunk per AKU
4. Embed all chunks in batch (parallelized)
5. Write vectors + payloads to new index partition
6. Validate index: count check, spot-check top-5 queries
7. Swap partition to active; retire old partition
```

Full rebuild time target: < 2 hours for 100k AKUs.

### Incremental Update (PATCH or MINOR version bump)

```
1. Diff: identify added, updated, deprecated AKUs since last snapshot
2. Re-embed only changed AKUs
3. Upsert vectors; delete deprecated AKU vectors
4. Update snapshot_id payload on unchanged vectors
```

Incremental update time target: < 5 minutes for < 100 changed AKUs.

---

## Drift Detection

After each rebuild or incremental update, run the retrieval quality eval (M05 metrics) against the held-out query test set. If quality drops below threshold:

| Metric Drop | Action |
|-------------|--------|
| Recall@10 < 0.90 | Alert; trigger full rebuild |
| MRR < 0.85 | Alert; investigate embedding model degradation |
| Any metric drops > 5% | Block snapshot activation; require investigation |

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Embedding model unavailable | Block index build; alert; do not activate snapshot |
| Chunk exceeds token limit | Truncate at `exclusion_criteria`; log truncation; flag AKU for review |
| Batch embedding fails partially | Retry failed chunks; report un-embedded AKUs; block activation if > 1% failure rate |
| Index write fails | Retry with backoff; alert after 3 failures |
| Quality eval fails post-build | Block snapshot activation; open investigation ticket |
