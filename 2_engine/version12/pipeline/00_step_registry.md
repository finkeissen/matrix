# Step Registry v2 — Atomic Problem Identification Pipeline
## All 15 Envelopes

**Version:** 2.0.0
**Reference:** `00_step_registry.md` (original, do not modify), `engine.md` (decision log)
**Replaces:** `04_hypothesis` → `04a_generation` + `04b_generation_review`
**Key changes from v1:** Generative semantics throughout; two-stage generation (E-05); model routing per step (E-06); category-scoped envelopes for steps 04a/04b; `kb_snapshot_id` = sha256(subdomains.jsonl) (E-03).

---

## Envelope Summary Table

| Step | Type | Model | Retries | Novelty Guard | Snapshot After | Required Outputs |
|------|------|-------|---------|---------------|----------------|-----------------|
| `01_scope` | llm | 19b | 1 | yes | no | `scope` |
| `01_scope_confidence` | llm | 19b | 1 | yes | no | `scope_confidence` |
| `02_retrieval` | deterministic | — | 0 | no | no | `canonical_structure` |
| `03_categories` | llm | 35b | 1 | yes | no | `categories` |
| `03_normalize` | deterministic | — | 0 | no | no | `normalized_categories` |
| `03_gap_detection` | llm | 35b | 1 | yes | **yes** | `gap_detection` |
| `04a_generation` ×N | llm | 35b | 1 | yes | no | `problems_draft` |
| `04b_generation_review` ×N | llm | 122b | 1 | yes | no | `problems_reviewed` |
| `05_validation` | deterministic+llm | 35b | 0 | no | **yes** | `validation_report` |
| `06_clarification` | llm | 19b | 1 | yes | **yes** | `clarification_request` |
| `07_hallucination_scan` | llm | 122b | 1 | yes | no | `hallucination_report` |
| `07_alternative_check` | llm | 35b | 1 | yes | no | `alternative_check` |
| `08_finalization` | deterministic+llm | 19b | 1 | yes | **yes** | `final_problems` |
| `09_commit` | deterministic | — | 0 | no | **yes** | `commit_record` |

> **×N** — Steps `04a` and `04b` are instantiated once per category from `03_normalize` output. Each instance is an independent envelope with its own `task_id`. N = number of normalized categories.

---

## Input/Output Chain

```
subdomain_definition (from subdomains.jsonl + seed CSV)
    │
    ▼ [01_scope]
scope{ subdomain, parent_domain, canonical_source, boundaries, exclusions, ambiguities[] }
    │
    ▼ [01_scope_confidence]
scope_confidence{ score, flagged_ambiguities[], recommendation }
    │
    ▼ [02_retrieval]
canonical_structure{ source_id, chapters[], entries[], retrieval_method }
    │
    ▼ [03_categories]
categories{ items[{ name, description, estimated_problem_count }] }
    │
    ▼ [03_normalize]
normalized_categories{ items[{ name_normalized, name_original, description }] }  ◄── deterministic
    │
    ├─ for each category:
    │       ▼ [04a_generation]
    │   problems_draft{ category, problems[{ title, problem_statement, ... }] }
    │       │
    │       ▼ [04b_generation_review]
    │   problems_reviewed{ category, problems[atomic_problem schema], changes_made[] }
    │
    ▼ [merge all 04b outputs]
    │
    ▼ [05_validation]
validation_report{ valid, schema_errors[], duplicates[], atomicity_failures[], completeness_score }
    │
    ├─[scope_unclear, round < 2]──► [06_clarification]
    │                                clarification_request{ questions[], scope_refinement }
    │                                └─► back to 01_scope with refined input (E-01: max 2 rounds)
    ▼
    ▼ [07_hallucination_scan]
hallucination_report{ flagged[{ problem_id, risk_level, reason }], scan_coverage }
    │
    ▼ [07_alternative_check]
alternative_check{ coverage_gaps[], recategorization_suggestions[], decision }
    │
    ▼ [08_finalization]
final_problems{ problems[atomic_problem schema, ids assigned], run_audit{} }  ◄── JSONL output
    │
    ▼ [09_commit]
commit_record{ problems_committed, registry_appended, snapshot_after }
    └─► registry/problems.jsonl (append-only)
```

---

## Scheduling Order

Steps are dispatched in index order. No parallel execution within a single run. `04a`/`04b` instances for different categories are sequential (ordered by normalized category index).

```
01_scope → 01_scope_confidence → 02_retrieval → 03_categories → 03_normalize → 03_gap_detection
→ [04a_cat_1 → 04b_cat_1] → [04a_cat_2 → 04b_cat_2] → ... → [04a_cat_N → 04b_cat_N]
→ 05_validation → [06_clarification → loop back to 01_scope, max 2 rounds]
→ 07_hallucination_scan → 07_alternative_check → 08_finalization → 09_commit
```

Retries re-dispatch the same envelope; downstream steps do not execute until retry resolves or STOP is emitted.

---

## Generation Retry Context Injection

When `04b_generation_review` flags problems as non-atomic or requests regeneration for a category, `04a` is re-created with enriched inputs:

```json
{
  "inputs": {
    "scope_hash": "sha256:...",
    "category_hash": "sha256:...",
    "retry_context_hash": "sha256:..."
  }
}
```

The new `task_id` differs because inputs differ — treated as a new task. Prior `problems_draft` artifact marked `superseded` in manifest.

---

## Clarification Re-entry (E-01)

When `05_validation` flags scope as unclear (`scope_unclear: true`):

1. `06_clarification` runs → produces `clarification_request`
2. Orchestrator checks `run_record.clarification_rounds`:
   - If `< 2`: increment counter, re-run `01_scope` with refined input → new `task_id`
   - If `>= 2`: STOP with code `scope_clarification_exhausted`
3. Pipeline continues from `01_scope` forward on re-entry
4. Prior `scope`, `categories`, `normalized_categories`, `gap_detection` artifacts marked `superseded`
5. All `04a`/`04b` envelopes are re-instantiated from new categories

---

## kb_snapshot_id (E-03)

In generation runs, `kb_snapshot_id` is not a knowledge base snapshot — it is the content hash of the subdomain registry:

```
kb_snapshot_id = sha256(subdomains.jsonl content)
```

Computed at preflight. Written into `run_record.json`. All envelopes in the run reference the same `kb_snapshot_id`. Cross-run Novelty Guard reuse is only valid when `kb_snapshot_id` matches — ensuring stale cache hits are prevented when the subdomain registry changes.

---

## Model Routing Summary (E-06)

| Model | Steps | Rationale |
|-------|-------|-----------|
| `19b` (19B/A3B, 65 T/s) | `01_scope`, `01_scope_confidence`, `06_clarification`, `08_finalization` (explanation) | Fast, structured JSON output, no deep reasoning required |
| `35b` (35B/A3B, 30 T/s) | `03_categories`, `03_gap_detection`, `04a_generation`, `05_validation` (LLM part), `07_alternative_check` | Balanced knowledge breadth and generation quality |
| `122b` (122B/A10B) | `04b_generation_review`, `07_hallucination_scan` | Strongest reasoning; atomicity enforcement and hallucination detection justify the cost |

`policy.model` is declared per envelope. Executor resolves model ID to local endpoint at dispatch time.

---

## Re-Run Strategy (E-07)

Periodic re-runs (every ~3 months or on new model availability) target only the generation and review steps:

```
Steps re-run:   04a_generation → 04b_generation_review → 05_validation
                → 07_hallucination_scan → 08_finalization → 09_commit

Steps skipped:  01_scope, 01_scope_confidence, 02_retrieval,
                03_categories, 03_normalize, 03_gap_detection
                (Novelty Guard: same inputs + same kb_snapshot_id → cache hit)
```

New problems committed as `review_status: draft`. Existing `approved` problems are never overwritten. All versions traceable via `created_by` and `run_log.jsonl`.
