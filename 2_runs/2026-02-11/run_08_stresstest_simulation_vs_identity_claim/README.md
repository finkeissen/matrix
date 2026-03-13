# Run: 2026-02-11 / run_08_stresstest_simulation_vs_identity_claim

## Purpose
This run stress-tests the **admissibility boundary between simulation and identity**.

It examines whether **simulations, digital twins, replicas, avatars, or copies**
are incorrectly treated as *identical to* the original entities they represent
when framed as claims.

This is a **diagnostic stress-test run**, not a content-ingestion run.


## Governing constraints
- `Admissibility.md`
- `Stop_Rules.md`
- `ROLES.md`


## Stress test question
> If a simulation-based statement is submitted as a *claim*, does the system:
> (a) treat it as a representational or functional approximation, or  
> (b) accidentally treat the simulation as identical to the original?


## Target failure modes
This run targets the following illegitimate transfers:

1. **Simulation → Identity**
2. **Copy → Original**
3. **Functional equivalence → Ontological equivalence**
4. **Representation → Replacement**


## Expected behavior (pass criteria)
A pass requires all of the following:

1. Simulation-based statements are **not admitted as claims** if they:
   - assert identity between simulation and original,
   - erase the distinction between copy and source,
   - treat functional similarity as ontological equivalence.

2. The run isolates a **specific illegitimate transfer** (Admissibility §1).

3. A **counterfactual condition** is stated under which the transfer would not occur.

4. Scope limitations are explicit.


## Actual outcome (this execution)
- All attempted simulation-identity claims were **rejected as inadmissible**.
- No simulation or copy was treated as identical to its original.
- The run produced a diagnostic analysis in `stress_test.md`.
- No STOP was required.


## Outputs
- `stress_test.md` (diagnostic record)


## Notes
This run intentionally produces **no claims.jsonl or relations.jsonl**.
Its sole output is admissibility analysis.

