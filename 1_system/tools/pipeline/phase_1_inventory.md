# Phase 1 — Identify Atomic Problems

**Goal:** Generate a comprehensive list of atomic problems across all domains and subdomains.

**Input:** Taxonomy (`catalog.subdomains.jsonl`) + run parameters  
**Output:** `problems.jsonl`, `sources.jsonl`, `relations.jsonl`

---

## Step 1a — Candidate Generation (per subdomain)

For each subdomain:

- Ask the LLM to generate **N candidate problems**.
- Enforce **strict structured output** (JSON array or JSONL only, no prose).
- Store the raw LLM interaction as a `source` record (provenance).

Prompt template:
```
"List X atomic problems typical for subdomain Y..."
Output rules: strict JSON array / JSONL, no prose.
```

---

## Step 1b — Atomization & Normalization

For each candidate:

- Split compound problems into atomic units.
- Remove conjunction chains ("and/or"), multi-topic bundling, vague "overview" statements.
- Normalize phrasing into a consistent structure.
- Assign deterministic IDs: `hash(domain + subdomain + normalized_problem_text)`
- Attach metadata: `domain`, `subdomain`, `run_id`, `model_id`, `timestamp`

Prompt template:
```
"Decompose candidate into atomic problems..."
Enforce schema fields + unique IDs (or ID seed + hash).
```

---

## Step 1c — Local Deduplication (within subdomain)

- Remove exact duplicates after normalization.
- Perform semantic dedup: LLM-assisted pairwise judging or embedding clustering (optional).
- **Do not delete history:** create `relations` for `supersedes` / `equivalent_to` as needed.

---

## Cost & Performance Notes

- Start **broad**: 10–30 candidates per subdomain
- Go **deep** into subdomains with gaps or high relevance after Phase 3 gap analysis
- Batching, retry logic, and rate-limiting are mandatory at this scale

---

## Output Files

| File | Content |
|---|---|
| `problems.jsonl` | Atomic problem objects (one per line) |
| `sources.jsonl` | LLM prompt/response captures per generation call |
| `relations.jsonl` | Domain/subdomain membership + supersession links |
