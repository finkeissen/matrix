# Phase 2 — Enrich Atomic Problems

**Goal:** For each atomic problem, attach structured details that support later verification and reuse.

**Input:** `problems.jsonl` from Phase 1  
**Output:** `enrichments.jsonl`, `sources.jsonl` (expanded), `relations.jsonl` (expanded)

---

## Step 2a — Structured Description

Collect per problem:

- Formal problem statement (precise, atomic)
- Scope/context (what is in-scope / out-of-scope)
- Variables and parameters
- Assumptions and prerequisites
- Constraints (legal / physical / ethical / operational)

---

## Step 2b — Methods & Approaches

Collect:

- Typical solution strategies
- Competing approaches
- Known trade-offs
- When each approach tends to work / fail

---

## Step 2c — Failure Modes & Edge Cases

Collect:

- Common failure patterns
- Edge cases
- Blind spots / uncertainty sources
- Known confounders (domain-specific)

---

## Step 2d — References / Evidence Pointers

Two layers:

**Layer 1 — LLM-derived structured knowledge**
- Good for bootstrap and initial coverage
- Store each generation as a `source` record with model/prompt provenance

**Layer 2 — External sources (later)**
- Papers, standards, regulations, textbooks
- Store as `sources.jsonl` entries with stable identifiers and provenance

---

## Quality Gate (per step)

After each enrichment step, run a quality check prompt:
```
"Check schema conformity, mark unclear formulations, set flags..."
```

Flag items that:
- violate schema
- are ambiguous or under-specified
- lack sufficient detail for later verification

---

## Output Files

| File | Content |
|---|---|
| `enrichments.jsonl` | Structured detail objects per problem |
| `sources.jsonl` | Expanded with enrichment provenance |
| `relations.jsonl` | problem↔enrichment links |
| `claims.jsonl` | Optional: if enrichments are modeled as individual claims |
