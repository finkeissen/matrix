# M03 — Ingestion Pipeline
## Transform Source Documents into Validated AKUs

**Layer:** Knowledge
**Version:** 2.0.0
**Deterministic:** Partially (extraction uses LLM; validation is deterministic)
**Depends on:** M01 (schema), M02 (store)
**Used by:** M02 (receives validated AKUs)
**Pipeline steps:** Authoring time only

---

## Purpose

Transform **raw source documents** (regulations, clinical guidelines, technical standards, internal rule sets) into well-formed, schema-compliant AKUs that can be stored, versioned, and queried. Ingestion is the only point at which new knowledge enters the system.

---

## Ingestion Pipeline (Internal)

```
Source Document (PDF, text, structured)
    |
    v
[1] Segmentation         -- split into candidate AKU-sized units
    |
    v
[2] Extraction (LLM)     -- extract fields per M01 schema
    |
    v
[3] Schema Validation    -- enforce M01 required properties
    |
    v
[4] Integrity Checks     -- circular deps, conflict symmetry, parent coherence
    |
    v
[5] Deduplication        -- match against existing active AKUs
    |
    v
[6] Review Queue         -- route to domain expert for approval
    |
    v
[7] Activation           -- transition to `active`; trigger snapshot update
```

---

## Stage Specifications

### Stage 1 — Segmentation

Split source documents into units that map to individual AKU scope. A segment should correspond to one concept, one rule, or one diagnostic/legal criterion set.

Segmentation strategies by source type:

| Source Type | Segmentation Strategy |
|-------------|----------------------|
| Regulatory text | Per article or sub-article |
| Clinical guideline | Per diagnostic criterion set |
| Technical standard | Per requirement clause |
| Internal rule set | Per rule or policy item |

Output: `raw_segments[]`, each with `source_ref` (document + section).

### Stage 2 — Extraction (LLM-assisted)

For each segment, the LLM extracts the M01 schema fields. Prompt constraints:

```
Extract the following fields from this source segment.
Use only information explicitly present in the text.
Do not infer, generalize, or add criteria not stated.
If a field cannot be filled from the source, set it to null and explain why.
Output strictly as JSON matching the AKU schema.
```

LLM output is **always treated as a draft**, never directly activated. Expert review is mandatory.

### Stage 3 — Schema Validation

Run M01 schema validator on each extracted AKU draft. Reject immediately on:
- Missing required fields
- Type violations
- Invalid status value
- Empty `required_criteria`

### Stage 4 — Integrity Checks

Run all M01 integrity constraints:
- No circular definitions
- Conflict symmetry (may require cross-referencing existing KB)
- Parent coherence
- No criteria duplication

### Stage 5 — Deduplication

Compare new AKU candidates against existing active AKUs using semantic similarity.

| Similarity Score | Action |
|-----------------|--------|
| >= 0.95 | Flag as probable duplicate; block activation; require explicit merge decision |
| 0.80–0.94 | Flag as possible duplicate; add to review queue; allow activation with reviewer sign-off |
| < 0.80 | No duplicate concern; proceed |

### Stage 6 — Review Queue

All AKUs that pass schema + integrity checks are placed in the review queue for domain expert approval. The expert verifies:

- Criteria faithfully represent the source document
- Exclusion criteria are complete
- Relations (parent, children, conflicts) are correctly declared
- Source provenance is accurate

### Stage 7 — Activation

Upon approval, the AKU transitions to `active`, M02 stores it, and a snapshot update is triggered.

---

## Batch Ingestion

For large source documents (e.g., a full clinical guideline with 50+ criteria sets), ingestion runs as a batch job:

```
batch_ingest(source_document, domain, ontology_version)
  -> ingestion_report {
       segments_extracted: N,
       aku_drafts_created: N,
       schema_rejections: N,
       integrity_failures: N,
       duplicates_flagged: N,
       review_queue_entries: N
     }
```

Batch jobs are asynchronous; the review queue is populated on completion.

---

## Ingestion Report Schema

```json
{
  "ingestion_id": "ING-20250601-0042",
  "source": "WHO Diabetes Diagnostic Criteria 2023",
  "domain": "endocrinology",
  "started_at": "2025-06-01T09:00:00Z",
  "completed_at": "2025-06-01T09:14:32Z",
  "segments_extracted": 24,
  "aku_drafts_created": 21,
  "schema_rejections": 3,
  "integrity_failures": 1,
  "duplicates_flagged": 2,
  "review_queue_entries": 18,
  "rejection_details": [
    { "segment_ref": "§3.2.1", "reason": "required_criteria empty after extraction" }
  ]
}
```

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM extraction returns malformed JSON | Retry once; then reject segment; log for manual review |
| Schema validation fails | Reject AKU draft; include in ingestion report |
| Integrity check fails | Reject AKU draft; surface specific constraint violated |
| Deduplication service unavailable | Proceed without dedup check; flag all new AKUs for manual duplicate review |
| Review queue write fails | Block activation; retry; alert |
