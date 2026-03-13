# Foundation Scope and Terminology Alignment

This document records the current **foundational scope**
and **terminology alignment** of the Matrix repository.

It exists to make explicit what is otherwise implicit.

---

## Foundational Domains (Active)

The following domains constitute the **current foundational core**
of the Matrix system:

- `research-program` — epistemic boundaries and assumptions
- `mms` — structural invariants and identity
- `matrix` — execution and meta-level stress environment
- `informatics` — formal recursion and computability limits
- `physics` — external formal reality anchor

These domains are intentionally prioritized because they test:
- epistemic validity
- structural identity
- formal limits
- self-reference
- real-world consistency

All other domains are currently **out of scope** for active development.

---

## Paused Domains

Domains not listed above are considered **paused**.

This means:
- no new runs are expected
- no structural migration is required
- existing material is retained as-is
- presence does not imply maturity or endorsement

Paused domains are not deprecated.
They are intentionally deferred.

---

## Terminology Alignment (Binding)

Across all foundational domains, the following terminology rules apply:

- The Matrix does **not** contain facts.
- The Matrix does **not** assert truth.
- The Matrix operates exclusively on **epistemic artifacts**.

Epistemic artifacts include:
- claims attributed to sources
- relations between claims
- scope and applicability constraints
- conflicts and incompatibilities
- uncertainty and evidence qualifiers
- gaps and explicit non-knowledge
- runs and snapshots

Any appearance of factuality is treated as
an external assumption, not a Matrix entity.

---

## Structural Interpretation

- Completeness is not a goal.
- Consistency is not enforced.
- Conflict is not an error.
- Uncertainty is not a defect.
- Silence is a valid outcome.

Structure is evaluated by **survivability under load**,
not by apparent clarity.

---

## Change Policy

Changes to:
- the set of foundational domains, or
- the global terminology rules

must be made explicitly by updating this document.

Implicit drift is considered a structural failure.

---

## Status

This document reflects the current foundational phase
of the Matrix system.

It is expected to change infrequently.

---


## On Schema, Terminology, and Language Uniformity (Binding)

The Matrix does **not** assume a unified schema, terminology,
or language layer across domains, runs, or phases
at the current foundational stage.

Structural, terminological, and linguistic heterogeneity
is **intentional** and treated as a **diagnostic signal**, not as a defect.

This explicitly includes differences in:
- structural schemas and representations
- field names and formats
- conceptual labels
- synonyms and near-synonyms
- natural languages (e.g. EN, DE)

Schema alignment, terminology harmonization,
synonym resolution, and multilingual consolidation
are **explicitly deferred** to a later exploratory phase.

They must **not** occur:
- implicitly
- silently
- during raw → pre-matrix migration
- inside pre-matrix material
- inside domains
- inside runs
- or inside MMS

Any future harmonization:
- occurs explicitly in `exploratory/`
- is reversible and traceable
- preserves original phrasing and language
- never overwrites historical artifacts

Premature normalization of structure, terms, or language
is considered a **structural risk**
because it collapses epistemic variation
before it has been tested.

Uniformity, if it emerges at all,
must be **earned through comparison and failure**,
not imposed by design.


## MMS Self-Description and Reflexive Admissibility

### Status

This section is **normative** for the MMS architecture.

It clarifies how the MMS may represent, process, and constrain
**knowledge about itself**, the Matrix, the DBMS layer,
and the Research Program.

---

## 1. No External Meta-Layer

The MMS does **not** assume, require, or permit an external meta-layer
from which the system is described, validated, or grounded.

There is:
- no privileged observer position,
- no meta-authority,
- no system-external semantics.

All descriptions of:
- the MMS,
- the Matrix,
- the DBMS layer,
- and the Research Program

must appear **inside the same artifact space**
and are subject to the same structural rules
as any other epistemic artifact.

Self-description does not grant authority.

---

## 2. Self-Description as Artifact

Any statement *about* the MMS architecture,
its principles, constraints, or limitations
must be represented explicitly as one or more artifacts, such as:

- documents (e.g. architectural specifications),
- claims (with declared scope),
- relations (e.g. “constrains”, “assumes”, “excludes”),
- annotations (warnings, limitations, failure modes),
- policies (admissibility, enforcement, deprecation).

No implicit system knowledge is permitted.

Silence is interpreted as **non-commitment**, not as default truth.

---

## 3. Reflexive Symmetry Constraint

Artifacts that describe the MMS or the Matrix
are subject to **the same constraints** as any other artifact:

- explicit scope declaration,
- versioning and immutability by version,
- provenance and authorship,
- conflict admissibility,
- possible supersession or deprecation.

There is no exemption for “foundational” artifacts.

Foundationality is a **policy decision**, not a structural privilege.

---

## 4. MMS as Enforcer, Not Knower

The MMS enforces:
- structural admissibility,
- artifact integrity,
- relation validity,
- policy application.

The MMS does **not**:
- know what artifacts mean,
- decide which descriptions are correct,
- resolve conflicts,
- infer truth from structure.

Descriptions of MMS behavior or intent
do not become operative unless explicitly referenced
by active policies.

---

## 5. DBMS Boundary (Blindness Preserved)

All MMS self-descriptions are persisted via the DBMS
without semantic inspection.

The DBMS:
- stores MMS architecture artifacts,
- versions them,
- relates them,
- audits their history,

but remains blind to:
- their meaning,
- their correctness,
- their normative force.

No MMS rule may rely on DBMS interpretation.

---

## 6. Research Program Reflexivity

The Research Program may:
- formulate questions about the MMS,
- generate problems concerning its limits,
- produce runs that stress MMS assumptions,
- record failure modes and breakdowns.

These outputs are first-class artifacts.

The MMS must admit research outputs
that challenge, weaken, or destabilize
its own architectural assumptions,
provided they satisfy structural constraints.

Self-critique is admissible by design.

---

## 7. Explicit Non-Goals

The MMS architecture does **not** aim to:

- encode total knowledge,
- achieve closure or completeness,
- stabilize a final self-description,
- converge to a single correct architecture,
- immunize itself against revision.

Any attempt to introduce implicit closure,
hidden authority, or finality
constitutes a structural violation.

---

## 8. Failure Modes (Mandatory Awareness)

The following are recognized MMS-specific failure modes
and must be representable explicitly when they occur:

- implicit meta-assumptions,
- architectural drift without versioning,
- silent schema normalization,
- unscoped “foundational” claims,
- self-descriptions treated as truths,
- enforcement rules justified by narrative instead of policy.

Detection does not imply resolution.
Recording is sufficient.

---

## 9. Architectural Invariant (Binding)

> The MMS may describe itself,
> but never from outside itself,
> never without scope,
> and never with implicit authority.

Self-reference is permitted.
Self-privilege is not.
