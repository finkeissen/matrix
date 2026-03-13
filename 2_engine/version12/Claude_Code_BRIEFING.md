# Claude Code Briefing — Atomic Problem Identification Pipeline

**Version:** 1.0.0  
**Language:** All outputs in English  
**Status:** Greenfield — build from scratch

---

## 1. Context

We have a curated list of ~153 subdomains across 30 parent domains (see `subdomaenen_priorisiert_v2.csv`), prioritized into three tiers:

- **Tier 1 – Now (65 subdomains):** High LLM suitability, stable knowledge, strong canonical sources (e.g. Algebra, Netzwerktechnik, Anatomie)
- **Tier 2 – Mid-term (64 subdomains):** Requires expert curation and verification
- **Tier 3 – Later (24 subdomains):** Wait for better LLMs (volatile, high hallucination risk)

An existing pipeline (`00_step_registry.md`) defines a 13-step document-processing envelope. That pipeline is the **structural reference** — its retry logic, novelty guard, snapshot mechanism and commit pattern are sound and should be preserved. However, its semantics must be adapted: instead of processing an incoming document, we are **generating** a list of atomic problems from a scope definition.

---

## 2. Goal

For each subdomain, identify **all atomic problems** in that subdomain and describe each one in a **unified JSON schema**.

An **atomic problem** is defined as:
- A single, self-contained question, task, or failure mode that can be posed and answered independently
- Granular enough that it cannot be meaningfully split further without losing context
- Specific enough that a correct answer exists (or a clear evaluation rubric)
- Examples:
  - ✅ "What is the time complexity of QuickSort in the average case?"
  - ✅ "Identify the functional group in CH₃COOH"
  - ✅ "Which ICD-11 code applies to Type 2 Diabetes Mellitus?"
  - ❌ "Explain computer science" (too broad)
  - ❌ "What is 2+2?" (too trivial, not domain-specific)

---

## 3. Target Output: JSON Schema

Every atomic problem must be described with the following unified schema:

```json
{
  "problem_id": "string",          // e.g. "ALG-0042" — domain prefix + zero-padded index
  "subdomain_id": "string",        // e.g. "S0001" — from subdomains.jsonl
  "domain_id": "string",           // e.g. "D-06"
  "parent_domain": "string",       // e.g. "Mathematik"
  "subdomain_label": "string",     // e.g. "Algebra"
  "title": "string",               // short problem title (max 80 chars, English)
  "problem_statement": "string",   // full, self-contained problem description (English)
  "category": "string",            // thematic cluster within subdomain (e.g. "Group Theory")
  "difficulty": "basic|intermediate|advanced|expert",
  "answer_type": "factual|procedural|analytical|evaluative",
  "canonical_source": "string",    // authoritative reference (e.g. "ISO 80000", "ICD-11", "RFC 791")
  "verifiable": true,              // boolean: can correctness be checked deterministically?
  "hallucination_risk": "low|medium|high",
  "requires_context": false,       // boolean: does solving it require external data not in the problem?
  "tags": ["string"],              // free-form keywords
  "created_by": "string",          // e.g. "pipeline_v1/run_001"
  "created_at": "string",          // ISO 8601 timestamp
  "review_status": "draft|reviewed|approved"
}
```

### Schema Notes
- `verifiable: true` means an automated checker could in principle validate the answer
- `hallucination_risk` maps from the subdomain's score: Gesamt ≥ 79 → low, 55–78 → medium, < 55 → high
- `requires_context: true` means the problem needs a specific document, case, or dataset to be solvable
- All string fields in English
- `problem_id` prefix derived from subdomain label (first 5 characters uppercase; compound labels use initials of all words excluding stopwords, padded to 5), e.g. ALGEB for Algebra, NETZW for Netzwerktechnik, ALGDS for Algorithmen & Datenstrukturen — see engine.md E-02

---

## 4. Pipeline Adaptation

The existing `00_step_registry.md` defines 13 steps. Adapt them as follows for **generative** runs:

| Original Step | Adapted Purpose | Type |
|---|---|---|
| `01_parsing_01` → `01_scope` | Define subdomain boundaries, exclusions, canonical source | LLM |
| `01_parsing_02` → `01_scope_confidence` | Score scope clarity; flag ambiguities | LLM |
| `02_retrieval` | Load canonical structure (ICD chapters, DIN numbers, RFC index…) | deterministic |
| `03_enrichment_01` → `03_categories` | Identify thematic clusters within subdomain | LLM |
| `03_enrichment_02` → `03_normalize` | Normalize category names to canonical form | deterministic |
| `03_enrichment_03` → `03_gap_detection` | Which categories are missing or underrepresented? | LLM + snapshot |
| `04_hypothesis` → `04_generation` | Generate atomic problems per category | LLM, retries=2 |
| `05_validation` | Check: duplicates, atomicity, schema compliance, completeness | deterministic + LLM |
| `06_clarification` | Scope refinement only — loop back to `01_scope`, not full restart | LLM + snapshot |
| `07_examination_01` | Hallucination scan: flag problems with hallucination_risk=high | LLM |
| `07_examination_02` | Alternative categorizations; coverage gaps | LLM |
| `08_finalization` | Assign IDs, timestamps, review_status=draft; produce JSONL | deterministic + LLM + snapshot |
| `09_commit` | Write to run registry; update subdomain status | deterministic + snapshot |

Preserve from original:
- Novelty Guard on all LLM steps
- Retry logic (max 2 for generation step)
- Snapshot mechanism (after steps 03_gap, 05, 06, 08, 09)
- Artifact superseding on retry

---

## 5. File Structure

```
project/
├── CC_BRIEFING.md                    ← this file
├── subdomaenen_priorisiert_v2.csv    ← subdomain priority list
├── subdomains.jsonl                  ← original subdomain registry (1798 entries)
├── schema/
│   └── atomic_problem.schema.json   ← JSON Schema (to be created)
├── pipeline/
│   ├── 00_step_registry.md           ← original (reference only, do not modify)
│   ├── 00_step_registry_v2.md        ← adapted registry (to be created)
│   └── steps/
│       ├── 01_scope.md
│       ├── 01_scope_confidence.md
│       ├── 02_retrieval.md
│       ├── 03_categories.md
│       ├── 03_normalize.md
│       ├── 03_gap_detection.md
│       ├── 04_generation.md
│       ├── 05_validation.md
│       ├── 06_clarification.md
│       ├── 07_hallucination_scan.md
│       ├── 07_alternative_check.md
│       ├── 08_finalization.md
│       └── 09_commit.md
├── runs/
│   ├── run_001_algebra/
│   │   ├── run_manifest.json
│   │   ├── 01_scope.json
│   │   ├── 03_categories.json
│   │   ├── 04_generation.jsonl
│   │   ├── 05_validation.json
│   │   ├── 08_final.jsonl            ← atomic problems, schema-compliant
│   │   └── 09_commit.json
│   └── ...
└── registry/
    ├── problems.jsonl                ← all committed atomic problems (append-only)
    └── run_log.jsonl                 ← all runs with status
```

---

## 6. First Task for Claude Code

**Do exactly this, nothing more:**

1. Read `subdomaenen_priorisiert_v2.csv` and `subdomains.jsonl`
2. Create `schema/atomic_problem.schema.json` — the formal JSON Schema (draft-07) matching the schema defined in Section 3
3. Create `pipeline/00_step_registry_v2.md` — the adapted step registry (Section 4), preserving the exact format of the original
4. Create `pipeline/steps/01_scope.md` — the prompt template for the first step only, for the subdomain **Algebra (D-06 / S0001)**

**Do not** generate any atomic problems yet.  
**Do not** build the run infrastructure yet.  
**Do not** process any other subdomain.

This first task is about getting the schema and pipeline structure right before running anything.

---

## 7. Definition of Done (First Task)

- [ ] `schema/atomic_problem.schema.json` validates against JSON Schema draft-07
- [ ] All fields from Section 3 are present with correct types and enums
- [ ] `pipeline/00_step_registry_v2.md` matches the adapted table in Section 4, same format as original
- [ ] `pipeline/steps/01_scope.md` contains a concrete, runnable prompt for Algebra — not a template with placeholders, but a real prompt ready to send to a local LLM (19B/A3B)
- [ ] The scope prompt produces a structured JSON output matching a `scope` object with: `subdomain`, `parent_domain`, `canonical_source`, `boundaries`, `exclusions`, `ambiguities[]`

---

## 8. Subsequent Tasks (do not start yet)

After the first task is approved:
- Step templates for 02 through 09
- First full manual run: Algebra
- Review and adjustment of schema based on real output
- Automation scaffold for all 65 Tier-1 subdomains
- Quality management layer (duplicate detection, coverage scoring, hallucination flagging)

---

## 9. Key Decisions Already Made

| Decision | Choice | Rationale |
|---|---|---|
| Output language | English only | Consistency, model performance |
| First subdomain | Algebra | Score 93, closed problem space, easy to verify |
| LLM target | Local 19B / A3B | Privacy, cost, offline capability |
| Problem granularity | Atomic (unsplittable) | Enables precise retrieval and evaluation |
| Storage format | JSONL (append-only) | Scalable, git-friendly, streamable |
| Pipeline base | Adapted from existing step registry | Preserve retry/snapshot/novelty logic |
| Tier 1 count | 65 subdomains | First automation wave |
| Schema version | draft-07 | Broad tooling support |
