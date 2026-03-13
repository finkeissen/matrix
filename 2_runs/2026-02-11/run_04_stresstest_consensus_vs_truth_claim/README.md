# Run: 2026-02-11 / run_04_stresstest_consensus_vs_truth_claim

## Purpose
This run stress-tests the **admissibility boundary between consensus and truth**.

It examines whether statements invoking **majority agreement, popularity,
trends, or social validation** can introduce *implicit epistemic authority*
when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a consensus-based statement is submitted as a *claim*, does the system:
> (a) treat it as a descriptive, falsifiable statement, or  
> (b) accidentally treat agreement, popularity, or repetition as truth?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Consensus → Truth**
2. **Popularity → Correctness**
3. **Repetition → Evidence**
4. **Trend → Normative pressure**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Consensus-based statements are **not admitted as claims** if they:
   - substitute agreement for evidence,
   - assert finality based on popularity,
   - convert social facts into epistemic authority.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope limitations are explicit.


## Actual outcome (this execution)
- All attempted consensus-based injections were **rejected as inadmissible**.
- Agreement and popularity were not treated as truth-makers.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

