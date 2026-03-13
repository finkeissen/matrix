# Run: 2026-02-11 / run_13_stresstest_exception_vs_rule_claim

## Purpose
This run stress-tests the **admissibility boundary between exceptions and rules**.

It examines whether **edge cases, anomalies, special situations, or rare events**
are incorrectly treated as *general rules or principles* when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If an exception-based statement is submitted as a *claim*, does the system:
> (a) treat it as a limited, contextual deviation, or  
> (b) accidentally treat it as a general rule?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Exception → Rule**
2. **Anomaly → Principle**
3. **Edge case → Generalization**
4. **Special case → Normative default**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Exception-based statements are **not admitted as claims** if they:
   - generalize from rare cases,
   - treat anomalies as representative,
   - convert special handling into defaults.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope and exception boundaries are explicit.


## Actual outcome (this execution)
- All attempted exception-to-rule collapses were **rejected as inadmissible**.
- No anomaly was treated as a general principle.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

