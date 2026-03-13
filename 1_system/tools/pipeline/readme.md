# Pipeline: Atomic Problems → Details → Reconciliation → Iterative Knowledge Base (LM Studio)

This pipeline builds and continuously improves a structured knowledge base of **atomic problems**
across many domains and subdomains using AI (LM Studio / OpenAI-compatible providers).
It is **model-driven** and designed to be **re-run with better LLMs** over time.

---

## Overview

The pipeline consists of three main phases:

1. Identify atomic problems (1a, 1b, 1c, ...)
2. Enrich each atomic problem with detailed information (2a, 2b, 2c, ...)
3. Reconcile and cross-check all collected information

The knowledge base is improved iteratively and versioned through append-only runs.

**Input:** A catalog of ~80 domains and ~1,700 subdomains (e.g., medicine, law).  
**Output:** `problems.jsonl` (atomic problems) + companion files (`sources.jsonl`, `claims.jsonl`, logs, manifest).  
**Provider:** LM Studio (OpenAI-compatible API) via `1.system/tools/providers/lm_studio_openai_compat.py`.

---

## Repository Placement (Recommended)

| Purpose | Path |
|---|---|
| Pipeline code | `1.system/tools/pipelines/problem_inventory/` |
| Run templates | `2.runs/templates/problem_inventory/` |
| Run outputs | `2.runs/YYYY-MM-DD/run_XX_problem_inventory_.../` |
| Frozen snapshots (optional) | `3.commit/YYYY-MM-DD/` |

This file lives at:
`1.system/tools/pipelines/problem_inventory/README.md`

---

## Artifacts (Run Outputs)

Per run, write structured JSONL artifacts (append-only):

- `problems.jsonl` — atomic problems (core objects)
- `enrichments.jsonl` — structured details per problem *(optional)*
- `sources.jsonl` — LLM prompt/response captures + later external references
- `relations.jsonl` — links: domain↔subdomain↔problem, dedup/supersede/equivalence, traceability
- `conflicts.jsonl` — explicit contradictions found during reconciliation
- `claims.jsonl` — claims extracted from enrichments, if versioned separately *(optional)*

### Problem Objects

Use the existing problem schema consistently:

- Schema: `1.system/schema/problem.schema.json`
- Minimal examples: `1.system/examples/artifacts/problem.minimal.json`

---

## Phase 1 — Identify Atomic Problems

**Goal:** Generate a comprehensive list of atomic problems across domains/subdomains.

### 1a) Candidate Generation (per subdomain)

For each subdomain:

- Ask the LLM to generate **N candidate problems**.
- Enforce **strict structured output** (JSON array or JSONL only, no prose).
- Store the raw LLM interaction as a `source` record (provenance).

Prompt template (recommended):
```
"List X atomic problems typical for subdomain Y..."
Output rules: strict JSON array / JSONL, no prose.
```

### 1b) Atomization & Normalization

For each candidate:

- Split compound problems into atomic units.
- Remove conjunction chains ("and/or"), multi-topic bundling, vague "overview" statements.
- Normalize phrasing into a consistent structure.
- Assign deterministic IDs: e.g., `hash(domain + subdomain + normalized_problem_text)`
- Attach metadata: `domain`, `subdomain`, `run_id`, `model_id`, `timestamp`, etc.

Prompt template (recommended):
```
"Decompose candidate into atomic problems..."
Enforce schema fields + unique IDs (or ID seed + hash).
```

### 1c) Local Deduplication (within subdomain)

- Remove exact duplicates after normalization.
- Perform semantic dedup: LLM-assisted pairwise judging or embedding clustering (optional).
- **Do not delete history:** create `relations` for `supersedes` / `equivalent_to` as needed.

**Phase 1 output:** `problems.jsonl`, `sources.jsonl`, `relations.jsonl`

---

## Phase 2 — Enrich Atomic Problems

**Goal:** For each atomic problem, attach structured details that support later verification and reuse.

### 2a) Structured Description

- Formal problem statement (precise, atomic)
- Scope/context (in-scope / out-of-scope)
- Variables and parameters
- Assumptions and prerequisites
- Constraints (legal / physical / ethical / operational)

### 2b) Methods & Approaches

- Typical solution strategies
- Competing approaches
- Known trade-offs
- When each approach tends to work / fail

### 2c) Failure Modes & Edge Cases

- Common failure patterns
- Edge cases
- Blind spots / uncertainty sources
- Known confounders (domain-specific)

### 2d) References / Evidence Pointers

Two layers:

1. **LLM-derived structured knowledge** (good for bootstrap)
2. **External sources** later (papers, standards, regulations, textbooks) — stored as `sources.jsonl` with stable identifiers and provenance

Quality gate prompt (recommended, per phase):
```
"Check schema conformity, mark unclear formulations, set flags..."
```

**Phase 2 output:** `enrichments.jsonl`, `sources.jsonl` (expanded), `relations.jsonl`

---

## Phase 3 — Reconciliation & Cross-Checking

**Goal:** Ensure internal consistency, remove structural weaknesses, and improve coverage.

### 3a) Cross-Problem Deduplication (global)

Identify semantically equivalent problems across subdomains/domains.  
Produce `relations`: `equivalent_to`, `supersedes` / `superseded_by`, `duplicate_of`.

### 3b) Conflict Detection

Detect contradictions between definitions, assumptions, constraints, and recommended approaches.  
Write `conflicts.jsonl`; link conflict↔problem(s) and conflict↔sources via `relations`.

### 3c) Coverage & Gap Analysis

- Identify subdomains with too few problems or missing standard categories.
- Generate targeted follow-up tasks: new candidate prompts for weak areas, deeper enrichment for thin detail.

**Phase 3 output:** `relations.jsonl`, `conflicts.jsonl`, optional reports (markdown/json)

---

## Iterative Knowledge Improvement (Core Loop)

- Re-run phases with stronger LLMs over time
- Re-enrich weak/low-confidence items
- Reconcile and detect new conflicts introduced by better models
- Track changes via supersession (never overwrite)
- Freeze stable snapshots into `3.commit/YYYY-MM-DD/`

### Versioning Rule

- **Append-only runs**
- Every object includes: `run_id`, `model_id`, timestamps, provenance pointers
- Improvements become new objects + `supersedes` relations

---

## Folder Structure

### Pipeline code
```
1.system/tools/pipelines/problem_inventory/
├── README.md                    ← this file
├── pipeline.py                  ← entrypoint / orchestration
├── prompts/
│   ├── generate_candidates.md
│   ├── atomize_normalize.md
│   └── quality_gate.md
├── config/
│   └── defaults.toml
└── lib/
    ├── taxonomy.py              ← load/filter taxonomy
    ├── writer.py                ← JSONL writer + manifest updates
    ├── dedup.py                 ← dedup logic
    └── ids.py                   ← stable IDs / hashes
```

### Run outputs
```
2.runs/YYYY-MM-DD/run_XX_problem_inventory_all_domains/
├── manifest.json
├── params.json
├── inputs.json
├── problems.jsonl
├── enrichments.jsonl            ← optional
├── sources.jsonl                ← optional
├── claims.jsonl                 ← optional
├── relations.jsonl              ← optional
├── conflicts.jsonl              ← optional
├── README.md                    ← short: what ran, scope, versions
├── logs/
└── assets/
```

### Run templates
```
2.runs/templates/problem_inventory/
├── manifest.json                ← run metadata
├── inputs.json                  ← taxonomy path + filters
└── params.json                  ← model, temperature, batch size, max items, etc.
```

---

## Inputs

### 1) Taxonomy (Domains / Subdomains)

Machine-readable source, e.g.:

- `3.commit/<date>/catalog.domains.jsonl`
- `3.commit/<date>/catalog.subdomains.jsonl`
- or work-in-progress: `2.work/.../catalog.subdomains.jsonl`

**Recommendation:** use `2.work/...` during development; copy to `3.commit/...` once stable.

### 2) Run Parameters

Template under `2.runs/templates/problem_inventory/`:

- `manifest.json` — run metadata
- `inputs.json` — taxonomy path + filters
- `params.json` — model, temperature, batch size, max items, etc.

---

## Operational Guidelines

### Deterministic IDs

Use stable hashing: `hash(domain + subdomain + normalized_problem_text)`.  
Keep a mapping table if normalization logic changes later.

### Checkpointing

For 1,700+ subdomains: checkpoint per subdomain, write incremental JSONL, resume on crash.  
Without checkpointing, a crash loses all progress.

### Dedup Strategy

- **Local (per subdomain):** exact match + normalization first
- **Global (cross-subdomain):** embedding / LLM-judge optional, but expensive

### Cost / Performance

- Start **broad**: 10–30 candidates per subdomain
- Go **deep** into subdomains with gaps or high relevance
- Batching, retry logic, and rate-limiting are mandatory at this scale

### Multi-Model Validation (optional but powerful)

Generate with model A; validate/dedup/conflict-check with model B.  
Use disagreement as a trigger for "needs verification."

---

## Definition of "Atomic" (Working Definition)

A problem is atomic if it:

- expresses **one** decision / uncertainty / failure mode
- avoids multi-part bundling ("diagnosis and therapy and prevention")
- is specific enough to later attach structured details, be testable / sourceable, and be compared for equivalence

Examples:

- ❌ "Diagnosis and treatment of diabetes" — too broad
- ✅ "Which HbA1c threshold should be used as a treatment target for population X?" — atomic

---

## Contact Points in the Existing Repo

| Component | Path |
|---|---|
| Provider | `1.system/tools/providers/lm_studio_openai_compat.py` |
| Runner / CLI | `1.system/tools/run_module.py` |
| Module: seed | `1.system/tools/modules/problems/problem_seed.py` |
| Module: atomize | `1.system/tools/modules/problems/problem_atomize.py` |
| Schema | `1.system/schema/problem.schema.json` |
| Examples | `1.system/examples/artifacts/problem.minimal.json` |

---

## Future Extensions

- Confidence scoring per enrichment field
- Embedding-based clustering for dedup and topic structure
- Automated regression detection between runs
- External source ingestion + citation normalization
- Active learning loop: prioritize areas with highest uncertainty/conflict

---

This pipeline turns broad domain knowledge into a continuously refined,
machine-structured knowledge base of atomic problems — generated, enriched,
and reconciled using AI.
