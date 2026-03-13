# Envelope: 03_enrichment_02_normalize

**Parent step:** `03_enrichment`
**Type:** `deterministic`
**Model:** —
**Upstream:** `03_enrichment_01_categories` → `categories`
**Downstream:** `03_enrichment_03_gap_detection`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "03_enrichment_02_normalize",
  "parent_step": "03_enrichment",
  "type": "deterministic",
  "inputs": {
    "categories_hash": "<sha256 of categories.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "normalized_categories",
      "path": "runs/<run_id>/artifacts/03_enrichment_02_normalize/normalized_categories.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 0,
    "timeout_sec": 5,
    "priority": "normal",
    "novelty_guard": false
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "soft_normalize_category_names"
  }
}
```

---

## What This Step Does

Soft normalization of category names from `03_enrichment_01_categories`. No LLM call.
No synonym resolution, no translation, no semantic clustering (E-04).

**Normalization rules applied (in order):**

1. Trim leading and trailing whitespace
2. Collapse internal whitespace (multiple spaces → single space)
3. Apply Title Case (first letter of each word capitalized, rest lowercase — except acronyms)
4. Normalize special characters: `&` → `and`, `/` → `-`
5. Remove duplicate entries (case-insensitive comparison on normalized name)

**Acronym preservation:** Words that are fully uppercase in the original (e.g. `SQL`, `RFC`, `ICD`, `CAD`) are preserved as-is after Title Case is applied to surrounding words.

**Original name preserved:** `name_original` carries the raw LLM output for traceability. `name_normalized` is the canonical form used by all downstream steps.

---

## Output Schema

```json
{
  "subdomain": "string",
  "subdomain_id": "string",
  "category_count": "integer",
  "duplicates_removed": "integer",
  "items": [
    {
      "index": "integer (1-based, stable ordering for 04a/04b envelope instantiation)",
      "name_normalized": "string",
      "name_original": "string",
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
  "duplicates_removed": 0,
  "items": [
    { "index": 1, "name_normalized": "Equations and Inequalities", "name_original": "Equations and Inequalities", "description": "Solving linear, quadratic, and polynomial equations and inequalities over real and complex numbers.", "canonical_chapter_ref": 1, "estimated_problem_count": 20 },
    { "index": 2, "name_normalized": "Linear Algebra - Vector Spaces", "name_original": "Linear Algebra — Vector Spaces", "description": "Definitions, subspaces, bases, dimension, and linear independence.", "canonical_chapter_ref": 2, "estimated_problem_count": 18 },
    { "index": 3, "name_normalized": "Linear Algebra - Matrices and Linear Maps", "name_original": "Linear Algebra — Matrices and Linear Maps", "description": "Matrix operations, determinants, rank, invertibility, and linear transformations.", "canonical_chapter_ref": 2, "estimated_problem_count": 22 },
    { "index": 4, "name_normalized": "Eigenvalues and Diagonalization", "name_original": "Eigenvalues and Diagonalization", "description": "Eigenvalues, eigenvectors, characteristic polynomial, diagonalization, and Jordan normal form.", "canonical_chapter_ref": 2, "estimated_problem_count": 15 },
    { "index": 5, "name_normalized": "Group Theory", "name_original": "Group Theory", "description": "Groups, subgroups, homomorphisms, cosets, Lagrange's theorem, normal subgroups, and quotient groups.", "canonical_chapter_ref": 3, "estimated_problem_count": 25 },
    { "index": 6, "name_normalized": "Rings and Fields", "name_original": "Rings and Fields", "description": "Ring axioms, ideals, quotient rings, integral domains, fields, and field extensions.", "canonical_chapter_ref": 3, "estimated_problem_count": 20 },
    { "index": 7, "name_normalized": "Polynomial Rings and Factorization", "name_original": "Polynomial Rings and Factorization", "description": "Polynomial rings, irreducibility, unique factorization domains, and Euclidean algorithm for polynomials.", "canonical_chapter_ref": 4, "estimated_problem_count": 15 },
    { "index": 8, "name_normalized": "Number Systems and Algebraic Structures", "name_original": "Number Systems and Algebraic Structures", "description": "Integers, rationals, reals, and complex numbers treated as algebraic structures; construction and properties.", "canonical_chapter_ref": 5, "estimated_problem_count": 12 },
    { "index": 9, "name_normalized": "Homomorphisms and Isomorphisms", "name_original": "Homomorphisms and Isomorphisms", "description": "Structure-preserving maps, isomorphism theorems, automorphisms, and classification of structures.", "canonical_chapter_ref": 6, "estimated_problem_count": 14 },
    { "index": 10, "name_normalized": "Boolean Algebra", "name_original": "Boolean Algebra", "description": "Boolean operations, truth tables, Boolean expressions, simplification, and Karnaugh maps.", "canonical_chapter_ref": 7, "estimated_problem_count": 10 }
  ]
}
```

---

## Content State on Completion
`candidate` — remains `candidate` until a future review step promotes to `verified` (E-04)

## STOP Conditions
- Input `categories.json` missing or unreadable → `deterministic_step_error`
- `items` empty after deduplication → `deterministic_step_error`
