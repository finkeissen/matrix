# Pipeline Overview
## Step Index & Execution Map

**Version:** 1.0.0
**Status:** Reference
**Related:** `PIPELINE_v2.md`, `GIA_v2.md`

---

## Execution Sequence

```
User Input
    │
    ▼
01_parsing          → structured case facts
    │
    ▼
02_retrieval        → ranked AKU context
    │
    ▼
03_enrichment       → normalized + deduplicated entities
    │
    ▼
04_hypothesis       → candidate AKU(s) with citations
    │
    ▼
05_validation       → validation report (accept / reject / clarify)
    │
    ├──[missing facts]──► 06_clarification ──► (back to 01)
    │
    ▼
06_examination      → adversarial stress-test of candidate
    │
    ├──[rejected, retry ≤ 2]──► 04_hypothesis
    │
    ▼
07_finalization     → structured output + audit trace
    │
    ▼
08_commit           → state snapshot published
```

---

## Step Registry

| File | Step | Input | Output | Deterministic |
|------|------|-------|--------|---------------|
| `01_parsing.md` | Semantic Parsing | Raw user text | `case_facts` | No (LLM) |
| `02_retrieval.md` | AKU Retrieval | `case_facts` | `context_units[]` | Yes |
| `03_enrichment.md` | Entity Enrichment | `context_units[]` | Enriched entities + patches | No (LLM) |
| `04_hypothesis.md` | Hypothesis Generation | `case_facts`, `context_units[]` | `candidate` + rationale | No (LLM) |
| `05_validation.md` | Deterministic Validation | `candidate`, `case_facts` | `validation_report` | Yes |
| `06_clarification.md` | Clarification Loop | `validation_report` | Clarification questions | No (LLM) |
| `07_examination.md` | Adversarial Examination | `candidate`, `validation_report` | Examination result | No (LLM) |
| `08_finalization.md` | Finalization & Output | All prior outputs | Final answer + trace | Yes |
| `09_commit.md` | Commit Gate | Proposed patches | Committed state snapshot | Yes |

---

## Core Contract (All Steps)

Every step implements:

```
update(state, inputs, params) -> (patches, report)
```

- `state` is read-only.
- `patches` are append-only proposals; applied only after commit gate.
- `report` is machine-readable with `status: ok | warn | error | blocked`.

See `PIPELINE_v2.md §2` for full contract specification.

---

## Failure Routing

| Condition | Route |
|-----------|-------|
| Missing required case facts | 05 → 06_clarification → 01 |
| Validation failed, retry available (≤ 2) | 05 → 04_hypothesis |
| Examination rejected, retry available (≤ 2) | 07 → 04_hypothesis |
| Max retries exceeded | 08_finalization with `status: insufficient` |
| No relevant AKU found | 02 → 08_finalization with `status: no_knowledge` |
