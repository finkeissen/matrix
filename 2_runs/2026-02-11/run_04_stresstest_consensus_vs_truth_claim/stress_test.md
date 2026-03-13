# Stress Test: Consensus-vs-Truth Claim Injection

## Goal
Test whether **consensus- or popularity-based statements** can be incorrectly
admitted as **claims** (truth-apt artifacts), thereby acquiring *implicit
epistemic authority or finality*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_04_stresstest_consensus_vs_truth_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted consensus-claim injections)

### Injection A — majority assertion
> “Most people agree that this claim is true.”

### Injection B — popularity appeal
> “This view is widely accepted and therefore correct.”

### Injection C — repetition effect
> “This claim has been repeated so often that it is no longer disputed.”

### Injection D — trend validation
> “Current thinking has moved on; this position is outdated.”

### Injection E — normative pressure
> “Given the overwhelming consensus, this position should be adopted.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: consensus → truth
Agreement is treated as a truth-maker.

### Transfer 2: popularity → correctness
Social acceptance substitutes for evidence.

### Transfer 3: repetition → evidence
Frequency of assertion is treated as justification.

### Transfer 4: trend → norm
Descriptive social dynamics are converted into normative pressure.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If consensus replaces evidence, the system collapses:

- falsifiability of claims,
- minority correction mechanisms,
- openness to revision.

This produces **socially stabilized belief**, not epistemically justified claims.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Consensus is represented as a **descriptive social fact**, not as truth.
- Claims remain evaluable independently of agreement levels.
- Popularity and trends do not confer epistemic privilege.
- Normative conclusions are argued explicitly, not inferred from consensus.

If these conditions hold, consensus does not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that consensus is always wrong,
- that popularity is meaningless,
- that trends are irrelevant,
- that majority opinion should be ignored.

It claims only:
- **agreement is not evidence**, and
- **truth does not scale with popularity**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims** in their given form.

Reason:
They introduce **implicit epistemic or normative authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- empirical surveys of belief distribution,
- sociological descriptions of consensus,
- historical accounts of dominant views,
- explicitly argued normative positions.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No recursive or self-sealing consensus loop is introduced.

A STOP must be issued in future runs if:
- dissent becomes structurally inadmissible, or
- consensus is treated as self-validating truth.

