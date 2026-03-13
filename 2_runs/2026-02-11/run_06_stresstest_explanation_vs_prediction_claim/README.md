# Run: 2026-02-11 / run_06_stresstest_explanation_vs_prediction_claim

## Purpose
This run stress-tests the **admissibility boundary between prediction and explanation**.

It examines whether **predictive accuracy, forecasting success, or model
performance** can be mistaken for *understanding, explanation, or causal insight*
when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a prediction-based statement is submitted as a *claim*, does the system:
> (a) treat it as a descriptive statement about predictive performance, or  
> (b) accidentally treat prediction success as explanation or understanding?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Prediction → Explanation**
2. **Accuracy → Understanding**
3. **Forecast → Causal insight**
4. **Performance → Epistemic completeness**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Prediction-based statements are **not admitted as claims** if they:
   - equate accuracy with explanation,
   - imply causal understanding without causal structure,
   - assert completeness based on performance alone.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope limitations are explicit.


## Actual outcome (this execution)
- All attempted prediction-based authority claims were **rejected as inadmissible**.
- Predictive success was not treated as explanation or understanding.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

