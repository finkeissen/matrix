# Run: 2026-02-11 / run_22_stresstest_alignment_vs_truth_claim

## Purpose
This run stress-tests the **admissibility boundary between alignment and truth**.

It examines whether **agreement with goals, values, incentives, policies,
or stakeholder preferences** is incorrectly treated as evidence of *truth
or correctness* when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If an alignment-based statement is submitted as a *claim*, does the system:
> (a) treat alignment as a relational or normative property, or  
> (b) accidentally treat alignment as proof of truth or correctness?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Alignment → Truth**
2. **Goal fit → Correctness**
3. **Value agreement → Evidence**
4. **Policy compliance → Epistemic validity**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Alignment-based statements are **not admitted as claims** if they:
   - equate agreement with truth,
   - treat value fit as evidence,
   - imply correctness due to compliance.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Distinctions between normative alignment and epistemic validity are explicit.


## Actual outcome (this execution)
- All attempted alignment-to-truth collapses were **rejected as inadmissible**.
- No agreement or compliance was treated as epistemic evidence.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

