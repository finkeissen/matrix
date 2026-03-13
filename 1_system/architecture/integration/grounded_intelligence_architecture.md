# Grounded Intelligence Architecture
## A Complete Framework for Solving Atomic Problems with Validated Knowledge

**Version:** 2.0.0
**Status:** Reference Architecture
**Scope:** Domain-agnostic

---

## Table of Contents

1. Purpose
2. Core Principles
3. Definitions
4. Architectural Overview
5. Knowledge Model
6. Retrieval Layer
7. Validation Layer
8. LLM Orchestration
9. Multi-Agent Self-Correction
10. Interfaces & APIs
11. End-to-End Execution Flow
12. Transparency & Auditability
13. Knowledge Lifecycle & Versioning
14. Security & Governance
15. Scalability & Performance
16. Maturity Model
17. Implementation Roadmap
18. Design Anti-Patterns
19. Formal Model
20. Summary

---

## 1. Purpose

This document defines a production-grade architecture for AI systems that solve **atomic problems** using **structured, validated, and externally grounded knowledge**.

The framework transforms probabilistic language models into systems that are:

- **Rule-aligned:** reasoning is constrained by deterministic criteria, not model priors.
- **Auditable:** every conclusion is traceable to a specific knowledge unit and validation result.
- **Hallucination-resistant:** the model cannot assert facts that lack explicit grounding in the knowledge base.

This architecture is applicable to any domain in which correctness depends on formal definitions, explicit criteria, or regulated rule sets — including medical classification, legal compliance, technical diagnostics, and enterprise decision support.

---

## 2. Core Principles

| # | Principle | Implication |
|---|-----------|-------------|
| 1 | External knowledge overrides model memory. | The knowledge base is the ground truth; model weights are fallback only. |
| 2 | Structured data overrides free text. | Formal criteria take precedence over natural language descriptions. |
| 3 | Validation overrides probability. | A statistically plausible but unvalidated answer is rejected. |
| 4 | Determinism at rule layer, flexibility at language layer. | Rules are hard constraints; natural language is used only for interface and explanation. |
| 5 | Transparency is non-negotiable. | Every output must reference its source AKUs and validation result. |
| 6 | Every conclusion must be reproducible. | Given the same input and knowledge snapshot, the system must return the same result. |

---

## 3. Definitions

### 3.1 Atomic Problem

A problem whose solution depends exclusively on:

- Explicit, formally declared definitions
- Enumerated inclusion and exclusion criteria
- Deterministic rules with no ambiguity
- Structured relational constraints (parent/child, mutual exclusion, dependency)

*Example (medical):* Determining whether a patient meets diagnostic criteria for Type 2 Diabetes Mellitus based on fasting glucose thresholds, HbA1c values, and exclusion of Type 1 indicators.

*Example (legal compliance):* Determining whether a software product qualifies as a "high-risk AI system" under EU AI Act Article 6, based on enumerated use-case categories.

### 3.2 Atomic Knowledge Unit (AKU)

The smallest independently verifiable unit of structured knowledge required to resolve a problem. An AKU is not a document or a chunk — it is a formalized, versioned, relational entity with explicit criteria.

### 3.3 Grounded Reasoning

Reasoning that is logically constrained to a retrieved, validated subset of the knowledge base. The model may not introduce claims, criteria, or relationships that are not present in the retrieved context.

---

## 4. Architectural Overview

The system is organized as a sequential, independently auditable pipeline:

```
User Input
  → [1] Semantic Parsing         — extract structured case facts
  → [2] Retrieval                — fetch relevant AKUs + hierarchy
  → [3] Hypothesis Generation    — LLM proposes candidate(s) with AKU citations
  → [4] Deterministic Validation — rule engine checks criteria
  → [5] Self-Consistency Check   — adversarial agent examines the candidate
  → [6] Finalization             — structured, transparent output
```

Each stage produces a discrete artifact (parsed facts, ranked AKUs, candidate, validation report, final answer) and can be independently tested, mocked, or replayed.

### 4.1 Component Dependency Map

```
Knowledge Base ──► Retrieval Layer ──► LLM Orchestrator ──► Output
       │                                      │
       └──────────► Validation Engine ◄───────┘
                          │
                    Audit Logger
```

### 4.2 Failure Modes and Fallback Behavior

| Failure | Behavior |
|---------|----------|
| No relevant AKU found | Return "insufficient knowledge" response; do not guess. |
| Missing required case facts | Trigger clarification loop; ask targeted questions. |
| Validation fails | Return failure report with specific missing/violated criteria. |
| LLM unavailable | Return cached result if reproducible; else degrade gracefully. |

---

## 5. Knowledge Model

### 5.1 Atomic Knowledge Unit — Full Schema

```json
{
  "id": "AKU-00123",
  "title": "Type 2 Diabetes Mellitus — Diagnostic Criteria",
  "definition": "A metabolic disorder characterized by chronic hyperglycemia resulting from insulin resistance, with or without relative insulin deficiency.",
  "required_criteria": [
    "Fasting plasma glucose >= 7.0 mmol/L on two separate occasions",
    "OR HbA1c >= 48 mmol/mol (6.5%) confirmed by repeat test",
    "OR 2-hour plasma glucose >= 11.1 mmol/L during OGTT"
  ],
  "exclusion_criteria": [
    "Confirmed autoimmune beta-cell destruction (Type 1 indicator)",
    "Secondary diabetes due to exocrine pancreatic pathology"
  ],
  "relations": {
    "parent": "AKU-00100",
    "children": ["AKU-00124", "AKU-00125"],
    "conflicts_with": ["AKU-00130"]
  },
  "metadata": {
    "domain": "endocrinology",
    "version": "2.1.0",
    "created_at": "2024-01-15T00:00:00Z",
    "updated_at": "2025-03-01T00:00:00Z",
    "source": "WHO Diabetes Diagnostic Criteria 2023",
    "reviewed_by": "domain-expert-id-42",
    "status": "active"
  }
}
```

### 5.2 Required Properties

Every AKU must declare:

- A globally unique, stable identifier (never reused after deprecation)
- At least one explicit required criterion (no implicit "common knowledge" criteria)
- Explicit exclusion criteria (even if empty, this must be declared as `[]`)
- All relations (parent, children, conflicts) — no undeclared dependencies
- Full version metadata with source provenance

### 5.3 Knowledge Integrity Constraints

The knowledge base must enforce at ingestion time:

- **No circular definitions:** AKU-A cannot depend on AKU-B if AKU-B depends on AKU-A.
- **No implicit criteria:** every decision condition must be machine-readable.
- **No hidden dependencies:** all structural relationships must be explicitly declared.
- **Conflict symmetry:** if AKU-A conflicts with AKU-B, AKU-B must declare a conflict with AKU-A.
- **Parent coherence:** every declared parent ID must reference an existing, active AKU.

---

## 6. Retrieval Layer

### 6.1 Purpose

Reduce the reasoning space to a bounded, relevant set of AKUs before the LLM is invoked. The retrieval layer prevents both under-retrieval (missing critical context) and over-retrieval (confusing the model with irrelevant material).

### 6.2 Architecture

```
Input Text / Case Facts
        │
        ▼
  Embedding Generator       ← domain-tuned model preferred
        │
        ▼
  Vector Database Search    ← approximate nearest neighbor (ANN)
        │
        ▼
  Metadata Filter           ← domain, version, status=active
        │
        ▼
  Hierarchical Expander     ← include parent + sibling AKUs
        │
        ▼
  Ranker                    ← score by relevance + structural importance
        │
        ▼
  Bounded Context (top-k)   ← enforce hard upper limit on AKU count
```

### 6.3 Retrieval Rules

- Always retrieve the **ancestor path** (breadcrumb) of every matched AKU to provide structural context.
- Enforce a **hard context limit** (e.g., top-15 AKUs) to prevent context dilution.
- Always include AKU identifiers in the context payload — the LLM must cite them.
- Filter by `status: active` to exclude deprecated units unless explicitly queried.
- Log retrieval parameters (top-k, filters, embedding model version) for auditability.

### 6.4 Retrieval Quality Metrics

| Metric | Target |
|--------|--------|
| Recall@10 (relevant AKUs retrieved) | ≥ 0.90 |
| Precision@10 | ≥ 0.75 |
| Mean Reciprocal Rank (MRR) | ≥ 0.85 |
| Latency (p95) | < 200ms |

---

## 7. Validation Layer

### 7.1 Role and Constraints

The validation layer is **deterministic and non-bypassable.** The LLM may not override it. A candidate answer is only accepted if `validation_report.valid == true`. All other outcomes trigger clarification or rejection.

### 7.2 Validation Checks

For each candidate solution, the validator executes the following checks in order:

1. **Required criteria check:** are all `required_criteria` of the target AKU satisfied by the case facts?
2. **Exclusion check:** do any case facts match `exclusion_criteria`? If yes, the candidate is rejected.
3. **Structural consistency check:** are parent/child/sibling constraints respected?
4. **Conflict check:** does selecting this AKU violate any `conflicts_with` relationships?

### 7.3 Validation Output Contract

```json
{
  "candidate_id": "AKU-00123",
  "valid": false,
  "matched_required": [
    "Fasting plasma glucose >= 7.0 mmol/L confirmed"
  ],
  "missing_required": [
    "Confirmation on second separate occasion not documented"
  ],
  "violated_exclusions": [],
  "conflicts": [],
  "structural_issues": [],
  "notes": [
    "Single glucose reading is insufficient per WHO 2023 criteria. Request repeat measurement."
  ]
}
```

### 7.4 Clarification Trigger

If `missing_required` is non-empty and the missing facts are potentially obtainable from the user, the system must generate **targeted clarification questions** — one question per missing criterion — rather than returning an indeterminate result.

*Example clarification output:*
> "To complete the assessment, one additional data point is required: Was the fasting plasma glucose measurement confirmed on a second, separate occasion? (Yes / No / Not yet measured)"

---

## 8. LLM Orchestration

### 8.1 Responsibilities

The LLM performs only the following tasks. It does not validate, does not access the knowledge base directly, and does not make final decisions.

| Task | Description |
|------|-------------|
| Semantic parsing | Extract structured case facts from user input |
| Fact normalization | Standardize units, terminology, and format |
| Criteria comparison | Map case facts to AKU criteria |
| Candidate proposal | Propose one or more candidate AKU IDs with justification |
| Explanation generation | Produce a user-facing natural language explanation |
| Clarification generation | Formulate targeted questions for missing facts |

### 8.2 Minimum Prompt Constraints

Every prompt sent to the LLM must include the following instructions:

```
CONSTRAINTS:
1. Use only the AKUs provided in this context. Do not introduce external knowledge.
2. Cite the AKU ID for every claim you make.
3. List matched criteria and missing criteria explicitly and separately.
4. If required criteria are incomplete, generate targeted clarification questions — do not guess.
5. If no AKU in the context is sufficient, respond with: "INSUFFICIENT_KNOWLEDGE" and propose next steps.
6. Express uncertainty as a structured field, not as hedging language.
```

### 8.3 Required Output Schema

```json
{
  "parsed_facts": {},
  "candidate_aku_id": "AKU-00123",
  "matched_criteria": [],
  "missing_criteria": [],
  "excluded_criteria_triggered": [],
  "uncertainty": {
    "level": "medium",
    "reason": "One required criterion cannot be confirmed from available facts."
  },
  "alternatives": [],
  "explanation": "Human-readable summary for the end user.",
  "clarification_questions": []
}
```

### 8.4 Prompt Engineering Patterns

**Pattern A — Criteria Matching Prompt (abbreviated):**
```
You are a diagnostic reasoning assistant. You have been given:
- Case facts: {case_facts}
- Relevant AKUs: {aku_context}

Task: Identify which AKU best matches the case facts.
Follow the output schema exactly. Cite AKU IDs. Do not guess.
```

**Pattern B — Clarification Prompt:**
```
The following required criteria could not be confirmed: {missing_criteria}
Generate one targeted question per missing criterion.
Questions must be answerable with structured data (yes/no, numeric value, date).
```

---

## 9. Multi-Agent Self-Correction

### 9.1 Motivation

A single-pass LLM response is subject to self-confirmation bias — the model tends to justify its first candidate rather than rigorously test it. Multi-agent separation enforces adversarial verification.

### 9.2 Agent Roles

| Agent | Role | May Access |
|-------|------|------------|
| **Generator (A)** | Proposes candidate AKU + rationale | Retrieved AKUs, case facts |
| **Rule Engine** | Executes deterministic validation | Knowledge base, validation rules |
| **Examiner (B)** | Stress-tests candidate strictly against criteria | Candidate + validation report |
| **Finalizer** | Consolidates result, uncertainty, and alternatives | All outputs |

### 9.3 Examiner Prompt Pattern

```
You are a strict criteria examiner. Your role is adversarial — find reasons to reject.
Candidate: {candidate_aku_id}
Validation report: {validation_report}

Your tasks:
1. Identify any criterion that was marked as matched but is weakly supported by case facts.
2. Identify any alternative AKU that may be a better fit.
3. Flag if confidence in the candidate is below threshold.

Do not be lenient. If in doubt, reject.
```

### 9.4 Correction Loop

```
Generator → Rule Engine → Examiner
                              │
                    ┌─────────┴──────────┐
                    │ Rejected           │ Accepted
                    ▼                    ▼
             Clarification          Finalizer
             Loop / Alt             → Output
```

Maximum correction iterations: 2. After 2 failed attempts, return structured uncertainty response.

---

## 10. Interfaces & APIs

### 10.1 Knowledge Base API

```
GET    /units/{id}                         → AKU object
GET    /units/{id}/relations               → related AKU IDs and types
GET    /units/{id}/criteria                → required + exclusion criteria
GET    /units/{id}/history                 → version history
GET    /version                            → current KB snapshot ID + timestamp
SEARCH /units?query=...&domain=...&status= → ranked AKU list
POST   /units                              → create AKU (authorized roles only)
PUT    /units/{id}                         → update AKU (triggers version bump)
```

### 10.2 Retrieval API

```
POST /embed          { text }                         → vector
POST /search         { vector, filters, top_k }       → ranked_units[]
POST /expand         { aku_id }                       → ancestor path + siblings
```

### 10.3 Validation API

```
POST /validate       { candidate_id, case_facts }     → validation_report
POST /check-conflict { candidate_id, context_ids }    → conflict_report
POST /check-structure { candidate_id }                → structural_report
```

### 10.4 Orchestration Interface

```
POST /parse          { raw_input }                    → case_facts
POST /retrieve       { case_facts }                   → context_units[]
POST /build-prompt   { case_facts, context_units }    → prompt
POST /generate       { prompt }                       → candidates[]
POST /finalize       { case_facts, context_units, validation_reports } → answer
```

### 10.5 Audit Interface

```
POST /traces         { trace }                        → trace_id
GET  /traces/{id}                                     → full_decision_record
GET  /traces/{id}/replay                              → reproduce result from snapshot
```

---

## 11. End-to-End Execution Flow

```
1. User submits problem statement.
2. Parser extracts structured case facts (with confidence scores per field).
3. Retrieval fetches top-k AKUs + ancestor paths from the active KB snapshot.
4. Generator proposes candidate(s) with AKU citations and criteria mapping.
5. Rule Engine runs required / exclusion / conflict / structural checks.
6. If missing required facts → generate clarification questions → return to user.
7. Examiner stress-tests the candidate against the validation report.
8. If rejected → retry with alternatives (max 2 iterations).
9. Finalizer constructs structured output: result, confidence, alternatives, trace ID.
10. Audit logger records full decision trace (input, KB version, retrieval config, validation).
```

---

## 12. Transparency & Auditability

### 12.1 Mandatory Output Fields

Every system response must include:

| Field | Description |
|-------|-------------|
| `kb_version` | Snapshot ID of the knowledge base used |
| `aku_ids_used` | List of all AKU IDs referenced |
| `retrieval_config` | top-k value, filters applied, embedding model version |
| `validation_report` | Full structured validation output |
| `timestamp` | ISO 8601 UTC |
| `system_version` | Version of the orchestration system |
| `trace_id` | Optional; enables full replay |

### 12.2 Reproducibility Guarantee

A result is reproducible if and only if:

- The same KB snapshot version is used.
- The same case facts (normalized) are provided as input.
- The same retrieval configuration (top-k, filters) is applied.
- The same system version is running.

These four parameters must be stored with every audit trace.

---

## 13. Knowledge Lifecycle & Versioning

### 13.1 Versioning Scheme

The knowledge base uses **semantic versioning** (`MAJOR.MINOR.PATCH`):

| Increment | Trigger | Impact |
|-----------|---------|--------|
| PATCH | Typo fix, metadata correction | No behavioral change |
| MINOR | New AKU added, criteria clarified | Additive; existing results unaffected |
| MAJOR | Criteria changed, AKU deprecated/replaced | May change existing results; requires regression testing |

MAJOR version bumps require a **migration report** documenting which prior results may be affected and why.

### 13.2 AKU Lifecycle States

```
Draft → Review → Active → Deprecated → Archived
                   │
                   └─► Superseded (replaced by new AKU version)
```

- **Active:** used in retrieval and validation.
- **Deprecated:** excluded from retrieval; existing traces remain valid.
- **Archived:** immutable historical record; not queryable in production.

### 13.3 Update Workflow

```
1. Author submits AKU update (PR / change request).
2. Automated integrity checks run (circular dependency, schema validation, conflict symmetry).
3. Domain expert review and approval (required for MINOR and MAJOR changes).
4. Regression test suite executes against existing validated cases.
5. Embeddings updated (incremental or full rebuild depending on change scope).
6. New snapshot published with version bump and changelog entry.
7. Backward ID mapping updated if identifiers change.
```

### 13.4 Regression Testing

Each MINOR or MAJOR update must run against a curated set of **canonical test cases** — known inputs with expected outputs — to detect unintended behavioral changes. Failures block the release until resolved.

---

## 14. Security & Governance

### 14.1 Access Control

| Role | Permissions |
|------|-------------|
| Reader | Query AKUs, retrieve results |
| Contributor | Submit new AKUs (Draft state only) |
| Reviewer | Approve transitions to Active; reject with rationale |
| Administrator | Deprecate, archive, manage schema, manage users |

All write operations are authenticated, timestamped, and attributed to a named user.

### 14.2 Audit Log Requirements

- Immutable append-only log (no deletions, no edits).
- Every query, validation, and output is logged with: user/session ID, input hash, KB snapshot version, result hash, timestamp.
- Audit logs are stored separately from the operational database and are tamper-evident.

### 14.3 Provenance Tracking

Every AKU must declare:

- `source`: the authoritative external document or regulation it encodes.
- `reviewed_by`: the user ID of the domain expert who approved it.
- `review_date`: ISO 8601 date of last review.

### 14.4 Domain Boundary Enforcement

AKUs are tagged with a `domain` field. The retrieval layer enforces domain isolation: a query scoped to `endocrinology` cannot retrieve AKUs from `oncology` unless cross-domain retrieval is explicitly enabled and logged.

### 14.5 Safe-Fail Behavior

When the system cannot produce a validated answer, it must return a structured uncertainty response — never a fabricated result. The default failure mode is **transparent refusal**, not silent degradation.

---

## 15. Scalability & Performance

| Concern | Strategy |
|---------|----------|
| Ingestion throughput | Batch embedding pipelines; async KB updates |
| Query latency | ANN index with metadata pre-filters; result caching for frequent queries |
| Validation throughput | Stateless validation workers; horizontal scaling |
| Context window limits | Retrieval hard cap (top-k) prevents oversized prompts |
| Embedding freshness | Incremental re-embedding on PATCH; full rebuild on MAJOR |
| Graceful degradation | Return cached validated result or structured uncertainty on LLM timeout |

**Target SLAs:**

| Operation | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| Retrieval | 80ms | 200ms | 500ms |
| Validation | 20ms | 50ms | 150ms |
| End-to-end (no clarification) | 1.5s | 4s | 8s |

---

## 16. Maturity Model

| Level | Capability | Key Indicator |
|-------|------------|---------------|
| **1 — Basic RAG** | Semantic retrieval, unvalidated LLM response | Answers are grounded but not validated |
| **2 — Validated RAG** | Retrieval + deterministic validation layer | Invalid answers are rejected, not returned |
| **3 — Structural Reasoning** | Hierarchical navigation, structural consistency checks | Parent/child/conflict constraints enforced |
| **4 — Adversarial Verification** | Multi-agent self-correction, examiner agent | Candidates are stress-tested before acceptance |
| **5 — Governed Intelligence** | Full versioning, audit, reproducibility, governance workflow | Every result is replayable and governed |

Organizations should treat Level 3 as the minimum for production use in regulated domains.

---

## 17. Implementation Roadmap

### Phase 1 — Foundations (Weeks 1–4)

**Goal:** A queryable, versioned knowledge base with well-formed AKUs.

- Define AKU schema with all required fields; implement schema validator.
- Establish AKU identifier convention and uniqueness enforcement.
- Build knowledge store (JSON files + SQLite or PostgreSQL for relational queries).
- Implement semantic versioning and snapshot mechanism.
- Seed with 20–50 AKUs from target domain; run integrity checks.

**Exit criterion:** Knowledge base passes all integrity constraints with zero violations.

### Phase 2 — Retrieval (Weeks 5–8)

**Goal:** Contextually accurate, bounded AKU retrieval.

- Build rich embedding chunks: definition + criteria + relations + breadcrumb path.
- Select and deploy embedding model; create vector index (e.g., pgvector, Qdrant, Weaviate).
- Implement metadata filtering (domain, status, version).
- Implement hierarchical expander (ancestor path inclusion).
- Evaluate retrieval quality against target metrics (Recall@10 ≥ 0.90).

**Exit criterion:** Retrieval evaluation suite passes on held-out test queries.

### Phase 3 — Validation (Weeks 9–12)

**Goal:** A deterministic, auditable validation engine.

- Implement required criteria checker with structured case fact matching.
- Implement exclusion and conflict checkers.
- Implement structural consistency checker (parent/child/sibling).
- Define and test validation output contract (JSON schema).
- Build clarification question generator for missing-criteria cases.

**Exit criterion:** Validation engine returns correct results on 100% of canonical test cases.

### Phase 4 — Orchestration (Weeks 13–16)

**Goal:** A complete, auditable end-to-end pipeline.

- Implement constrained prompting with required output schema.
- Integrate Generator → Rule Engine → Examiner → Finalizer pipeline.
- Implement iterative clarification loop (max 2 iterations).
- Add audit trace logging and trace replay endpoint.
- Build developer-facing API surface (see Section 10).

**Exit criterion:** End-to-end integration tests pass; trace replay produces identical results.

### Phase 5 — Hardening (Weeks 17–24)

**Goal:** Production-ready governance, monitoring, and security.

- Implement role-based access control and immutable audit logs.
- Set up domain boundary enforcement.
- Deploy monitoring: latency, validation failure rates, clarification loop frequency.
- Build regression test suite; integrate with CI/CD pipeline.
- Implement drift detection for retrieval quality degradation.
- Conduct security review and compliance assessment.

**Exit criterion:** System passes security review; all SLA targets met under load test.

---

## 18. Design Anti-Patterns

These patterns frequently appear in naive RAG implementations and must be actively avoided.

| Anti-Pattern | Description | Correct Approach |
|--------------|-------------|------------------|
| **Validation bypass** | The LLM's output is returned directly without deterministic checking. | Route all candidates through the validation engine before finalization. |
| **Isolated field embedding** | Embedding only the `definition` field, omitting criteria, relations, and breadcrumbs. | Embed rich chunks that include all semantically relevant fields. |
| **Implicit criteria** | Domain rules are embedded in the system prompt rather than formalized as AKUs. | All rules must live in the knowledge base as explicit, versioned AKUs. |
| **Versionless knowledge** | The KB has no versioning; it is edited in-place without snapshots. | Immutable snapshots required; MAJOR changes trigger regression testing. |
| **Unlogged decisions** | Outputs are returned without audit records. | Every response must be logged with its full decision trace. |
| **Over-retrieval** | Too many AKUs are passed to the LLM, diluting signal and increasing hallucination risk. | Enforce a hard top-k limit; prefer precision over recall in context assembly. |
| **Under-retrieval** | Too few AKUs are retrieved, causing the model to guess missing context. | Validate retrieval quality metrics; include ancestor paths to provide structural context. |
| **Monolithic prompt** | All logic (parsing, reasoning, explanation, validation) is packed into a single prompt. | Separate concerns across pipeline stages; each stage has a single, testable responsibility. |
| **Confidence theater** | The LLM expresses uncertainty with hedging phrases ("it may be...") rather than structured uncertainty fields. | Require structured uncertainty output; treat hedging language as a schema violation. |

---

## 19. Formal Model

Let the following notation apply:

```
P  = atomic problem (structured case facts)
K  = knowledge base (set of all active AKUs)
R  = retrieval function: R(P, K) → K' ⊆ K  (bounded relevant subset)
H  = hypothesis function (LLM): H(P, K') → h  (candidate AKU ID + rationale)
V  = validation function (deterministic): V(h, P, K') → report
```

**Acceptance condition:**

```
result = V(H(P, R(P, K)), P, R(P, K))

Accept(result) ⟺ result.valid = true
                  ∧ result.missing_required = ∅
                  ∧ result.violated_exclusions = ∅
                  ∧ result.conflicts = ∅
```

**Rejection behavior:**

```
If result.missing_required ≠ ∅  →  generate clarification questions
If result.violated_exclusions ≠ ∅  →  reject; propose alternatives from K'
If result.conflicts ≠ ∅  →  reject; surface conflict explanation
```

**Reproducibility invariant:**

```
∀ P, K_v, cfg_r:
  V(H(P, R(P, K_v, cfg_r)), P, R(P, K_v, cfg_r)) = constant
```

where `K_v` is a fixed KB snapshot at version `v` and `cfg_r` is a fixed retrieval configuration.

---

## 20. Summary

**Grounded Intelligence** is the composition of:

| Component | Role |
|-----------|------|
| Atomic Knowledge Base | Ground truth; formally structured; versioned |
| Retrieval Layer | Bounded, ranked, semantically accurate context assembly |
| LLM Orchestrator | Language interface; parsing; explanation; never the decision-maker |
| Validation Engine | Deterministic rule enforcement; non-bypassable |
| Multi-Agent Self-Correction | Adversarial verification; bias reduction |
| Audit & Transparency Layer | Reproducibility; accountability; compliance |

The result is a system that is **scalable, verifiable, and hallucination-resistant** — capable of producing decisions that are not merely plausible, but formally defensible.

