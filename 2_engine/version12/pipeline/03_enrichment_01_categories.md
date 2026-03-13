# Envelope: 03_enrichment_01_categories

**Parent step:** `03_enrichment`
**Type:** `llm`
**Model:** `35b`
**Upstream:** `02_retrieval` → `canonical_structure`, `01_scope` → `scope`
**Downstream:** `03_enrichment_02_normalize`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "03_enrichment_01_categories",
  "parent_step": "03_enrichment",
  "type": "llm",
  "inputs": {
    "scope_hash": "<sha256 of scope.json>",
    "canonical_structure_hash": "<sha256 of canonical_structure.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "categories",
      "path": "runs/<run_id>/artifacts/03_enrichment_01_categories/categories.json",
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
    "reason": "identify_thematic_clusters"
  }
}
```

---

## Prompt (Algebra — SD-001)

```
You are a precise academic knowledge engineer. Your task is to identify the thematic categories within a subdomain for an atomic problem generation pipeline.

You will receive:
1. A scope definition for the subdomain Algebra (SD-001, Mathematics)
2. A canonical structure (table of contents or topic index from the authoritative source)

Your goal is to produce a flat list of thematic categories. Each category will later be used as a generation unit — one LLM call per category will generate all atomic problems for that category.

Input scope:
<SCOPE_JSON>

Input canonical structure:
<CANONICAL_STRUCTURE_JSON>

Rules for categories:
- Each category must correspond to a coherent, teachable topic cluster within Algebra
- Categories must be mutually exclusive — no problem should belong to two categories
- Categories must be collectively exhaustive — every atomic problem in the subdomain must fit into exactly one category
- Category names must be in English
- Category names must be specific enough to guide problem generation (not "Miscellaneous" or "Other")
- Estimated problem count per category should be between 5 and 40; split larger topics, merge smaller ones
- Base categories on the canonical structure where possible; add categories for important topics not covered

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "category_count": <integer>,
  "items": [
    {
      "name": <string: category name in English, Title Case>,
      "description": <string: one sentence describing what problems belong here>,
      "canonical_chapter_ref": <integer or null: index from canonical_structure, null if no match>,
      "estimated_problem_count": <integer>
    }
  ]
}
```

---

## Expected Output Schema

```json
{
  "subdomain": "string",
  "subdomain_id": "string",
  "category_count": "integer",
  "items": [
    {
      "name": "string",
      "description": "string",
      "canonical_chapter_ref": "integer | null",
      "estimated_problem_count": "integer"
    }
  ]
}
```

## Reference Output (Algebra — SD-001)

```json
{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "category_count": 10,
  "items": [
    { "name": "Equations and Inequalities", "description": "Solving linear, quadratic, and polynomial equations and inequalities over real and complex numbers.", "canonical_chapter_ref": 1, "estimated_problem_count": 20 },
    { "name": "Linear Algebra — Vector Spaces", "description": "Definitions, subspaces, bases, dimension, and linear independence.", "canonical_chapter_ref": 2, "estimated_problem_count": 18 },
    { "name": "Linear Algebra — Matrices and Linear Maps", "description": "Matrix operations, determinants, rank, invertibility, and linear transformations.", "canonical_chapter_ref": 2, "estimated_problem_count": 22 },
    { "name": "Eigenvalues and Diagonalization", "description": "Eigenvalues, eigenvectors, characteristic polynomial, diagonalization, and Jordan normal form.", "canonical_chapter_ref": 2, "estimated_problem_count": 15 },
    { "name": "Group Theory", "description": "Groups, subgroups, homomorphisms, cosets, Lagrange's theorem, normal subgroups, and quotient groups.", "canonical_chapter_ref": 3, "estimated_problem_count": 25 },
    { "name": "Rings and Fields", "description": "Ring axioms, ideals, quotient rings, integral domains, fields, and field extensions.", "canonical_chapter_ref": 3, "estimated_problem_count": 20 },
    { "name": "Polynomial Rings and Factorization", "description": "Polynomial rings, irreducibility, unique factorization domains, and Euclidean algorithm for polynomials.", "canonical_chapter_ref": 4, "estimated_problem_count": 15 },
    { "name": "Number Systems and Algebraic Structures", "description": "Integers, rationals, reals, and complex numbers treated as algebraic structures; construction and properties.", "canonical_chapter_ref": 5, "estimated_problem_count": 12 },
    { "name": "Homomorphisms and Isomorphisms", "description": "Structure-preserving maps, isomorphism theorems, automorphisms, and classification of structures.", "canonical_chapter_ref": 6, "estimated_problem_count": 14 },
    { "name": "Boolean Algebra", "description": "Boolean operations, truth tables, Boolean expressions, simplification, and Karnaugh maps.", "canonical_chapter_ref": 7, "estimated_problem_count": 10 }
  ]
}
```

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- `items` array empty or missing → `llm_output_invalid`
- Any item missing `name` or `description` → `llm_output_invalid`
