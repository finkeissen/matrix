# Envelope: 04b_generation_review

**Parent step:** `04_generation`
**Type:** `llm`
**Model:** `122b`
**Upstream:** `04a_generation` → `problems_draft` (per category), `03_enrichment_03_gap_detection` → `gap_detection`, `01_scope` → `scope`
**Downstream:** `05_validation` (merge of all 04b outputs)
**Instantiation:** ×N — one envelope per category, paired with `04a_generation`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "04b_generation_review",
  "parent_step": "04_generation",
  "type": "llm",
  "inputs": {
    "problems_draft_hash": "<sha256 of problems_draft.json>",
    "scope_hash": "<sha256 of scope.json>",
    "gap_detection_hash": "<sha256 of gap_detection.json>",
    "category_index": "<integer: 1-based>",
    "category_hash": "<sha256 of category object>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "problems_reviewed",
      "path": "runs/<run_id>/artifacts/04b_generation_review/cat_<index>/problems_reviewed.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 90,
    "priority": "normal",
    "novelty_guard": true,
    "model": "122b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "review_and_refine_problems_draft"
  }
}
```

---

## Prompt (Algebra — category: Group Theory)

```
You are a rigorous academic quality reviewer. Your task is to review and refine a draft set of atomic problems for the category Group Theory within the subdomain Algebra (SD-001, Mathematics).

For each problem in the draft, apply the following checks:

1. ATOMICITY: Can this problem be split further without losing context? If yes, split it or flag it.
2. SELF-CONTAINMENT: Is the problem fully solvable without external data? If not, set requires_context: true.
3. HALLUCINATION RISK: Is this a well-established fact with a stable, verifiable answer? Assign hallucination_risk: low / medium / high.
4. DIFFICULTY: Is the assigned difficulty appropriate for the subdomain level? Correct if not.
5. CANONICAL SOURCE: Is the canonical_source specific and authoritative? Improve vague references.
6. DUPLICATION: Are any two problems asking essentially the same thing? Merge or remove duplicates.

Then check against the gap detection report: are there important topics from the gap report that are missing from the draft? Add problems for missing topics.

Input scope:
<SCOPE_JSON>

Input draft problems:
<PROBLEMS_DRAFT_JSON>

Input gap detection report:
<GAP_DETECTION_JSON>

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain_id": "SD-001",
  "category": "Group Theory",
  "category_index": 5,
  "problem_count": <integer>,
  "problems_added": <integer: new problems added from gap report>,
  "problems_removed": <integer: duplicates or invalid problems removed>,
  "problems_modified": <integer: problems changed from draft>,
  "changes_made": [
    {
      "action": "added" | "removed" | "modified" | "split",
      "title": <string: problem title>,
      "reason": <string: why this change was made>
    }
  ],
  "problems": [
    {
      "title": <string: max 80 chars, English>,
      "problem_statement": <string: full self-contained problem, English>,
      "difficulty": "basic" | "intermediate" | "advanced" | "expert",
      "answer_type": "factual" | "procedural" | "analytical" | "evaluative",
      "canonical_source": <string>,
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
  "problems_added": "integer",
  "problems_removed": "integer",
  "problems_modified": "integer",
  "changes_made": [
    {
      "action": "added | removed | modified | split",
      "title": "string",
      "reason": "string"
    }
  ],
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

---

## Context Budget

```
System prompt + step instruction:  ~600 tokens
Scope object:                      ~300 tokens
Draft problems (20–30 items):      ~1.500 tokens
Gap detection report:              ~400 tokens
──────────────────────────────────────────────
Total input:                       ~2.800 tokens
Expected output (refined list):    ~2.000 tokens
Total per call:                    ~4.800 tokens  ✅ fits in 8k
```

---

## Retry Context Injection

If `05_validation` rejects the output of this step for a category, `04a_generation` is re-run with enriched inputs (`retry_context_hash` non-null). This step then runs again on the new draft. Prior `problems_reviewed` artifact marked `superseded`.

---

## Content State on Completion
`candidate` — promoted to `verified` by `05_validation` if valid

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- `problems` array empty or missing → `llm_output_invalid`
- `problem_count` = 0 after review → `llm_output_invalid`
