# Matrix Engine — version06 Complete Specification

This document is the normative system contract for the Matrix Engine.

It defines:

- architecture
- runtime invariants
- agent model
- workspace model
- verification model
- legacy governance
- operational details
- implementation guidance
- version06 deterministic vertical slice

This README MUST be sufficient to implement and operate the engine without additional documentation.

---

# Table of Contents

1. [Core Invariant](#core-invariant)
2. [Architecture](#architecture)
3. [Workspace Model](#workspace-model)
4. [Agent Sandbox Model](#agent-sandbox-model)
5. [Lifecycle State Machine](#lifecycle-state-machine)
6. [Stage Model](#stage-model)
7. [Manifest & Determinism](#manifest--determinism)
8. [Verification Model](#verification-model)
9. [Dedup & Canonicalization](#dedup--canonicalization)
10. [Anti-Loop Safeguards](#anti-loop-safeguards)
11. [Problem Model](#problem-model)
12. [Legacy Governance](#legacy-governance)
13. [Compute Classification](#compute-classification)
14. [Operational Model](#operational-model)
15. [File Ownership](#file-ownership)
16. [Logging Model](#logging-model)
17. [Problem Catalog Pipeline](#problem-catalog-pipeline)
18. [Failure Philosophy](#failure-philosophy)
19. [TaskEnvelope Runtime](#taskenvelope-runtime)
20. [Resume Invariant](#resume-invariant)
21. [Claude Orchestration Boundary](#claude-orchestration-boundary)
22. [Version Boundary](#version-boundary)
23. [Matrix Consistency Status](#matrix-consistency-status)
24. [Implementation Roadmap](#implementation-roadmap)

---

# Core Invariant

A run is the canonical unit of work.

Everything reproducible MUST exist under:

```
2.runs/<date>/<run_id>/
```

Workspace is execution projection only.  
Canonical run directory is the source of truth.

Ramdisk is acceleration only — never canonical.

---

# Architecture (Persistent since version05)

The engine is a coordinated system:

- **Orchestrator** → lifecycle + state authority
- **Planner** → task definition + policy
- **Load balancing** → placement + objectives
- **Stage workers** → execution
- **Integrator** → external boundary
- **Shared infrastructure** → ids, fs, hashing, logging

Control plane:
- orchestrator + planner

Execution plane:
- stage workers / agents

Data plane:
- run directory

This separation MUST remain stable across versions.

---

# Workspace Model

Runs execute inside a materialized workspace on ramdisk.

## Workspace vs Canonical Rule

**Workspace:**
- mutable
- complete
- ephemeral
- fast

**Canonical run:**
- append-only
- durable
- auditable
- authoritative

Snapshots materialize workspace into canonical storage.

Resume MUST work using canonical data only.

No hidden runtime state allowed.

## Workspace Location

Workspace root:
```
/home/ef/ram/matrix/<run_id>/
```

Used for:
- temp files
- intermediate artifacts
- caches
- large model IO

## Workspace Rules

- Stages MAY write to ram
- Stages MUST write canonical artifacts to run directory
- Orchestrator cleans ram workspace after finalize
- debug_keep may preserve workspace

If ram is unavailable → STOP run (preflight failure)

## Runtime State Invariant

All runtime information MUST exist inside the run and therefore inside every snapshot.

This includes:
- planner state
- task lifecycle
- stage partial outputs
- logs
- intermediate artifacts
- snapshot markers
- resume metadata

No hidden runtime state outside the run directory is allowed.

## Periodic Snapshot Model

The orchestrator periodically materializes the workspace into the canonical run directory:

```
workspace → 2.runs/<date>/<run_id>/
```

Snapshots are:
- append-only
- resumable
- versioned
- atomic

Snapshots may occur during execution (e.g. every 10–30 minutes).

Execution MUST be restartable from the latest snapshot.

---

# Agent Sandbox Model

Agents operate inside isolated directories within the workspace.

## Agent Directory Assignment

Each agent receives its own directory:

- agent_orchestrator
- agent_planner
- agent_validate_<id>
- agent_execute_<provider>_<id>
- agent_self_control_<id>
- agent_update_single

Agents are isolated writers.  
Canonical state is written only to the run directory.

## Agent Directory Structure

Each agent directory contains:

### 1. log
Agent-specific execution log (JSONL format).

### 2. staging
Temporary work area for outputs before commit.

Files placed here are candidates for atomic commit to canonical run directory.

### 3. claims
Agent-produced knowledge claims.

Each agent may produce:
- facts.jsonl
- relations.jsonl
- sources.jsonl
- problems.jsonl

Claims are always candidates subject to verification.

### 4. cache
Optional persistent cache that survives across task executions within same run.

Used for:
- embedding vectors
- tokenization
- parsed schemas
- provider responses

### 5. tmp
Ephemeral working directory, cleared after task completion.

### 6. metrics
Task-level performance data:
- token counts
- latency
- retries
- cost estimates

## Agent Isolation Rules

- Agents never read from other agent directories
- Agents never write to canonical run directory directly
- Orchestrator coordinates all cross-agent communication
- Agents produce outputs via staging → atomic commit

## Agent Output Workflow

1. Agent writes to staging/
2. Agent signals completion
3. Orchestrator validates outputs
4. Orchestrator atomically commits to canonical run directory
5. Orchestrator updates manifest

Agents never own canonical state.

Agents are replaceable.  
Runs are durable.

---

# Lifecycle State Machine

```
INIT  
PREFLIGHT  
PLANNED  
RUNNING  
FINALIZING  
DONE | STOP
```

Transitions MUST be explicit and logged.

STOP is a valid terminal outcome.

## State Definitions

**INIT**  
Run created, initial setup in progress.

**PREFLIGHT**  
Validating prerequisites:
- ram workspace available
- required inputs exist
- configuration valid

**PLANNED**  
Task graph generated, ready for execution.

**RUNNING**  
Active task execution in progress.

**FINALIZING**  
All tasks complete, performing cleanup and snapshot.

**DONE**  
Successful completion, all artifacts canonical.

**STOP**  
Explicit halt due to:
- unrecoverable error
- resource exhaustion
- policy violation
- manual termination

---

# Stage Model

Minimal stage set:

- intake
- validate
- execute
- self_control
- update

## Stage Contracts

Stages:
- declare inputs
- declare outputs
- are idempotent
- cannot mutate previous artifacts
- complete only when outputs exist canonically

## Stage Descriptions

### intake
Normalize external inputs into canonical format.

Produces:
- normalized_inputs/

### validate
Check admissibility and structural correctness.

Produces:
- admissibility_records/
- validation_reports/

### execute
Primary work execution (deterministic, semantic, or LLM-based).

Produces:
- claims/
- problems/
- relations/
- sources/

### self_control
Verify integrity and consistency of produced artifacts.

Produces:
- control_reports/
- conflict_logs/
- verification_status/

### update
Append-only state changes to canonical structures.

Produces:
- state_updates/
- index_changes/

Stages never manage global state.

---

# Manifest & Determinism

The manifest is authoritative metadata.

## Manifest Requirements

Artifacts MUST be hashed (SHA-256).  
State MUST be append-only.  
Resume MUST verify hashes.

## Determinism Rules

Determinism is required for resume safety.

For deterministic tasks:
- Same inputs → same outputs
- Same task_id → same artifact hashes
- Output path deterministic from task_id

For non-deterministic tasks (LLM, semantic):
- Task_id captures policy + inputs
- Multiple executions allowed
- Verification required before canonical acceptance

---

# Verification Model

Generated content is not accepted by default.

Verification is explicit work:

- schema validation
- conflict detection
- matrix alignment
- cross-provider recomputation
- reasoning comparison

Verification is iterative and persistent across runs.

## Content States

**candidate**  
Newly generated, not yet verified.

**verified**  
Passed verification criteria, canonical.

**disputed**  
Conflicting claims exist, requires resolution.

**superseded**  
Replaced by newer verified content.

**rejected**  
Failed verification, not canonical.

## Verification Tasks

Verification happens through dedicated tasks in the planner:

- verify_matrix_alignment
- detect_conflicts
- recompute_disagreement
- canonicalization_pass

These are scheduled like any other task.

---

# Dedup & Canonicalization

Dedup occurs at:

- task level
- artifact level
- knowledge level

Equivalent artifacts produce canonical representation with provenance.

History is never deleted.

## Task-Level Dedup

Tasks with identical:
- stage
- inputs
- policy

Share the same task_id.

Orchestrator skips execution if outputs already exist.

## Artifact-Level Dedup

Artifacts with identical content hash are deduplicated.

Canonical location is deterministic.

All references point to canonical location.

Provenance tracks all generation contexts.

## Knowledge-Level Dedup

Claims with equivalent semantics are linked.

Requires verification stage to detect equivalence.

Canonical claim is selected based on:
- verification score
- provenance quality
- timeliness

---

# Anti-Loop Safeguards

The engine MUST prevent regeneration loops via:

- deterministic task ids
- cooldown windows
- recomputation limits
- novelty scoring
- verification gating

Repeated generation without novelty is discouraged.

## Loop Detection

If the same task_id is generated repeatedly within a run:
- Cooldown enforced (e.g., 10 minutes)
- Recomputation limit checked (e.g., max 3 attempts)
- Novelty score evaluated

If no novelty detected → task rejected.

## Novelty Scoring

Novelty measured by:
- New facts not in existing claims
- New relations not in graph
- Conflict resolution progress
- Verification state changes

Tasks producing zero novelty are suppressed.

---

# Problem Model

Problems are first-class runtime events.

## Problem Lifecycle

```
detect  
record  
classify  
mitigate  
re-evaluate
```

Problems never silently disappear.

## Problem Classification

**Local problems** → mitigation  
- Single task failure
- Retriable error
- Resource constraint

**Global problems** → STOP  
- Invariant violation
- Data corruption
- Unrecoverable state

## Problem Recording

All problems written to:
```
<run_id>/problems/problem_collect.log
```

Format: JSONL

Required fields:
- problem_id
- task_id (if applicable)
- stage
- severity (local | global)
- description
- timestamp
- context

---

# Legacy Governance

Legacy code may be reused only via wrapper.

## Legacy Rules

Legacy:
- never writes canonical artifacts
- must declare provenance
- must be archivable in 0.legacy/

Rejected structures are moved, not deleted.

Repository hygiene is mandatory.

Legacy is memory, not dependency.

## Allowed Reuse Modes

### Import & Wrap (preferred)

Legacy logic is reused through a version06 wrapper.

The wrapper:
- translates TaskEnvelope + run layout → legacy inputs
- executes legacy logic
- validates outputs
- materializes canonical artifacts into the run directory
- produces logs + STOP records if necessary

Legacy code never writes canonical artifacts directly.

### Adapter Invocation (short-term allowed)

Legacy tools may be invoked as subprocesses.

Constraints:
- IO strictly via declared files inside the run directory
- wrapper owns validation and logging
- no hidden writes

## Non-Negotiables

- canonical artifacts live in `2.runs/<date>/<run_id>/`
- ramdisk remains ephemeral
- failures produce explicit STOP
- provenance of reused legacy must be documented

## Rejected Structures → Legacy Archival

version06 keeps active directories clean.

Structures that are no longer valid move to:

```
0.legacy/
```

`0.legacy/` is archive — not production.

### Rejection Criteria

A structure is rejected when:
- it violates version06 invariants
- it duplicates an accepted structure
- it represents an abandoned prototype
- ownership is unclear
- it creates architectural confusion

### Move Protocol

**1. Freeze**  
Stop edits and ensure a stable snapshot.

**2. Move**

Move to:
```
0.legacy/<area>/<YYYY-MM-DD>_<slug>/
```

Examples:
- engine
- stages
- docs
- experiments
- orchestration layouts
- data model prototypes

**3. Annotate (required files)**

Inside the moved folder create:
- README.md — description + how to run (if applicable)
- REASON.md — why rejected
- PROVENANCE.md — original path + commit/date
- STATUS.md — rejected | deprecated | superseded

**4. Link back**

At the original location leave one:
- MOVED_TO_LEGACY.md with new path  
or
- symlink (if tooling supports)

No silent removal.

**5. Register**

Append entry to:
```
0.legacy/INDEX.md
```

Append-only.

### Deprecation vs Rejection

**Deprecated**
- still indirectly used
- wrapper remains
- removal scheduled

**Rejected**
- not used anymore
- archived only
- no active dependencies

Deprecated items may later become rejected.

### Legacy Usage Rule

version06 must never implicitly depend on legacy paths.

If legacy is reused:
- reuse is explicit
- wrapper exists
- validation exists
- provenance is documented

### Repository Hygiene Principle

Active directories contain only:
- canonical execution code
- active schemas
- current documentation
- maintained tooling

Everything else moves to legacy.

### Lifecycle of Reused Legacy

A reused legacy component progresses through:

1. wrapped
2. validated
3. optionally replaced by native version06 implementation
4. moved to legacy archive

Legacy reuse is temporary by default.

### Auditability Requirement

Every architectural decision that removes or replaces structure must be traceable via:
- legacy folder annotations
- INDEX entry
- run logs referencing the change

No silent structural loss.

### Design Intent

Legacy is memory, not dependency.

version06 is the execution authority.

---

# Compute Classification

Deterministic → stability  
Semantic → prioritization  
LLM → exploration  

## Scheduling Priority

```
deterministic  
semantic  
LLM
```

No single LLM failure halts a run.

## Classification Rules

**Deterministic tasks:**
- Pure functions
- Schema validation
- Hash computation
- File operations
- Manifest updates

**Semantic tasks:**
- Embedding generation
- Similarity search
- Clustering
- Ranking

**LLM tasks:**
- Text generation
- Reasoning
- Planning
- Verification synthesis

Load balancer prioritizes deterministic → semantic → LLM.

LLM failures trigger retry, not STOP.

---

# Operational Model

## Self-Discovery

run.py determines automatically:

- repo root
- runs root
- current engine version
- ram workspace

No hardcoded paths.

## Ramdisk Policy

Ram root:
```
/home/ef/ram/matrix
```

For each run:
```
/home/ef/ram/matrix/<run_id>/
```

Used for:
- temp files
- intermediate artifacts
- caches
- large model IO

Rules:
- stages MAY write to ram
- stages MUST write canonical artifacts to run directory
- orchestrator cleans ram workspace after finalize
- debug_keep may preserve workspace

If ram is unavailable → STOP run (preflight failure)

---

# File Ownership (Who Writes What)

## Orchestrator

- manifest
- run state
- STOP records
- run logs
- task lifecycle

## Planner

- decides which tasks exist
- defines cost tier
- defines retries
- defines exploration vs deterministic execution

## Load Balancer

- selects worker placement
- may influence run objectives
- applies backpressure

## Stages

Produce canonical artifacts:

- intake → normalized inputs
- validate → admissibility records
- execute → claims / problems / relations / sources
- self_control → control reports
- update → append-only state changes

Stages never manage global state.

## Integrator

Produces boundary artifacts:

- bundles
- exports
- contract validation reports

Integrator does not change engine state.

## Shared

Pure utilities only.

No writes.

---

# Logging Model

Logs belong to the run.

## Location

```
2.runs/<date>/<run_id>/logs/
```

Format: JSONL

## Required Fields

- run_id
- task_id
- stage
- attempt
- event
- timestamp

version06/logs/ exists only for engine bootstrap and crashes.

## Log Events

Events include:
- task_created
- task_started
- task_completed
- task_failed
- snapshot_started
- snapshot_completed
- state_transition
- problem_detected
- problem_mitigated

All events append-only.

---

# Problem Catalog Pipeline

Discovery is append-only:

```
problem_collect.log
```

From this we materialize:

```
atomic_problems.matrix
```

Atomic problems are the primary execution targets.

## Problem Discovery

Problems detected during:
- validation stage
- execute stage
- self_control stage
- orchestrator lifecycle

All recorded to problem_collect.log.

## Problem Materialization

Planner consumes problem_collect.log and generates:
- atomic_problems.matrix (canonical problem list)
- task envelopes for problem resolution

Problems are first-class work items.

---

# Failure Philosophy

STOP is a valid result.

Prefer:

- explicit STOP
- partial materialization
- traceable logs

over silent continuation.

## Failure Handling

When failure occurs:
1. Record problem
2. Classify severity
3. Attempt mitigation (if local)
4. Emit STOP (if global)
5. Snapshot current state
6. Log full context

Runs may resume from STOP state after mitigation.

---

# TaskEnvelope Runtime

All work executes via TaskEnvelope.

## Envelope Definition

Envelope defines:

- task identity (task_id)
- stage
- inputs (paths + hashes)
- expected outputs (paths)
- policy (compute class, retries, timeout)
- provenance (created by, reason)

Envelope is immutable.

Completion = outputs exist + hashes registered.

## Envelope Lifecycle

1. Planner creates envelope
2. Orchestrator validates envelope
3. Orchestrator assigns to worker
4. Worker claims envelope
5. Worker executes stage logic
6. Worker produces outputs to staging
7. Worker signals completion
8. Orchestrator validates outputs
9. Orchestrator commits outputs to canonical run
10. Orchestrator updates manifest
11. Task marked complete

## Completion Criteria

Task complete when:
- All expected outputs exist at canonical paths
- All output hashes registered in manifest
- No problems recorded during execution
- self_control stage passed (if required)

Incomplete tasks remain in RUNNING state.

---

# Resume Invariant

Using only canonical run directory:

The engine MUST:

- rebuild workspace
- restore planner state
- continue deterministically

No manual reconstruction.

## Resume Process

1. Detect existing run directory
2. Read manifest
3. Read state.jsonl (latest state)
4. Rebuild workspace on ramdisk
5. Restore planner state from canonical files
6. Verify existing artifact hashes
7. Determine incomplete tasks
8. Resume from last snapshot marker
9. Continue execution

## Resume Validation

Before resuming:
- Verify all canonical artifact hashes
- Check manifest consistency
- Validate state transitions in state.jsonl
- Ensure no orphaned staging files

If validation fails → STOP with corruption report.

## Resume Safety

Resume MUST be deterministic for deterministic tasks.

For non-deterministic tasks:
- Resume continues task graph
- May produce different artifacts
- Verification layer handles divergence

Resume never re-executes completed deterministic tasks.

---

# Claude Orchestration Boundary

Claude may:

- plan envelopes
- select next deterministic task
- verify outputs
- trigger snapshot
- emit STOP

Claude may NOT:

- bypass contracts
- overwrite artifacts
- change lifecycle
- assign authority

Claude optimizes execution only.

## Claude's Role

Claude acts as:
- Planner (generates task envelopes)
- Policy advisor (suggests priorities)
- Verification orchestrator (triggers verification tasks)
- Problem classifier (categorizes problems)

Claude does NOT:
- Write canonical artifacts directly
- Manage state transitions (orchestrator's job)
- Execute stages (workers' job)
- Own run authority (orchestrator's job)

---

# Version Boundary

version06 complete when:

- minimal run executes
- resume deterministic
- STOP enforced
- artifacts reproducible

Future versions introduce:

- queue + leases
- remote agents
- semantic planning
- distributed execution

---

# version06 Focus — Deterministic Vertical Slice

version06 implements the first fully runnable slice.

Required capabilities:

- CLI run entry
- preflight
- manifest creation
- append-only state
- minimal stage pipeline
- hello artifact
- snapshot
- deterministic resume
- STOP emission

No distributed execution required.

## version06 Phase 1 Scope

**In scope:**
- Single-machine execution
- Ramdisk workspace
- Deterministic tasks only
- Manual planner (no LLM planning yet)
- Local file-based coordination
- Minimal stage set (intake, validate, execute, update)
- Basic self_control (hash verification)

**Out of scope:**
- Distributed agents
- Remote execution
- LLM-based planning
- Semantic verification
- Matrix consistency engine
- Load balancing
- Queue + lease system

These are future versions.

---

# Matrix Consistency Status in version06

Kurz:
Nein, noch nicht vollständig integriert.

Absichtlich.

version06 Phase 1 implementiert nur die Infrastruktur,
nicht die vollständige Matrix-Konsistenzprüfung.

## What Already Exists (Indirectly)

Die Architektur unterstützt Matrix-Konsistenz bereits strukturell:

- append-only artifacts
- canonicalization
- verification stages vorgesehen
- self_control stage existiert
- provenance + task graph vorhanden
- dedup Modell definiert
- problem records vorgesehen
- verification als first-class work definiert

Das ist das Fundament.

Aber:
Die eigentlichen Konsistenzalgorithmen laufen noch nicht.

## What Concretely Is Missing

### A. Konsistenz-Artefakte

Noch nicht implementiert:

- consistency reports
- conflict graphs
- matrix alignment checks
- constraint violations
- invariant proofs

Aktuell erzeugt execute nur hello.json.

### B. Matrix Index

Es fehlt:

- global artifact index über Runs
- relation graph
- claim equivalence detection
- canonical entity resolution

Ohne Index keine echte Konsistenzprüfung.

### C. Konsistenz-Tasks im Planner

Planner erzeugt aktuell nur:

- intake
- validate
- execute
- update

Es fehlen:

- verify_matrix_alignment
- detect_conflicts
- recompute_disagreement
- canonicalization pass

### D. Konsistenz-Regeln als Code

Noch nicht implementiert:

- invariant engine
- relation consistency rules
- dependency checks
- world state reconciliation

Das ist version07+.

## version06 Role

version06 baut die Voraussetzungen:

- deterministische Runs
- reproduzierbare Artefakte
- provenance
- idempotente Tasks
- Resume
- Logging/Tracing
- Envelope Modell

Ohne das wäre Konsistenz nicht zuverlässig möglich.

## Where Consistency Enters in version06 Minimally

Nur hier:

### self_control stage

Phase-1 Minimalaufgaben:

- artifact hash verification
- expected_outputs completeness
- duplicate detection (hash level)
- manifest integrity

Das ist technische Konsistenz,
nicht semantische Matrix-Konsistenz.

## version07 — Echte Matrix Konsistenz

Erste echte Integrationen:

- artifact relation graph
- claim equivalence detection
- conflict detection tasks
- canonicalization tasks
- novelty signals
- verification scheduling
- cross-run reconciliation

Das wird planner-getrieben.

## Decisive Clarification

Matrix Konsistenz ist kein Feature.
Sie ist eine Dauerarbeitsschicht.

Deshalb:

version06 = Infrastructure  
version07+ = Consistency Engine

## Most Important Rule

Niemals Konsistenz vor Infrastruktur.

Sonst:

- nicht reproduzierbar
- nicht resumable
- nicht auditierbar
- nicht skalierbar

Das ist eine klassische Architektur-Falle.

## Fazit

Konsistenz ist vorbereitet,
aber bewusst noch nicht integriert.

Das ist korrekt.

version06 macht Konsistenz möglich.
version07 beginnt sie auszuführen.

---

# Implementation Roadmap

## Where We Go Deep Now

Die README ist ausreichend vollständig.

Ab jetzt gehen wir nicht mehr breiter,
sondern tiefer entlang der echten Runtime-Kette.

Die Reihenfolge ist fest.

## The Only Correct Depth Order

Engine wird von unten nach oben gebaut:

```
IO → Lifecycle → Tasks → Stages → Resume → Consistency
```

Alles andere erzeugt Chaos.

## Step 1 — Deterministic IO (Shared)

Tiefe bedeutet hier:

- atomare Writes absolut korrekt
- Hashing stabil
- Pfade deterministisch
- JSON Normalisierung festgelegt

Ohne das ist Manifest wertlos.

Konkreter Fokus:

- shared/fs.py
- shared/hashing.py
- shared/ids.py

Das ist der wichtigste technische Schritt der gesamten Engine.

### Implementation Requirements

**shared/fs.py:**
- atomic_write_json
- atomic_write_text
- atomic_rename
- write_delete_test
- ensure_dir
- safe_read_json
- safe_read_text

**shared/hashing.py:**
- hash_file (SHA-256)
- hash_json (normalized)
- hash_string
- verify_hash

**shared/ids.py:**
- generate_run_id (timestamp-based, deterministic)
- generate_task_id (content-addressed)
- generate_artifact_id

## Step 2 — Orchestrator Lifecycle

Nicht Features.

Lifecycle.

Tiefe:

- state.jsonl Events exakt definieren
- STOP Emission garantiert
- manifest Updates atomar
- Conductor Sequenz unveränderlich

Das macht Runs reproduzierbar.

### Implementation Requirements

**orchestrator/conductor.py:**
- init_run
- preflight
- plan
- execute_stage
- finalize
- emit_stop
- snapshot
- state_transition (INIT → PREFLIGHT → PLANNED → RUNNING → FINALIZING → DONE | STOP)

**orchestrator/state.py:**
- write_state_event (append to state.jsonl)
- read_state_history
- get_current_state
- validate_state_transition

## Step 3 — TaskEnvelope Runtime

Jetzt wird es architektonisch echt:

- Planner erzeugt Envelope
- Orchestrator dispatcht
- Stage claimt
- Outputs validiert
- Manifest registriert

Tiefe = Envelope → Completion Logik.

### Implementation Requirements

**planner/envelope.py:**
- TaskEnvelope (dataclass)
- create_envelope
- validate_envelope
- serialize_envelope

**orchestrator/dispatch.py:**
- assign_task
- claim_task
- complete_task
- fail_task

**orchestrator/manifest.py:**
- register_artifact
- verify_artifact
- get_artifact_hash
- list_artifacts

## Step 4 — Resume Semantik

Hier wird entschieden,
ob die Engine seriös ist.

Tiefe:

- Output existence check
- Hash verification
- Skip Regeln
- Snapshot Marker
- Partial run recovery

Wenn das sauber ist:
Engine lebt.

### Implementation Requirements

**orchestrator/resume.py:**
- detect_existing_run
- validate_run_state
- rebuild_workspace
- restore_planner_state
- verify_artifacts
- determine_incomplete_tasks
- resume_execution

## Step 5 — self_control (erste Konsistenz)

Nur technische Konsistenz:

- Hash mismatch detection
- Missing outputs
- Duplicate artifacts
- Manifest drift

Noch keine Matrixlogik.

### Implementation Requirements

**stages/self_control.py:**
- verify_output_hashes
- check_output_completeness
- detect_duplicates
- validate_manifest_integrity
- produce_control_report

## What We Do NOT Deepen Yet

Noch nicht:

- Agent Intelligence
- Load Balancer
- Distributed Agents
- Matrix Graph
- Semantic Verification
- UI
- Performance

Alles davon baut auf den ersten 4 Schritten.

## Mental Model

Du baust gerade:

Ein deterministisches Betriebssystem für Wissensruns.

Nicht:

Eine Pipeline.

## Your Concrete Next Move

Beginne exakt hier:

**shared/fs.py**

Implementiere:

- atomic_write_json
- atomic_write_text
- atomic_rename
- write_delete_test

Dann:

**hashing.py** (normalized JSON hashing)

Dann melden.

Danach gehen wir in:

**conductor.py Skeleton**

## Orientation

Solange Run lifecycle nicht stabil ist,
ist jede weitere Tiefe Schein-Tiefe.

Das ist die wichtigste Architekturregel.

---

# Design Principles

- append-only
- reproducible runs
- idempotent stages
- planner driven execution
- load balancing influences strategy
- boundaries explicit

---

# End of Specification

This document is complete and authoritative for version06 implementation.

All further implementation decisions must derive from contracts defined here.

No additional documentation is required to implement the engine.

When in doubt, refer to core invariant:

**A run is the canonical unit of work.**

Everything else follows from this.


---

# CLI Specification (Normative)

This section defines the required command-line interface behavior for version06.

The CLI MUST be deterministic and side-effect free before PREFLIGHT completes.

## Entry Point

Primary entry point:

- `2.engine/version06/run.py` (or versioned engine entrypoint in repo)

If entrypoint changes → engine version bump required.

## Required Arguments

- `--job <path>` (required)

Behavior:
- If `--job` is missing → process MUST exit with exit code **1** and MUST NOT create a run directory.

## Optional Arguments

- `--runs-root <path>`  
  Overrides canonical runs root (default: `2.runs/`).

- `--ram-root <path>`  
  Overrides ram workspace root (default: `/home/ef/ram/matrix`).

- `--resume <run_id>`  
  Resume an existing run from canonical run directory.

- `--keep-ram`  
  Do not delete ram workspace after finalize (debug-only).

- `--dry-run`  
  Validate job + preflight + planning only, do not execute stages.

- `--log-level <debug|info|warn|error>`  
  Controls console verbosity only; canonical run logs remain JSONL.

## Exit Codes (Normative)

- **0** → DONE (successful completion)
- **2** → STOP (explicit STOP terminal state; stop_record.json exists)
- **1** → internal error or invalid invocation (no valid STOP record may exist)

## Required Environment Variables (Defaults allowed)

Implementations MAY accept environment variables for defaults.

Recommended variables:

- `ENGINE_RUNS_ROOT` (default: `<repo>/2.runs`)
- `ENGINE_RAM_ROOT` (default: `/home/ef/ram/matrix`)
- `ENGINE_PROVIDER_CONFIG` (default: `<repo>/1.system/tools/providers`)

Rules:
- CLI flags override environment variables.
- Missing env vars is not an error if defaults exist.

## Minimal Execution

Example:

```bash
python run.py --job examples/minimal/job.json



---

## Ergänzung 2: STOP Code Registry + Recoverability (Normativ)

```md
---

# STOP Code Registry (Normative)

STOP is a valid terminal state.  
STOP MUST always be explicit, recorded, and auditable.

## STOP Record (Canonical)

When STOP occurs, the engine MUST write:

`stop_record.json` in the canonical run directory.

Minimal schema:

```json
{
  "run_id": "",
  "stage": "",
  "code": "",
  "reason": "",
  "details": {},
  "recoverable": true,
  "timestamp": ""
}


