# handbook

The `handbook/` directory contains **human-readable orientation material**
for understanding and navigating the Matrix repository.

It is written **for readers**, not for systems.

Nothing in `handbook/` is normative.
Nothing in `handbook/` defines system behavior.
Nothing in `handbook/` overrides the research-program,
the MMS, or the Matrix structure.

The handbook exists to make the Matrix **approachable without simplifying it**.

---

## Role of the Handbook

The handbook serves three purposes:

1. **Orientation**  
   Helping readers understand what this repository is,
   how it is structured,
   and how its parts relate.

2. **Explanation**  
   Describing concepts, terms, and design intentions
   that are difficult to infer from structure alone.

3. **Navigation**  
   Pointing to relevant locations in the repository
   without asserting priority or correctness.

The handbook is **descriptive**, not prescriptive.

---

## Relationship to Other Repository Areas

This repository distinguishes clearly between:

- `handbook/` — explanation and orientation  
- `system/` — matrix-internal specifications  
- `domains/` — structured epistemic artifacts  
- `work/` — exploratory and provisional material  
- `runs/` — executable and auditable transitions  
- `exports/` — frozen external snapshots  

The handbook may **reference** all of these,
but it must **not replace or reinterpret** them.

If there is a conflict between:
- handbook text, and
- system definitions or domain artifacts,

the handbook is **wrong by definition**.

---

## What Belongs in the Handbook

The handbook may contain:

- high-level explanations of Matrix concepts
- descriptions of architectural intent
- reading guides and orientation paths
- glossary-style explanations
- rationale for design decisions
- references to canonical documents

The handbook may explain **why** something exists,
but must not redefine **what** it is.

---

## What Does Not Belong in the Handbook

The handbook must not contain:

- factual claims about the world
- domain content or interpretations
- system rules or constraints
- executable logic
- validation criteria
- decisions or recommendations

If something could affect
how MMS behaves
or how domains are structured,
it does **not** belong here.

---

## Relationship to the Architecture Contract

The conceptual and epistemic contract
governing the separation between
research-program, MMS, and Matrix
is documented in:

`handbook/research-program_mms_matrix.md`

That document is **normative at the architectural level**.

This handbook:
- may summarize it informally
- may link to it
- may explain its intent

It must **not reinterpret or weaken it**.

---

## Tone and Expectations

The handbook deliberately avoids:
- simplification through omission
- motivational framing
- claims of usefulness or relevance
- promises of outcomes

Understanding the Matrix
requires patience and precision.

The handbook exists to support that effort,
not to shortcut it.

---

## Summary

> **The handbook explains the Matrix.
> It does not speak for it.**

It exists to help readers navigate
a system that is intentionally
non-authoritative, non-final,
and structurally demanding.

