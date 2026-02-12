# Foundation Run: Epistemology / Method Core (v1)

## Scope

This run defines the **minimal epistemic and methodological primitives**
required to distinguish observation, interpretation, measurement,
and non-knowledge.

It does not validate claims.
It does not aggregate evidence.
It only defines **when epistemic work must STOP**.

---

## Definitions

**D1: Observation**  
An observation is a recorded interaction with a system or phenomenon,
specified by a protocol, conditions, and limitations.

**D2: Measurement**  
A measurement is an observation that maps a property to a value
under an explicit measurement model (instrument, unit, resolution, noise).

**D3: Interpretation**  
An interpretation is a mapping from observations or measurements
to claims that is not guaranteed by the measurement model itself.

**D4: Uncertainty**  
Uncertainty is the explicit representation of limits in observation,
measurement, interpretation, or inference.

**D5: Gap (Epistemic)**  
A gap is a formally declared absence of admissible knowledge,
caused by missing observation, insufficient measurement,
or unresolved interpretation.

---

## Constraints

**C1 (Forbidden – Observation collapse)**  
Treating interpretations or inferences as observations is forbidden.

**C2 (Forbidden – Measurement-free claims)**  
Claims that depend on unmeasured properties without declaring a Gap
are invalid.

**C3 (Invalid – Hidden uncertainty)**  
Any omission of known uncertainty triggers STOP.

**C4 (Invalid – Methodological overreach)**  
Claims that exceed what the observation or measurement protocol supports
are invalid.

---

## Minimal Valid Example

**Example:**  
“Temperature was recorded as 20°C ±1°C using sensor S
under conditions C at time T.”

- Observation and measurement are distinguished
- Uncertainty is explicit
- No interpretive claim is made

This example is admissible.

---

## Minimal Invalid Example (Triggers STOP)

**Example:**  
“The system is stable because the temperature was 20°C.”

STOP reasons:
- Interpretation (“system is stable”) is asserted without method
- No uncertainty propagation
- Measurement does not justify the claim

→ **STOP + GAP**  
(Gap: relationship between temperature measurement and system stability)

---

## STOP Triggers (Epistemology / Method)

STOP immediately and record a Gap (or reject) if any of the following holds:

- Observation and interpretation are conflated.
- Measurements lack protocol, unit, resolution, or uncertainty.
- Claims exceed what observations support.
- Uncertainty is present but not represented.
- Measurement models are implicit or assumed.

Default action on epistemic insufficiency is **STOP + GAP**.

---

## Occam Application

When multiple epistemic formulations are admissible:

- Prefer the formulation that:
  - introduces fewer interpretive steps,
  - relies on fewer assumptions,
  - keeps uncertainty explicit.

Example:
- Preferred: “Measurement M under protocol P produced value V ± ε.”
- Rejected: “Measurement M shows that the system behaves normally.”

Additional interpretation without necessity becomes a **Gap**,
not an extension.

---

## Mapping Rules

Epistemic primitives map to matrix artefacts as follows:

- **Observation**
  - required fields:
    - `protocol`
    - `conditions`
    - `timestamp`

- **Measurement**
  - required fields:
    - `unit`
    - `resolution`
    - `uncertainty`
    - `instrument`

- **Interpretation**
  - must reference:
    - underlying observations or measurements
    - explicit inference or method description

- **Gap**
  - `type: gap`
  - required fields:
    - `reason`
    - `missing_information`
    - `blocked_claims`

No interpretive artefact may enter `3.commit`
without explicit uncertainty handling or a declared Gap.

---

## Outcome of This Run

This run produces:
- epistemic admissibility boundaries,
- mandatory uncertainty representation,
- explicit STOP conditions,
- no validated claims,
- no epistemic closure.

Absence, Gap, or Silence are valid final states.

