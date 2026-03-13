# Problem Record — Required Fields (v1)

---

## Status

- **Contract level:** v1 (required)
- **Applies to:** canonical Matrix commits (`3.commit`)
- **Scope:** structural admissibility (not semantic correctness)
- **Authority:** technical contract only (non-epistemic)

---

## Purpose of the Problem Record

A **Problem** is the primary epistemic anchor of the Matrix.

Problems define:
- why claims exist,
- how relevance is determined,
- where scope applies,
- and how conflicting claims can coexist without structural collapse.

The Matrix does not store free-floating knowledge.
All canonical claims, relations, and conflicts are anchored to at least one explicit problem.

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

Every canonical problem record **MUST** include the following fields.

### `problem_id` (required)

- Stable, unique identifier for the problem.
- MUST NOT be reused for a semantically different problem.
- MAY be content-addressed or curated.
- MUST remain stable across commits.

The `problem_id` is the primary reference key used by claims, relations, and conflicts.

**Structural constraints**
- MUST be ASCII-safe (recommended: `[a-z0-9._:-]`).
- MUST be unique within a commit bundle.

---

### `problem_statement` (required)

- A clear, explicit articulation of the problem.
- MUST be phrased as a question or challenge.
- MUST allow for multiple possible answers.
- MUST be understandable without relying on external context.

The statement is not required to be “good” or “important”.
It is required to be **explicit**.

---

### `problem_scope` (required)

Defines the intended scope of the problem.

MUST include (as text or structured subfields):
- temporal scope (explicit or implicit),
- domain or application context,
- relevant constraints or exclusions.

Scope limits applicability.
It does not assert correctness.

**Minimum requirement**
- `problem_scope` MUST contain at least one explicit limiting dimension
  (time, geography, jurisdiction, audience, domain, or exclusions).

---

### `problem_context` (required)

Describes the context in which the problem arises.

This MAY include:
- institutional context,
- practical or theoretical background,
- motivating circumstances,
- assumptions taken as given for this problem.

Context explains **why the problem exists**, not how it should be solved.

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

Describes when the problem is considered valid (as a simplification, treated as global and discrete).

MUST include:
- `valid_from` (required)
- `valid_until` (optional)

**Date format**
- MUST use ISO-8601 date or datetime (recommended: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`).

Validity does not imply correctness.
It only defines the temporal applicability window for structural filtering.

---

### `sources` (required, non-empty)

References to sources that:
- justify the existence of the problem,
- document why it matters,
- or establish that it is recognized.

Sources do **not** need to agree.
They establish provenance, not correctness.

**Minimum structure**
- `sources` MUST be a non-empty list.
- Each entry MUST include at least:
  - `source_id` (string; must correspond to a Source record within the same commit bundle or a referenced bundle)
- Each entry MAY include:
  - `locator` (e.g., URL, DOI, page range, section)
  - `note` (short justification for why this source is attached)

If a referenced `source_id` does not resolve, the commit MUST STOP.

---

## Optional Problem Fields (Explicitly Non-Required in v1)

Allowed but not required:
- `related_problems`
- `notes`
- `tags`
- `assumptions`
- `known_gaps`

Their absence MUST NOT block a canonical commit.

---

## Structural Constraints (Binding)

1. **Uniqueness**  
   Each `problem_id` refers to exactly one problem within a commit bundle.

2. **Anchor Integrity**  
   All claims referencing a problem MUST reference an existing `problem_id`.

3. **No Implicit Problems**  
   Problems MUST be explicitly recorded; they MUST NOT be inferred from claims or relations.

4. **Immutability in Place (Append-only)**  
   Problems are not modified in place.
   Changes are expressed via:
   - a new problem record, and/or
   - explicit relations (e.g., `supersedes`, `refines`) captured in Relation records.

5. **No Hidden Normativity**  
   A Problem record MUST NOT encode solutions as if they were scope or context.

---

## STOP Conditions (v1)

A canonical commit MUST STOP if any of the following holds:

- `problem_id` is missing, empty, or duplicated.
- `problem_statement` is missing or empty.
- `problem_scope` is missing or empty.
- `problem_context` is missing or empty.
- `problem_status` is missing or not one of the allowed values.
- `problem_validity.valid_from` is missing or not parseable as an ISO-8601 date/datetime.
- `sources` is missing or empty.
- any `sources[*].source_id` is missing or does not resolve to a Source record.

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

- **Claims** MUST reference ≥ 1 `problem_id`.
- **Relations** MAY reference problems directly.
- **Conflicts** typically reference problems indirectly via claims.
- **Sources** MAY justify problems, claims, or both.

Problems are the **root nodes** of the Matrix graph.

---

## Versioning Notes

This is **v1 (required)**.

Expected future changes (non-required for v1 correctness):
- richer scope modeling,
- jurisdictional or contextual validity,
- problem lifecycle modeling,
- finer-grained status transitions,
- optional structured fields for domain constraints.

---

## Guiding Statement

> **Problems define where epistemic work may begin.  
> Without a problem, the Matrix must remain silent.**

