# Pipeline Overview — v2
## Step Index & Execution Map (Small-LLM Optimized)

**Version:** 2.0.0
**Status:** Reference
**Supersedes:** `00_overview.md` v1.0.0
**Related:** `PIPELINE_v2.md`, `GIA_v2.md`, `M00_index.md`

---

## Design Rationale

Steps marked LLM in v1 were split where a single prompt required more than one distinct cognitive task. The rule applied:

> **One prompt — one task — one flat output object (≤ 8 fields).**

Steps 01, 03, and 07 were split. Steps 02, 04, 05, 06, 08, 09 are unchanged.

---

## Execution Sequence

```
User Input
    │
    ▼
01_parsing_01_extraction          → raw key-value facts (no scoring)
    │
    ▼
01_parsing_02_confidence          → confidence score per field + unparsed fragments
    │
    ▼
02_retrieval                      → ranked AKU context           [UNCHANGED]
    │
    ▼
03_enrichment_01_terminology      → colloquial terms → canonical field names
    │
    ▼
03_enrichment_02_unit_normalization → unit conversions (rule-based, no LLM)
    │
    ▼
03_enrichment_03_gap_detection    → missing fields vs AKU criteria
    │
    ▼
04_hypothesis                     → candidate AKU(s) with criteria mapping [UNCHANGED]
    │
    ▼
05_validation                     → validation report             [UNCHANGED]
    │
    ├──[missing facts]──► 06_clarification ──► (back to 01_parsing_01)
    │
    ▼
07_examination_01_weakness_scan   → weak/ambiguous criteria identified
    │
    ▼
07_examination_02_alternative_check → better AKU candidates in context?
    │
    ├──[rejected, retry ≤ 2]──► 04_hypothesis
    │
    ▼
08_finalization                   → structured output + audit trace [UNCHANGED]
    │
    ▼
09_commit                         → state snapshot published       [UNCHANGED]
```

---

## Full Step Registry

| File | Parent Step | Task | LLM | Deterministic |
|------|-------------|------|-----|---------------|
| `01_parsing_01_extraction.md` | 01_parsing | Extract raw facts from text | Yes | No |
| `01_parsing_02_confidence.md` | 01_parsing | Score confidence per field | Yes | No |
| `02_retrieval.md` | — | AKU vector search + hierarchy | No | Yes |
| `03_enrichment_01_terminology.md` | 03_enrichment | Map terms to canonical names | Yes | No |
| `03_enrichment_02_unit_normalization.md` | 03_enrichment | Convert units via rule table | No | Yes |
| `03_enrichment_03_gap_detection.md` | 03_enrichment | Identify missing AKU criteria fields | Yes | No |
| `04_hypothesis.md` | — | Propose candidate AKU(s) | Yes | No |
| `05_validation.md` | — | Deterministic criteria check | No | Yes |
| `06_clarification.md` | — | Generate targeted questions | Yes | No |
| `07_examination_01_weakness_scan.md` | 07_examination | Find weakly supported criteria | Yes | No |
| `07_examination_02_alternative_check.md` | 07_examination | Find better AKU alternatives | Yes | No |
| `08_finalization.md` | — | Assemble result + explanation | Yes (1 call) | Partial |
| `09_commit.md` | — | Commit gate + snapshot | No | Yes |

---

## Output Handoff Chain

```
raw_text
  → [01_01] raw_facts{}
  → [01_02] raw_facts{} + confidence{} + unparsed_fragments[]
  → [02]    context_units[]
  → [03_01] facts_normalized{} (canonical field names)
  → [03_02] facts_normalized{} (canonical units)
  → [03_03] facts_normalized{} + missing_fields[]
  → [04]    candidate{} + matched_criteria[] + missing_criteria[]
  → [05]    validation_report{}
  → [07_01] weak_criteria[]
  → [07_02] decision + better_alternatives[]
  → [08]    final_answer{} + audit_trace{}
  → [09]    committed_snapshot
```

---

## Prompt Budget Guidelines (Small LLM)

| Step | Input tokens (est.) | Output tokens (est.) | Output fields |
|------|--------------------|--------------------|---------------|
| 01_01 extraction | 200–600 | 100–300 | 5 |
| 01_02 confidence | 300–500 | 100–200 | 4 |
| 03_01 terminology | 400–800 | 100–250 | 4 |
| 03_03 gap detection | 600–1200 | 100–200 | 3 |
| 04 hypothesis | 800–2000 | 200–500 | 7 |
| 06 clarification | 400–800 | 100–300 | 4 |
| 07_01 weakness scan | 600–1200 | 150–350 | 5 |
| 07_02 alternative check | 500–1000 | 100–200 | 4 |
| 08 explanation | 400–800 | 100–300 | 3 |

All output schemas are **flat** (no nested objects) unless marked otherwise.

---

## Failure Routing

| Condition | Route |
|-----------|-------|
| No facts extractable (01_01) | Warn; empty facts; proceed to 02 |
| All confidence < 0.5 (01_02) | Warn; flag for clarification after validation |
| No AKU found (02) | → 08_finalization `status: no_knowledge` |
| No canonical mapping found (03_01) | Retain original; flag field |
| Unit conversion rule missing (03_02) | Retain original; flag field |
| Candidate NO_MATCH (04) | → 08_finalization `status: no_match` |
| Missing required facts (05) | → 06_clarification → 01_01 |
| Validation rejected (05) | Retry 04 (≤ 2x) or → 08 `status: insufficient` |
| High-severity weakness (07_01) | → reject → 04 retry |
| Better alternative found (07_02) | Surface in 08; do not auto-substitute |
| Max retries exceeded | → 08_finalization `status: insufficient` |

---

## Core Contract (All Steps)

```
update(state, inputs, params) -> (patches, report)
```

- `state` read-only during execution.
- `patches` append-only; committed only via 09_commit.
- `report.status`: `ok | warn | error | blocked`.

See `PIPELINE_v2.md §2` for full specification.
