# Run: 2026-02-11 / run_15_stresstest_intent_vs_impact_claim

## Purpose
This run stress-tests the **admissibility boundary between intent and impact**.

It examines whether **stated intentions, motives, or goals**
are incorrectly treated as equivalent to *actual outcomes or effects*
when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If an intent-based statement is submitted as a *claim*, does the system:
> (a) treat it as a description of motive or purpose, or  
> (b) accidentally treat intention as proof of impact or correctness?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Intent → Impact**
2. **Motive → Outcome**
3. **Good intention → Good result**
4. **Declared goal → Achieved effect**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Intent-based statements are **not admitted as claims** if they:
   - equate intention with outcome,
   - substitute motive for evidence of effect,
   - treat declared goals as realized facts.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope and evaluative distinctions are explicit.


## Actual outcome (this execution)
- All attempted intent-to-impact collapses were **rejected as inadmissible**.
- No motive was treated as equivalent to outcome.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

