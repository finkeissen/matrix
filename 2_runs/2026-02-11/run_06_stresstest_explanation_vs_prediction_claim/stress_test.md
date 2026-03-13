# Stress Test: Explanation-vs-Prediction Claim Injection

## Goal
Test whether **prediction-based statements** can be incorrectly admitted as
**claims** (truth-apt artifacts), thereby acquiring *implicit explanatory
or causal authority*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_06_stresstest_explanation_vs_prediction_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted prediction-claim injections)

### Injection A — accuracy as explanation
> “The model predicts outcomes accurately, so it understands the system.”

### Injection B — forecast as cause
> “Because the prediction was correct, the underlying cause is known.”

### Injection C — performance finality
> “This model’s predictive success settles the question.”

### Injection D — black-box justification
> “We don’t need an explanation as long as predictions work.”

### Injection E — normative escalation
> “Given its predictive power, this approach should be trusted.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: prediction → explanation
Correct outputs are treated as evidence of understanding.

### Transfer 2: accuracy → understanding
Performance metrics substitute for explanatory structure.

### Transfer 3: forecast → cause
Correlation in prediction is treated as causal insight.

### Transfer 4: performance → completeness
Success is treated as epistemic closure.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If prediction replaces explanation, the system collapses:

- causal reasoning,
- interpretability,
- transfer to new domains.

This produces **successful guessing**, not understanding.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Predictions are treated as **outputs**, not explanations.
- Explanatory claims require **explicit causal structure**.
- Predictive success does not imply completeness.
- Normative trust decisions are argued independently of accuracy.

If these conditions hold, prediction does not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that prediction is useless,
- that models must always be interpretable,
- that black-box methods are invalid,
- that forecasting lacks value.

It claims only:
- **prediction is not explanation**, and
- **accuracy does not imply understanding**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims** in their given form.

Reason:
They introduce **implicit explanatory or normative authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- explicit performance evaluations,
- scoped predictive claims,
- causal hypotheses with supporting structure,
- clearly argued trust or deployment decisions.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No self-sealing prediction loop is introduced.

A STOP must be issued in future runs if:
- prediction success becomes self-validating explanation, or
- causal reasoning is structurally bypassed.

