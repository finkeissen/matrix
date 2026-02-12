# Foundation Run: Mathematical Structures Core (v1)

## Scope

This run defines the **minimal mathematical primitives**
permitted in downstream artefacts.

It does not prove theorems.
It does not introduce advanced mathematics.
It defines **which structures are allowed by default
and when mathematical reasoning must STOP**.

---

## Definitions

**D1: Set**  
A set is a collection of distinct elements defined by explicit membership criteria.

**D2: Element**  
An element is a member of a set under the set’s membership rule.

**D3: Relation**  
A relation is a defined association between elements of one or more sets.

**D4: Function**  
A function is a relation that assigns **exactly one** output element
to each input element within a specified domain.

**D5: Structure**  
A structure is a set together with one or more relations or functions
defined on it.

---

## Constraints

**C1 (Forbidden – Undefined domains)**  
Sets without explicit membership criteria are invalid.

**C2 (Forbidden – Implicit structure upgrade)**  
Introducing topology, metric, order, continuity, or algebraic structure
without explicit definition triggers STOP.

**C3 (Invalid – Function misuse)**  
Relations that do not assign exactly one output per input
must not be treated as functions.

**C4 (Invalid – Mathematical authority)**  
Referencing mathematical results, intuitions, or “well-known facts”
without explicit structure definition is invalid.

---

## Minimal Valid Example

**Example:**  
“Let S be the set of recorded observations.
Define a relation R ⊆ S × S such that (a, b) ∈ R
if observation a precedes observation b in time.”

- Set defined
- Relation explicitly specified
- No hidden structure assumed

Admissible.

---

## Minimal Invalid Example (Triggers STOP)

**Example:**  
“Let the system state vary continuously over time.”

STOP reasons:
- Continuity assumed without topology
- Time structure not defined
- Implicit metric introduced

→ **STOP + GAP**  
(Gap: missing definition of mathematical structure supporting continuity)

---

## STOP Triggers (Mathematical Structures)

STOP immediately and record a Gap (or reject) if:

- A mathematical concept is used without defining its structure.
- Additional structure is assumed implicitly.
- Functions are inferred from relations without justification.
- Optimization or minimization is invoked without a defined objective space.
- Limits, continuity, or convergence are referenced without topology.

Default action: **STOP + GAP**, not structural escalation.

---

## Occam Application

When multiple mathematical representations are admissible:

- Prefer the representation with:
  - fewer primitives,
  - weaker structure,
  - fewer assumed properties.

Example:
- Preferred: set + relation
- Rejected (unless required): metric space + continuous function

Unnecessary mathematical strength becomes a **Gap**, not a default.

---

## Mapping Rules

Mathematical primitives map to matrix artefacts as follows:

- **Set**
  - required fields:
    - `elements_definition`
    - `membership_criteria`

- **Relation**
  - required fields:
    - `domain`
    - `codomain`
    - `relation_rule`

- **Function**
  - required fields:
    - `domain`
    - `codomain`
    - `mapping_rule`

Any artefact implying additional structure
must explicitly declare it or trigger STOP.

---

## Outcome of This Run

This run produces:
- admissible mathematical primitives,
- explicit structural boundaries,
- STOP conditions for implicit mathematics,
- no derived results,
- no optimization or proof obligations.

Absence, Gap, or Silence are valid final states.

