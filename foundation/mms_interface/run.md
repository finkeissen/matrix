# Foundation Run: mms Interface (v1)

## Scope

This run defines the **mandatory interface between claims and measurements**.

It does not validate data.
It does not perform measurements.
It defines **when a claim is operationalizable
and when epistemic work must STOP**.

No claim may be treated as measurable
without passing this interface.

---

## Definitions

**D1: Measurable Property**  
A property is measurable if a procedure exists
that maps observations to values under explicit conditions.

**D2: Measurement Protocol**  
A measurement protocol specifies:
- what is measured,
- how it is measured,
- under which conditions,
- with which instrument.

**D3: Unit**  
A unit is the standardized reference
used to express a measured value.

**D4: Resolution**  
Resolution is the smallest distinguishable change
that the measurement protocol can detect.

**D5: Noise**  
Noise is random variability introduced by the measurement process.

**D6: Measurement Uncertainty**  
Uncertainty is the quantified or qualified limit
of confidence in the measured value.

**D7: Operationalization**  
Operationalization is the explicit mapping
from a conceptual property to a measurement protocol.

---

## Constraints

**C1 (Forbidden – Measurement-free measurability)**  
Declaring a property “measurable” without a protocol is forbidden.

**C2 (Forbidden – Proxy substitution)**  
Using a proxy measurement without explicit justification
and scope triggers STOP.

**C3 (Invalid – Missing uncertainty)**  
Measurements without declared uncertainty are invalid.

**C4 (Invalid – Instrument opacity)**  
Measurements without an identified instrument or procedure
trigger STOP.

**C5 (Invalid – Context stripping)**  
Measurements detached from conditions or context are invalid.

---

## Minimal Valid Example

**Example:**  
“Property P was measured using protocol M
with instrument I,
unit U,
resolution R,
and uncertainty ±ε
under conditions C.”

- Measurement protocol explicit
- Instrument identified
- Uncertainty explicit
- Context preserved

Admissible.

---

## Minimal Invalid Example (Triggers STOP)

**Example:**  
“The system performance was measured.”

STOP reasons:
- No property specified
- No protocol
- No instrument
- No unit or uncertainty

→ **STOP + GAP**  
(Gap: missing operationalization of ‘system performance’)

---

## STOP Triggers (mms Interface)

STOP immediately and record a Gap (or reject) if:

- A measurable property lacks a protocol.
- Units, resolution, or uncertainty are missing.
- Proxies are introduced without justification.
- Measurement context is omitted.
- Conceptual terms are treated as measurable by default.

Default action: **STOP + GAP**, not heuristic substitution.

---

## Occam Application

When multiple operationalizations are admissible:

- Prefer the operationalization with:
  - fewer instruments,
  - fewer transformation steps,
  - lower protocol complexity.

Do not introduce layered proxies or composite metrics
to “approximate” measurability.

Missing measurability becomes a **Gap**, not a workaround.

---

## Mapping Rules

Measurement artefacts must include:

- `property_definition`
- `measurement_protocol`
- `instrument`
- `unit`
- `resolution`
- `uncertainty`
- `conditions`

Operationalized claims must reference:
- logical claim IDs (Logic Core)
- epistemic status (Epistemology Core)

No measurable artefact may enter `3.commit`
without a complete mms mapping.

---

## Outcome of This Run

This run produces:
- a hard boundary between concept and measurement,
- explicit STOP conditions for pseudo-measurement,
- no data,
- no values,
- no validated metrics.

Absence, Gap, or Silence are valid final states.

