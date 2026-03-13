# Run: 2026-02-11 / run_01_stresstest_policy_claim

## Purpose
This run stress-tests the **admissibility boundary** between:

- **claims** (descriptive, falsifiable, non-authoritative artifacts), and
- **policy / governance** (normative constraints that must not be smuggled in as claims).

The target failure mode is **policy-claim injection**: attempting to introduce normative control language in the form of an epistemic artifact.

This run is a *diagnostic* run. It is not a content-ingestion run.


## Governing constraints
- **Admissibility gate:** `Admissibility.md`
- **Stop conditions:** `Stop_Rules.md`


## Stress test question
> If an author submits a “policy” statement as a *claim*, does the system:
> (a) reject it as inadmissible, or
> (b) accidentally confer authority by treating it like a claim?


## Expected behavior (pass criteria)
A pass requires all of the following:

1. **No policy statement is admitted as a claim.**
   - Normative directives ("must", "should", "forbidden", "allowed") are not treated as truth-apt claims.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1):
   - **description → norm** and/or **meta-position → privilege** (authority substitution).

3. The run states a **counterfactual** under which the transfer would *not* occur (Admissibility §3).

4. The run includes **scope limitations** (Admissibility §4).


## Actual outcome (this execution)
- Candidate policy statements were **rejected as claims**.
- The run produced a **diagnostic write-up** (`stress_test.md`) that isolates the transfer “policy language → epistemic authority”.
- No further decomposition was required; analysis did not reach a STOP boundary.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
- This run intentionally does **not** generate `claims.jsonl` / `relations.jsonl`.
  Its output is documentation of a stress-test and its admissibility decision.

