# relations.vocab.md

**Status:** v1 (controlled vocabulary, non-normative)  
**Scope:** Relation `relation_type` values used in Matrix artifacts  
**Applies to:** `3.commit/*` canonical relation records  
**Authority:** descriptive only (no epistemic or operational authority)

---

## Purpose

This document defines a **controlled but extensible vocabulary**
for values used in the `relation_type` field of relation records.

It exists to:

- make relation labels **explicit and readable**
- reduce ambiguity in graph interpretation
- support structural navigation and inspection
- enable consistent usage across commits

This document:

- does **not** introduce new schema fields
- does **not** modify `relation.required.md`
- does **not** enforce semantics
- does **not** imply correctness, priority, or recommendation

It is a **reference vocabulary**, not a contract.

---

## General Rules

1. **String-based**
   - `relation_type` values are always strings.

2. **Controlled but extensible**
   - Prefer values listed here.
   - If no value fits, introduce a new one explicitly using:
     - `domain:<domain>/<type>` for domain-specific relations
     - `exp/<type>` for experimental relations

3. **No implicit evaluation**
   - Relation types must not encode “better”, “worse”, or “best”.

4. **No implicit resolution**
   - Relation types never resolve conflicts or collapse disagreement.

---

## Core Structural Relations

These relations are domain-agnostic and purely structural.

- `answers`  
  Indicates that a claim contributes to addressing a problem
  (without asserting correctness or sufficiency).

- `refines`  
  Narrows or specifies another artifact without asserting superiority.

- `supersedes`  
  Declares that one artifact structurally replaces another
  while preserving append-only history.

- `depends_on`  
  Indicates that one artifact assumes or requires another.

- `supports`  
  Structural support relation (non-evaluative).

- `contradicts`  
  Structural contradiction signal (does not resolve).

- `is_variant_of`  
  Indicates alternative formulations without preference.

- `scopes`  
  Indicates applicability or contextual restriction.

---

## Knowledge Navigation Relations  
*(Position → Target → Routing)*

These relation types support representation of **individual knowledge navigation**
as an explicit graph, without embedding decision logic.

### Position (Standortbestimmung)

- `has_position`  
  Links a problem to claims describing the current position or context.

- `position_of`  
  Inverse form (claim → problem).

---

### Target (Zielbestimmung)

- `has_target`  
  Links a problem to claims describing targets, goals, or preferences.

- `target_of`  
  Inverse form.

---

### Routing (Options / Paths)

- `has_option`  
  Links a problem to option claims (candidate paths or actions).

- `option_of`  
  Inverse form.

- `has_route_segment`  
  Links an option to intermediate route or path segment claims.

- `route_segment_of`  
  Inverse form.

---

## Tradeoffs and Costs

These relations represent tradeoffs explicitly, without optimization.

- `has_pro`  
  Links an option to a pro (advantage) claim.

- `has_con`  
  Links an option to a con (disadvantage) claim.

- `has_tradeoff`  
  Links an option to a structured tradeoff claim
  (e.g. cost vs. risk vs. time).

- `tradeoff_of`  
  Inverse form.

- `has_cost`  
  Links an option to a cost claim
  (financial, temporal, cognitive, etc.).

---

## Norms, Constraints, and Authorities  
*(Represented, Not Enforced)*

These relation types express constraint interaction
without enforcement or authority transfer.

### Constraint Interaction

- `constrains`  
  A norm or constraint limits an option or route segment.

- `permits`  
  A norm permits an option or route segment under a scope.

- `prohibits`  
  A norm prohibits an option or route segment under a scope.

- `requires`  
  A norm requires conditions for an option or route segment.

---

### Authority Attribution

- `issued_by`  
  Links a norm claim to an authority or institution claim.

- `interpreted_by`  
  Links a norm claim to an interpreter (court, agency, body).

- `derived_from`  
  Links a norm or constraint claim to a source or upstream artifact.

---

### Applicability and Scope

- `applies_under_scope`  
  Links a norm, constraint, or tradeoff to a scope claim.

- `scope_of`  
  Inverse form.

---

## Directionality

Directionality is determined by:

- usage of `from_ids` and `to_ids`
- optional `directionality` metadata in relation records

Both forward and inverse relation types are listed
to support different run and extraction styles.

---

## Minimal Compliance Note

A canonical commit is considered vocabulary-compliant if:

- every `relation_type` is:
  - listed in this document, **or**
  - explicitly introduced using `domain:*` or `exp/*`
    with traceable explanation in commit notes

Vocabulary compliance has **no epistemic meaning**.
It exists solely to improve structural clarity and inspection.

---

## Closing Statement

This vocabulary exists to make **structure legible**.

It must never be used to:
- infer correctness
- rank alternatives
- recommend actions
- resolve disagreement

All such operations remain **explicit, external, and contestable**.

