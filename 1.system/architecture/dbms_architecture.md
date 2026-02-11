# DBMS Architecture  
## A Blind Substrate for Artifacts, Provenance, and Audit

---

## 0. Scope and Non-Goals

This document specifies the **DBMS layer** of the system.

The DBMS is responsible for:
- persistence,
- versioning,
- provenance,
- auditability.

The DBMS is **intentionally blind** to:
- semantics,
- truth,
- correctness,
- interpretation,
- ontology.

It stores and relates artifacts.  
It never endorses them.

---

## 1. Core Design Principle

> **The DBMS enforces discipline, not meaning.**

All semantic authority lies **outside** the DBMS.
All interpretive rules are enforced **above** it (in the MMS).

---

## 2. Artifact Types

The DBMS recognizes a small, closed set of artifact types.
All are equal in status.

### 2.1 Model
A declared model artifact constructed via the Model Toolkit.

### 2.2 Dataset
Any structured or unstructured data used as input or output.

### 2.3 Run
A recorded execution of a model or process.

### 2.4 Result
Any output produced by a run (numerical, symbolic, structural).

### 2.5 Relation
An explicit link between artifacts (e.g. “uses”, “produced_by”).

### 2.6 Annotation
Non-operative metadata:
- warnings,
- fillet references,
- deprecation notes,
- scope clarifications.

Annotations never modify artifacts.

---

## 3. Mandatory Metadata (No Exceptions)

Every artifact stored in the DBMS must include:

```text
id                  (globally unique)
type                (Model | Dataset | Run | Result | Relation | Annotation)
created_at
created_by
version
status              (active | deprecated | superseded)
scope               (declared applicability)
dependencies        (explicit references only)
toolkit_compliance  (yes | no | unknown)


## Commit Semantics

A commit marks the transition of an artifact or artifact version
from provisional existence to system-recognized state.

A commit:
- freezes the artifact content and metadata,
- assigns a version identifier,
- records authorship and timestamp,
- makes the artifact addressable by other system components.

A commit does not:
- assert correctness,
- validate assumptions,
- grant semantic authority,
- imply truth or relevance.

Commit is a system operation, not an epistemic act.


## Commit Protocol (Consistency Gate)

A commit is a **consistency-enforcing gate**.  
It transitions an artifact (or artifact version) from provisional existence
to a system-recognized, addressable, immutable record.

Commit guarantees **integrity**, not truth.

### 1. Commit Preconditions (Must Hold)

Before a commit is accepted, the DBMS must verify:

1. **Type Validity**
   - `type` is one of: `Model | Dataset | Run | Result | Relation | Annotation`.

2. **Mandatory Metadata Completeness**
   - All required fields are present and well-formed:
     `id, type, created_at, created_by, version, status, scope, dependencies, toolkit_compliance`.

3. **Identifier and Version Discipline**
   - `id` is globally unique.
   - `(id, version)` pair is unique.
   - Version numbers/labels follow a single declared scheme (e.g., integer or semver).
   - No overwrites: a commit cannot modify an existing `(id, version)`.

4. **Status Constraints**
   - `status ∈ {active, deprecated, superseded}`.
   - If `status = superseded`, a `supersedes` relation must exist to the predecessor version.
   - If `status = deprecated`, an annotation must exist stating the reason and scope limit.

5. **Dependency Closure**
   - Every item in `dependencies` must reference existing, committed artifact versions.
   - No dangling references.

6. **Provenance Closure (when applicable)**
   - If `type = Result`, it must reference exactly one producing `Run`.
   - If `type = Run`, it must reference all input artifacts it consumed.
   - Run → Result links must be explicit relations.

7. **Relation Integrity (when applicable)**
   - If `type = Relation`, it must declare:
     - `relation_type` (from an allowed set),
     - `source` (artifact ref),
     - `target` (artifact ref).
   - Both endpoints must exist and be committed.
   - The relation must satisfy type constraints (see below).

8. **Model Toolkit Compliance Flag (when applicable)**
   - If `type = Model`, `toolkit_compliance` must be `yes | no | unknown`.
   - If `toolkit_compliance = yes`, the commit must include an annotation or structured check record
     indicating which toolkit requirements were verified.

### 2. Allowed Relation Types (DBMS-Level)

The DBMS only enforces **structural** relation validity.
Recommended minimal set:

- `uses` (Run → Model/Dataset)
- `produces` (Run → Result)
- `depends_on` (Artifact → Artifact)
- `supersedes` (Artifact(version) → Artifact(previous version))
- `annotates` (Annotation → Artifact)

No relation implies truth, correctness, or importance.

### 3. Type Constraints for Relations (Structural Only)

The DBMS must reject relations that violate the following:

- `produces`: source must be `Run`, target must be `Result`.
- `uses`: source must be `Run`, target must be `Model` or `Dataset`.
- `supersedes`: both endpoints must be the same artifact type and same `id`, with different versions.
- `annotates`: source must be `Annotation`, target may be any artifact type.

### 4. Commit Actions (Atomic)

On successful commit, the DBMS must atomically:

1. Store the artifact content and metadata as an immutable record.
2. Store all declared relations (or reject the commit if relations fail validation).
3. Append an audit event recording:
   - who, when, what, previous_state (if any), new_state.
4. Return a stable reference handle for addressing the committed version.

### 5. What Commit Does Not Do

Commit does not:
- validate empirical adequacy,
- evaluate model quality,
- infer semantics,
- grant epistemic authority.

Commit is an integrity operation, not an epistemic act.


# Matrix Architecture (v0)
## One Structural Scheme for Matrix, MMS, and Research Program

---

## 0. Declaration

This architecture defines a **single structural scheme** for representing:
- the Matrix (knowledge instances),
- the MMS (meta-model system),
- and the Research Program (methods, questions, outputs).

The difference between these layers is **not structural** but **policy-bound**:
they share the same artifact graph, but enforce different admissibility,
interfaces, and evaluation policies.

This is an anti-overreach architecture:
it represents artifacts and relations explicitly,
and blocks illicit upgrades by construction.

---

## 1. Core Principle

> Everything is an artifact.  
> Everything connectable is a typed relation.  
> Nothing is implicitly privileged.

No component (Matrix, MMS, Research) introduces hidden authority.
Authority can only appear as explicit, local, revocable policy.

---

## 2. The Matrix Kernel (Shared by All Layers)

### 2.1 Artifact (the universal unit)
An artifact is any explicit record with:
- identity,
- type,
- version,
- status,
- scope,
- provenance.

Artifacts may carry payloads (documents, parameters, code, data),
but the kernel treats payloads as opaque.

### 2.2 Relation (first-class link)
A relation is an artifact connecting two artifacts with:
- relation_type,
- source_ref,
- target_ref,
- scope,
- optional constraints.

No relation implies truth. Relations only declare structure.

### 2.3 Run (execution record)
A run is an artifact that:
- references inputs,
- records execution context,
- produces results,
- is reproducible only relative to declared environment.

### 2.4 Result (output record)
A result is an artifact produced by a run.
It has no epistemic authority by default.

### 2.5 Annotation / Evaluation (explicit feedback)
All “quality”, “usefulness”, “risk”, “robustness”, “confidence”
must enter the system only as:
- annotations (freeform or structured),
- evaluations (typed metrics with context).

No feedback may modify kernel invariants.

---

## 3. Structural Invariants (Must Hold Everywhere)

1. **Immutability by version**
   - committed versions are immutable.

2. **Explicit provenance**
   - every artifact can be traced to inputs/runs/authorship.

3. **No implicit semantics**
   - meaning and truth are never inferred from presence.

4. **No implicit privilege**
   - popularity, frequency, recency do not imply priority.

5. **Scope is mandatory**
   - every artifact and relation declares applicability bounds.

6. **Policy is explicit**
   - any ranking, selection, or default behavior must be declared as policy.

---

## 4. Layering as Policy (Not as Structure)

### 4.1 Matrix Mode (Knowledge Instances)
Policy focus:
- representing concrete model configurations,
- linking runs, datasets, results,
- attaching evaluations under explicit contexts.

### 4.2 MMS Mode (Meta-Model System)
Policy focus:
- enforcing admissibility constraints,
- validating structural integrity,
- supporting composition and comparison,
- applying domain-scoped policies for ranking/recommendation.

MMS is not a separate ontology.
It is the Matrix running under stricter constraints.

### 4.3 Research Program Mode
Policy focus:
- representing research questions as artifacts,
- representing methods as workflows/runs,
- representing outputs as artifacts with provenance,
- tracking failure modes and negative results explicitly.

The research program is not “outside”.
It is the Matrix applied to its own modeling practices.

---

## 5. Minimal Type System (Kernel-Level)

The kernel recognizes a minimal closed set:

- Model
- Dataset
- Run
- Result
- Relation
- Annotation
- Evaluation
- Policy
- Question
- Method
- Claim
- FailureMode

Notes:
- Types do not imply legitimacy; only structure.
- Any domain extension must be explicit and versioned.

---

## 6. Policy Objects (How Control Enters Without Overreach)

Policies are artifacts that specify:
- allowed relation types,
- admissibility checks,
- ranking/selection rules,
- deprecation rules,
- required metadata,
- permitted interfaces to external data or systems.

Policies are:
- local (scoped),
- revocable,
- versioned,
- auditable.

> Authority exists only as explicit policy artifacts.

---

## 7. Interfaces (Where the World Touches the Matrix)

Interfaces are explicit artifacts describing:
- what is imported/exported,
- how it is mapped,
- what uncertainty/assumptions apply,
- what privacy/security constraints apply.

No external signal enters as “ground truth” by default.
It enters as a dataset with declared provenance and scope.

---

## 8. The Commit Gate (Shared)

Commit is the single integrity gate:
- verifies metadata completeness,
- checks dependency closure,
- enforces relation type constraints,
- records audit events,
- freezes versions.

Commit does not validate correctness.
Commit guarantees only structural integrity.

---

## 9. The Core Loop (Universal Workflow)

1. Construct artifacts (models, questions, methods).
2. Run workflows (runs produce results).
3. Attach evaluations/annotations (context-bound).
4. Revise artifacts (new versions).
5. Deprecate/replace (explicitly).
6. Audit everything.

This loop applies to:
- scientific modeling,
- engineering systems,
- the research program itself.

---

## 10. Guardrails (Global)

- Storage ≠ endorsement  
- Success ≠ authority  
- Formalism ≠ ontology  
- Models ≠ worlds  
- Evidence enters only as artifacts  
- Privilege enters only as scoped policy  

Violating these guardrails invalidates interpretation,
not the kernel.

---

End of Matrix architecture.



