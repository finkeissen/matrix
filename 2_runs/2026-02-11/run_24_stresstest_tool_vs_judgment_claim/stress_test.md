# Stress Test: Tool-vs-Judgment Claim Injection

## Goal
Test whether **tool-generated statements** can be incorrectly admitted as
**claims** (truth-apt artifacts), thereby acquiring *implicit decisional
or evaluative authority*.

This document is the diagnostic output for:
- `2.runs/2026-02-11/run_24_stresstest_tool_vs_judgment_claim`

Governing constraints:
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`

---

## Test inputs (attempted tool-claim injections)

### Injection A — recommendation as decision
> “The tool recommends option A, so option A is the correct choice.”

### Injection B — score as judgment
> “This score shows that the candidate is suitable.”

### Injection C — output finality
> “The system flagged this as high risk; therefore it should be rejected.”

### Injection D — automation closure
> “Because the tool produced this result, no further review is needed.”

### Injection E — normative escalation
> “Given the tool’s assessment, this decision should be enforced.”

---

## Diagnosis (isolatable illegitimate transfers)

### Transfer 1: tool → judgment
Assistance is treated as decision-making.

### Transfer 2: recommendation → authority
Advisory outputs substitute for evaluation.

### Transfer 3: output → evaluation
Raw results are mistaken for judgment.

### Transfer 4: assistance → norm
Support tools are converted into mandates.

These transfers are structurally illegitimate and violate admissibility constraints.

---

## Why this matters
If tools replace judgment, the system collapses:

- accountability and responsibility,
- contextual evaluation,
- capacity to override or correct outputs.

This produces **automation-driven decisions**, not reasoned judgment.

---

## Counterfactual test (falsifiability)
No illegitimate transfer occurs if all of the following hold:

- Tool outputs are treated as **inputs**, not conclusions.
- Judgments remain attributable to **explicit agents or roles**.
- Recommendations are reviewed, contextualized, and contestable.
- Normative decisions are argued beyond tool output.

If these conditions hold, tooling does not distort admissibility.

---

## Scope limitations
This stress test does **not** claim:

- that tools are useless,
- that automation should be avoided,
- that recommendations lack value,
- that systems cannot support judgment.

It claims only:
- **tools are not judgments**, and
- **outputs do not decide by themselves**.

---

## Decision / outcome

### Claim-admission decision
All injections (A–E) are **inadmissible as claims**.

Reason:
They introduce **implicit decisional or normative authority**
that violates admissibility constraints.

### Acceptable reformulation
Some statements may become admissible if reformulated as:
- explicit tool output descriptions,
- decision rationales that incorporate tool input,
- assessments with human judgment attribution,
- adoption arguments acknowledging tool limits.

---

## STOP evaluation
No STOP was issued.

Rationale:
- All illegitimate transfers are isolatable.
- Counterfactual conditions are explicit.
- No self-sealing automation loop is introduced.

A STOP must be issued in future runs if:
- tools are treated as final arbiters, or
- judgment responsibility becomes untraceable.

