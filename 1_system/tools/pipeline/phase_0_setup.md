# Phase 0 — Setup & Conventions

This document defines the prerequisites, input formats, naming conventions,
and operational rules shared across all pipeline phases.

---

## Inputs

### 1) Taxonomy (Domains / Subdomains)

Provide a machine-readable source:

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

## Deterministic IDs

Use stable hashing for every object:
```
id = hash(domain + subdomain + normalized_problem_text)
```

Keep a mapping table if normalization logic changes later.

---

## Versioning Rule (all phases)

- **Append-only runs** — never overwrite existing objects
- Every object must include: `run_id`, `model_id`, `timestamp`, provenance pointers
- Improvements become **new objects** + `supersedes` relations
- Freeze stable snapshots into `3.commit/YYYY-MM-DD/`

---

## Checkpointing

For 1,700+ subdomains:

- Checkpoint per subdomain
- Write incremental JSONL after each subdomain completes
- Resume from last completed subdomain on crash

Without checkpointing, a crash loses all progress.

---

## Run Output Structure
```
2.runs/YYYY-MM-DD/run_XX_problem_inventory_all_domains/
├── manifest.json
├── params.json
├── inputs.json
├── problems.jsonl
├── enrichments.jsonl      ← optional
├── sources.jsonl          ← optional
├── claims.jsonl           ← optional
├── relations.jsonl        ← optional
├── conflicts.jsonl        ← optional
├── README.md              ← short: what ran, scope, versions
├── logs/
└── assets/
```

---

## Definition of "Atomic"

A problem is atomic if it:

- expresses **one** decision / uncertainty / failure mode
- avoids multi-part bundling ("diagnosis and therapy and prevention")
- is specific enough to later:
  - attach structured details
  - be testable / sourceable
  - be compared for equivalence

Examples:

- ❌ "Diagnosis and treatment of diabetes" — too broad
- ✅ "Which HbA1c threshold should be used as a treatment target for population X?" — atomic

---

## Schema & Contact Points

| Component | Path |
|---|---|
| Provider | `1.system/tools/providers/lm_studio_openai_compat.py` |
| Runner / CLI | `1.system/tools/run_module.py` |
| Module: seed | `1.system/tools/modules/problems/problem_seed.py` |
| Module: atomize | `1.system/tools/modules/problems/problem_atomize.py` |
| Schema | `1.system/schema/problem.schema.json` |
| Examples | `1.system/examples/artifacts/problem.minimal.json` |
