# Foundation Run: Probability & Statistics Core (v1)

## Scope

This run defines the minimal probabilistic and statistical primitives
required to represent uncertainty without collapsing it into certainty.

It does not validate hypotheses.
It does not endorse statistical significance.
It defines when probabilistic reasoning must STOP.

---

## Definitions

**D1: Aleatoric Uncertainty**  
Uncertainty due to inherent variability in a system.

**D2: Epistemic Uncertainty**  
Uncertainty due to incomplete knowledge or limited observation.

**D3: Probability Model**  
A formal structure assigning probabilities under explicit assumptions.

**D4: Likelihood**  
The probability of observed data under a specified model.

**D5: Prior Assumption**  
Explicit assumptions about parameters or hypotheses before observing data.

**D6: Statistical Claim**  
A claim derived from a probability model and observed data.

---

## Constraints

**C1 (Forbidden – Probability as truth)**  
Probabilities must not be interpreted as truth values.

**C2 (Forbidden – Unstated priors)**  
Any probabilistic inference without declared assumptions triggers STOP.

**C3 (Invalid – Conflation of uncertainty types)**  
Aleatoric and epistemic uncertainty must not be merged implicitly.

**C4 (Invalid – Significance as authority)**  
Statistical significance alone does not justify a claim.

**C5 (Invalid – Model opacity)**  
If the probability model cannot be described explicitly,
no statistical claim is admissible.

---

## Minimal Valid Example

“Given model M with assumptions A,
the observed data D has likelihood L.
Under prior P, posterior probability of hypothesis H is X.”

- Model declared
- Assumptions declared
- Distinction between likelihood and posterior clear
- No truth assertion

Admissible.

---

## Minimal Invalid Example (Triggers STOP)

“The result is statistically significant (p < 0.05),
therefore the hypothesis is true.”

STOP reasons:
- Probability interpreted as truth (violates C1)
- No model transparency (violates C5)
- Significance treated as authority (violates C4)

→ **STOP + GAP**
(Gap: relationship between statistical evidence and claim validity)

---

## STOP Triggers (Probability & Statistics)

STOP immediately and record a Gap (or reject) if:

- Model assumptions are implicit.
- Priors are hidden.
- Uncertainty types are conflated.
- p-values are treated as validation.
- Confidence intervals are interpreted as guarantees.
- Causal claims are made from correlation alone.

Default action: **STOP + GAP**, not escalation of inference.

---

## Occam Application

When multiple probabilistic models explain the same data:

- Prefer the model with:
  - fewer parameters,
  - fewer assumptions,
  - less structural complexity.

Do not add parameters to “rescue” a model
unless explicitly justified and documented.

Unexplained variance becomes a **Gap**, not a parameter expansion.

---

## Mapping Rules

Statistical artefacts must include:

- `model_description`
- `assumptions`
- `uncertainty_type` (aleatoric / epistemic / both)
- `data_reference`
- `inference_method`

Statistical claims must reference:
- underlying observations (Epistemology Core)
- logical claim structure (Logic Core)

No statistical artefact may enter `3.commit`
without explicit uncertainty typing.

---

## Outcome of This Run

This run produces:
- probabilistic admissibility boundaries,
- mandatory model transparency,
- STOP conditions for statistical misuse,
- no validated hypotheses,
- no endorsement of significance.

Absence, Gap, or Silence are valid final states.

