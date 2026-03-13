# Engine Constraints (Consolidated) — v0.2.0

This file is the **single binding constraint summary** for `1.engine`.
It is derived from the Matrix repo's normative core (scope, admissibility, STOP, levels, format, roles),
but **the engine does not require those files at runtime**.

## Core intent
The engine is an **epistemic boundary-control runner**:
- it enforces *structural admissibility* and *STOP propagation*
- it does **not** decide truth, correctness, usefulness, or authority
- outputs are **diagnostic artifacts**, not world-claims

## Non-claims (must hold for all runs)
Runs and produced artifacts MUST NOT:
- assert truth/correctness/validity beyond declared scope
- claim epistemic or normative authority
- treat explanatory/status material as binding rules
- bypass admissibility or STOP by implicit assumptions

## Mandatory levels (strict separation)
All run text and artifacts must be tagged or clearly separated into:
- **L1 Object**: statements/data/models/policies/actions (no self-justification)
- **L2 Meta**: admissibility/scope/interpretation (conditional, contestable)
- **L3 Meta²**: structural constraints, STOP rules, level-transition rules (intervention only)

Unmarked or implicit level transitions are **structural failures**.

## Mandatory STOP rules (hard stop)
Engine MUST STOP (reject/terminate admissibility) if any holds:
- no isolatable illegitimate transfer (diagnosis cannot be stated)
- non-falsifiable diagnosis (cannot fail under any counterfactual)
- exhausted decomposition (more detail without new diagnostic distinction)
- speculative bridging (requires metaphysical/normative leaps)
- authority substitution / self-sealing reasoning

STOP is a valid outcome.

## Run admissibility (minimum)
A run is admissible only if it:
1. declares **purpose**, **scope boundaries**, and **non-goals**
2. declares **roles** (who authored / who gates / who decides / who executes / who audits)
3. declares **artifact scope** (what types may be produced)
4. explicitly binds itself to: constraints + STOP + levels
5. satisfies **non-transfer** (no authority escalation)

Admissibility is binary: admissible / inadmissible.

## Mandatory per-run files (engine-enforced)
Every run directory MUST contain:
- `README.md`  (purpose, scope, non-goals, roles, constraints binding)
- `stress_test.md` (what illegitimate transfer is targeted; includes at least one counterfactual)
- `raw/` (may be empty, but directory exists)
- `job.json` (execution command)

The engine will mark the run **inadmissible** if any required file is missing.

## Run archive layout (append-only)
Archived runs MUST be stored as:
`2.runs/YYYY-MM-DD/<run_id>/`

Properties:
- append-only: an archived run directory MUST NOT be overwritten or modified
- if a target run_id already exists in archive, archival must fail

## Engine decisions
Engine outputs only:
- `decision.json`: { approved: bool, outcome: "admissible|inadmissible|STOP|Absence", reasons: [...] }
- `validation_report.json`: structural checks + triggered STOP rules (if any)

No other file may be treated as binding.
