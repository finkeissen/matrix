# Matrix Pipeline: Atomic Problems → Precise Descriptions → Global Alignment (Iterative, Append-Only)

**Scope:** This pipeline lives inside **Matrix (Layer-3)**.  
**Goal:** Build and maintain a *coherent, inspectable* set of **atomic problems** and their descriptions, aligned across the Matrix without introducing authority or silent decisions.

**Design constraints (inherit from system):**
- **Append-only:** no deletion/overwrite of canonical artifacts; changes are new artifacts + links.
- **No implicit decisions:** Matrix records structure, conflicts, absences; it does not “pick winners”.
- **STOP is valid:** inability to establish admissibility becomes an explicit STOP record.
- **Information hiding:** Matrix does not require reading MMS/Hypotheses internals to function; it uses bound inputs and artifact IDs.

---

## 0) Core Data Model (Matrix-internal, minimal)

Matrix maintains three first-class kinds of things:

1. **Atomic Problem (AP)**  
   The smallest unit that can be *precisely described* without referencing unresolved sub-questions.

2. **Description (D)**  
   A structured problem statement for an AP (with explicit scope and exclusions).

3. **Alignment Records (A)**  
   Explicit relations between descriptions (equivalence, overlap, conflict, refinement, dependency).

Additionally, Matrix stores:
- **Consistency Findings (CF)**: computed or manually asserted checks (never silent).
- **Legacy Bucket (L0)**: a *quarantine* of items that cannot (yet) be made admissible or atomic.

All of these are append-only artifacts with `(run_id, artifact_id)` and optional `content_hash`.

---

## 1) Pipeline Overview (Stages)

Matrix runs in cycles. Each cycle consumes:
- the current **Matrix snapshot/view** (previous cycle output), and
- new incoming artifacts from upstream (typically via MMS→Matrix export).

Each cycle produces:
- new APs / Ds / As,
- new CFs (consistency findings),
- new Legacy moves (quarantine records),
- and a new Matrix snapshot.

### Stage 1 — Intake & Normalization
**Input:** MMS bundle + prior snapshot  
**Output:** normalized candidates (claims/relations/conflicts/absences) with stable references

Rules:
- Validate envelope + integrity hashes if present.
- Enforce **run binding** and **artifact identity**.
- Do not interpret meaning; only normalize structure.

If validation fails:
- record a Matrix ingestion run with `outcome=STOP|UNKNOWN` and localized `failure`.
- do not “best-effort” ingest silently.

### Stage 2 — Candidate Problem Extraction
**Goal:** produce *problem candidates* (PCs) from raw artifacts.

A **Problem Candidate (PC)** is any statement that looks like:
- an unresolved question,
- an inconsistency to resolve,
- an undefined term,
- an unbound variable,
- a missing constraint,
- or a conflict that demands partitioning.

Extraction methods (can be multiple, recorded as modes):
- rule-based patterns (e.g., “unknown”, “inconsistent”, “missing definition”)
- conflict-driven extraction (each conflict yields ≥1 PC)
- gap-driven extraction (explicit absences yield PCs)

Output artifacts:
- `problem_candidate` records: `{pc_id, evidence_refs[], extraction_mode, notes}`

### Stage 3 — Atomization (PC → AP)
**Goal:** transform PCs into **Atomic Problems** (APs) that are *well-formed*.

Atomization tests (must pass, otherwise STOP or Legacy):
1. **Single target:** AP asks exactly one question (no hidden conjunction).
2. **Bound scope:** AP has explicit scope boundary and declared exclusions.
3. **No implicit dependencies:** if AP depends on unresolved sub-problems, those must be split out as separate APs and linked.
4. **Admissible vocabulary:** all used terms are either:
   - already defined in Matrix, or
   - explicitly marked as “undefined term” and linked to its own AP.

Outputs:
- `atomic_problem` artifacts: `{ap_id, derived_from_pc_ids[], evidence_refs[], status}`  
- `ap_dependency` relations (AP→AP): `DEPENDS_ON`, `REFINES`, `BLOCKS`

If atomization fails:
- create a `legacy_move` record with reason, evidence, and what would be needed to re-attempt.

### Stage 4 — Precise Description (AP → D)
**Goal:** for each AP, generate one or more **Descriptions** (D). Multiple Ds are allowed; conflicts are first-class.

A **Description (D)** must include:
- **Problem statement** (one sentence)
- **Scope** (what is included)
- **Exclusions** (what is explicitly not included)
- **Inputs** (required references/evidence sets)
- **Success criteria** (what counts as “resolved” structurally)
- **Non-goals** (explicit)
- **Failure modes** (how it can STOP)

Outputs:
- `problem_description` artifacts: `{d_id, ap_id, statement, scope, exclusions, inputs, success_criteria, non_goals}`

If a description cannot be made precise:
- record `description_stop` (STOP-equivalent) bound to the AP and evidence.

### Stage 5 — Alignment (D ↔ D across Matrix)
**Goal:** align all descriptions against each other without forcing a single “truth”.

Alignment relations (first-class artifacts):
- `EQUIVALENT_TO` (same AP described differently)
- `OVERLAPS_WITH` (partial overlap)
- `CONFLICTS_WITH` (cannot both be maintained as compatible under current constraints)
- `REFINES` (one is stricter/more specific)
- `GENERALIZES` (one is broader)
- `DUPLICATES` (procedural duplicate; safe to treat as same for navigation)

Alignment process (iterative):
1. Compare new Ds to existing Ds in snapshot (by evidence refs, scope, key terms).
2. Propose alignment edges (as artifacts).
3. If ambiguous: create a new AP: “Is D1 equivalent to D2 under scope S?”
4. Never auto-merge; merging is a Layer-6 action. Matrix only records structure.

Outputs:
- `alignment_relation` artifacts linking `d_id`s
- optional `alignment_conflict` if multiple incompatible alignments exist

### Stage 6 — Consistency Checking (CF generation)
**Goal:** produce explicit findings about consistency. No silent pruning.

Consistency checks are *structural*, e.g.:
- **Cycle detection:** AP dependency cycles
- **Dangling references:** D refers to missing evidence
- **Contradictory constraints:** Two Ds for same AP with mutually exclusive scope
- **Alignment inconsistency:** D1 equivalent to D2 but also conflicts with D2
- **Undefined term leakage:** D uses term not defined and not linked to a “define term” AP

Each check produces a **Consistency Finding (CF)**:
- `{cf_id, severity, check_name, affected_ids[], evidence_refs[], recommendation}`

Severity is non-authoritative:
- `INFO | WARN | BLOCKING`
(“BLOCKING” means “cannot proceed structurally”; not “bad”)

### Stage 7 — Legacy Quarantine & Re-admission
**Goal:** “legacy” is not trash; it is a structured holding area.

A **Legacy Move (L0)** record includes:
- what was moved (pc_id / ap_id / d_id)
- why (failed atomization, undefined terms, unbound scope, invalid evidence)
- what would be required to re-admit (explicit list of missing prerequisites)
- links to CFs and evidence

Re-admission happens when prerequisites are satisfied:
- create a `legacy_readmission` record referencing the prior legacy_move and the new evidence.
- re-run atomization/description on the item (new artifacts, append-only).

### Stage 8 — Snapshot Emission (Matrix State)
Each cycle ends by emitting a new **Matrix snapshot**:
- snapshot_id, created_at, view parameters
- included APs, Ds, Alignments, CFs, Legacy records
- snapshot_hash (optional)

No “latest” is assumed—consumers bind to snapshot_id.

---

## 2) Iteration & Update Mechanics (How it “keeps updating”)

### 2.1 Everything is a Run
Each cycle is a Matrix run with:
- declared inputs (which MMS export(s), which prior snapshot)
- declared modes (which extraction/atomization/alignment checks were used)
- explicit outcome: `SUCCESS | NOCLAIM | UNKNOWN | CONFLICT | STOP`
- failure localization when STOP/UNKNOWN

### 2.2 Updates are new artifacts + links
You never “edit” an AP or D. You:
- create a new version (new artifact_id)
- link via `SUPERSEDES` or `REVISION_OF`
- keep both visible in history

### 2.3 Convergence strategy (non-authoritative)
Matrix does not decide. It converges by:
- making conflicts explicit,
- making scopes explicit,
- pushing ambiguity into new APs,
- and letting Layer-6 choose when needed.

---

## 3) How Consistency Checking Leads to “Legacy Aussortieren”

The rule is not “inconsistent ⇒ delete”.  
The rule is:

- If something fails *structural admissibility* (cannot be made atomic, cannot be precisely described, or has unbound prerequisites), it moves to **Legacy (L0)** with an explicit reason and re-admission criteria.
- If something is merely conflicting or ambiguous, it stays in Matrix as first-class conflict/alignment uncertainty, and may generate new APs.

### Practical decision table (purely structural)

| Condition | Action |
|---|---|
| invalid references / missing evidence | CF + Legacy Move (until evidence exists) |
| cannot atomize (multiple questions glued) | split into multiple APs; if split impossible → Legacy Move |
| undefined term blocks precision | create “define term” AP; keep D in draft/STOP; possibly Legacy Move if it cannot progress |
| alignment ambiguous | create new AP (“are these equivalent?”) + keep both Ds |
| hard contradiction under same scope | record `CONFLICTS_WITH` + CF; do not legacy by default |

---

## 4) Minimal Deliverables to Implement This in Matrix Repo

1. **Artifact types (schemas or structs):**
- atomic_problem
- problem_candidate
- problem_description
- alignment_relation
- consistency_finding
- legacy_move
- legacy_readmission
- snapshot_descriptor

2. **Pipelines as runs:**
- intake_run
- extraction_run
- atomization_run
- description_run
- alignment_run
- consistency_run
- snapshot_run

3. **Fixtures + contract tests:**
- minimal cycle producing 1 AP + 1 D
- conflict-driven cycle producing alignment conflict
- STOP cycle (invalid evidence)
- legacy move + readmission cycle

---

## 5) Non-Goals (to prevent scope creep)

- Matrix does not resolve truth.
- Matrix does not prioritize which AP to work on.
- Matrix does not “merge” descriptions automatically.
- Matrix does not delete; it only supersedes and quarantines structurally inadmissible items.

---

## 6) Next Step (implementation order inside Matrix)

Recommended order to implement with minimal context:
1. Snapshot store + run logger
2. Intake normalization (validate IDs, run binding)
3. Problem candidate extraction (very simple rules first)
4. Atomization rules (single-target + dependency split)
5. Description template enforcement
6. Alignment edges (start with duplicate/equivalent heuristics)
7. Consistency findings (dangling refs + cycles)
8. Legacy move + readmission


Ich würde gerne von Tests übergehen zur produktion. Also:
1. 80 (alte) Domänen durchforsten und liste der atomaren Probleme mit jedem run erweitern. Dabei stellt sich die Frage, wie der run überhaupt begrenzt wird.
2. Wir müssen definieren, wann wir probleme nicht weitere unterteilen (z.B. wenn keine separaten Lösungen mehr unterschieden werden).
3. dann müssen wir die Probleme beschreiben (Domänen und Subdomänen bzw. Problemgruppen sind dann nur noch beschreiben; 1 Problem kann zu mehreren Gruppen gehören).
4. Das wissen wüssen wir in mehreren Interationen immer weiter verfeinern. Wie bestimmet wir die Anzahl der Interationen?
5. Welche Quellen ziehen wir heran? Kataloge (wie z.b. ICD-11)? verschiedene LLM (die alle 3 Monate besser werden)? Was noch?
6. Wie können wir Pipeline so aufbauen, dass sie nur noch gestartet werden muss und die Wissensmatrix auf der Basis eines aktuellen LLM bzw. von externen Katalogen immer weiter verbessert?

for domain in scheduled_domains:
ingest sources
extract candidates
atomize
refine descriptions
align
run consistency checks
move legacy items
emit snapshot


Human intervention is required only for:
- unresolved alignment ambiguity
- policy choices (Layer-6)
- catastrophic STOP clusters

---

### 7.8 When Is the Pipeline “Finished”?

The pipeline is never epistemically finished.

It is **operationally complete** when:

- new domains can be added without redesign
- rerunning with new models produces bounded deltas
- legacy backlog is explainable (not opaque)
- consistency findings are mostly local, not systemic
- snapshots are reproducible

At that point Matrix becomes a **maintenance system**, not a construction project.

Completion therefore means:
→ the system can improve itself without structural redesign.



Human intervention is required only for:
- unresolved alignment ambiguity
- policy choices (Layer-6)
- catastrophic STOP clusters

---

### 7.8 When Is the Pipeline “Finished”?

The pipeline is never epistemically finished.

It is **operationally complete** when:

- new domains can be added without redesign
- rerunning with new models produces bounded deltas
- legacy backlog is explainable (not opaque)
- consistency findings are mostly local, not systemic
- snapshots are reproducible

At that point Matrix becomes a **maintenance system**, not a construction project.

Completion therefore means:
→ the system can improve itself without structural redesign.

---

## 8) Domain Registry (Production Backbone)

The Domain Registry defines what gets explored and provides stable boundaries for runs.  
It is append-only and versioned.

### 8.1 Domain Record (minimal)

Each domain entry MUST include:

- domain_id  
- title  
- description  
- seed_sources  
- priority  
- status (NEW | ACTIVE | STABLE | ARCHIVED)

Optional:
- parent_domain_id  
- tags  
- sweep_history  
- stability_metrics  

Example structure:

domain_id: medicine.diagnostics  
title: Medical diagnostics  
description: Problems related to identifying conditions from evidence.  
seed_sources: ICD-11, review_papers, clinical_guidelines  
priority: high  
status: ACTIVE  

### 8.2 Scheduling Rules

Domain sweeps are scheduled using:

- priority  
- instability metrics  
- legacy pressure  
- cross-domain dependency density  

This prevents over-exploring already stable areas.

---

## 9) Formal Atomicity Tests

Atomicity must be testable, not intuitive.  
Each AP is evaluated using explicit checks recorded as artifacts.

### 9.1 Solution Distinguishability Test

Question:  
Do multiple structurally distinct solution paths exist?

If YES → split AP.

Signals:
- different constraint sets  
- different evidence classes  
- different evaluation criteria  

Artifact: atomicity_check.solution_distinguishability

---

### 9.2 Dependency Leakage Test

Question:  
Does solving this AP implicitly require solving another hidden question?

If YES → create dependency AP and split.

Artifact: atomicity_check.dependency_leakage

---

### 9.3 Scope Compression Test

Question:  
Would subdivision change structural constraints or only wording/examples?

If only wording → stop subdividing.

Artifact: atomicity_check.scope_compression

---

### 9.4 Executability Test

Question:  
Can this AP drive hypothesis generation without further decomposition?

If NO → not atomic.

Artifact: atomicity_check.executability

---

### 9.5 Meta-Atomicity Escalation

If tests disagree:  
Create a meta-problem asking whether AP X is atomic under criterion Y.  
Uncertainty remains explicit.

---

## 10) Consistency & Convergence Metrics

Matrix needs measurable signals to guide iteration.  
Metrics are descriptive, not authoritative.

### 10.1 Structural Consistency Metrics

Per snapshot:

- dangling reference rate  
- dependency cycle count  
- contradictory description pairs  
- undefined term leakage  
- alignment inconsistency count  

These produce aggregated consistency findings.

---

### 10.2 Refinement Dynamics Metrics

Per domain:

- AP creation velocity  
- AP split rate  
- description revision rate  
- alignment edge growth  
- conflict density  

Interpretation:  
High rates → exploration phase  
Low rates → stabilization phase

---

### 10.3 Legacy Pressure Metrics

- legacy inflow  
- legacy readmission rate  
- average legacy age  
- prerequisite closure rate  

Healthy system: steady readmission rather than monotonic growth.

---

### 10.4 Convergence Signals

A domain approaches structural stability when:

- AP creation velocity decreases  
- splits decrease  
- alignment stabilizes  
- blocking consistency findings are local  
- legacy backlog is explainable  

No global threshold exists; signals are comparative over time.

---

## 11) Iteration Control (When to Revisit)

Iteration is triggered by:

- new source availability  
- new model version  
- spike in consistency findings  
- legacy backlog increase  
- cross-domain dependency discovery  

Each trigger produces a targeted run rather than a full sweep.

---

## 12) Automation Interfaces Required

To sustain production:

- domain scheduler  
- source connectors  
- atomicity evaluator  
- alignment engine  
- consistency engine  
- snapshot differ  
- legacy manager  

Each component is replaceable and versioned.

---

## 13) Failure Modes to Monitor

Critical failure patterns:

- over-splitting (problem explosion)  
- premature atomicity (hidden dependencies)  
- alignment collapse (everything becomes equivalent)  
- legacy black hole (items never re-enter)  
- model bias loops  

These are recorded as system-level consistency findings.

---

## 14) Operational Definition of Maturity

Matrix is mature when:

- new domains integrate without schema change  
- reruns produce refinements rather than restructures  
- atomicity disagreements become explicit problems  
- legacy backlog is bounded  
- consistency findings guide work automatically  

At this stage Matrix becomes a continuous structural observatory.

