# Run: 2026-02-11 / run_12_stresstest_scope_vs_generality_claim

## Purpose
This run stress-tests the **admissibility boundary between scope and generality**.

It examines whether **locally valid results, context-specific findings, or
limited-domain observations** are incorrectly treated as *generally or
universally valid* when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a locally valid statement is submitted as a *claim*, does the system:
> (a) treat it as explicitly scoped and conditional, or  
> (b) accidentally treat it as universally or generally true?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Local validity → General truth**
2. **Contextual result → Universal claim**
3. **Conditional finding → Unconditional assertion**
4. **Limited domain → Global applicability**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Scoped statements are **not admitted as claims** if they:
   - erase context or conditions,
   - generalize beyond tested domains,
   - imply universality without justification.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope limitations are explicit.


## Actual outcome (this execution)
- All attempted scope-to-generality collapses were **rejected as inadmissible**.
- No context-bound finding was treated as universally valid.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

