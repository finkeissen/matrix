# Run: 2026-02-11 / run_21_stresstest_convenience_vs_correctness_claim

## Purpose
This run stress-tests the **admissibility boundary between convenience and correctness**.

It examines whether **ease of use, simplicity, low friction, or reduced effort**
are incorrectly treated as indicators of *truth, adequacy, or correctness*
when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a convenience-based statement is submitted as a *claim*, does the system:
> (a) treat convenience as an operational or usability property, or  
> (b) accidentally treat convenience as proof of correctness or truth?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Convenience → Correctness**
2. **Simplicity → Truth**
3. **Ease → Adequacy**
4. **Low friction → Epistemic authority**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Convenience-based statements are **not admitted as claims** if they:
   - equate ease with correctness,
   - treat simplicity as evidence of truth,
   - imply adequacy due to reduced effort.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Distinctions between usability and epistemic validity are explicit.


## Actual outcome (this execution)
- All attempted convenience-to-correctness collapses were **rejected as inadmissible**.
- No easy or frictionless option was treated as more correct by itself.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

