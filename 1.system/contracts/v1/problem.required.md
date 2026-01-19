# Problem Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit`)
- **Scope:** structural admissibility, not semantic correctness
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Problem Record

A **Problem** is the primary epistemic anchor of the Matrix.

Problems define:
- why claims exist,
- how relevance is determined,
- where responsibility and scope apply,
- and how conflicting claims can coexist without collapse.

The Matrix does not store free-floating knowledge.
All canonical claims, relations, and conflicts
are anchored to at least one explicit problem.

Accordingly:

> **Without a problem record, no canonical Matrix content is admissible.**

This is a **structural requirement**, not an evaluative judgment.

---

## What a Problem Is (and Is Not)

### A Problem Is

A Problem is:
- an explicitly articulated question, task, or challenge,
- framed such that multiple competing answers are possible,
- scoped in time, domain, and applicability,
- stable enough to serve as a long-term reference anchor.

Problems function as **epistemic containers**, not as claims.

---

### A Problem Is Not

A Problem is **not**:
- a solution,
- a claim about the world,
- a hypothesis or conclusion,
- a vague topic label,
- a domain or category,
- a goal statement without epistemic content.

Problems do not assert truth.
They define the **space in which truth claims may be articulated**.

---

## Required Problem Record Fields (v1)

Every canonical problem record **must** include the following fields.

### `problem_id` (required)

- Stable, unique identifier for the problem.
- Must not be reused for a semantically different problem.
- May be content-addressed or curated.
- Must remain stable across commits.

The `problem_id` is the primary reference key
used by claims, relations, and conflicts.

---

### `problem_statement` (required)

- A clear, explicit articulation of the problem.
- Must be phrased as a question or challenge.
- Must make epistemic uncertainty explicit or implicit.
- Must allow for multiple possible answers.

The statement must be understandable
without relying on external context.

---

### `problem_scope` (required)

Defines the **intended scope** of the problem.

Must include:
- temporal scope (explicit or implicit),
- domain or application context,
- relevant constraints or exclusions.

Scope limits applicability.
It does not assert correctness.

---

### `problem_context` (required)

Describes the **context in which the problem arises**.

This may include:
- institutional context,
- practical or theoretical background,
- motivating circumstances,
- assumptions taken as given for this problem.

Context explains *why the problem exists*,
not how it should be solved.

---

### `problem_status` (required)

Indicates the current status of the problem **within the Matrix**.

Allowed values (v1):
- `open`
- `closed`
- `deprecated`
- `superseded`

Status reflects **Matrix handling**, not real-world resolution.

---

### `problem_validity` (required)

Describes when the problem is considered valid.

Must include:
- `valid_from`
- optional `valid_until`

Validity is treated as global and discrete
as an explicit simplification.

---

### `sources` (required, non-empty)

References to sources that:
- justify the existence of the problem,
- document why it matters,
- or establish that it is recognized.

Sources do **not** need to agree.
They establish provenance, not correctness.

---

## Optional Problem Fields (Explicitly Non-Required)

The following fields are allowed but **not required** in v1:

- `related_problems`
- `notes`
- `tags`
- `assumptions`
- `known_gaps`

Their absence must not block a canonical commit.

---

## Structural Constraints

The following constraints are binding:

1. **Uniqueness**  
   Each `problem_id` refers to exactly one problem.

2. **Anchor Integrity**  
   All claims referencing a problem
   must reference an existing `problem_id`.

3. **No Implicit Problems**  
   Problems must be explicitly recorded.
   They must not be inferred from claims or relations.

4. **Immutability in Place**  
   Problems are not modified in place.
   Changes are expressed via:
   - new problem records,
   - explicit `supersedes` / `refines` relations.

---

## What This Contract Does Not Enforce

This contract does **not** enforce:
- problem quality,
- problem importance,
- problem correctness,
- problem completeness,
- problem usefulness.

It enforces **structural admissibility only**.

Evaluation lies outside the Matrix.

---

## Relationship to Other Record Types

- **Claims** must reference ≥ 1 `problem_id`.
- **Relations** may reference problems directly.
- **Conflicts** often reference problems implicitly via claims.
- **Sources** may justify problems, claims, or both.

Problems are the **root nodes** of the Matrix graph.

---

## Versioning Notes

This is **v1 (required)**.

Expected future changes:
- richer scope modeling,
- jurisdictional or contextual validity,
- problem lifecycle modeling,
- finer-grained status transitions.

None of these are required for v1 correctness.

---

## Guiding Statement

> **Problems define where epistemic work may begin.  
> Without a problem, the Matrix must remain silent.**

