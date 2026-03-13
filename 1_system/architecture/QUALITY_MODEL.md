# Quality Model

Quality is **constraint satisfaction under declared policy**.
It is not truth.

---

## 1) Constraints
Constraints are versioned artifacts that evaluate records and emit:
- violations/warnings,
- review items,
- optional STOP recommendations.

Constraints are scoped (which types, which contexts).

---

## 2) Status labels (recommended)
- `draft`
- `needs_review`
- `validated` (relative to a policy set)
- `deprecated`

Validated means: validated under policy P and scope S.

---

## 3) Review queues
Review queues are artifacts, not assignments.
They are produced whenever:
- evidence is missing,
- confidence is low,
- conflicts exist,
- completeness thresholds fail.

---

## 4) STOP
STOP is explicit and policy-driven.
It blocks downstream modules but does not rewrite history.
