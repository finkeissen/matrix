# Envelope: 04a_generation

**Parent step:** `04_generation`
**Type:** `llm`
**Model:** `35b`
**Upstream:** `03_enrichment_02_normalize` → `normalized_categories` (one envelope per category), `01_scope` → `scope`
**Downstream:** `04b_generation_review` (per category)
**Instantiation:** ×N — one envelope per category in `normalized_categories.items`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "04a_generation",
  "parent_step": "04_generation",
  "type": "llm",
  "inputs": {
    "scope_hash": "<sha256 of scope.json>",
    "category_index": "<integer: 1-based index from normalized_categories>",
    "category_hash": "<sha256 of category object: {index, name_normalized, description}>",
    "gap_detection_hash": "<sha256 of gap_detection.json> | null",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>",
    "retry_context_hash": null
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "problems_draft",
      "path": "runs/<run_id>/artifacts/04a_generation/cat_<index>/problems_draft.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 60,
    "priority": "normal",
    "novelty_guard": true,
    "model": "35b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "generate_atomic_problems_draft"
  }
}
```

**On retry**, `retry_context_hash` is non-null — points to a `retry_context.json` containing the rejection reason from `04b_generation_review`. This changes `task_id`. Prior `problems_draft` artifact marked `superseded`.

---

## Prompt (Algebra — category: Group Theory)

```
You are a precise academic problem designer. Your task is to generate atomic problems for a specific category within the subdomain Algebra (SD-001, Mathematics).

An atomic problem is:
- A single, self-contained question or task that can be posed and answered independently
- Granular enough that it cannot be meaningfully split further without losing context
- Specific enough that a correct answer exists or a clear evaluation rubric can be applied
- NOT too trivial (e.g. "What is 2+2?") and NOT too broad (e.g. "Explain group theory")

Subdomain scope:
<SCOPE_JSON>

Category to generate problems for:
Name: Group Theory
Description: Groups, subgroups, homomorphisms, cosets, Lagrange's theorem, normal subgroups, and quotient groups.
Estimated problem count: 25

Known coverage gaps for this category (from gap analysis — may be "none" if no gaps detected):
<GAP_DETECTION_FOR_CATEGORY_JSON or "none">
If gaps are listed, prioritize those areas when generating problems.

Generate atomic problems for this category. Cover the full range of the category description.
Include problems at all difficulty levels: basic, intermediate, advanced, expert.
Include all answer types: factual, procedural, analytical, evaluative.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain_id": "SD-001",
  "category": "Group Theory",
  "category_index": 5,
  "problem_count": <integer>,
  "problems": [
    {
      "title": <string: short problem title, max 80 chars, English>,
      "problem_statement": <string: full self-contained problem description, English>,
      "difficulty": "basic" | "intermediate" | "advanced" | "expert",
      "answer_type": "factual" | "procedural" | "analytical" | "evaluative",
      "canonical_source": <string: authoritative reference for this specific problem>,
      "verifiable": <boolean>,
      "hallucination_risk": "low" | "medium" | "high",
      "requires_context": <boolean>,
      "tags": [<string>]
    }
  ]
}
```

---

## Expected Output Schema

```json
{
  "subdomain_id": "string",
  "category": "string",
  "category_index": "integer",
  "problem_count": "integer",
  "problems": [
    {
      "title": "string (max 80 chars)",
      "problem_statement": "string",
      "difficulty": "basic | intermediate | advanced | expert",
      "answer_type": "factual | procedural | analytical | evaluative",
      "canonical_source": "string",
      "verifiable": "boolean",
      "hallucination_risk": "low | medium | high",
      "requires_context": "boolean",
      "tags": ["string"]
    }
  ]
}
```

Note: `problem_id`, `subdomain_label`, `parent_domain`, `created_by`, `created_at`, and `review_status` are NOT generated here — they are assigned deterministically in `08_finalization`.

---

## Context Budget

```
System prompt + step instruction:  ~500 tokens
Scope object:                      ~300 tokens
Category name + description:       ~100 tokens
Gap detection (filtered, optional):~200 tokens
Schema reference:                  ~400 tokens
──────────────────────────────────────────────
Total input:                       ~1.500 tokens
Expected output (20–30 problems):  ~1.500 tokens
Total per call:                    ~3.000 tokens  ✅ fits in 4k
```

Note: `gap_detection_hash` is optional — if `null`, the gap section is omitted from the prompt. Orchestrator filters `gap_detection.json` to only pass `missing_topics` relevant to the current category (by `suggested_category` name match) to keep input lean.

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- `problems` array empty or missing → `llm_output_invalid`
- Any problem missing `title` or `problem_statement` → `llm_output_invalid`
