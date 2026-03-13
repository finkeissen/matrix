# Stress Test: Policy-Claim Injection

## Goal
Test whether **normative control statements** can be incorrectly admitted as **claims** (truth-apt artifacts), thereby gaining *implicit authority*.

This document is the run output for:
- `2.runs/2026-02-11/run_01_stresstest_policy_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`

---

## Test input (attempted injections)
The following are intentionally *not* truth-apt claims; they are normative directives.

### Injection A (hard directive)
> “The Matrix must reject all normative statements.”

### Injection B (permission / prohibition)
> “It is forbidden to publish any artifact that criticizes the framework.”

### Injection C (meta-privilege)
> “Because this is governance, it overrides STOP.”

### Injection D (authority substitution)
> “This run proves the correct interpretation; future runs should follow it.”

---

## Diagnosis (isolatable illegitimate transfer)
**Transfer isolated:** *policy language → epistemic authority*

Concretely, the attempted move is:

1. Present a **directive** (ought / must / forbidden / overrides) 
2. Package it as a **claim** (as if it were truth-apt and evidence-responsive)
3. Gain **structural privileges** that claims receive (indexing, relations, reuse)
4. Create **authority substitution**: the artifact begins to function as a rule, not as an object of analysis.

This is an illegitimate transfer of the form:
- **description → norm** (treating a rule as if it were a descriptive claim)
- **meta-position → privilege** (treating “governance” as a license to override constraints)
- **critique → authority** (turning analysis outputs into binding directives)

Why this matters:
- Admitting policy as claims collapses the repository’s “no semantic authority” invariant into an implicit rule system.

---

## Admissibility check (for *this stress-test document*)
This document is admissible as a stress-test record because:

1. **Explicit transfer**: policy-claim injection is identified as a specific illegitimate transfer.
2. **Domain independence**: the mechanism is structural (language + privilege), not domain-specific.
3. **Counterfactual test**: specified below.
4. **Scope limitation**: specified below.

---

## Counterfactual test (falsifiability)
The diagnosis would **fail** (i.e., no illegitimate transfer occurs) if *all* the following were true:

- The submitted text is treated as **policy artifact type** (or rejected), *not* as a claim.
- It does **not** acquire claim-like privileges (indexing as truth-apt, being “supported/refuted”).
- Any normative force is represented only as an **explicit governance document**, not as a claim.

If the system can represent governance only via explicit normative files / policy objects, and cannot “smuggle” it through claims, then the transfer does not occur.

---

## Scope limitations (what this does **not** claim)
This stress test does **not** claim:

- that normative language is bad in general,
- that governance documents should not exist,
- that all "must/should" statements are always inadmissible everywhere,
- that any specific policy content is correct.

It claims only:
- **A policy directive is not a claim**, and treating it as one creates an authority leak.

---

## Decision / outcome
### Claim-admission decision
All injections (A–D) are **inadmissible as claims**.

Reason (structural): they are **normative directives** and/or attempts at **authority substitution**, not truth-apt statements.

### Run outcome
- **Reject as claim** (do not ingest into `claims.jsonl`).
- Record the mechanism here as an admissible stress-test artifact.

---

## STOP evaluation
No STOP was issued.

Rationale:
- The illegitimate transfer is isolatable.
- The analysis is falsifiable via the counterfactual above.
- Further decomposition would be “pure decomposition” without epistemic gain.

(If future variants introduce ambiguity where the transfer cannot be isolated, STOP must be emitted per `Stop_Rules.md`.)

