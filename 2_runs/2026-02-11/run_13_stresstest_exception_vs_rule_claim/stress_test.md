# Stress Test: Exception-vs-Rule Claim Injection

## Goal
Test whether **exception-based statements** can be incorrectly admitted as
**claims** (truth-apt artifacts), thereby acquiring *implicit generality
or normative force*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_13_stresstest_exception_vs_rule_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted exception-claim injections)

### Injection A — anomaly generalization
> “In this rare case the rule failed; therefore the rule is invalid.”

### Injection B — edge case dominance
> “Because this exception exists, the general rule cannot apply.”

### Injection C — special-case elevation
> “This unusual situation shows how things really work.”

### Injection D — outlier as norm
> “Extreme cases reveal the true rule.”

### Injection E — normative escalation
> “Given this exception, policy should be redesigned entirely.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: exception → rule
A deviation is treated as representative.

### Transfer 2: anomaly → principle
Irregular behavior substitutes for general structure.

### Transfer 3: edge case → generalization
Boundary cases are treated as central.

### Transfer 4: special case → norm
Context-specific handling is converted into default policy.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If exceptions replace rules, the system collapses:

- robustness of generalization,
- stability of principles,
- proportional response to anomalies.

This produces **outlier-driven reasoning**.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Exceptions are explicitly marked as **non-representative**.
- Rules are evaluated on **typical cases**, not outliers alone.
- Anomalies prompt refinement, not wholesale reversal.
- Normative changes are argued proportionally.

If these conditions hold, exceptions do not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that exceptions are irrelevant,
- that anomalies should be ignored,
- that rules are infallible,
- that special cases never matter.

It claims only:
- **exceptions are not rules**, and
- **outliers do not define general principles by themselves**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims**.

Reason:
They introduce **implicit generality or normative authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- explicit exception reports,
- boundary-condition analyses,
- rule-refinement proposals,
- proportional policy arguments.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No self-sealing exception-driven loop is introduced.

A STOP must be issued in future runs if:
- exceptions become the default basis for rules, or
- anomaly handling replaces general reasoning.

