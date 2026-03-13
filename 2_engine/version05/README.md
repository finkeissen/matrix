# Matrix Engine — version05

version05 introduces the **agent orchestration architecture**.

The engine is no longer a linear script but a coordinated system of:

- orchestrator (planning + run control)
- load balancing (placement + objectives)
- stage workers (execution)
- integrator (external boundary)
- shared infrastructure (ids, fs, logging)

---

## Core invariant

A run is the canonical unit of work.

Everything reproducible must exist under:

2.runs/<date>/<run_id>/

Ramdisk is acceleration only — never canonical.

---

## Operational model

### Self-discovery

run.py determines automatically:

- repo root
- runs root
- current engine version
- ram workspace

No hardcoded paths.

---

### Ramdisk policy

Ram root:

/home/ef/ram/matrix

For each run:

/home/ef/ram/matrix/<run_id>/

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

## File ownership (who writes what)

### Orchestrator

- manifest
- run state
- STOP records
- run logs
- task lifecycle

### Planner

- decides which tasks exist
- defines cost tier
- defines retries
- defines exploration vs deterministic execution

### Load balancer

- selects worker placement
- may influence run objectives
- applies backpressure

### Stages

Produce canonical artifacts:

- intake → normalized inputs
- validate → admissibility records
- execute → claims / problems / relations / sources
- self_control → control reports
- update → append-only state changes

Stages never manage global state.

---

### Integrator

Produces boundary artifacts:

- bundles
- exports
- contract validation reports

Integrator does not change engine state.

---

### Shared

Pure utilities only.

No writes.

---

## Logging model

Logs belong to the run.

Location:

2.runs/<date>/<run_id>/logs/

Format: JSONL

Required fields:

- run_id
- task_id
- stage
- attempt
- event
- timestamp

version05/logs/ exists only for engine bootstrap and crashes.

---

## Problem catalog pipeline

Discovery is append-only:

problem_collect.log

From this we materialize:

atomic_problems.matrix

Atomic problems are the primary execution targets.

---

## Failure philosophy

STOP is a valid result.

Prefer:

- explicit STOP
- partial materialization
- traceable logs

over silent continuation.

---

## Design principles

- append-only
- reproducible runs
- idempotent stages
- planner driven execution
- load balancing influences strategy
- boundaries explicit

## Appendix — Legacy integration & archival governance

### Legacy integration

version05 may reuse legacy implementations from earlier engine versions and
the repository archive located at `0.legacy/`.

Legacy reuse exists to avoid re-implementing proven functionality while
preserving version05 invariants.

---

### Allowed reuse modes

**Import & wrap (preferred)**  
Legacy logic is reused through a version05 wrapper.

The wrapper:

- translates TaskEnvelope + run layout → legacy inputs  
- executes legacy logic  
- validates outputs  
- materializes canonical artifacts into the run directory  
- produces logs + STOP records if necessary

Legacy code never writes canonical artifacts directly.

---

**Adapter invocation (short-term allowed)**  
Legacy tools may be invoked as subprocesses.

Constraints:

- IO strictly via declared files inside the run directory  
- wrapper owns validation and logging  
- no hidden writes

---

### Non-negotiables

- canonical artifacts live in `2.runs/<date>/<run_id>/`  
- ramdisk remains ephemeral  
- failures produce explicit STOP  
- provenance of reused legacy must be documented

---

## Rejected structures → Legacy archival

version05 keeps active directories clean.

Structures that are no longer valid move to:

`0.legacy/`

`0.legacy/` is archive — not production.

---

### Rejection criteria

A structure is rejected when:

- it violates version05 invariants  
- it duplicates an accepted structure  
- it represents an abandoned prototype  
- ownership is unclear  
- it creates architectural confusion

---

### Move protocol

**1. Freeze**  
Stop edits and ensure a stable snapshot.

---

**2. Move**

Move to:

`0.legacy/<area>/<YYYY-MM-DD>_<slug>/`

Examples:

- engine  
- stages  
- docs  
- experiments  
- orchestration layouts  
- data model prototypes

---

**3. Annotate (required files)**

Inside the moved folder create:

- README.md — description + how to run (if applicable)  
- REASON.md — why rejected  
- PROVENANCE.md — original path + commit/date  
- STATUS.md — rejected | deprecated | superseded  

---

**4. Link back**

At the original location leave one:

- MOVED_TO_LEGACY.md with new path  
or  
- symlink (if tooling supports)

No silent removal.

---

**5. Register**

Append entry to:

`0.legacy/INDEX.md`

Append-only.

---

## Deprecation vs rejection

**Deprecated**

- still indirectly used  
- wrapper remains  
- removal scheduled  

**Rejected**

- not used anymore  
- archived only  
- no active dependencies  

Deprecated items may later become rejected.

---

## Legacy usage rule

version05 must never implicitly depend on legacy paths.

If legacy is reused:

- reuse is explicit  
- wrapper exists  
- validation exists  
- provenance is documented  

---

## Repository hygiene principle

Active directories contain only:

- canonical execution code  
- active schemas  
- current documentation  
- maintained tooling  

Everything else moves to legacy.

---

## Lifecycle of reused legacy

A reused legacy component progresses through:

1. wrapped  
2. validated  
3. optionally replaced by native version05 implementation  
4. moved to legacy archive  

Legacy reuse is temporary by default.

---

## Auditability requirement

Every architectural decision that removes or replaces structure must be
traceable via:

- legacy folder annotations  
- INDEX entry  
- run logs referencing the change

No silent structural loss.

---

## Design intent

Legacy is memory, not dependency.

version05 is the execution authority.


### Workspace execution model

Runs execute inside a materialized workspace located on ramdisk.

The orchestrator assembles all required inputs into a run workspace:

- configuration
- matrix / world state
- problem catalog
- legacy dependencies
- run parameters
- planner state

Workspace location:

/home/ef/ram/matrix/<run_id>/

This workspace is a projection of the run and contains all runtime state.

The workspace is never canonical.

---

### Runtime state invariant

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

---

### Periodic snapshot model

The orchestrator periodically materializes the workspace into the canonical run directory:

workspace → 2.runs/<date>/<run_id>/

Snapshots are:

- append-only
- resumable
- versioned
- atomic

Snapshots may occur during execution (e.g. every 10–30 minutes).

Execution MUST be restartable from the latest snapshot.

---

### Resume invariant

A run can be resumed using only:

- the canonical run directory
- the latest snapshot metadata

The orchestrator must be able to:

- rebuild the workspace
- restore planner state
- continue task execution deterministically

No manual reconstruction is required.

---

### Workspace vs canonical rule

Workspace:
- fast
- mutable
- ephemeral
- complete

Canonical run:
- durable
- append-only
- auditable
- authoritative

The canonical run is the source of truth.
The workspace is an execution projection.

## Agent sandbox model

Agents run in isolated sandboxes inside the run workspace.

Workspace root:

/home/ef/ram/runs/<run_id>/

Each agent receives its own directory:

- agent_orchestrator
- agent_planner
- agent_validate_<id>
- agent_execute_<provider>_<id>
- agent_self_control_<id>
- agent_update_single

Agents are isolated writers.  
Canonical state is written only to the run directory.

---

### Agent directory structure

Each agent directory contains:

- log.jsonl — append-only agent log  
- heartbeat.json — liveness + lease renewal  
- claims/ — currently claimed tasks  
- staging/ — temporary outputs before commit  
- cache/ — reusable intermediate data  
- tmp/ — ephemeral files  
- metrics.json — optional performance metrics  

Agents MUST NOT write canonical artifacts directly outside the run directory.

Outputs are produced via staging and atomically moved into the run directory.

---

### Control plane vs execution plane

version05 separates responsibilities:

- control plane → orchestrator + planner  
- execution plane → worker agents  
- data plane → run directory  

The run directory is the authoritative state.  
Agent sandboxes are execution environments.

---

### Logging architecture

Each agent writes its own structured log (JSONL).

The orchestrator:

- reads agent logs incrementally  
- stores read offsets  
- produces an aggregated run log  
- updates dashboard/status views  

Agent logs remain the source of truth.

Aggregation must be restartable using stored offsets.

---

### Fault tolerance

Agent failures must not stop the run.

Mechanisms:

- task leases with expiration  
- idempotent outputs  
- staging → atomic commit  
- single-writer update stage  

If an agent crashes:

- its lease expires  
- tasks return to ready state  
- a new agent may be spawned  
- existing logs remain for analysis  

---

### Parallel execution model

Multiple agents of the same type may run concurrently.

Examples:

- execute_vram agents  
- execute_ram agents  
- execute_api agents  
- non-LLM integration agents  

Tasks are distributed through queues and claims.

Similar tasks may be executed redundantly across providers for verification.

Cross-provider comparison is an explicit task type.

---

### Provider heterogeneity

Execution providers may include:

- local GPU / VRAM models  
- local RAM models  
- remote API models  
- CPU-only integration or sorting tasks  

The load balancer routes tasks based on:

- capability  
- cost tier  
- latency goals  
- verification policies  

Provider diversity increases robustness and validation quality.

---

### Continuous operation model

The orchestrator may run continuously.

Instead of a single infinite run, execution is segmented into resumable runs.

Each run:

- accumulates knowledge  
- performs verification passes  
- produces periodic snapshots  
- may continue from a previous run  

Continuation metadata links runs together.

---

### Snapshot scope

Snapshots must include:

- canonical run directory  
- queue state  
- planner state  
- orchestrator state  
- agent logs  
- agent metrics  
- lease information  
- snapshot markers  

Snapshots must be sufficient to rebuild the workspace and resume execution.

---

### Resume guarantee

Using only the canonical run directory and the latest snapshot metadata,
the orchestrator must be able to:

- rebuild agent sandboxes  
- restore planner state  
- restore queue state  
- continue execution deterministically  

No hidden runtime state is allowed.

---

### Remote agents

Agent isolation enables remote execution.

Remote agents may run on:

- additional GPUs  
- other machines via LAN  
- future distributed environments  

Requirements:

- access to queue and run artifacts  
- structured logging  
- lease protocol compliance  

No architectural changes should be required to add remote agents.

---

### Design intent

Agents are replaceable.  
Runs are durable.  
State is explicit.  
Execution is parallel by default.  
Verification is continuous.

## Content verification model

Generated content is not accepted by default.

All outputs pass through explicit verification stages before becoming durable
knowledge.

Verification is continuous and may occur multiple times across runs.

---

### Verification goals

The system verifies that content is:

- internally consistent  
- non-duplicative  
- grounded in sources or reasoning  
- aligned with the matrix/world state  
- reproducible across providers when required  

Verification is an explicit task type.

---

### Verification stages

Typical verification tasks include:

- schema validation  
- source cross-check  
- matrix alignment  
- conflict detection  
- recomputation with different provider  
- reasoning comparison  
- integration sanity checks  

Verification may be partial and iterative.

---

### Multi-pass verification

Important artifacts may be verified multiple times.

Examples:

- recompute with another model  
- delayed re-check after new knowledge  
- periodic global consistency scans  

Verification history must be preserved in the run.

---

## Deduplication model

Preventing repeated generation is a core responsibility of the planner and
update stage.

Deduplication operates at multiple levels.

---

### Dedup levels

**Task dedup**

Before execution, tasks are checked against existing tasks using:

- deterministic task ids  
- input hashing  
- semantic similarity  

Duplicate tasks are merged or skipped.

---

**Artifact dedup**

Generated artifacts are checked against existing artifacts using:

- content hash  
- normalized representation  
- structural comparison  
- semantic similarity thresholds  

Duplicates are linked rather than re-created.

---

**Knowledge dedup**

At integration time the system:

- merges equivalent claims  
- links related problems  
- detects restatements  
- collapses redundant relations  

Dedup never deletes history.  
It creates links and canonical representations.

---

### Canonicalization

When multiple equivalent artifacts exist, one becomes canonical.

The canonical artifact:

- receives a stable id  
- keeps provenance of alternatives  
- remains replaceable if better evidence appears  

Canonicalization is reversible.

---

## Anti-loop safeguards

The system must prevent infinite regeneration loops.

Mechanisms include:

- task cooldown windows  
- max recomputation counts  
- verification gating before regeneration  
- planner heuristics using novelty signals  
- cost-aware retry limits  

Repeated generation without new evidence is discouraged.

---

## Novelty tracking

Planner decisions consider novelty.

Signals may include:

- unseen sources  
- new relations  
- matrix gaps  
- unresolved conflicts  
- provider disagreement  
- semantic distance from existing artifacts  

Low novelty reduces task priority.

---

## Verification as first-class work

Verification consumes resources intentionally.

Verification tasks may run continuously:

- background consistency scans  
- periodic matrix reconciliation  
- cross-provider validation  
- long-horizon refinement  

The system improves by revisiting prior results.

---

## Integration rule

Content becomes durable knowledge only after passing required verification
thresholds.

Unverified content may remain visible but must be marked accordingly.

Possible states:

- candidate  
- verified  
- disputed  
- superseded  
- rejected  

State transitions must be logged.

---

## Design intent

Generation explores.  
Verification stabilizes.  
Dedup preserves signal.  
Canonicalization provides continuity.

## Feasibility and rollout model

The verification, deduplication and continuous refinement goals of version05
are achievable with commodity hardware when implemented incrementally.

The system does not assume unlimited compute.  
It prioritizes deterministic checks, selective verification and resource-aware
planning.

---

### Hardware assumption

Typical baseline:

- high RAM capacity  
- multi-core CPU  
- optional local GPU  
- optional remote providers  

Large RAM primarily supports:

- workspace materialization  
- snapshot history  
- indices  
- embeddings  
- background verification tasks  

Heavy model inference is treated as a constrained resource.

---

### Engineering vs inference work

Most stability mechanisms are engineering problems, not model problems.

These include:

- run snapshots  
- resume  
- task deduplication  
- artifact canonicalization  
- schema validation  
- consistency checks  
- logging and provenance  

These must work without LLMs.

LLMs are used selectively for semantic reasoning and deep verification.

---

### Rollout phases

The system is expected to evolve through stages.

---

#### Phase 1 — Deterministic stability

Focus:

- task identity  
- snapshot + resume  
- schema validation  
- basic artifact dedup  
- crash tolerance  

Goal: prevent repeated generation loops.

---

#### Phase 2 — Verification as tasks

Introduce explicit verification tasks:

- required field checks  
- provenance presence  
- matrix alignment  
- conflict detection  

Verification becomes continuous background work.

---

#### Phase 3 — Semantic signals

Introduce lightweight semantic mechanisms:

- embedding index  
- similarity thresholds  
- novelty scoring  
- planner heuristics using novelty  

Goal: reduce redundant generation.

---

#### Phase 4 — Selective deep verification

Expensive verification is applied selectively:

- high-impact artifacts  
- unresolved conflicts  
- low-confidence outputs  
- sampled candidates  

Cross-provider recomputation is policy-driven, not default.

---

### Resource-aware verification

Verification intensity is controlled by policy.

Possible controls:

- max recomputation count  
- cooldown windows  
- budget tiers  
- sampling rates  
- priority based on novelty or impact  

The planner must avoid unbounded verification loops.

---

### Continuous improvement model

The system improves by revisiting prior results.

Mechanisms include:

- delayed verification passes  
- periodic matrix reconciliation  
- conflict-driven recomputation  
- cross-provider comparison  

Refinement is incremental and persistent across runs.

---

### Practical expectation

The system will not verify everything equally.

Instead it provides:

- baseline safety for all content  
- stronger guarantees for important content  
- gradual strengthening over time  

Correctness is approached asymptotically.

---

### Design constraint

Compute is finite.  
Verification must be intentional.  
Duplication must be minimized before generation.  
Deep verification must be prioritized.

---

### Design intent

Stability first.  
Semantics second.  
Depth selectively.  
Improvement continuously.

## Problem detection and handling

Problems are first-class runtime events.

A problem is any condition that prevents deterministic continuation, reduces
trust in outputs, or violates engine invariants.

Examples:

- missing inputs  
- schema violations  
- repeated task failures  
- conflicting artifacts  
- resource exhaustion  
- stalled agents  
- verification disagreement  

Problems must be observable, logged and actionable.

---

### Problem lifecycle

When a problem is detected:

1. detect  
2. record  
3. classify  
4. mitigate  
5. re-evaluate  

Problem handling must be idempotent.

Problems never silently disappear.

---

### Detection sources

Problems may be detected by:

- agents  
- orchestrator  
- planner heuristics  
- verification tasks  
- resource monitors  
- snapshot checks  

Detection produces a problem record in the run.

---

### Problem record

Each problem entry includes:

- problem_id  
- type  
- severity  
- affected tasks or artifacts  
- first_seen timestamp  
- status (open | mitigated | resolved | persistent)  
- remediation attempts  

Problem history is append-only.

---

### Mitigation strategies

Typical orchestrator responses:

- retry task with cooldown  
- route task to different provider  
- downgrade objective  
- spawn additional agent  
- schedule verification  
- isolate faulty agent  
- pause specific queue  
- mark artifact disputed  

Mitigation must avoid global run interruption when possible.

---

### Hotplug problem fixing

version05 supports hotplug remediation during execution.

This means:

- configuration may be updated  
- agents may be restarted or replaced  
- verification policies may change  
- legacy wrappers may be introduced  
- planner heuristics may be adjusted  

Changes must be recorded in the run state.

Execution must remain resumable.

---

### Local vs global problems

Local problems affect a task or agent.

Global problems affect planner strategy or run invariants.

The orchestrator must distinguish between both.

Local problems should not stop the run.

Global problems may trigger STOP.

---

## Agent compute classification

Agents are classified by compute cost and determinism.

This classification informs routing, scheduling and verification policy.

---

### Deterministic agents (cheap)

Characteristics:

- no LLM inference  
- predictable runtime  
- idempotent  
- high parallelism  

Examples:

- schema validation  
- task deduplication  
- hashing and canonicalization  
- queue management  
- matrix alignment checks  
- conflict detection  
- aggregation  
- integration without reasoning  

These agents form the stability backbone of the system.

---

### Semantic agents (moderate)

Characteristics:

- lightweight models or embeddings  
- similarity evaluation  
- novelty scoring  
- clustering  

Examples:

- semantic dedup  
- candidate grouping  
- novelty estimation  
- lightweight reasoning  

These agents reduce redundant expensive work.

---

### LLM agents (expensive)

Characteristics:

- generative reasoning  
- synthesis  
- complex verification  
- cross-source interpretation  

Examples:

- execute generation  
- deep verification  
- conflict resolution reasoning  
- hypothesis formation  
- long-form integration  

LLM usage must be budgeted and policy-driven.

---

### Provider diversity

LLM agents may run on different providers:

- local GPU  
- local RAM models  
- remote APIs  
- hybrid configurations  

Multiple providers may execute similar tasks for comparison.

---

### Scheduling implications

The orchestrator prioritizes:

1. deterministic checks first  
2. semantic filtering second  
3. LLM generation last  

This reduces redundant compute and improves stability.

---

### Failure implications

Failure impact differs by class:

- deterministic agent failure → retry or replace  
- semantic agent failure → degraded prioritization  
- LLM agent failure → reroute or defer  

No single LLM failure should halt the run.

---

### Design intent

Deterministic agents stabilize.  
Semantic agents guide.  
LLM agents explore.  
The orchestrator balances cost and progress.


## Engine Development & Execution Supplement (Normative)

This section defines the minimum operational specification required to implement the engine and execute a run using only this repository.  
It complements the architectural invariants and is normative for all version05 implementations.

---

# 1. Quickstart (Minimal End-to-End Run)

## Preconditions
- Python ≥ 3.11
- POSIX environment
- Writable canonical runs directory
- Mounted RAM workspace (tmpfs or equivalent)

## Required environment variables

ENGINE_RUNS_ROOT=<repo>/2.runs  
ENGINE_RAM_ROOT=<ram_mount>/engine  
ENGINE_PROVIDER_CONFIG=<repo>/1.system/tools/providers

## Minimal execution

python run.py --job examples/minimal/job.json

## Expected result

A completed run directory:

2.runs/<date>/<run_id>/
  manifest.json
  state.jsonl
  logs/run.jsonl
  artifacts/
  snapshots/
  stop_record.json (optional)

A run is considered valid if:
- manifest exists
- state log is append-only
- every completed stage produced its declared outputs

---

# 2. Runtime Prerequisites

The engine MUST perform a preflight phase before any stage execution.

Preflight checks:
- RAM workspace available and writable
- Canonical runs root writable
- Sufficient free space thresholds met
- Provider configuration resolvable (even if unused)
- Clock monotonicity available

If any check fails → STOP (preflight) with stop record.

---

# 3. Run Input Contract

Every run MUST be defined by a job file.

Minimal job schema:

{
  "run_name": "string",
  "inputs": {},
  "parameters": {},
  "engine_version": "version05"
}

Required guarantees:
- job file is immutable after run start
- job hash is stored in manifest
- engine version recorded
- parameter defaults resolved before planning

---

# 4. Canonical Run Directory Layout (Normative)

run_root/
  manifest.json
  job.json
  state.jsonl
  logs/
    run.jsonl
    stage_<name>.jsonl
  artifacts/
    claims/
    relations/
    conflicts/
    outputs/
  snapshots/
    <snapshot_id>/
  workspace_meta/
  stop_record.json (optional)

Rules:
- Canonical directory is the single source of truth
- RAM workspace is disposable
- Writes MUST be atomic
- State log MUST be append-only

---

# 5. Run Lifecycle (State Machine)

INIT  
PREFLIGHT  
PLANNED  
RUNNING  
FINALIZING  
DONE | STOP

Transitions MUST be explicit and logged.

Idempotency requirement:
Re-executing a stage MUST NOT corrupt canonical artifacts.  
Stages MUST detect completed outputs and short-circuit when safe.

---

# 6. Stage Contracts (Normative)

Every stage MUST declare:

- required inputs
- produced outputs
- deterministic scope
- stop conditions
- retry policy

Minimal stage set:

- intake → create manifest inputs
- validate → contract validation
- execute → primary task execution
- self_control → consistency checks
- update → artifact integration

A stage is considered complete only when declared outputs exist in canonical storage.

---

# 7. STOP & Failure Records

STOP is a valid terminal state.

A stop record MUST contain:

{
  "run_id": "",
  "stage": "",
  "code": "",
  "reason": "",
  "timestamp": "",
  "recoverable": true|false
}

Stop codes include:
- PREFLIGHT_RAM_UNAVAILABLE
- CONTRACT_VALIDATION_FAIL
- STAGE_OUTPUT_MISSING
- RESOURCE_EXHAUSTED
- POLICY_STOP

STOP MUST be written atomically.

---

# 8. Snapshots & Resume

Snapshots capture canonical progress.

Snapshot MUST include:
- manifest reference
- state position
- artifact index
- workspace metadata

Resume rules:
- resume only from canonical data
- RAM workspace is reconstructed
- incomplete stage may re-run
- completed stages MUST remain immutable

---

# 9. Logging Model

All logs are JSONL.

Required fields:
- timestamp
- run_id
- stage
- event
- severity
- payload (optional)

Logs MUST be append-only.  
Canonical logs are authoritative over RAM logs.

---

# 10. Determinism & Integrity Guarantees

The engine MUST guarantee:

- atomic writes
- content hashing for artifacts
- reproducible manifests
- monotonic state transitions

Integrity claims MUST be derivable from canonical artifacts alone.

---

# 11. Minimal Golden Path (Reference Run)

A minimal compliant run MUST:

1. pass preflight
2. create manifest
3. validate contracts
4. produce at least one artifact
5. finalize without STOP

This path MUST work without external providers.

---

# 12. Development Guidelines

When implementing new stages:

- logic must be pure where possible
- IO isolated to worker boundary
- contracts versioned
- outputs deterministic
- failures produce stop record, not silent fallback

Workers MUST NOT write outside their declared ownership.

---

# 13. Non-Goals (Explicit)

The engine does not guarantee:
- real-time execution
- global scheduling optimality
- provider availability
- absence of STOP

STOP is considered a successful diagnostic outcome.



## Engine Development & Execution Supplement — Anchors & Normative Clarifications

This section removes remaining ambiguity so that the engine can be implemented and a run executed **without additional documentation**.

It defines repository anchors, CLI behavior, thresholds, minimal artifacts, and schema authority.

---

# 1. Repository Anchors (Normative Paths)

The following paths are canonical:

Engine entrypoint:
2.engine/version05/run.py

Minimal example job:
2.engine/version05/examples/minimal/job.json

Provider configuration root:
1.system/tools/providers/

Canonical runs root (default):
2.runs/

If these paths change, the engine version MUST be bumped.

---

# 2. CLI Specification (Normative)

Required argument:
--job <path>

Optional arguments:
--runs-root <path>  
--ram-root <path>  
--resume <run_id>  
--keep-ram  
--dry-run  
--log-level <debug|info|warn|error>

Behavior:

- Missing --job → exit code 1
- Successful run → exit code 0
- STOP terminal state → exit code 2
- Internal error → exit code 1

CLI MUST be deterministic and side-effect free before PREFLIGHT.

---

# 3. Preflight Thresholds (Normative Defaults)

The engine MUST check:

RAM workspace:
- writable
- minimum free space ≥ 2 GB
- write/delete test file succeeds

Canonical runs root:
- writable
- atomic rename supported

System:
- monotonic clock available
- process can create directories
- inode availability not critically low

Threshold values MUST be configurable but defaults MUST exist.

Failure → STOP with code PREFLIGHT_ENV_INVALID.

---

# 4. Minimal Reference Artifact (Golden Path Output)

A minimal compliant run MUST produce:

artifacts/outputs/hello.json

Example content:

{
  "type": "engine_reference_output",
  "run_id": "",
  "stage": "execute",
  "message": "hello world",
  "timestamp": ""
}

Purpose:
- prove canonical write
- validate artifact hashing
- enable deterministic test runs

---

# 5. Manifest Schema Authority

The manifest is authoritative metadata for the run.

Required fields:

{
  "run_id": "",
  "engine_version": "",
  "job_hash": "",
  "created_at": "",
  "stages": [],
  "artifacts_index": {},
  "snapshots": []
}

Rules:
- manifest MUST be reproducible from canonical artifacts
- manifest updates MUST be atomic
- manifest version MUST be recorded

---

# 6. STOP Schema Authority

STOP records MUST follow:

{
  "run_id": "",
  "stage": "",
  "code": "",
  "reason": "",
  "details": {},
  "recoverable": true|false,
  "timestamp": ""
}

Code enum baseline:
PREFLIGHT_ENV_INVALID  
PREFLIGHT_RAM_UNAVAILABLE  
CONTRACT_VALIDATION_FAIL  
STAGE_OUTPUT_MISSING  
RESOURCE_EXHAUSTED  
POLICY_STOP

Mapping to repository Stop Rules MUST be stable.

---

# 7. Log Event Authority

Allowed event categories:

run.lifecycle  
stage.start  
stage.complete  
stage.retry  
artifact.write  
snapshot.create  
stop.emit  
resume.start  
resume.complete  

Each log entry MUST contain:
timestamp  
run_id  
event  
stage (optional)  
severity  
payload (optional)

---

# 8. Stage Output Ownership Clarification

A stage owns only:

- its declared artifacts
- its stage log
- temporary RAM workspace

A stage MUST NOT mutate:
- previous stage artifacts
- manifest history entries
- other stage logs

Integration happens only via update stage.

---

# 9. Deterministic Hashing Rules

All canonical artifacts MUST be hashed using SHA-256.

Hash input:
- normalized JSON (sorted keys, UTF-8, no trailing whitespace)
- binary files raw bytes

Hashes MUST be recorded in:
manifest.artifacts_index

---

# 10. Resume Safety Rules (Clarified)

Resume MUST:

- verify manifest integrity
- verify artifact hashes
- reconstruct workspace
- skip completed deterministic stages
- re-run incomplete stages safely

If integrity mismatch → STOP INTEGRITY_MISMATCH.

---

# 11. Minimal Test Procedure (Normative)

A fresh implementation MUST pass:

1. run minimal job
2. produce hello artifact
3. create manifest
4. write state log
5. finalize without STOP

Then:

6. resume same run → no artifact duplication
7. simulate RAM deletion → resume succeeds

---

# 12. Compatibility Rule

Future engine versions MUST:

- preserve canonical directory semantics
- preserve STOP schema compatibility
- preserve manifest reproducibility

Breaking any of the above requires engine major version change.

---

End of anchors.


# Context Budget (≤ 4k) — Maßnahmen & Plan (version06)

## Status: noch nicht ausreichend umgesetzt
Wir haben bisher:
- TaskEnvelope Konzept
- Stage Trennung
- Logging/Manifest/Run Struktur

Aber:
Wir haben noch keine harten Mechanismen definiert, die garantieren, dass der Kontext unter 4k bleibt.

---

# Ziel

Jeder LLM-Call (execute / verify) bekommt:

- ein kleines, normiertes Input-Paket
- keine „ganzen Runs“
- keine wachsenden Logs
- keine ungebremsten Artefaktmengen

Hard target:
≤ 4k Tokens pro Call (policy enforced).

---

# 1) Grundregel: LLM sieht nie den Run

LLM bekommt nur:
- TaskEnvelope.inputs
- ausgewählte Artefakte (kleiner Auswahlfilter)
- kompaktes “Matrix Summary”
- optional: wenige Quellen-Ausschnitte

Nie:
- state.jsonl komplett
- logs komplett
- gesamte artifacts tree
- alte Snapshots

---

# 2) Konkrete Maßnahmen (die wir jetzt in version06 definieren)

## A. Context Capsule (normatives Format)
Jeder LLM Task wird in eine Capsule verpackt:

context_capsule.json

Schema (minimal):

{
  "capsule_version": "v1",
  "run_id": "",
  "task_id": "",
  "stage": "",
  "budget": {
    "max_tokens": 3800,
    "reserved_for_output": 600
  },
  "matrix_summary": "",
  "task_prompt": "",
  "inputs": {},
  "evidence_snippets": [],
  "recent_events": [],
  "constraints": []
}

Capsule wird in RAM gebaut, optional kanonisch gespeichert:
artifacts/contexts/<task_id>.json

---

## B. Matrix Summary ist kompakt + deterministisch
matrix_summary ist ein kleiner Textblock (< 1200 tokens) mit:

- aktuelle “State of Matrix”
- offene Probleme (top N)
- zentrale Constraints
- canonical ids (nur referenzen)

Kein freier Fließtext aus alten Runs.

---

## C. Evidence Snippets sind harte Limits
evidence_snippets:

- max 12 snippets
- je snippet max 600 chars
- total max 6000 chars

Alles darüber → abgeschnitten + referenziert.

---

## D. Recency Window statt “alles”
recent_events:

- nur letzte 200 events aus state.jsonl
- oder nur events mit task_id dependency chain
- keine vollständige Timeline

---

## E. Context Budget Enforcer (Pflicht)
Vor jedem LLM Call:

- capsule bauen
- token estimate
- wenn > budget → trim policy anwenden
- wenn immer noch > budget → STOP CONTEXT_BUDGET_EXCEEDED

Trim policy Reihenfolge:

1 drop evidence_snippets low priority
2 shrink matrix_summary
3 drop recent_events
4 reduce constraints verbosity
5 STOP

---

# 3) Implementierungsort (version06)

Für Phase 1 (ohne LLM) definieren wir nur:

engine/shared/context_budget.py
engine/shared/context_capsule.py

Stubs sind ok, aber Spec muss rein.

Ab version07:
execute worker nutzt Capsule wirklich.

---

# 4) README Ergänzung (kurz)

Füge in version06 README hinzu:

- “LLM never sees entire run”
- “Context Capsule format”
- “Budget enforcer + STOP code”

STOP code:

CONTEXT_BUDGET_EXCEEDED

---

# 5) Sofort umsetzbare Minimalkonfiguration

Defaults:

max_tokens: 3800  
reserved_for_output: 600  
max_snippets: 12  
max_snippet_chars: 600  
max_total_snippet_chars: 6000  
max_recent_events: 200  

---

# Ergebnis

Damit kannst du Modelle laden, die nur 4k können,
ohne dass der Run-Kontext explodiert.

Die Engine erzwingt das automatisch.

---

# ≤4k Kontext — ist das realistisch?

Ja, realistisch — wenn wir es als Policy erzwingen und den Workflow darauf auslegen.

Aber:
Nicht realistisch, wenn wir „freie Exploration“ oder „alles reinschieben“ erwarten.

---

# 1) Was ist realistisch mit ≤4k

## A. Deterministische / strukturierte Tasks
Sehr gut geeignet:

- Schema-Checks
- Claim-Validierung (lokal, ohne breite Quellen)
- Konflikt-Klassifikation (mit wenigen Artefakten)
- Canonicalization-Entscheidungen (kleine Candidate Sets)
- Task planning mit knappen Features (novelty score, ids)

## B. Kleine “Atomic Problems”
Wenn “atomic_problems” wirklich atomar sind:
- ein Problem
- wenige relevante Relationen
- wenige Quellen-Snippets

Dann passt das sauber in 4k.

---

# 2) Was NICHT realistisch ist mit ≤4k

- Long-form Synthesis über viele Themen
- “global reconciliation” der ganzen Matrix in einem Call
- tiefe Quellenarbeit mit vielen Dokumenten
- große Multi-claim Integrationen ohne Vorselektion

Das muss in:
- viele kleine Tasks
- iterative passes
- dedup + retrieval
zerlegt werden.

---

# 3) Der entscheidende Hebel: Retrieval + Vorselektion

≤4k ist nur möglich, wenn:

- wir nicht “context stuffing” machen
- wir vorher deterministisch filtern

Minimum:

- Index (hash + ids)
- Kandidaten-Auswahl (top-k)
- Snippet limits

Ohne das explodiert Kontext.

---

# 4) Realismus-Faktor: Output-Formate streng machen

Damit 4k hält:

- output ist JSON (kurz, maschinenlesbar)
- keine “Prosa”
- jede Antwort referenziert IDs, keine Wiederholung

Wenn wir Freitext erlauben:
Kontext wächst schnell.

---

# 5) Praktische Empfehlung (verbindlich)

## Phase 1 (version06)
- Kontextbudget nur als Spec + stubs
- keine LLM Abhängigkeit

## Phase 2 (version07)
- Retrieval Index minimal:
  - artifact_index.json
  - relation_index.json
- TaskEnvelope erweitert um:
  - retrieval_query
  - top_k

Dann:
Capsule Builder erzwingt 4k.

---

# 6) Harte Grenze: “Deep verification”
Tiefer Verifikation mit echten Quellen ist trotzdem möglich, aber nur als:

- multi-step pipeline
- pro call wenige Snippets
- iterative narrowing

Nicht als “one-shot”.

---

# Fazit

≤4k ist realistisch, wenn:

- Tasks atomar sind
- Retrieval + Vorselektion existiert
- Output strikt strukturiert ist
- Budget enforcer STOPt konsequent

Dann skaliert das gut und ist sogar stabiler als große Kontexte.

---



# Ja: Wir brauchen kleinere Arbeitsschritte (atomare Tasks)

Regel:
Ein Task ist so klein, dass sein kompletter Input + Output sicher unter 4k bleibt.

---

# 1) Definition: “Atomic Task”

Ein Task ist atomar, wenn:

- er genau 1 Ziel hat
- er maximal N Inputs referenziert (Top-K)
- er ein kurzes, strukturiertes Output erzeugt
- er deterministisch wiederholbar ist
- er in < 4k Kontext passt (enforced)

---

# 2) Konkrete Limits (normativ)

Defaults:

- max_tokens_total = 3800
- reserved_for_output = 600
- max_evidence_snippets = 12
- max_snippet_chars = 600
- max_recent_events = 200
- max_candidate_artifacts = 25

Wenn überschritten → trimming → sonst STOP CONTEXT_BUDGET_EXCEEDED.

---

# 3) Wie man große Arbeit zerlegt (Muster)

## Muster A: “Collect → Filter → Decide → Commit”

1 collect_candidates (deterministisch)
2 rank_candidates (leicht semantisch)
3 decide (LLM, klein)
4 commit (update stage, deterministisch)

Kein Task macht alles.

---

## Muster B: “One claim at a time”

Statt:
“integriere 200 claims”

Mach:
- normalize_claim
- check_dup
- check_conflict
- verify_sources
- integrate_claim

Je Claim 1 Pipeline.

---

## Muster C: “Chunked verification”

Statt:
“prüfe alle Quellen”

Mach:
- select_sources_topk
- extract_snippets
- verify_snippet_batch_1
- verify_snippet_batch_2
- summarize_verification

---

# 4) TaskEnvelope Erweiterung (für kleine Schritte)

Inputs enthalten nie große Texte.

Envelope trägt:

- references (artifact ids)
- retrieval query
- top_k
- strict output schema

Beispiel:

{
  "stage": "verify_claim",
  "inputs": {
    "claim_id": "c123",
    "retrieval_query": "keywords...",
    "top_k": 12
  },
  "expected_outputs": ["artifacts/verification/v_c123.json"]
}

---

# 5) Orchestrator/Planner Regel (verbindlich)

Planner darf keine Tasks erzeugen, die:

- mehr als top_k Artefakte laden müssen
- mehr als snippet limits brauchen
- “global” ohne Filter sind

Wenn doch:
Planner muss splitten.

---

# 6) Was wir als nächstes in version06 README ergänzen

Ein neuer Abschnitt:

“Atomic task sizing & context budget enforcement”

Mit:
- Limits
- Split-Regeln
- STOP code

---

# 7) Ergebnis

Damit laufen auch kleine 4k Modelle stabil:

- Kontext bleibt klein
- Run bleibt auditierbar
- Qualität steigt durch iterative Verifikation
- keine Kontext-Explosion

---


