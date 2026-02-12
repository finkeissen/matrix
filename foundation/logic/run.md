# Foundation Run: Logic Core (v1)

## Scope

This run defines the **minimal logical primitives** required for all downstream
claims, relations, and validations.

It does not establish truth.
It does not resolve conflicts.
It only defines **what may be expressed without immediate STOP**.

---

## Definitions

**D1: Claim**  
A claim is a declarative statement with a truth value
that is *in principle* evaluable under explicit conditions.

**D2: Support**  
Support is an explicit relation indicating that one or more claims
are intended to increase the plausibility of another claim.

**D3: Counterexample**  
A counterexample is a claim that, if admissible and valid,
is sufficient to invalidate another claim.

**D4: Contradiction**  
A contradiction exists if two admissible claims
cannot be simultaneously true under the same conditions.

---

## Constraints

**C1 (Forbidden – Non-declarative statements)**  
Imperatives, recommendations, value judgments, or intentions
are not admissible as claims.

**C2 (Forbidden – Implicit premises)**  
Claims that rely on unstated assumptions are invalid.

**C3 (Invalid – Self-referential truth claims)**  
Claims asserting their own truth, validity, or authority are invalid.

**C4 (Invalid – Unscoped generality)**  
Claims using universal quantifiers (“always”, “never”, “all”)
without explicit scope trigger STOP.

---

## Minimal Valid Example

**Claim A:**  
“Under conditions C, system S produces output O.”

- Declarative
- Scoped
- No implicit premises
- No self-reference

This claim is admissible.

---

## Minimal Invalid Example (Triggers STOP)

**Claim B:**  
“This claim is correct.”

STOP reason:
- Violates C3 (self-referential truth claim)
- Cannot be evaluated without circularity

→ **STOP + REJECT**  
(No Gap, because the form itself is forbidden.)

---

## STOP Triggers (Logic)

STOP immediately and record a Gap (or Reject) if any of the following holds:

- A claim cannot be evaluated even in principle.
- A required premise is missing or implicit.
- A contradiction is detected without resolution rules.
- A claim attempts to assert authority, truth, or correctness.
- Universal or existential scope is unclear or missing.

Default action: **STOP + GAP**, unless explicitly forbidden.

---

## Occam Application

When multiple logical formulations are admissible:

- Prefer the formulation with:
  - fewer primitives,
  - fewer assumptions,
  - narrower scope.

Example:
- Preferred: “In context C, X implies Y.”
- Rejected: “X universally and necessarily implies Y in all contexts.”

Unexplained generality becomes a **Gap**, not added structure.

---

## Mapping Rules

Logical primitives map to matrix artefacts as follows:

- **Claim**
  - `type: claim`
  - required fields:
    - `statement`
    - `scope`
    - `conditions`

- **Support**
  - `type: relation`
  - `relation: supports`
  - requires source and target claim IDs

- **Counterexample**
  - `type: claim`
  - `relation: counters`
  - explicit reference to target claim

No artefact may enter `3.commit`
without satisfying these mappings.

---

## Outcome of This Run

This run produces:
- a **logic admissibility boundary**,
- explicit STOP conditions,
- no knowledge claims,
- no resolution of contradictions.

All downstream work is constrained by this boundary.

