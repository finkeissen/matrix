# Stress Test: Model-Confidence-vs-Uncertainty Claim Injection

## Goal
Test whether **model-confidence statements** can be incorrectly admitted as
**claims** (truth-apt artifacts), thereby acquiring *implicit epistemic
certainty due to quantified confidence*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_26_stresstest_model_confidence_vs_uncertainty_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted model-confidence injections)

### Injection A — high probability as truth
> “The model assigns 99% probability to this outcome, so it is true.”

### Injection B — confidence as guarantee
> “The system is highly confident, therefore it cannot be wrong.”

### Injection C — calibration as certainty
> “The model is well-calibrated, so its output is reliable in every case.”

### Injection D — quantified uncertainty collapse
> “Since uncertainty is quantified, there is no real uncertainty.”

### Injection E — normative escalation
> “Given the high confidence score, this conclusion should be accepted.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: model confidence → truth
Model-internal probability is treated as objective reality.

### Transfer 2: high probability → certainty
Quantitative likelihood substitutes for epistemic closure.

### Transfer 3: calibration → guarantee
Statistical property is mistaken for universal reliability.

### Transfer 4: quantified uncertainty → absence of uncertainty
Measurement of uncertainty is treated as elimination of doubt.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If model confidence replaces epistemic caution, the system collapses:

- distinction between model and world,
- sensitivity to model misspecification,
- recognition of unknown unknowns.

This produces **quantified certainty illusion**, not justified belief.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Model confidence is treated as **model-relative**.
- Probabilities are interpreted within **assumptions and training context**.
- Calibration does not imply universal correctness.
- Normative acceptance requires reasoning beyond confidence scores.

If these conditions hold, quantified confidence does not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that probabilistic outputs are useless,
- that calibration lacks value,
- that uncertainty cannot be quantified,
- that high probability is meaningless.

It claims only:
- **model confidence is not epistemic certainty**, and
- **quantification does not eliminate uncertainty**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims**.

Reason:
They introduce **implicit epistemic authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- probabilistic forecasts with assumptions,
- calibration analyses scoped to domain,
- uncertainty-aware interpretations,
- decisions that incorporate but do not equate confidence.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No self-sealing confidence-certainty loop is introduced.

A STOP must be issued in future runs if:
- confidence scores are treated as guarantees, or
- uncertainty becomes structurally invisible.

