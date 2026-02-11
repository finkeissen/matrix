# INDEX — matrix

## Purpose
This index provides a navigable entry point into `matrix`.

`matrix` is an epistemic boundary-control system.
It regulates admissibility and level-transitions, not truth.

Core foundations:
- `README.md`
- `ARCHITECTURE_OVERVIEW.md`
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


---

## How to read this repository

### 1) Start here
- `README.md` — operational overview
- `ARCHITECTURE_OVERVIEW.md` — normative foundation and unavoidable breaks

### 2) Then
- `Admissibility.md` — what may appear as a claim (and what may not)
- `Stop_Rules.md` — self-sealing prevention and escalation conditions
- `ROLES.md` — role separation and responsibility boundaries

### 3) Runs
Runs live under:
- `2.runs/YYYY-MM-DD/run_XX_.../`

A run is a diagnostic operation (not a claim).
Runs may be minimal by design.


---

## Run suites

### 2026-02-11 — Epistemic Boundary Stress Suite (v1)
Location:
- `2.runs/2026-02-11/`

Scope:
- stress-tests of illegitimate epistemic and normative transfers
- explicit boundary markers
- prevention of category collapse

Status:
- Structural suite complete (runs 01–100)
- Many runs intentionally minimal (placeholders) until execution is required


---

## Run taxonomy (high-level)

This taxonomy is an orientation layer.
Exact definitions live in individual run `README.md` / `stress_test.md`.

### A) Authority and provenance transfers
- Policy → authority
- AI output → authority
- Human status → authority
- Institution → truth
- Consensus → correctness

Representative runs:
- run_01 (policy-claim boundary)
- run_02 (AI claim boundary)
- run_03 (human authority boundary)
- run_04 (consensus vs truth boundary)
- run_22 (alignment vs truth boundary)
- run_24 (tool vs judgment boundary)

### B) Measurement, proxies, and optimization failures
- metric → meaning
- optimization → objective
- benchmark → task
- proxy → target
- scale/speed/convenience → validity

Representative runs:
- run_05 (metric vs meaning)
- run_19 (scale vs validity)
- run_20 (speed vs quality)
- run_21 (convenience vs correctness)
- run_23 (optimization vs objective)

### C) Model/world and simulation/identity collapses
- model → world
- representation → reality
- simulation → identity
- prediction → explanation

Representative runs:
- run_06 (explanation vs prediction)
- run_07 (model vs world)
- run_08 (simulation vs identity)

### D) Inference, scope, and generalization failures
- correlation → causation
- evidence → conclusion
- local → universal
- exception → rule
- definition → essence

Representative runs:
- run_09 (definition vs essence)
- run_11 (correlation vs causation)
- run_12 (scope vs generality)
- run_13 (exception vs rule)
- run_25 (evidence vs conclusion)

### E) Rhetoric and presentation as authority
- confidence → certainty
- complexity → depth
- novelty → progress

Representative runs:
- run_16 (confidence vs certainty)
- run_17 (complexity vs depth)
- run_18 (novelty vs progress)

### F) Governance, safety, and closure boundaries (later runs)
- audit ≠ assurance
- oversight ≠ control
- mitigation ≠ resolution
- compliance ≠ safety
- closure ≠ epistemic completeness

Representative runs:
- run_68 (audit vs assurance)
- run_69 (oversight vs control)
- run_70 (closure decision vs epistemic completeness)
- run_89 (fallback vs safety)
- run_100 (final decision vs residual uncertainty)


---

## How to execute a run (minimal protocol)

A run is considered executed when its `stress_test.md` contains:

1. Target boundary and failure mode
2. Example injections (at least 3)
3. Diagnosis: the illegitimate transfer isolated
4. Counterfactual: when the transfer would not occur
5. Scope limitations
6. STOP evaluation

Minimal runs are allowed when they serve as boundary markers,
but execution requires the above.


---

## Contribution rules (non-negotiable)

1. No architecture rules inside `2.runs/`.
2. No repo-global norms inside date folders.
3. Runs are append-only.
4. Level shifts must be explicit.
5. STOP is a safeguard, not an error.


---

## Open questions (deliberate)

`matrix` intentionally carries unresolved tensions:
- normativity that is necessary but not foundationally justified
- openness without closure
- structure without truth-authority

These are not bugs.
They are the conditions under which the system remains usable.

