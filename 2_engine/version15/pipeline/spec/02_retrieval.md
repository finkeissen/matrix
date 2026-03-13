# Envelope: 02_retrieval

**Parent step:** `02_retrieval`
**Type:** `deterministic`
**Model:** —
**Upstream:** `01_scope_confidence` → `scope_confidence` (recommendation: proceed), `01_scope` → `scope`
**Downstream:** `03_categories`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "02_retrieval",
  "parent_step": "02_retrieval",
  "type": "deterministic",
  "inputs": {
    "scope_hash": "<sha256 of scope.json>",
    "scope_confidence_hash": "<sha256 of scope_confidence.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>",
    "canonical_source": "Lang, S. — Algebra (Springer, 3rd ed.); supplemented by Dummit & Foote — Abstract Algebra"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "canonical_structure",
      "path": "runs/<run_id>/artifacts/02_retrieval/canonical_structure.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 0,
    "timeout_sec": 10,
    "priority": "normal",
    "novelty_guard": false
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "load_canonical_structure"
  }
}
```

---

## What This Step Does

In the generative pipeline, `02_retrieval` does not query a vector database. Instead it loads the **canonical structural index** for the subdomain — the authoritative table of contents, chapter structure, or topic taxonomy from the `canonical_source` declared in `scope.json`.

This structure is used by `03_categories` as a grounding reference — ensuring generated categories align with how the canonical source organises the subdomain, rather than being invented freely by the LLM.

**Retrieval strategy by source type:**

| Source type | Retrieval method | Example |
|---|---|---|
| Textbook (local file) | Parse table of contents from PDF/EPUB | Lang Algebra — chapter list |
| Standard / norm (local file) | Parse section index | ISO 80000, DIN 8580 |
| RFC / specification | Parse section headers from plain text | RFC 791 |
| Curriculum standard | Load structured JSON/CSV index | ICD-11 chapter list |
| Fallback (no file available) | Write static stub from scope.boundaries | Use `scope.boundaries` as chapter list |

For Algebra (SD-001): the canonical source is a textbook. If the PDF/EPUB is not available locally, the fallback applies — `scope.boundaries` from `01_scope` is used directly as the chapter list.

---

## Output Schema

```json
{
  "subdomain_id": "SD-001",
  "subdomain": "Algebra",
  "canonical_source": "string",
  "retrieval_method": "textbook_toc | standard_index | rfc_headers | curriculum_index | fallback_from_scope",
  "source_available": true,
  "chapters": [
    {
      "index": 1,
      "title": "string",
      "description": "string or null"
    }
  ],
  "chapter_count": "integer",
  "retrieved_at": "ISO 8601 timestamp"
}
```

## Reference Output (Algebra — fallback_from_scope)

```json
{
  "subdomain_id": "SD-001",
  "subdomain": "Algebra",
  "canonical_source": "Lang, S. — Algebra (Springer, 3rd ed.); supplemented by Dummit & Foote — Abstract Algebra",
  "retrieval_method": "fallback_from_scope",
  "source_available": false,
  "chapters": [
    { "index": 1, "title": "Elementary Algebra", "description": "Variables, expressions, equations, inequalities" },
    { "index": 2, "title": "Linear Algebra", "description": "Vector spaces, matrices, linear maps, eigenvalues" },
    { "index": 3, "title": "Abstract Algebra", "description": "Groups, rings, fields, modules" },
    { "index": 4, "title": "Polynomial Algebra", "description": "Factoring, roots, polynomial rings" },
    { "index": 5, "title": "Number Systems", "description": "Integers, rationals, reals, complex numbers as algebraic structures" },
    { "index": 6, "title": "Algebraic Structures", "description": "Homomorphisms, isomorphisms, quotient structures" },
    { "index": 7, "title": "Boolean Algebra and Algebraic Logic", "description": null }
  ],
  "chapter_count": 7,
  "retrieved_at": "2026-03-04T10:00:00Z"
}
```

---

## Content State on Completion
`candidate`

## Special Routing
- `source_available: false` → continue with fallback; log warning `retrieval_fallback_used`
- `chapter_count == 0` → STOP: `retrieval_empty` (fallback also failed — scope.boundaries was empty)

## STOP Conditions
- `scope.boundaries` empty AND source file unavailable → `retrieval_empty`
- Output file not writable → `deterministic_step_error`
