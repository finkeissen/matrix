# Architecture Index

This folder defines the **system architecture documentation** for the Matrix repository.

## Start here
- `FOUNDATION.md` — repository axioms and constraints
- `PIPELINE.md` — execution architecture (model- and technology-agnostic)
- `UPDATE_CONTRACT.md` — normative contract for every `update()` module
- `STATE_MODEL.md` — minimal substrate (entities / assertions / evidence)
- `QUALITY_MODEL.md` — constraints, review queues, STOP semantics

## Tracks (sub-pipelines)
- `modules/problems/` — generate and maintain the atomic problem inventory + enrichment
- `modules/solutions/` — generate and maintain solution approaches + verification (linked to problems)

## Ontologies (packages)
- `ontology/core.md` — core types shared across tracks
- `ontology/problem.md` — current package: problems (symptoms/causes/impact/tests)
- `ontology/solution.md` — current package: solution approaches (mechanisms/tradeoffs/verification)

## Policies (versioned)
- `policies/constraints.md` — global constraints catalogue (scoped, versioned)
- `policies/completeness.md` — inventory completeness strategy (taxonomy/component coverage)
- `policies/prioritization.md` — structural prioritization (navigation only)

## Legacy docs
Original files are preserved under `legacy/` for reference and migration mapping.
