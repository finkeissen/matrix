# matrix

**Public meta-level stress test for structured epistemic artifacts under real-world domains**

---

## What This Repository Is

Matrix is **not a knowledge base**, **not a fact store**, and **not an authoritative source of truth**.

> **Matrix is a public stress test for whether structured epistemic artifacts  
> (claims, relations, scopes, conflicts, gaps, and constraints)  
> can be represented and maintained  
> without collapsing into false certainty or hidden assumptions.**

Matrix does not answer *“What is true?”*.  
It answers:

> **“Can structure survive when truth is incomplete, uncertain, disputed, or unavailable?”**

Uncertainty, contradiction, and incompleteness are **expected outcomes**, not defects.

---

## Why the Matrix Is Problem-Centered  
*(Derived Constraint, Not a Repository Preference)*

The Matrix does not aim to store “knowledge” as isolated facts.

Facts without a problem context:
- cannot be meaningfully evaluated,
- cannot be prioritized,
- cannot be acted upon,
- and cannot be reliably retired or superseded.

In contrast, problem–solution structures:
- anchor claims to a concrete purpose,
- make relevance explicit,
- allow competing claims to coexist as alternatives,
- and provide a stable unit for indexing, filtering, and responsibility assignment.

Accordingly, the Matrix treats **problem-context binding** as a **derived admissibility constraint**:

- The **research-program** defines that epistemic processing is admissible only in relation to explicitly articulated problems.
- **MMS** remains infrastructure and does not define epistemic admissibility.
- The **Matrix** records only artifacts that are explicitly bound to at least one problem.

Therefore, the Matrix does not accept “general knowledge” as free-standing artifacts.
Every claim must be anchored to at least one explicit problem.
Without a problem reference, a statement has no admissible place in this repository.

This does **not** assert that problems are objective, correct, complete, or stable.
It only asserts that **problem articulation is the required index**
for admissible epistemic artifacts within this architecture.

---

## Matrix as Stress Environment

Matrix is an **environment**, not a container of results.

Its primary function is to expose structural failure modes  
that remain invisible in authoritative or decision-oriented systems.

Any apparent stability must be treated as provisional.

---

## What the Matrix Is Made Of (Not Facts)

The Matrix consists exclusively of **epistemic artifacts**, such as:

- claims attributed to sources  
- relations between claims  
- scope and applicability constraints  
- conflicts and parallel validity  
- uncertainty and evidence qualifiers  
- explicit gaps and non-knowledge  
- versioned runs and snapshots  

> **Facts are not Matrix entities.  
> If something appears factual, it is treated as an external assumption.**

No artifact in the Matrix may be interpreted as a fact about the world.  
Any such interpretation lies outside Matrix responsibility.

---

## Clarification — Scope of Representable Claims (Additive)

Within the Matrix, claims may represent, without distinction or special status:

- descriptive statements,
- normative statements,
- alternative options or courses of action,
- advantages, disadvantages, and tradeoffs,
- rules, norms, or requirements,
- institutional or authoritative statements,
- interpretations and counter-interpretations.

Such claims are represented **only as articulated positions**.
They do not imply endorsement, enforcement, prioritization,
recommendation, or decision.

Their presence reflects that such statements
exist in the problem space,
not that they are valid, binding, correct, or applicable.

This clarification introduces no new artifact types,
no new admissibility criteria,
and no new evaluative logic.

---

## Role in the Overall System

Matrix is part of a deliberately separated epistemic architecture.

This architecture consists of three clearly separated layers:

| Component | Role |
|---------|------|
| `research-program` | epistemic boundaries, admissibility rules, and assumptions |
| `mms` | rule-bound operative kernel and execution logic |
| **`matrix`** | **instantiated artifacts and stress environment** |

Matrix **contains the results of MMS runs**,  
but never their endorsement, completion, or authority.

Calling the Matrix an “output” would imply finality or truth.  
Matrix is instead a **continuous pressure test**.

Matrix does not define epistemic rules  
and does not implement operational logic.  
It stores instantiated artifacts, provenance, conflicts, gaps,
and explicit problem bindings.

For the full architectural and epistemic contract governing the separation  
between research-program, MMS, and Matrix, see:

`handbook/research-program_mms_matrix.md`

---

## Core Principle

> **Structure is validated by survivability under load,  
> not by completeness or apparent correctness.**

Survivability means that structure:
- does not collapse under contradiction,
- does not erase uncertainty,
- and does not silently normalize disagreement.

Failure is informative. Collapse is not.

---

## The Matrix as an Ideal

The Matrix represents an **asymptotic ideal of structural honesty**.

It does **not** aim at:
- factual completeness,
- final truth,
- authoritative resolution,
- or a finished body of knowledge.

Progress consists in making:
- assumptions increasingly explicit,  
- conflicts increasingly visible,  
- scopes increasingly precise,  
- gaps increasingly preserved,  
- limitations increasingly unavoidable.

> **The Matrix does not converge toward certainty.  
> It converges toward maximal epistemic transparency.**

The Matrix is therefore never finished.  
Any appearance of finality is treated as a warning signal.

---

## Domain-Driven by Design

Matrix is **domain-first**, not pipeline-first.

> **Domains define admissible artifact types.  
> Scripts are tools, not architecture.**

Each domain specifies:
- its test purpose,  
- admissible artifact types,  
- relation semantics,  
- uncertainty tolerance,  
- explicit non-goals.

Domains are not forced into alignment.  
Misalignment is a diagnostic signal.

---

## Schema, Terminology, and Language

Matrix does **not** assume a unified schema, terminology, or language layer.

Structural, terminological, and linguistic heterogeneity is **intentional**  
and treated as a **diagnostic signal**, not a defect.

Schema alignment and harmonization are explicitly deferred,  
must be explicit, reversible, and traceable,  
and must never overwrite historical material.

Uniformity, if it emerges at all, must be **earned through comparison and failure**, not imposed by design.

---

## Runs as Structural Measurements

A **run** is a **measurement of structural behavior**, not a knowledge update.

Runs are executed by the **Matrix Management System (MMS)**  
and recorded in this repository as immutable execution traces.

A run captures:
- inputs and sources,  
- execution logic,  
- constraints and gates,  
- produced artifacts,  
- surfaced conflicts and gaps.

> **A run never establishes facts.  
> It only shows what structure can or cannot hold.**

Runs are append-only and comparable over time.

No artifact exists in the Matrix without at least one corresponding run.

---

## Repository Structure (Orientation)

This repository distinguishes clearly between:

- `handbook/` — human-readable documentation and concepts  
- `system/` — matrix-internal specifications and schemas  
- `domains/` — the current, referencable Matrix state  
- `work/` — non-normative working spaces (raw, pre-matrix, exploration, production)  
- `runs/` — versioned execution records produced by MMS  
- `exports/` — frozen snapshots and external-facing artifacts  

Directory names describe **roles**, not certainty or finality.

---

## Self-Reference Is Mandatory

Matrix treats itself as an epistemic subject.

It represents:
- its own conventions as artifacts,  
- its own structural assumptions,  
- its own failure modes,  
- its own unresolved tensions.

If Matrix cannot represent its own uncertainty,  
it cannot represent anyone else’s.

---

## Guiding Statement

> **The Matrix does not know.  
> It remembers, relates, constrains, and exposes.**

That is its entire purpose.

---

# Working Agreement: Documentation and Sequencing

## Decision

We keep `3.commit/readme.md` as-is for now to avoid losing context.  
We treat it as the current **source of truth** for goals, constraints, and pipeline assumptions.

Only after the repository structures and the first real commits exist
will we refactor and tighten it.

---

## Why This Order

- Early tightening risks deleting implicit decisions that later prove important.
- The next work is structural and operational
  (folders, contracts, first runs).
- Editorial tightening should happen only once
  we have real friction from real data.

---

## Execution Plan (In Order)

### Step 1 — Freeze commit-readme (soft freeze)
- No major edits for now.
- Small fixes allowed only for:
  - typos,
  - broken links,
  - obvious contradictions (if discovered).

### Step 2 — Create / align repository structures
- Ensure the layer structure exists and is clean:
  - `0.foundation/`
  - `1.system/`
  - `1.handbook/`
  - `2.runs/`
  - `2.work/`
  - `3.commit/`

- Define and create the canonical commit directory contract:
  - file names,
  - required vs optional files,
  - manifest shape.

### Step 3 — Update `matrix/README.md`
- Make it consistent with `3.commit/readme.md`.
- Scope:
  - repository overview,
  - navigation of layers,
  - where to put what,
  - how the pipeline flows.
- Do not duplicate deep details
  (leave those in `3.commit/readme.md` for now).
- Link to `3.commit/readme.md` as the detailed canonical contract.

### Step 4 — Add “v1 contracts” in `1.system/`
- Minimal required fields per record type
  (problem, claim, relation, source, conflict).
- ID strategy statement:
  - content-addressed for problems/claims,
  - curated stable IDs for catalog nodes.
- Supersession rule (no mutation in place).

### Step 5 — Build the first real end-to-end commit
- Small slice:
  - a tiny catalog slice,
  - 5–20 problems,
  - 30–100 claims,
  - minimal relations + sources.
- Commit into `3.commit/<date>/`.
- Validate JSONL against v1 required fields.

### Step 6 — Tighten the commit-readme (after reality exists)
- Remove repetition.
- Split into:
  - “3.commit contract” (short, normative),
  - “pipeline guide” (separate doc),
  - “background rationale” (optional appendix).

---

## Success Criteria

We consider the foundation complete when:
- the first commit exists and validates,
- the indexing smoke test works
  (problem search, facets, time filters),
- and the process can be repeated
  with a second independent source bundle.

