# Envelope: 03_enrichment_03_gap_detection

**Parent step:** `03_enrichment`
**Type:** `llm`
**Model:** `35b`
**Upstream:** `03_enrichment_02_normalize` → `normalized_categories`, `01_scope` → `scope`, `02_retrieval` → `canonical_structure`
**Downstream:** `04a_generation` (×N categories)
**Snapshot after:** yes (pre-generation checkpoint)

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "03_enrichment_03_gap_detection",
  "parent_step": "03_enrichment",
  "type": "llm",
  "inputs": {
    "normalized_categories_hash": "<sha256 of normalized_categories.json>",
    "scope_hash": "<sha256 of scope.json>",
    "canonical_structure_hash": "<sha256 of canonical_structure.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "gap_detection",
      "path": "runs/<run_id>/artifacts/03_enrichment_03_gap_detection/gap_detection.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 45,
    "priority": "normal",
    "novelty_guard": true,
    "model": "35b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "detect_missing_or_underrepresented_categories"
  }
}
```

---

## Prompt (Algebra — SD-001)

```
You are a precise academic knowledge engineer. Your task is to identify gaps and underrepresented areas in a set of thematic categories for the subdomain Algebra (SD-001, Mathematics).

You will receive:
1. The scope definition for Algebra
2. The canonical structure (authoritative table of contents)
3. The normalized category list produced by the pipeline so far

Your goal is to identify:
- Topics from the scope boundaries that are NOT covered by any category
- Topics from the canonical structure that are NOT covered by any category
- Categories that appear underrepresented (estimated_problem_count < 5)
- Categories that may be too broad (estimated_problem_count > 40)

Input scope:
<SCOPE_JSON>

Input canonical structure:
<CANONICAL_STRUCTURE_JSON>

Input normalized categories:
<NORMALIZED_CATEGORIES_JSON>

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "covered_topics": [<string: topic areas adequately covered by existing categories>],
  "missing_topics": [
    {
      "topic": <string: topic name>,
      "source": "scope_boundary" | "canonical_structure" | "domain_knowledge",
      "suggested_category": <string: suggested category name to add or merge into>,
      "action": "add_category" | "merge_into_existing" | "expand_existing"
    }
  ],
  "underrepresented_categories": [
    {
      "category_index": <integer: index from normalized_categories>,
      "category_name": <string>,
      "issue": <string: why it is underrepresented>,
      "suggestion": <string: how to address it>
    }
  ],
  "oversized_categories": [
    {
      "category_index": <integer>,
      "category_name": <string>,
      "suggestion": <string: how to split it>
    }
  ],
  "overall_coverage": "good" | "acceptable" | "poor",
  "notes": <string or null>
}
```

---

## Expected Output Schema

```json
{
  "subdomain": "string",
  "subdomain_id": "string",
  "covered_topics": ["string"],
  "missing_topics": [
    {
      "topic": "string",
      "source": "scope_boundary | canonical_structure | domain_knowledge",
      "suggested_category": "string",
      "action": "add_category | merge_into_existing | expand_existing"
    }
  ],
  "underrepresented_categories": [
    {
      "category_index": "integer",
      "category_name": "string",
      "issue": "string",
      "suggestion": "string"
    }
  ],
  "oversized_categories": [
    {
      "category_index": "integer",
      "category_name": "string",
      "suggestion": "string"
    }
  ],
  "overall_coverage": "good | acceptable | poor",
  "notes": "string | null"
}
```

## Note
This output is a hint, not a gate. `04a_generation` proceeds with the normalized categories as-is. Gap detection results are passed as optional context:
- To `04a_generation`: filtered per category (only `missing_topics` where `suggested_category` matches current category). Passed as `gap_detection_hash` — `null` if no relevant gaps exist for a category.
- To `04b_generation_review`: full `gap_detection.json` — reviewer checks whether 04a addressed the gaps.
- To `07_examination_02_alternative_check`: full `gap_detection.json` — final coverage check.

## Snapshot
Orchestrator creates snapshot after this step completes — this is the last checkpoint before the generation steps begin.

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- `overall_coverage` field missing → `llm_output_invalid`
