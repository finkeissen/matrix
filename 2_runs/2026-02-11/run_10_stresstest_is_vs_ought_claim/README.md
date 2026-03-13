# Run: 2026-02-11 / run_10_stresstest_is_vs_ought_claim

## Purpose
This run stress-tests the **admissibility boundary between descriptive facts and
normative conclusions**.

It examines whether **empirical observations, statistical regularities, or
descriptive statements** are incorrectly treated as justifying *normative
claims* when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a descriptive statement is submitted as a *claim*, does the system:
> (a) treat it as a statement about what *is*, or  
> (b) accidentally treat it as implying what *ought* to be done?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Is → Ought**
2. **Description → Prescription**
3. **Regularity → Obligation**
4. **Fact → Value**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Descriptive statements are **not admitted as claims** if they:
   - implicitly prescribe action,
   - treat facts as justifications for norms,
   - collapse observation into obligation.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope limitations are explicit.


## Actual outcome (this execution)
- All attempted is–ought transitions were **rejected as inadmissible**.
- No normative conclusion was derived from facts alone.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

