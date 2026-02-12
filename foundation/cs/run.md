# Foundation Run: Computer Science Core (v1)

## Scope

This run defines the **minimal computational primitives**
permitted in downstream artefacts.

It does not provide implementations.
It does not guarantee computability or efficiency.
It defines **when computational reasoning must STOP**.

---

## Definitions

**D1: Algorithm**  
An algorithm is a finite, explicit, and unambiguous procedure
that maps inputs to outputs under defined rules.

**D2: Input / Output Specification**  
An input/output specification defines the admissible input space,
output space, and the conditions under which the algorithm operates.

**D3: Data Structure**  
A data structure is an explicit organization of data
with defined access and update operations.

**D4: Computational Model**  
A computational model specifies the abstract machine
under which an algorithm is interpreted.

**D5: Complexity Measure**  
A complexity measure characterizes resource usage
(time, space, steps) relative to input size.

---

## Constraints

**C1 (Forbidden – Implicit computability)**  
Assuming that a task is computable without specifying an algorithm
or computational model is forbidden.

**C2 (Forbidden – Implicit efficiency)**  
Claims about speed, scalability, or feasibility
without an explicit complexity measure are invalid.

**C3 (Invalid – Model ambiguity)**  
Algorithms without a declared computational model
trigger STOP.

**C4 (Invalid – Pseudocode authority)**  
Pseudocode is not evidence of correctness or feasibility.

**C5 (Invalid – Optimization claims)**  
Claims of optimality or efficiency without a defined objective
and complexity analysis are invalid.

---

## Minimal Valid Example

**Example:**  
“Given input list L of size n,
algorithm A scans L once and outputs the maximum element.”

- Input defined
- Output defined
- Algorithm finite and explicit
- Complexity claim limited to linear scan

Admissible.

---

## Minimal Invalid Example (Triggers STOP)

**Example:**  
“The system efficiently computes the optimal solution.”

STOP reasons:
- No algorithm specified
- No computational model
- No complexity measure
- ‘Efficient’ and ‘optimal’ used as authority terms

→ **STOP + GAP**  
(Gap: missing algorithmic specification and complexity constraints)

---

## STOP Triggers (Computer Science)

STOP immediately and record a Gap (or reject) if:

- Computability is assumed without an algorithm.
- Efficiency or scalability is asserted without complexity measures.
- Algorithms are described informally or ambiguously.
- Optimization is referenced without explicit objectives.
- Feasibility is inferred from intuition or precedent.

Default action: **STOP + GAP**, not implementation pressure.

---

## Occam Application

When multiple computational formulations are admissible:

- Prefer the formulation with:
  - simpler algorithms,
  - fewer data structures,
  - weaker computational assumptions.

Example:
- Preferred: single-pass algorithm
- Rejected (unless justified): multi-stage optimization pipeline

Additional machinery without necessity becomes a **Gap**, not a feature.

---

## Mapping Rules

Computational primitives map to matrix artefacts as follows:

- **Algorithm**
  - required fields:
    - `input_specification`
    - `output_specification`
    - `procedure_description`

- **Computational Model**
  - required fields:
    - `model_type` (e.g. abstract machine class)
    - `assumptions`

- **Complexity**
  - required fields:
    - `resource_type`
    - `complexity_class`
    - `input_size_parameter`

No computational artefact may enter `3.commit`
without explicit algorithmic and complexity declarations.

---

## Outcome of This Run

This run produces:
- admissible computational primitives,
- explicit STOP conditions for algorithmic claims,
- no implementations,
- no performance guarantees,
- no optimization endorsement.

Absence, Gap, or Silence are valid final states.

