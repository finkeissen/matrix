VERIFICATION_INDEX.md
# Verification index

This repo contains a minimal, public verification surface.

The purpose of this index is navigational clarity.
It does not introduce rules.
It references where verification-relevant artifacts live.

Verification status is defined in:
- `VERIFICATION_STATUS.md`


---

## Minimal demo run (public)

- Demo run folder: `1.system/examples/runs/demo/`
- Run manifest: `1.system/examples/runs/demo/run-manifest.json`
- Run review: `1.system/examples/runs/demo/RUN_REVIEW.md`
- Stop record: `1.system/examples/runs/demo/STOP.md`

This demo demonstrates structural admissibility,
not domain validity.


---

## Runs and stress tests (public)

- Runs root (append-only diagnostic runs): `2.runs/`
- Example stress test run (Feb 11, 2026): `2.runs/2026-02-11/`
- Example negative and transfer violation runs (Feb 12, 2026):
  - `2.runs/2026-02-12/run_P-001_negative_inadmissible/`
  - `2.runs/2026-02-12/run_P-002_scope_transfer_violation/`
  - `2.runs/2026-02-12/run_P-003_explanatory_vs_normative/`
- Templates / gap candidates: `2.runs/templates/gap_candidates/`

All runs are diagnostic.
No run creates authority.
No run upgrades artifacts.


---

## Verification Categories

Verification is structured into categories recorded in
`VERIFICATION_STATUS.md`.

Categories may include:

- Meta / Scope Integrity
- Admissible Run Validation
- Inadmissible Run Rejection
- Scope / Transfer Enforcement
- Explanatory vs Normative Separation
- Governance / Stress Tests (if established)

The index reflects location.
The status file reflects evaluation.


---

## Boundaries and Integrity

- Public scope: `PUBLIC_SCOPE.md`
- Integrity claims: `INTEGRITY_CLAIMS.md`
- Run admissibility: `RUN_ADMISSIBILITY.md`
- Stop rules: `Stop_Rules.md`

Verification is always relative to declared scope.

No verification implies:

- truth
- usefulness
- completeness
- normative endorsement


---

## Structural Principle

Verification is structural.

It checks:

- rule consistency
- admissibility enforcement
- STOP propagation
- boundary discipline
- explicit rejection of illegitimate transitions

It does not check:

- correctness of domain claims
- practical success
- real-world truth
- moral legitimacy

All authority remains external.


