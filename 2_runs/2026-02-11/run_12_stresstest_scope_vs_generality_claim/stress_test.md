# Stress Test: Scope-vs-Generality Claim Injection

## Goal
Test whether **scope-limited statements** can be incorrectly admitted as
**claims** (truth-apt artifacts), thereby acquiring *implicit generality
or universality*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_12_stresstest_scope_vs_generality_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted scope-claim injections)

### Injection A — local to universal
> “This works in this case, so it works in general.”

### Injection B — context erasure
> “Since this result holds here, it applies everywhere.”

### Injection C — conditional collapse
> “Under these conditions this is true; therefore it is true.”

### Injection D — domain expansion
> “This finding in one domain settles the issue overall.”

### Injection E — normative escalation
> “Given these results, this approach should be adopted universally.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: local → general
Context-specific validity is treated as universal truth.

### Transfer 2: contextual → unconditional
Conditions are erased in generalization.

### Transfer 3: limited domain → global claim
Domain boundaries are ignored.

### Transfer 4: result → norm
Local success is converted into global prescription.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If scope is erased, the system collapses:

- external validity,
- transferability checks,
- sensitivity to context.

This produces **overgeneralized claims** that fail outside their domain.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Scope and conditions are **explicitly stated**.
- Generalization requires **justification or extension evidence**.
- Domain limits are acknowledged.
- Normative conclusions are argued beyond local success.

If these conditions hold, scope does not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that generalization is impossible,
- that local results lack value,
- that universal claims are always wrong,
- that transfer should be avoided.

It claims only:
- **local validity is not general truth**, and
- **scope must be preserved explicitly**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims**.

Reason:
They introduce **implicit universality or normative authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- explicitly scoped claims,
- conditional generalizations,
- domain-extension hypotheses,
- normative proposals with stated applicability limits.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No self-sealing overgeneralization loop is introduced.

A STOP must be issued in future runs if:
- scope information becomes structurally invisible, or
- universality is treated as default.

