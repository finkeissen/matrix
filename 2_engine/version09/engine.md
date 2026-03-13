# engine.md — Pipeline Decision Log
## Atomic Problem Identification Pipeline · version09

**Status:** Pre-coding reference
**Last updated:** 2026-03-04 (rev 2)
**Scope:** Decisions and open points captured before implementation begins. Feed into v2 files during coding — do not modify originals.

---

## Confirmed Decisions

### E-01 · `06_clarification` Exit Condition
**Decision:** Maximum 2 clarification rounds, then STOP.
**Stop code:** `scope_clarification_exhausted`
**Implementation:**
- `run_record.json` gets field `clarification_rounds: int` (default 0)
- Orchestrator checks *before* dispatch: `if clarification_rounds >= 2 → STOP`
- No further LLM call after round 2
**Affects:** `pipeline/steps/06_clarification.md` (v2), `core/run.md` (v2), `runtime/executor.md` (v2)

---

### E-02 · `problem_id` Prefix Schema
**Decision:** 5-character prefix instead of 3, derived deterministically from `subdomain_label`.
**Rules:**
- Simple labels (no spaces, no `&`, no `/`): first 5 characters, uppercase → `ALGEB`, `ANALY`
- Compound labels: initials of all words (excluding stopwords: `&`, `und`, `and`, `of`, `the`) + padding to 5 characters → `ALGDS` for "Algorithmen & Datenstrukturen"
- Special characters and umlauts normalized before extraction: `ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`
**Collision handling:** If two subdomains produce the same 5-character prefix, append suffix `-A` / `-B`. Collision table checked at runtime in `08_finalization`.
**Affects:** `schema/atomic_problem.schema.json`, `pipeline/steps/08_finalization.md` (v2)

> **Deferred:** Exact initial-extraction rule for compound labels will be decided on first run with non-trivial labels.

---

### E-03 · `kb_snapshot_id` in Generation Runs
**Decision:** `kb_snapshot_id = sha256(subdomains.jsonl content)`
**Semantics:** The "KB" for generation runs is the subdomain list. If `subdomains.jsonl` changes, the snapshot changes automatically — cross-run cache will not hit stale results.
**Implementation:**
- Preflight computes hash of `subdomains.jsonl` and writes it as `kb_snapshot_id` into `run_record.json`
- Novelty Guard remains active with `require_same_snapshot: true`
- No separate snapshot store needed — the hash is the identifier
**Affects:** `core/run.md` (v2), preflight checks in `runtime/executor.md` (v2)

---

### E-04 · `03_normalize` Scope
**Decision:** Remains `deterministic`, soft normalization only.
**In scope:**
- Trim whitespace
- Consistent Title Case
- Normalize special characters: `&` → `and`, `/` → `-`
- Remove duplicates within category list (case-insensitive)
**Out of scope:** Synonym resolution, translation, semantic clustering
**Rationale:** Every step is updatable. Later options remain open:
- Re-run with extended normalization canon → new `task_id`, Novelty Guard passes through
- `03_normalize_v2` with LLM or lookup table can be inserted without pipeline restructuring
- Post-hoc batch job over `registry/problems.jsonl`
- Manifest status remains `candidate` until a review step promotes to `verified`
**Affects:** `pipeline/steps/03_normalize.md` (v2)

---

### E-05 · `04_generation` Execution Strategy — Two-Stage (04a + 04b)
**Decision:** Generation is split into two sequential steps per category:
- **`04a_generation`** — 35b model generates all atomic problems for one category (first-pass draft)
- **`04b_generation_review`** — 122b model refines 04a output: checks atomicity, flags hallucination risk, fills obvious gaps

**Rationale:** A full subdomain generation in one pass would produce 8k–20k output tokens, exceeding any 4k–8k context window. Per-category calls stay within budget. The two-stage split separates cheap bulk generation (35b, fast) from quality enforcement (122b, slower but targeted).

**Implementation:**
- Both envelopes instantiated once per category from `03_categories` output
- `04b` takes `04a` output hash as input → different `task_id` → treated as independent step
- Novelty Guard operates per category per stage — a cached category-stage is skipped
- `05_validation` receives output of `04b`, not `04a`
- `04a` artifacts remain in run directory as reference (content state: `candidate`)
- `04b` artifacts are the authoritative generation output (content state: `candidate` → promoted by `05_validation`)

**Context budget per call:**

```
04a_generation (35b):
  Input:  scope + category + schema reference    ~1.300 tokens
  Output: 20–30 problems (first draft)           ~1.500 tokens
  Total:                                         ~2.800 tokens  ✅ fits in 4k

04b_generation_review (122b):
  Input:  04a output + review instructions       ~2.500 tokens
  Output: refined problem list + change notes    ~2.000 tokens
  Total:                                         ~4.500 tokens  ✅ fits in 8k
```

**Affects:** `pipeline/steps/04a_generation.md` (v2, new), `pipeline/steps/04b_generation_review.md` (v2, new), `pipeline/00_step_registry_v2.md`

---

### E-06 · Model Routing per Step
**Decision:** Step-specific model assignment via `policy.model` field in each envelope. Single run with two-stage generation (04a + 04b) — no full multi-pass strategy.
**Rationale:** Full pipeline re-runs would produce identical `task_id`s (same inputs → Novelty Guard cache hit). No quality gain, high cost. Two-stage generation separates bulk drafting (35b, fast) from quality review (122b, targeted). Step-specific routing achieves quality where it matters at lowest overall cost.

**Routing table:**

| Step | Model | Rationale |
|---|---|---|
| `01_scope` | `19b` | Structured JSON, closed format, no deep reasoning needed |
| `01_scope_confidence` | `19b` | Scoring only, no reasoning |
| `03_categories` | `35b` | Domain clustering benefits from broader knowledge |
| `03_gap_detection` | `35b` | Comparison against canon, moderate reasoning |
| `04a_generation` | `35b` | Fast first-pass draft, bulk generation per category |
| `04b_generation_review` | `122b` | Atomicity enforcement, hallucination flagging, gap filling |
| `05_validation` (LLM part) | `35b` | Schema compliance check, structured output |
| `06_clarification` | `19b` | Scope refinement loop, tight JSON output |
| `07_hallucination_scan` | `122b` | Exactly where the large model earns its cost |
| `07_alternative_check` | `35b` | Category comparison, moderate reasoning |
| `08_finalization` (explanation) | `19b` | Text generation only, no reasoning required |

**Available models:**

| ID | Parameters | Speed | Notes |
|---|---|---|---|
| `19b` | 19B/A3B | 65 T/s | Fast, reliable JSON with tight prompts |
| `35b` | 35B/A3B | 30 T/s | Good balance, stronger domain knowledge |
| `122b` | 122B/A10B | TBD | Strongest reasoning, lowest hallucination risk |

**Envelope field:** `policy.model: "19b" | "35b" | "122b"`
**Affects:** `core/envelope.md` (v2 — add `model` to policy schema), all LLM step files (v2), `runtime/executor.md` (v2 — model dispatch logic)

---

## Open Points

### O-01 · Language of category names in `03_categories`
**Status:** Unresolved — should the LLM prompt explicitly enforce English?
**Options:**
- A) English enforced in prompt → `03_normalize` receives consistent material
- B) Language unconstrained → `03_normalize` would need to handle translation (conflicts with E-04)
- C) English enforced in prompt, original language carried as optional field
**Recommendation:** Option A. Consistent with briefing decision "Output language: English only" and reduces burden on `03_normalize`.
**Decision pending.** Blocks: `pipeline/steps/03_categories.md` (v2)

---

### O-02 · Review Status Workflow
**Status:** Schema defines `review_status: draft | reviewed | approved` — but the process is unspecified.
**Open questions:**
- Who promotes `draft → reviewed`? Manual, or a dedicated validation step?
- Who promotes `reviewed → approved`? Human review, or automated checker?
- Is there a `rejected` status? What happens to rejected problems — delete or mark `superseded`?
- How does the Novelty Guard behave if an `approved` problem is re-generated?
**Affects:** `schema/atomic_problem.schema.json`, `pipeline/steps/09_commit.md` (v2), future quality management layer
**Decision pending.** Non-blocking for first run (all problems start as `draft`).

---

## Deliberately Deferred

### Z-01 · Maximum problem count per subdomain
No cap defined. Will be determined empirically after first run with Algebra.

### Z-02 · Exact prefix rule for compound labels
See E-02. Will be decided on first run with a non-trivial subdomain label.

---

### E-07 · Re-Run Strategy (Periodic Quality Improvement)
**Decision:** Periodic re-runs target only the generation and review steps — not the full pipeline.
**Cadence:** Every 3 months, or when a significantly better local model becomes available.
**Re-run scope:**

```
Steps re-run:        04a_generation → 04b_generation_review → 05_validation
                     → 07_hallucination_scan → 08_finalization → 09_commit
Steps skipped:       01_scope, 01_scope_confidence, 02_retrieval,
                     03_categories, 03_normalize, 03_gap_detection
                     (cached by Novelty Guard — same inputs, same kb_snapshot_id)
```

**Registry behavior on re-run:**
- New problems from re-run committed as `review_status: draft`
- Existing `approved` problems are never overwritten — only superseded if explicitly promoted
- `registry/problems.jsonl` is append-only; diff between runs is computable via `created_by` field
- `run_log.jsonl` records re-run with reference to prior run ID for traceability

**Trigger conditions:**
- New model available with meaningfully better benchmark scores
- `hallucination_risk: high` count in registry exceeds threshold (to be defined in Z-01 area)
- Manual trigger for specific subdomains only

**Affects:** `pipeline/steps/09_commit.md` (v2), `registry/run_log.jsonl` schema

---

### O-03 · Quality Gate for Flagged Problems (Online LLM — Optional)
**Status:** Unresolved — design agreed, implementation deferred.
**Scope:** Problems flagged as `hallucination_risk: medium | high` by `07_hallucination_scan` are candidates for an additional external validation pass.
**Design:**
- This is **not** a pipeline step — it is a post-commit quality gate, manually triggered
- Operates on `registry/problems.jsonl` filtered by `hallucination_risk` and `review_status: draft`
- Uses an online LLM (e.g. Claude, GPT-4) as independent second opinion
- Result feeds into `review_status` promotion: `draft → reviewed`
- Resolves O-02 (Review Status Workflow) for the high-risk subset
**Constraint:** Must remain optional — pipeline runs must be fully offline-capable (briefing decision preserved)
**Decision pending.** Non-blocking. Relevant from Tier-1 automation wave onward (~65 subdomains).

---

## Hardware Roadmap

**Current setup:** Dell 3630 · i7-8700 · 128 GB RAM · RTX 5060 Ti 16 GB VRAM

### Model capability over time

| Timeframe | Realistic local models | Notes |
|---|---|---|
| Now | 19B/A3B (65 T/s), 35B/A3B (30 T/s), 122B/A10B (slow) | MoE models fit VRAM efficiently; 122B via CPU offload |
| +3 months | 30B dense in 16 GB VRAM plausible | Quantization improving; Q4_K_M standard |
| +6 months | 70B MoE at 35B/A3B speeds realistic | Architecture efficiency gains |
| +12 months | 122B class at current 35B speeds | Hardware + software co-evolution |

### Why this matters for the pipeline
- `04b_generation_review` (122b) is the current bottleneck — ~650 calls for 65 subdomains
- As 122b gets faster, re-run cost drops proportionally
- `policy.model` is a string field — swapping `"122b"` to `"next_gen_model"` requires one config change, no pipeline restructuring
- The Novelty Guard ensures only changed/new categories are re-processed — re-run cost scales with delta, not full corpus

### Upgrade path
Each re-run is a natural model benchmark: compare `07_hallucination_scan` flag rates across runs to measure real-world quality improvement on your specific subdomain set.

---

## Relationship to Existing Files

| File (original) | Status | Action |
|---|---|---|
| `core/envelope.md` | Unchanged | Reference only |
| `core/run.md` | Adapt (E-03) | Incorporate into v2 files |
| `core/novelty_guard.md` | Unchanged | Reference only |
| `core/content_states.md` | Unchanged | Reference only |
| `steps/00_step_registry.md` | **Do not modify** | Reference only |
| `steps/06_clarification.md` | Adapt (E-01) | Incorporate into v2 step |
| `steps/03_enrichment_02_unit_normalization.md` | Adapt (E-04) | Incorporate into v2 step |
| `schemas/*.schema.json` | Adapt (E-02) | Incorporate into v2 schema |
| `core/envelope.md` | Adapt (E-06) | Add `model` field to policy schema |
| `steps/04_hypothesis.md` | Adapt (E-05, E-06) | Split into 04a + 04b, model routing |

---

*This document is updated during coding as new decisions are made.*
