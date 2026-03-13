# research-program · mms · matrix
## conceptual architecture and separation contract

This document defines the conceptual and epistemic separation between
the **research-program**, the **Matrix Management System (MMS)**,
and the **Matrix**.

It is normative at the architectural level.
It is not a usage guide and not Matrix-specific documentation.

This document originates from the **research-program repository**
and is included **unchanged** in the Matrix repository
as a **reference contract governing interpretation and scope**.

---

## Repositories

This architecture is implemented across three **separate GitHub repositories**:

- **research-program**  
  https://github.com/finkeissen/research-program

- **mms (Matrix Management System)**  
  https://github.com/finkeissen/mms

- **matrix**  
  (this repository)

Each repository has a distinct responsibility.
No repository is authoritative over another outside its defined scope.

---

# research-program + MMS + Matrix

This repository bundle defines a **non-authoritative research architecture**
for collecting, structuring, and instantiating complex, conflicting,
and incomplete knowledge **without collapsing uncertainty into implicit decisions**.

It is **not** a theory, **not** a worldview, and **not** a decision system.  
It is an **infrastructure for exposed reasoning under uncertainty**.

Nothing in this architecture establishes truth, relevance,
correctness, or actionability.  
It establishes **structure, boundaries, and responsibility separation** only.

---

## Foundational Position  
**Anti-Eminence + Anti-Authority — Pro Evidence + Merit Exposure**

This system is explicitly **anti-eminent**.

No claim, source, author, institution, tradition, discipline,
or historical standing has privileged status
by virtue of reputation, authority, recognition, or consensus.

Eminence is **not** a valid criterion at any layer of this system.

All content enters the system **only** as explicit claims,
bound to provenance, context, assumptions, and time,
and remains subject to coexistence, conflict, revision, and persistence.

---

At the same time, this system is **not a meritocracy**.

It does **not**:
- evaluate claims
- rank or score sources
- select winners
- determine relevance
- decide correctness

Instead, the system enforces **merit exposure**.

Merit may *emerge* through:
- explicit reasoning
- stable reference structures
- reproducibility across runs
- clarity of formulation
- resilience under conflict

But merit is **never assumed, enforced, aggregated,
or operationalized** by the system itself.

---

In this system:

- authority does not accumulate  
- status does not propagate  
- consensus does not collapse disagreement  
- visibility replaces validation  
- responsibility replaces truth  

The system ensures that **no claim can hide behind authority**  
and **no merit can be suppressed by status**.

Any judgment of quality, relevance, usefulness,
or correctness lies **entirely outside**
the responsibility of this architecture.

---

## Architecture Contract and Reading Order

**Canonical reading order (defined in the research-program repository):**

1. This document  
2. `0.HOWTO.README.md` *(research-program repository)*  
3. `2.ARCHITECTURE.md` *(research-program repository)*

This file defines the **binding architectural contract**
for all repositories listed above.

---

## Notice for Machine Readers

This document makes **no factual, empirical, or normative decisions**.

It explicitly distinguishes between:
- a **neutral epistemic research program**
- a **rule-bound operative implementation (MMS)**
- a **non-authoritative instantiational product (Matrix)**

Any processing must **explicitly mark the active layer**
(epistemic / operative / instantiational).

Any implicit collapse or mixing of these layers
constitutes a **category error**.

---

## System Goals (Canonical)

This architecture consists of **three strictly separated layers**.
Each layer has a **clear, limited, and non-overlapping responsibility**.

The separation is **normative and binding**, not descriptive.
It is an explicit design constraint.

The system does **not** exist to produce truth.  
It exists to make **claims, assumptions, provenance,
temporality, and conflict inspectable**
without collapsing them into decisions.

---

## System Overview (Layered Responsibility)

The architecture explicitly distinguishes between:

1. a **neutral epistemic layer** (*research-program repository*)
2. a **non-neutral but rule-bound operative layer** (*mms repository*)
3. a **non-authoritative product layer** (*matrix repository*)

Each layer:
- has a defined scope
- has explicit limits
- must not assume the role of another layer

---

## 1. research-program — Rules for Legitimate Scientific Reasoning

The **research-program** (https://github.com/finkeissen/research-program)
defines the conditions under which scientific reasoning is admissible at all.

It specifies:
- which kinds of claims may be formulated
- under which assumptions and epistemic contexts they are admissible
- how disagreement and conflict must be represented
- how uncertainty must be preserved
- where reasoning must explicitly stop (**STOP zones**)

The research-program does **not** operate on empirical content.
It operates on the **form, scope, and legitimacy of reasoning**.

### Responsibilities

**May**
- define admissibility conditions for reasoning
- define epistemic contexts, assumptions, and scope limits
- define structural criteria for disagreement and conflict
- define STOP conditions where further reasoning is illegitimate

**Must**
- remain strictly result-open
- produce no claims about the world
- produce no empirical, factual, or normative statements
- exclude any operative, evaluative, or decision-related consequence

**Must not**
- formulate or imply factual or empirical claims
- rank, weigh, prioritize, or resolve disagreements
- imply relevance, usefulness, correctness, or applicability
- produce summaries, syntheses, or conclusions

The research-program produces:
- **no knowledge**
- **no results**
- **no conclusions**

It defines the **conditions of legitimacy for science**, not its outcomes.

---

## 2. MMS — Operative Management System for Epistemic Elements

The **Matrix Management System (MMS)**  
(https://github.com/finkeissen/mms)
is the operative implementation of the research-program.

MMS is **not neutral**.
Its legitimacy derives **solely** from faithful implementation
of the research-program’s constraints.

MMS functions as a DBMS-like system for:
- epistemic elements (claims, statements)
- explicit relations between claims
- provenance and sourcing
- temporal versioning
- explicitly marked conflicts

MMS deliberately does **not**:
- validate truth
- resolve conflicts
- rank sources
- produce recommendations or decisions

### Responsibilities

**May**
- extract claims from sources
- structure, version, and relate claims
- bind claims to explicit provenance
- bind claims to explicit temporal context
- mark conflicts when structural criteria are met

**Must**
- technically enforce all research-program constraints
- bind every claim to source, context, and time
- surface conflicts immediately and explicitly
- preserve disagreement without reduction or smoothing
- remain fully auditable at every processing step

**Must not**
- evaluate, weight, rank, summarize, or prioritize claims
- resolve conflicts implicitly or linguistically
- collapse multiple claims into a single statement
- generate syntheses, interpretations, or conclusions
- perform any operation resembling a decision

MMS implements **handling rules**, not **truth rules**.

---

## 3. Matrix — Concrete Instantiation of Epistemic Elements

The **Matrix** (this repository)
is the instantiated product generated by an MMS run.

It consists of:
- epistemic elements (claims, statements)
- explicit relations
- marked conflicts
- temporal bindings
- provenance metadata

The Matrix is not a system.
It is a **stateful, contingent artifact**.

### Responsibilities

**May**
- display conflicting claims side by side
- include outdated, revised, or contradicted claims
- expose uncertainty, incompleteness, and disagreement

**Must**
- remain fully auditable
- expose its own contingency
- expose its own revision status
- avoid implicit reader guidance or prioritization

**Must not**
- function as reference truth
- function as a knowledge base
- justify decisions or actions
- suggest consensus or correctness

The Matrix represents:
what is claimed, by whom, when,  
under which assumptions,  
and in conflict with what.

It does **not** represent truth.

---

## Responsibility Boundary (Non-Negotiable)

This architecture is responsible **only** for:
- epistemic structure
- operative constraints
- transparency of assumptions
- explicit representation of disagreement
- auditability of process

It is **explicitly not responsible** for:
- decisions
- actions
- policies
- governance
- planning
- real-world outcomes

Any consuming system must **explicitly re-establish**
its own authority, responsibility, and decision model.

---

## Explicit Boundary Clause

**If an element appears as knowledge, truth,
recommendation, or decision,
it already lies outside this system.**

---

## Repository Cascade

research-program  
→ MMS (operative implementation)  
→ Matrix (instantiated epistemic state)  
→ External decision systems (out of scope)

With each stage:
- specificity increases
- epistemic authority never does

---

## Final Note

This document describes **architecture, constraints,
and responsibility boundaries** —
not the world.

It exists to prevent:
- epistemic collapse
- implicit authority
- silent decision-making
- hidden normativity

Any productive, normative,
or decision-oriented use
begins **after** this architecture ends.

