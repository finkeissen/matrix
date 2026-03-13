# Envelope: 01_scope

**Parent step:** `01_scope`
**Type:** `llm`
**Model:** `19b`
**Upstream:** subdomain definition (subdomains.jsonl + seed CSV)
**Downstream:** `01_scope_confidence`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "01_scope",
  "parent_step": "01_scope",
  "type": "llm",
  "inputs": {
    "subdomain_id": "SD-001",
    "subdomain_label_hash": "<sha256 of 'Algebra'>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "scope",
      "path": "runs/<run_id>/artifacts/01_scope/scope.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 30,
    "priority": "normal",
    "novelty_guard": true,
    "model": "19b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "initial_scope_definition"
  }
}
```

---

## Prompt (Algebra — SD-001)

```
You are a precise academic knowledge engineer. Your task is to define the exact scope of a subdomain for an atomic problem generation pipeline.

Subdomain: Algebra
Parent domain: Mathematics
Subdomain ID: SD-001
Score: 93 (Tier 1 — high LLM suitability, stable knowledge, closed problem space)

Define the scope of Algebra as a knowledge domain for the purpose of generating atomic problems. An atomic problem is a single, self-contained question or task that can be posed and answered independently, is granular enough that it cannot be meaningfully split further, and has a correct answer or a clear evaluation rubric.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

The JSON object must have exactly these fields:

{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "parent_domain": "Mathematics",
  "canonical_source": <string: the single most authoritative reference for Algebra as a whole, e.g. a standard textbook series, curriculum standard, or mathematical authority>,
  "boundaries": <array of strings: what IS in scope — be specific, list major topic areas>,
  "exclusions": <array of strings: what is explicitly OUT of scope — related areas that must not be included>,
  "ambiguities": <array of objects with fields "topic" and "resolution": topics that sit on the boundary and how to handle them>
}

Requirements:
- boundaries must list at least 6 specific topic areas
- exclusions must list at least 3 areas that could be confused with Algebra
- ambiguities must address at least 2 boundary cases
- All values in English
- Be precise: boundaries and exclusions will be used to validate generated problems
```

---

## Expected Output Schema

```json
{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "parent_domain": "Mathematics",
  "canonical_source": "string",
  "boundaries": ["string"],
  "exclusions": ["string"],
  "ambiguities": [
    {
      "topic": "string",
      "resolution": "string"
    }
  ]
}
```

## Reference Output (for validation and testing)

```json
{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "parent_domain": "Mathematics",
  "canonical_source": "Lang, S. — Algebra (Springer, 3rd ed.); supplemented by Dummit & Foote — Abstract Algebra",
  "boundaries": [
    "Elementary algebra: variables, expressions, equations, inequalities",
    "Linear algebra: vector spaces, matrices, linear maps, eigenvalues",
    "Abstract algebra: groups, rings, fields, modules",
    "Polynomial algebra: factoring, roots, polynomial rings",
    "Number systems: integers, rationals, reals, complex numbers as algebraic structures",
    "Algebraic structures: homomorphisms, isomorphisms, quotient structures",
    "Boolean algebra and algebraic logic"
  ],
  "exclusions": [
    "Calculus and real analysis (limits, derivatives, integrals — belongs to Analysis)",
    "Combinatorics and graph theory (belongs to Discrete Mathematics)",
    "Numerical methods and algorithmic computation (belongs to Numerical Analysis)",
    "Geometric reasoning and spatial proof (belongs to Geometry)"
  ],
  "ambiguities": [
    {
      "topic": "Linear algebra overlap with Analysis",
      "resolution": "Linear algebra is in scope. Functional analysis (infinite-dimensional spaces, operator theory) is out of scope — belongs to Analysis."
    },
    {
      "topic": "Number theory",
      "resolution": "Algebraic number theory (rings of integers, ideals, Galois theory) is in scope. Elementary number theory (divisibility, primes, congruences without algebraic structure) is out of scope — belongs to Number Theory subdomain."
    },
    {
      "topic": "Category theory",
      "resolution": "Basic categorical language (functors, natural transformations) as it appears in algebra is in scope. Pure category theory as an independent discipline is out of scope."
    }
  ]
}
```

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- Output missing required fields (`boundaries`, `exclusions`, `ambiguities`) → `llm_output_invalid`
- `boundaries` array empty or fewer than 3 items → `llm_output_invalid`
