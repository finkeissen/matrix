# statements

## Scope

This directory contains **epistemic statements**.

A statement is a **formulated, attributable assertion**
about something, made in a specific context and time,
and explicitly open to contradiction, revision, or coexistence.

Statements are **not facts**, **not data**, and **not knowledge**.
They are the basic epistemic units handled by the Matrix.

---

## What statements are

Statements are:
- explicitly formulated
- attributable to a source
- temporally bound
- context-dependent
- conflict-capable
- revisionable

They may describe:
- claims about the world
- interpretations
- assumptions
- critiques
- descriptions of systems or processes
- competing viewpoints

No statement has inherent authority or priority.

---

## Contents

Typical files in this directory include:

- `claims.jsonl`  
  Individual epistemic statements.

- `relations.jsonl`  
  Explicit relations between statements  
  (e.g. contradiction, support, revision, dependency).

- `sources.jsonl`  
  Provenance information for statements  
  (documents, discussions, runs, agents, timestamps).

These files together define **what is said, by whom, when,
and in relation to what else**.

---

## What statements are not

Statements are **not**:
- observations or measurements
- raw data
- validated facts
- conclusions
- summaries
- decisions
- rules or constraints

Any interpretation, evaluation, or action based on statements
lies **outside** the responsibility of this system.

---

## Role in the system

Statements are the **primary content units** across all domains.

They are:
- produced by MMS runs
- stored in domains
- exposed through Matrix states
- delivered via gateways

The system operates exclusively on statements
and their explicit relations.

---

## Design Principle

> Everything the system handles must be expressible as a statement.  
> Nothing the system handles is beyond being questioned.

---

## Status

This directory contains **living material**.

Statements may be added, revised, contradicted,
or superseded over time, but never silently replaced.

