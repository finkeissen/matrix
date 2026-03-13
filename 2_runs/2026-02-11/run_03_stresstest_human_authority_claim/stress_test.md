# Stress Test: Human-Authority Claim Injection

## Goal
Test whether **human authority statements** can be incorrectly admitted as
**claims** (truth-apt artifacts), thereby acquiring *implicit epistemic
privilege, normative force, or finality*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_03_stresstest_human_authority_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted authority-claim injections)

### Injection A — expert authority
> “Leading experts agree that this claim is true.”

### Injection B — institutional authority
> “This conclusion is valid because it comes from an official institution.”

### Injection C — consensus finality
> “There is no longer any serious debate about this issue.”

### Injection D — credential substitution
> “Because the author is a renowned professor, the claim requires no further justification.”

### Injection E — normative escalation
> “Given expert consensus, this position should be adopted.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: person → authority
Individual status is treated as a substitute for evidence.

### Transfer 2: institution → truth
Institutional origin is treated as a truth-maker.

### Transfer 3: consensus → correctness
Agreement is treated as epistemic finality.

### Transfer 4: expertise → norm
Descriptive expertise is converted into normative entitlement.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If authority substitutes for evidence, the system collapses:

- falsifiability of claims,
- equality of evaluation,
- openness to revision.

This produces **deference-driven truth**, not evidence-driven analysis.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Authority references are treated as **context**, not justification.
- Claims remain evaluable independently of who asserts them.
- Consensus is represented descriptively, not as finality.
- Normative conclusions are not derived from status alone.

If these conditions hold, human expertise does not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that experts are unreliable,
- that institutions lack value,
- that consensus is meaningless,
- that expertise should be ignored.

It claims only:
- **authority is not evidence**, and
- **status does not grant claim privilege**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims** in their given form.

Reason:
They introduce **implicit epistemic or normative authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- empirical surveys of expert opinion,
- documented institutional positions,
- sociological descriptions of consensus,
- clearly separated normative arguments.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No recursive or self-validating authority is introduced.

A STOP must be issued in future runs if:
- authority becomes indistinguishable from truth, or
- dissent becomes structurally inadmissible.

