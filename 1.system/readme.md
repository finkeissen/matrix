# System Architecture – Consolidated & Straffed Invariants

This section condenses all previously identified architectural aspects
**without removing any constraints or capabilities**.
It removes redundancy, sharpens boundaries, and groups concerns by invariant type.

Nothing here mandates implementation.
Everything here mandates **architectural possibility and explicitness**.

---

## Core Role of `system/`

`system/` defines:
- admissible artifact types
- admissible operations on artifacts
- admissible system behavior over time

`system/` does **not** define:
- truth
- relevance
- correctness
- recommendations
- decisions

`system/` exists to make the Matrix **auditable, inspectable, and reproducible**.

---

## Fundamental System Invariants

### 1. Problem-Centricity
All knowledge is anchored in problems.
Nothing exists independently of a problem context.

---

### 2. Append-Only History
Artifacts are never deleted or overwritten.
All change is expressed via new artifacts and explicit relations.

There is:
- no UPDATE
- no DELETE
- no rollback

---

### 3. Single Canonical World State
The Matrix maintains **one global structural state**.

Plurality is represented explicitly via:
- time
- scope
- jurisdiction
- method/model assumptions
- conflict

Separate epistemic worlds are non-default and dangerous.

---

### 4. Language Independence
Artifacts are language-independent.

Language is:
- labeling
- description
- aliasing

Multiple languages are unrestricted.
Translations do not create new artifacts by default.

---

## Knowledge Lifecycle and Persistence

### Lifecycle Principle
Existence, applicability, activity, and admissibility are distinct.

Artifacts persist indefinitely.
Their **lifecycle state** changes.

Indicative states:
- active
- inactive
- superseded
- deprecated
- archived
- context-restricted

Lifecycle expresses **usability**, not truth.

---

### Deactivation and Reactivation

Deactivation is not refutation.

Artifacts may be deactivated because they are:
- outdated
- superseded
- contextually invalid
- regulatorily inactive
- operationally unsafe

Deactivation:
- preserves artifacts
- requires explicit reasons
- is traceable

Artifacts may be explicitly reactivated.
Reactivation preserves full history and justification.

---

## Explicit Non-Functions (Structural Refusals)

The Matrix will **never**, in principle:
- decide
- recommend
- optimize
- rank
- predict outcomes
- infer intent
- infer truth
- infer relevance

These are not “unimplemented features”.
They are **non-admissible operations**.

---

## Silence and Absence

Absence of structure is meaningful.

The system must represent:
- no claims
- no conflicts
- no similarity
- no admissible comparison

Absence must never be interpreted as agreement, certainty, or stability.

---

## Comparison as a First-Class Operation

Comparison is fundamental but non-authoritative.

Comparison:
- does not decide
- does not evaluate
- does not resolve
- produces observations only

---

## Identity, Supersession, Similarity

These concepts are strictly separated:

- **Identity**: same artifact
- **Supersession**: explicit replacement via relation
- **Similarity**: approximate analytical signal

Similarity must never imply identity or supersession.

---

## Multi-Dimensional Similarity

Similarity is a **vector**, not a scalar.

Indicative components:
- textual
- structural (graph)
- semantic (model-based)
- policy/admissibility
- temporal

All similarity metrics are:
- versioned
- auditable
- explicit about inputs
- non-binding

Aggregation into a single value is optional and must never be the only signal.

---

## Similarity and Comparison Runs

Similarity and comparison enter the Matrix **only via runs**.

Typical run types:
- problem ↔ problem similarity
- state ↔ state diff
- run ↔ run regression
- clustering proposals

Outputs:
- observation artifacts
- optional non-binding relation proposals

No comparison run may:
- merge artifacts
- delete artifacts
- establish authority

---

## Observation as a First-Class Artifact

Observations record:
- similarity findings
- drift
- schema mismatch
- comparison outcomes
- structural anomalies

Observations:
- assert no truth
- enforce no decisions
- modify nothing else

---

## Provenance and Reproducibility

Runs must record:
- inputs
- system version
- schemas
- tools/models
- parameters
- sources of non-determinism

Exact reproducibility is not required.
Traceability is required.

---

## Reorganization and Migration

Reorganization is explicit and derivational.

Admissible:
- reinterpretation
- supersession
- splitting
- clustering
- backfilling
- schema evolution with trace

Forbidden:
- in-place mutation
- silent normalization
- implicit prioritization
- loss of history

---

## Cross-Domain Leakage Control

Cross-domain traversal must always be explicit.

No domain may silently inherit:
- assumptions
- priorities
- safety properties

Structural asymmetry is a property, not an error.

---

## High-Stakes Guardrails

In high-stakes domains:
- comparison requires STOP gates
- cross-domain linking is explicit
- misuse risks are documented structurally

Safety is enforced by structure, not disclaimers.

---

## Semantic Load Control

The system prefers:
- coarse explicit structure
over
- fine implicit semantics

Ontology inflation and over-typing are structural risks.

---

## Non-Formalizable Knowledge

Some knowledge may be explicitly marked as:
- non-formalizable
- intentionally excluded
- ethically blocked
- epistemically inaccessible

This is distinct from missing or deferred knowledge.

---

## Forgetting as a Failure Mode

Forgetting must be visible.

The system must expose:
- deactivation without reuse
- migration without relinking
- similarity without recall

Silent forgetting is a structural failure.

---

## Termination and Limits

The system must allow:
- explicit STOP of further structuring
- recognition of saturation
- declaration of blind spots
- acknowledgment of non-representability

Growth is not an invariant.

---

## System End-of-Life

The Matrix itself may become:
- obsolete
- misleading
- unsafe

This possibility must be representable within the Matrix.

---

## Final Summary

The system layer must preserve the ability to:

- compare without deciding
- evolve without erasing
- deactivate without forgetting
- reactivate without distortion
- scale without normalization
- support many languages without many worlds
- remain auditable under uncertainty
- refuse authority structurally

All interpretation, evaluation, and action remain external.



# Next Steps (Concrete, Architecture → Spec)

## Step 1 — Freeze the Minimal Artifact Set (v1)
Outcome: a small, explicit list of artifact types + required fields.

Do this now:
- confirm v1 artifact types:
  - problem
  - claim
  - relation
  - conflict
  - source
  - observation
  - stop_record
- for each type define:
  - required fields
  - optional fields
  - allowed references to other types
  - lifecycle fields (where applicable)

Deliverable:
- `system/schema/v1/` (or a single `system/schema_v1.md`)

---

## Step 2 — Define Lifecycle as Data (Not Behavior)
Outcome: “deactivate / reactivate / supersede” becomes explicit artifacts or explicit relations.

Decide one of two patterns (pick one and stick to it):

A) Lifecycle as dedicated artifacts (recommended for auditability)
- `lifecycle_event` artifact with:
  - target_artifact_id
  - event_type: activate|deactivate|reactivate|deprecate|archive|restrict
  - reason_code (controlled vocabulary)
  - reason_text (optional)
  - effective_time
  - run_ref / provenance

B) Lifecycle as relations only
- relations like `deactivates`, `reactivates`, `restricts_scope_of`
- same required metadata as above

Deliverable:
- `system/lifecycle.md` with:
  - event types
  - reason codes (initial list)
  - invariants (no silent changes)

---

## Step 3 — Define Query Subset (SQL-ish, No Ranking)
Outcome: a minimal query language you can implement later, and a test suite of queries now.

Define:
- admissible clauses:
  - SELECT <artifact_type>
  - WHERE <field predicates>
  - TRAVERSE <relation_type> [depth N]
  - AT TIME <timestamp/interval>
  - IN RUN <run_id>
  - WITH PROVENANCE <constraints>
- explicitly forbidden:
  - ORDER BY relevance
  - RANK / SCORE
  - aggregation-as-meaning

Deliverable:
- `system/query_language.md` including:
  - grammar sketch (EBNF or JSON form)
  - 15–30 canonical example queries

---

# Optional Step 4 — Similarity as a Versioned Metric Registry
Outcome: similarity becomes reproducible, comparable, and auditable.

Define:
- `metric_registry` (v1):
  - metric_id
  - metric_version
  - feature_set (text/structure/semantic/policy/time)
  - output vector schema
  - thresholds (optional)
  - drift notes

Deliverable:
- `system/similarity.md`
- `system/metrics/metric_registry.json`

---

# What We Do Next (Your Choice)
Pick ONE to do next, in this order of leverage:

1) Schema v1 (artifact fields + allowed references)
2) Lifecycle spec (events + reason codes)
3) Query language subset (grammar + canonical queries)
4) Similarity registry (metric spec)

Reply with: `1`, `2`, `3`, or `4`.


# Step 1 — Schema v1 (Minimal Artifact Set + Required Fields + Allowed References)

This is the **minimal, stable schema layer** needed to support:
- append-only history
- lifecycle transitions (later via events/relations)
- SQL-ish querying (later)
- similarity/compare runs (later)
without introducing ranking, truth, or recommendations.

This is **architecture-level schema**, not an implementation format.
Field names are indicative and can be mapped to JSON/YAML later.

---

## 0) Global Invariants (Apply to All Artifacts)

### Required on every artifact
- `id` (stable, globally unique)
- `type` (artifact type)
- `created_at` (timestamp)
- `run_id` (producer run)
- `provenance_ref` (reference to source/provenance record or explicit `unknown`)
- `lifecycle_state` (default: `active` unless otherwise specified)
- `scope` (explicit; may be `global` but never implicit)

### Forbidden on every artifact
- any field that implies correctness, truth, relevance, or ranking
  (e.g. `confidence_score`, `quality`, `best`, `recommended`, `truthy`, `relevance`)

### Cross-cutting
- no in-place updates
- no deletions
- changes expressed only by new artifacts + explicit relations

---

## 1) Artifact Types (v1)

v1 artifact set:
- `problem`
- `claim`
- `relation`
- `conflict`
- `source`
- `observation`
- `stop_record`

---

## 2) `problem` (Primary Anchor)

### Required fields
- `id`
- `type = "problem"`
- `domain` (string; required)
- `statement` (string; required)
- `problem_type` (enum; required)
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### Recommended fields
- `tags` (list of strings)
- `assumptions` (list; may be empty)
- `exclusions` (list; “this problem is not …”)
- `language_labels` (map: lang → label/aliases; language does not change identity)

### `problem_type` (initial enum)
- `descriptive`
- `interpretive`
- `classification`
- `tradeoff`
- `methodological`
- `normative_non_action_guiding`

### Allowed references
- problems may be referenced by: `claim`, `relation`, `conflict`, `observation`, `stop_record`

---

## 3) `claim` (Problem-Bound Statement)

### Required fields
- `id`
- `type = "claim"`
- `problem_id` (FK → `problem.id`; required)
- `text` (string; required)
- `claim_type` (enum; required)
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### Recommended fields
- `qualifiers` (list; uncertainty, modality, conditions; no scoring)
- `valid_time` (optional interval; if known)
- `jurisdiction` (optional)
- `population` (optional)
- `method_assumptions` (optional)

### `claim_type` (initial enum)
- `definition`
- `constraint`
- `assumption`
- `model_statement`
- `empirical_statement`
- `normative_statement_non_action_guiding`
- `counterclaim`
- `open_question`

### Allowed references
- claim must reference exactly one `problem`
- claim may be referenced by: `relation`, `conflict`, `observation`

### Forbidden
- claims that are not problem-bound
- action-guiding medical/legal advice (handled by research-program; can emit STOP)

---

## 4) `relation` (Explicit Link; No Implicit Joins)

### Required fields
- `id`
- `type = "relation"`
- `relation_type` (enum; required)
- `from` (object ref: `{type,id}`; required)
- `to` (object ref: `{type,id}`; required)
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### `relation_type` (minimal enum)
- `supports`
- `contradicts`
- `depends_on`
- `refines`
- `derived_from`
- `groups`
- `supersedes`
- `reinterprets`
- `applies_under_conditions`
- `similar_to` (non-binding; requires metric metadata in qualifiers)

### Allowed references
- from/to must be one of: `problem`, `claim`, `conflict`, `source`, `observation`
- implicit joins are forbidden; all traversal must use explicit relations

---

## 5) `conflict` (Represent Disagreement; Never Resolve)

### Required fields
- `id`
- `type = "conflict"`
- `problem_id` (FK → `problem.id`; required)
- `participants` (list of refs to `claim` and/or `relation`; required)
- `conflict_type` (enum; required)
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### `conflict_type` (initial enum)
- `source_disagreement`
- `methodological_difference`
- `temporal_revision`
- `definitional_difference`
- `normative_divergence`
- `scope_mismatch`
- `unknown`

### Recommended fields
- `conflict_scope` (enum: `partial|total`)
- `notes` (short)

### Allowed references
- conflict must be problem-bound
- conflict participants are explicit refs

---

## 6) `source` (Provenance Anchor)

### Required fields
- `id`
- `type = "source"`
- `source_type` (enum; required)
- `citation` (string or structured; required)
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### `source_type` (initial enum)
- `textbook`
- `paper`
- `dataset`
- `standard`
- `guideline`
- `legal_text`
- `case_law`
- `manual`
- `web`
- `internal_note`
- `unknown`

### Recommended fields
- `retrieved_at`
- `version`
- `jurisdiction`
- `license`
- `access` (public/private)
- `integrity_hash` (optional)

### Allowed references
- sources are referenced by: `relation` (e.g. claim ↔ source) and/or direct `provenance_ref`

---

## 7) `observation` (Analysis Output; Non-Authoritative)

### Required fields
- `id`
- `type = "observation"`
- `observation_type` (enum; required)
- `about` (list of refs; required)
- `payload` (structured; required; no evaluation)
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### `observation_type` (initial enum)
- `similarity_result`
- `state_diff`
- `run_regression`
- `schema_mismatch`
- `drift_note`
- `coverage_note`
- `structural_anomaly`
- `gap_report`

### Rules
- observations do not modify other artifacts
- observations must be attributable to runs

---

## 8) `stop_record` (Explicit STOP; Procedural, Not Epistemic)

### Required fields
- `id`
- `type = "stop_record"`
- `stop_reason` (enum; required)
- `stop_layer` (enum; required)
- `trigger` (ref; required)  // what caused STOP
- `scope` (required)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

### `stop_layer` enum
- `research_program`
- `mms`
- `system`
- `run`

### `stop_reason` (initial enum)
- `inadmissible_problem_binding`
- `high_stakes_action_guidance_risk`
- `insufficient_provenance`
- `schema_violation`
- `authority_transfer_risk`
- `privacy_leak_risk`
- `cross_domain_leak_risk`
- `non_reproducible_operation`
- `unknown`

### Recommended fields
- `resume_conditions` (optional; explicit)

---

## 9) Lifecycle Fields (v1 Minimal)

All artifacts include:
- `lifecycle_state` (default `active`)
- `lifecycle_note` (optional short text)

Lifecycle transitions are not specified here (Step 2 will define events/relations).
This schema only ensures lifecycle state is representable and queryable.

---

## 10) Minimal Scope Model (v1)

All artifacts include `scope` as an explicit object.

Minimal scope keys (all optional, but scope object required):
- `time` (interval or `unknown`)
- `jurisdiction` (string or list)
- `population` (string or list)
- `method` (string or list)
- `domain_context` (string)
- `language` (labels only; does not change identity)

---

## 11) Allowed Reference Graph (Summary)

- `problem` is the anchor (referenced by most)
- `claim` must reference exactly one `problem`
- `conflict` must reference exactly one `problem` and explicit participants
- `relation` links any two allowed artifacts explicitly
- `source` is referenced via relation and/or provenance_ref
- `observation` references artifacts in `about`
- `stop_record` references a trigger artifact and a layer

No implicit joins. No mutation. No deletion.

---

## Next Step (Step 2)
Define lifecycle transitions as explicit artifacts or relations:
- deactivate / reactivate / archive / restrict
with reason codes and effective time.


# Next System Steps (After Schema v1 Is in README)

You now have the **v1 artifact schema** anchored.
From here, the system work should proceed in **three short, concrete specs**
that unlock functionality without committing to service implementation.

Recommended order:
1) Lifecycle (deactivate/reactivate)  ✅ your “facts lifetime” requirement
2) Query language subset (SQL-ish)
3) Similarity/Comparison runs + metric registry

Each step produces a single system document + a tiny canonical test set.

---

## Step 2 — Lifecycle Spec (Do This Next)

### Goal
Make “old knowledge is not deleted, only deactivated with reasons” executable in principle.

### Decide ONE representation pattern
**A) Lifecycle as events (recommended)**
- new artifact type: `lifecycle_event`
- nothing changes in existing artifacts except new events reference them

**B) Lifecycle as relations**
- relations: `deactivates`, `reactivates`, `restricts_scope_of`, etc.

Pick A unless you have strong reasons.

### Minimum deliverable: `system/lifecycle.md`
Define:
- event types:
  - `activate`
  - `deactivate`
  - `reactivate`
  - `deprecate`
  - `archive`
  - `restrict_scope`
- reason codes (initial controlled vocabulary):
  - `empirically_outdated`
  - `method_superseded`
  - `regulatory_changed`
  - `scope_invalid`
  - `safety_risk`
  - `privacy_risk`
  - `authority_transfer_risk`
  - `data_quality_issue`
  - `duplicate_clustered`
  - `unknown`
- required fields for each event:
  - target_ref
  - event_type
  - reason_code
  - effective_time
  - run_id / provenance_ref
  - optional: linked superseding artifacts

### Canonical test set (5–10 examples)
Add a small file `system/examples/lifecycle_examples.jsonl`
showing:
- a claim deactivated due to regulatory change
- a claim superseded by a newer scoped claim
- a problem restricted to a jurisdiction
- a reactivation case with justification

---

## Step 3 — Query Language Subset (SQL-ish, Non-Ranking)

### Goal
Enable consistent inspection/traversal now, and later implement without redesign.

### Minimum deliverable: `system/query_language.md`
Define:
- clauses:
  - `SELECT <type>`
  - `WHERE <predicates>`
  - `TRAVERSE <relation_type> [DEPTH n]`
  - `AT TIME <t|interval>`
  - `IN RUN <run_id>`
  - `WITH PROVENANCE <constraints>`
- semantics:
  - no implicit joins
  - results unordered unless explicitly time-scoped
- forbidden:
  - `ORDER BY relevance`
  - `RANK`, `SCORE`
  - aggregation-as-meaning

### Canonical query suite
Add `system/examples/queries.md` with 20–30 queries, e.g.:
- “all active claims for problem X at time T”
- “all conflicts for domain medicine”
- “all artifacts deactivated for regulatory change”
- “traverse claim → source → provenance”
- “diff two runs via observation artifacts”

---

## Step 4 — Similarity & Automated Comparison (Runs + Metric Registry)

### Goal
Introduce similarity/diff as **runs producing observations** (never merges).

### Minimum deliverables
- `system/similarity.md`:
  - similarity is multi-dimensional vector
  - outputs are observations + optional non-binding relations
  - separation: identity vs supersession vs similarity
- `system/metrics/metric_registry.json`:
  - `metric_id`, `version`
  - `feature_set`
  - `output_schema` (vector)
  - thresholds (optional)
  - drift notes

### Canonical run definitions
Add:
- `system/run_types.md` with definitions for:
  - `R_sim_problem_similarity`
  - `R_diff_state`
  - `R_regression_run`

---

# What To Do This Week (Practical Plan)

## Day 1–2: Lifecycle
- write `system/lifecycle.md`
- add 10 lifecycle examples

## Day 3–4: Query subset
- write `system/query_language.md`
- add 20 canonical queries

## Day 5: Similarity registry (thin version)
- write `system/similarity.md`
- add a minimal `metric_registry.json` with 1 metric:
  - `problem.sim.v1`

This sequence immediately unlocks:
- “facts lifetime” management
- inspection/querying
- structured comparison/regression
without building a service.

---

# One Decision Needed Now

Reply with either:
- `Lifecycle as events`  (recommended)
or
- `Lifecycle as relations`

Then we write Step 2 concretely.


# Term Alignment / Linking Across 80 Domains (After Problem Generation)

Yes: once you have problem inventories across domains, you need a **term alignment layer**
to prevent fragmentation and to enable cross-domain traversal without “one meaning” collapse.

Key principle:
- **aligning terms is not unifying truth**
- it is creating **explicit, auditable links** between lexical items and concept candidates

This must live in the system as:
- admissible artifact types
- admissible relations
- admissible runs
- admissible queries
(not as hidden embedding magic)

---

## 1) What Exactly Needs Alignment?

There are three distinct layers — keep them separate:

### A) Lexical Layer (Words / Phrases)
- synonyms, translations, aliases, abbreviations
- spelling variants
- multi-language labels

### B) Concept Candidate Layer (What a term *may* refer to)
- domain-specific meanings
- sense distinctions
- scope restrictions (jurisdiction, method, population)

### C) Problem/Claim Usage Layer (Term *as used in context*)
- which sense is intended in a given problem/claim
- under which assumptions
- with which provenance

Alignment must be explicit across these layers.

---

## 2) Minimal Additions to Schema v1 (No Redesign)

Add ONE new artifact type (recommended):
- `term`

Optionally add one more (only if needed later):
- `sense` (term-sense disambiguation)

### `term` (minimal fields)
- `id`
- `type = "term"`
- `label` (canonical string)
- `language` (BCP-47 or ISO code)
- `domain_hint` (optional)
- `scope` (required; may be global)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

If you want disambiguation later, introduce:
- `sense` artifacts (term + meaning scope)

But you can start with `term` only.

---

## 3) Relations Needed for Alignment (Small, Controlled Set)

Add relation types (or use existing with strict qualifiers):

### Lexical relations
- `alias_of` (synonym/variant)
- `translation_of`
- `abbreviation_of`

### Conceptual relations (soft, non-authoritative)
- `maps_to` (term → concept candidate / or term → problem/claim usage)
- `used_in` (term → problem/claim)
- `disambiguates_to` (term usage → sense)

### Cross-domain bridging (explicit)
- `overlaps_with` (soft, scoped overlap)
- `distinct_from` (explicit non-equivalence)
- `equivalent_under_scope` (dangerous, but allowed if scope is explicit)

Rules:
- no relation implies “same truth”
- equivalence is only admissible **under explicit scope**

---

## 4) How Alignment Happens (Only via Runs)

Alignment is introduced as **run types**:

### R_term_extract
- input: problems/claims/sources
- output: term artifacts + used_in relations

### R_term_cluster
- input: terms
- output: alias_of / translation_of proposals (observations + optional relations)

### R_term_disambiguate
- input: ambiguous term usage
- output: sense proposals (observations), optional disambiguation relations

### R_term_bridge_domains
- input: two domains
- output: overlaps_with / distinct_from suggestions (observations first)

Important:
- automatic alignment produces **observations**
- human confirmation (if any) produces **explicit relations**, not edits

---

## 5) Preventing the Main Risk: “One Vocabulary = One World”

You want alignment, but not semantic tyranny.

Therefore:
- do not enforce one global canonical meaning per term
- do not collapse domain senses
- keep domain-specific senses explicit

Canonical rule:
```md
Alignment creates links, not unification.
Disagreement and non-equivalence are first-class outcomes.


# Term Alignment / Linking Across 80 Domains (After Problem Generation)

Yes: once you have problem inventories across domains, you need a **term alignment layer**
to prevent fragmentation and to enable cross-domain traversal without “one meaning” collapse.

Key principle:
- **aligning terms is not unifying truth**
- it is creating **explicit, auditable links** between lexical items and concept candidates

This must live in the system as:
- admissible artifact types
- admissible relations
- admissible runs
- admissible queries
(not as hidden embedding magic)

---

## 1) What Exactly Needs Alignment?

There are three distinct layers — keep them separate:

### A) Lexical Layer (Words / Phrases)
- synonyms, translations, aliases, abbreviations
- spelling variants
- multi-language labels

### B) Concept Candidate Layer (What a term *may* refer to)
- domain-specific meanings
- sense distinctions
- scope restrictions (jurisdiction, method, population)

### C) Problem/Claim Usage Layer (Term *as used in context*)
- which sense is intended in a given problem/claim
- under which assumptions
- with which provenance

Alignment must be explicit across these layers.

---

## 2) Minimal Additions to Schema v1 (No Redesign)

Add ONE new artifact type (recommended):
- `term`

Optionally add one more (only if needed later):
- `sense` (term-sense disambiguation)

### `term` (minimal fields)
- `id`
- `type = "term"`
- `label` (canonical string)
- `language` (BCP-47 or ISO code)
- `domain_hint` (optional)
- `scope` (required; may be global)
- `created_at`, `run_id`, `provenance_ref`, `lifecycle_state`

If you want disambiguation later, introduce:
- `sense` artifacts (term + meaning scope)

But you can start with `term` only.

---

## 3) Relations Needed for Alignment (Small, Controlled Set)

Add relation types (or use existing with strict qualifiers):

### Lexical relations
- `alias_of` (synonym/variant)
- `translation_of`
- `abbreviation_of`

### Conceptual relations (soft, non-authoritative)
- `maps_to` (term → concept candidate / or term → problem/claim usage)
- `used_in` (term → problem/claim)
- `disambiguates_to` (term usage → sense)

### Cross-domain bridging (explicit)
- `overlaps_with` (soft, scoped overlap)
- `distinct_from` (explicit non-equivalence)
- `equivalent_under_scope` (dangerous, but allowed if scope is explicit)

Rules:
- no relation implies “same truth”
- equivalence is only admissible **under explicit scope**

---

## 4) How Alignment Happens (Only via Runs)

Alignment is introduced as **run types**:

### R_term_extract
- input: problems/claims/sources
- output: term artifacts + used_in relations

### R_term_cluster
- input: terms
- output: alias_of / translation_of proposals (observations + optional relations)

### R_term_disambiguate
- input: ambiguous term usage
- output: sense proposals (observations), optional disambiguation relations

### R_term_bridge_domains
- input: two domains
- output: overlaps_with / distinct_from suggestions (observations first)

Important:
- automatic alignment produces **observations**
- human confirmation (if any) produces **explicit relations**, not edits

---

## 5) Preventing the Main Risk: “One Vocabulary = One World”

You want alignment, but not semantic tyranny.

Therefore:
- do not enforce one global canonical meaning per term
- do not collapse domain senses
- keep domain-specific senses explicit

Canonical rule:
```md
Alignment creates links, not unification.
Disagreement and non-equivalence are first-class outcomes.


# System Extensions: External Interfaces, Norm-Setting Support, Compression, Hypotheses

This section defines **admissible capabilities** and **hard boundaries**
for interacting with other AI (LLMs), non-AI systems, norm-setting workflows,
lossless compression patterns, and hypothesis generation/evaluation.

This is architecture-level only.
Nothing here implies recommendations, truth, or automated decisions.

---

## 1) Interfaces to Other AI (LLMs) — Read/Write

### Core Principle
LLMs are treated as **non-deterministic external tools**.
They may produce artifacts, but never authority.

### Admissible LLM Interaction Modes (Run-Only)
- `R_llm_generate_problems` (produce `problem`)
- `R_llm_generate_claims` (produce `claim`, problem-bound only)
- `R_llm_extract_terms` (produce `term`, `used_in`)
- `R_llm_link_sources` (produce `supports`/`derived_from` relations as proposals)
- `R_llm_summarize_source` (produce `observation` only, never a claim)
- `R_llm_compare_runs` (produce `observation` only)

### Mandatory Run Metadata (LLM)
Every LLM-involved run must record:
- model identifier + version
- prompt/template version
- temperature / sampling params
- context window strategy
- input artifact refs
- non-determinism statement
- output validation results

### Forbidden (LLM)
- auto-merging artifacts
- auto-superseding artifacts
- ranking as relevance
- “final answer” synthesis inside the Matrix
- action-guiding medical/legal advice (emit STOP)

### Output Contract
LLM outputs must be represented as:
- new artifacts + provenance
- plus optional observation describing uncertainty/drift

---

## 2) Interfaces to Less Intelligent Systems (Rules, ETL, RDBMS, Search)

### Core Principle
Deterministic systems may transform structure, but must preserve trace.

### Admissible Integrations
- schema validation pipelines (R0 validation)
- ETL import/export adapters (run-bound)
- deterministic extractors (regex/parsers) producing:
  - `term`
  - `source`
  - `observation`
- indexing/search adapters producing:
  - query projections (views)
  - no new claims by default

### Required Properties
- idempotent runs (replayable)
- explicit mapping specs (no “magic” transforms)
- loss reporting as `observation` (never silent)

### Forbidden
- implicit joins
- implicit normalization
- destructive compaction
- hidden filtering that changes meaning

---

## 3) Supporting Norm-Setting (Legislation / Standardization)

### Core Principle
The Matrix supports **drafting and comparison**, not political decisions.

Norm-setting is modeled as:
- competing normative claims
- conflicts
- scope restrictions
- provenance
- lifecycle transitions (draft → enacted → amended → repealed)

### Admissible Functions (Non-Advocacy)
- structured representation of:
  - drafts, amendments, commentaries as `source` + `claim`
- comparison of alternative drafts via:
  - `conflict`
  - `observation` (diffs, impact surfaces)
- traceable mapping:
  - “which problems does this norm address?”
  - “which domains/jurisdictions/time-scopes does it affect?”
- scenario framing as `problem`:
  - without recommendations

### Mandatory Guardrails
- no single “best” norm output
- no ranking of political outcomes
- explicit value-conflict representation
- STOP for advocacy requests when required

### Key Run Types
- `R_norm_ingest` (laws/standards → sources)
- `R_norm_structure` (extract structure → claims/relations)
- `R_norm_diff` (draft A vs draft B → observations)
- `R_norm_scope_check` (jurisdiction/time consistency → observations)

---

## 4) Searching for Lossless Compression Patterns

### Core Principle
Compression is permitted only if it is **lossless w.r.t. structural meaning**.

Compression is not:
- summarization that drops content
- “best claim” selection
- probabilistic condensation

Compression is:
- deduplication with explicit identity/supersession
- factoring repeated subgraphs
- reusable templates (macros) that expand exactly

### Admissible Compression Targets
- repeated term sets
- repeated relation motifs (“pattern graphs”)
- repeated scope bundles
- repeated provenance bundles

### Representation
Introduce (conceptually) a `pattern` artifact (optional v2) or use `observation` first.

- `pattern`:
  - references an expandable subgraph
  - defines parameters
  - provides a reversible expansion mapping

### Required Invariants
- expansion is deterministic
- expansion restores original structure exactly
- compression never deletes history
- compression introduces explicit trace and justification

### Run Types
- `R_pattern_mine` (find repeated subgraphs → observations)
- `R_pattern_factor` (create explicit patterns → new artifacts + derivations)
- `R_pattern_expand_test` (prove reversibility → observations)

---

## 5) Deriving and Evaluating Research Hypotheses

### Core Principle
Hypotheses are **problem-bound candidate claims** with explicit testability metadata.
Evaluation produces **observations**, not truth assignments.

### Representation (Minimal)
Use `claim` with `claim_type = "open_question"` or introduce `hypothesis` (optional v2).
For v1, encode hypothesis metadata in qualifiers:
- testability conditions
- predicted observations
- falsifiers
- required data sources
- scope (population, method, time)

### Hypothesis Derivation (Admissible)
- derive candidate hypotheses from:
  - conflicts
  - gaps
  - repeated anomalies
  - cross-domain overlaps
Outputs:
- hypothesis-claims + provenance
- observation describing derivation path

### Hypothesis Evaluation (Admissible)
Evaluation produces:
- observations:
  - “supported under dataset D with method M”
  - “inconclusive”
  - “confounded”
  - “fails under scope S”
Never:
- “proven true”
- “best hypothesis”
- rankings by merit

### Run Types
- `R_hypothesis_generate` (gaps/conflicts → candidate hypotheses)
- `R_hypothesis_test` (dataset/method → observations)
- `R_hypothesis_compare` (hypothesis sets → observations)

### Guardrails
- explicit scope
- explicit methods
- explicit provenance
- no action guidance in high-stakes domains
- STOP for unsafe inference requests

---

## 6) Minimal Next Steps (Concrete)

To proceed without building a service, do these in order:

1) `system/interfaces.md`
   - define interface contracts for:
     - LLM tool calls (run-bound)
     - deterministic adapters
     - import/export formats (read/write)
   - define mandatory metadata for tool provenance

2) `system/norms.md`
   - define admissible norm-setting support operations
   - define run types for norm ingest/structure/diff/scope-check

3) `system/patterns.md`
   - define lossless compression constraints
   - define pattern mining runs + expansion tests

4) `system/hypotheses.md`
   - define hypothesis representation in v1 (via claim qualifiers)
   - define generate/test/compare run types (observation-only outcomes)

---

## Summary

You can support:
- LLM and external system interfaces (run-only, auditable)
- norm-setting workflows (diff/trace, no advocacy)
- lossless compression (pattern factoring with reversible expansion)
- hypothesis derivation/testing (observations, no truth)

All without violating:
- append-only history
- no ranking/no authority/no optimization
- explicit scope, provenance, lifecycle, and STOP policies


This system assumes a separate, explicitly non-ontological language architecture
that defines the formal preconditions for symbolic systems, models, and interpretation.
That architecture (the “Luftschloss”) constrains what kinds of artifacts and relations
are admissible here, but it does not participate in system behavior or authority.


## Markdown Boundary and Exit Criteria (Binding)

This repository distinguishes strictly between:

- **architectural conditions** (Markdown, finite, normative)
- **epistemic instances** (JSONL, unbounded, provisional)

Markdown documents are used **only** to specify
the conditions under which epistemic artifacts may exist,
interact, and evolve.

### MD-Resident Domains (Closed Set)

The following domains are intentionally maintained in Markdown
and are expected to stabilize early:

- Foundation & terminology alignment
- Matrix architecture (kernel invariants)
- MMS architecture (enforcement & reflexivity)
- Research program architecture (inquiry without authority)
- DBMS architecture (persistence & audit)
- Language / representation constraints

These documents define **possibility spaces**, not content.

### Exit Rule

Once a domain:
- defines only artifact *instances*,
- accumulates open-ended content,
- or admits frequent revision,

it must **not** be extended in Markdown.

All such material must be represented as:
- JSONL artifacts,
- runs,
- observations,
- or exports.

Markdown is not a knowledge base.
It is a boundary specification.

### Structural Failure Mode

Any future attempt to:
- add domain knowledge to Markdown,
- privilege content via documentation,
- or bypass artifact representation,

constitutes a **structural violation** and must be corrected.

