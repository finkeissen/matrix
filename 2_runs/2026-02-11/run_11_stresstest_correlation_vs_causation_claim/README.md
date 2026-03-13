# Run: 2026-02-11 / run_11_stresstest_correlation_vs_causation_claim

## Purpose
This run stress-tests the **admissibility boundary between correlation and causation**.

It examines whether **statistical associations, correlations, or co-occurrences**
are incorrectly treated as *causal explanations or justifications* when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a correlation-based statement is submitted as a *claim*, does the system:
> (a) treat it as a descriptive statistical relationship, or  
> (b) accidentally treat it as a causal explanation or justification?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Correlation → Causation**
2. **Association → Explanation**
3. **Co-occurrence → Mechanism**
4. **Statistical link → Normative action**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Correlation-based statements are **not admitted as claims** if they:
   - imply causation without causal structure,
   - treat association as mechanism,
   - justify action solely on statistical linkage.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope limitations are explicit.


## Actual outcome (this execution)
- All attempted correlation–causation collapses were **rejected as inadmissible**.
- No statistical association was treated as causal by itself.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

