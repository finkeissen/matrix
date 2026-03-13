# Grounded Intelligence Architecture — Module Index
## Component Map & Integration Guide

**Version:** 2.0.0
**Status:** Reference
**Parent document:** `grounded_intelligence_architecture_v2.md`
**Related:** `00_overview.md` (Pipeline)

---

## Module Registry

| File | Module | Layer | Deterministic | Pipeline Steps |
|------|--------|-------|---------------|----------------|
| `M01_aku_schema.md` | AKU Schema & Integrity | Knowledge | Yes | — (authoring time) |
| `M02_knowledge_store.md` | Knowledge Store & Versioning | Knowledge | Yes | — (authoring time) |
| `M03_ingestion.md` | Ingestion Pipeline | Knowledge | Yes | — (authoring time) |
| `M04_embedding.md` | Embedding & Vector Index | Retrieval | Yes | 02_retrieval |
| `M05_retrieval_engine.md` | Retrieval Engine | Retrieval | Yes | 02_retrieval |
| `M06_validation_engine.md` | Validation Engine | Validation | Yes | 05_validation |
| `M07_llm_orchestrator.md` | LLM Orchestrator | Orchestration | No | 01, 03, 04, 06, 07, 08 |
| `M08_multi_agent.md` | Multi-Agent Self-Correction | Orchestration | No | 04, 07 |
| `M09_audit_layer.md` | Audit & Transparency Layer | Governance | Yes | 08, 09 |
| `M10_governance.md` | Security & Governance | Governance | Yes | — (operational) |

---

## Architectural Layers

```
+----------------------------------------------------------+
|  GOVERNANCE LAYER                                        |
|  M09 Audit & Transparency    M10 Security & Governance   |
+----------------------------------------------------------+
|  ORCHESTRATION LAYER                                     |
|  M07 LLM Orchestrator        M08 Multi-Agent             |
+----------------------------------------------------------+
|  VALIDATION LAYER                                        |
|  M06 Validation Engine                                   |
+----------------------------------------------------------+
|  RETRIEVAL LAYER                                         |
|  M04 Embedding & Vector Index    M05 Retrieval Engine    |
+----------------------------------------------------------+
|  KNOWLEDGE LAYER                                         |
|  M01 AKU Schema    M02 Knowledge Store    M03 Ingestion  |
+----------------------------------------------------------+
```

Data flows upward. No module accesses a lower-layer module's internals — only its declared interface.

---

## Cross-Cutting Invariants

These invariants apply to every module without exception:

| # | Invariant |
|---|-----------|
| 1 | External knowledge overrides model memory. Model weights are never the source of truth. |
| 2 | Validation overrides probability. A plausible but unvalidated result is rejected. |
| 3 | Every output must be reproducible given the same KB snapshot and retrieval config. |
| 4 | Safe-fail: when uncertain, return structured refusal — never fabricate. |
| 5 | Every decision is logged with its full provenance before being returned to the caller. |

---

## Interface Contract Summary

Every module exposes a typed, versioned interface. Modules communicate only through declared interfaces — no shared mutable state, no direct database access across layer boundaries.

| Module | Consumes | Produces |
|--------|----------|----------|
| M01 | (schema definition) | `AKU` objects |
| M02 | `AKU` objects | `KBSnapshot`, versioned store |
| M03 | Raw source documents | Validated `AKU` objects |
| M04 | `AKU` objects from M02 | Vector index |
| M05 | Query + vector index | `context_units[]` |
| M06 | `candidate` + `case_facts` + KB | `ValidationReport` |
| M07 | All pipeline inputs | Parsed facts, candidates, explanations |
| M08 | Generator output + validation report | Examination result |
| M09 | All module outputs | `AuditTrace`, `TraceReplay` |
| M10 | (policy definitions, RBAC config) | Access decisions, governance events |

---

## Maturity Levels vs. Modules

| Maturity Level | Required Modules |
|----------------|-----------------|
| Level 1 — Basic RAG | M04, M05, M07 (partial) |
| Level 2 — Validated RAG | + M06 |
| Level 3 — Structural Reasoning | + M01 (full), M02 |
| Level 4 — Adversarial Verification | + M08 |
| Level 5 — Governed Intelligence | + M03, M09, M10 |

Level 3 is the minimum for production use in regulated domains.

---

## Reading Order

For implementers, read modules in dependency order:

1. `M01_aku_schema.md` — what an AKU is
2. `M02_knowledge_store.md` — how AKUs are stored and versioned
3. `M03_ingestion.md` — how AKUs enter the system
4. `M04_embedding.md` — how AKUs become searchable
5. `M05_retrieval_engine.md` — how relevant AKUs are found
6. `M06_validation_engine.md` — how candidates are checked
7. `M07_llm_orchestrator.md` — how language models are constrained
8. `M08_multi_agent.md` — how self-correction works
9. `M09_audit_layer.md` — how decisions are recorded
10. `M10_governance.md` — how the system is secured and governed
