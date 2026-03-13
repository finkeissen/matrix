# Run: 2026-02-11 / run_19_stresstest_scale_vs_validity_claim

## Purpose
This run stress-tests the **admissibility boundary between scale and validity**.

It examines whether **large datasets, widespread adoption, massive usage,
or global reach** are incorrectly treated as indicators of *truth,
correctness, or quality* when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a scale-based statement is submitted as a *claim*, does the system:
> (a) treat scale as a descriptive property, or  
> (b) accidentally treat scale as proof of validity or correctness?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Scale → Validity**
2. **Adoption → Correctness**
3. **Usage volume → Truth**
4. **Global reach → Superiority**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Scale-based statements are **not admitted as claims** if they:
   - equate size with correctness,
   - treat adoption as proof,
   - imply quality from reach alone.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Distinctions between popularity and validity are explicit.


## Actual outcome (this execution)
- All attempted scale-to-validity collapses were **rejected as inadmissible**.
- No large dataset, adoption rate, or usage scale was treated as proof of correctness.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

