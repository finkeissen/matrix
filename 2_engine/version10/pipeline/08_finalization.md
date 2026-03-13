# Envelope: 08_finalization

**Parent step:** `08_finalization`
**Type:** `deterministic` + 1 LLM call (run summary only)
**Model:** `19b` (LLM part only)
**Upstream:** all `04b_generation_review` outputs, `07_examination_02_alternative_check` → `alternative_check`, `07_examination_01_hallucination_scan` → `hallucination_report`, `01_scope` → `scope`
**Downstream:** `09_commit`
**Snapshot after:** yes (pre-commit checkpoint)

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "08_finalization",
  "parent_step": "08_finalization",
  "type": "llm",
  "inputs": {
    "problems_reviewed_hashes": ["<sha256 per category>"],
    "hallucination_report_hash": "<sha256 of hallucination_report.json>",
    "alternative_check_hash": "<sha256 of alternative_check.json>",
    "scope_hash": "<sha256 of scope.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>",
    "pipeline_status": "validated | partial | insufficient"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "final_problems",
      "path": "runs/<run_id>/artifacts/08_finalization/final_problems.jsonl",
      "required": true
    },
    {
      "key": "run_audit",
      "path": "runs/<run_id>/artifacts/08_finalization/run_audit.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 60,
    "priority": "normal",
    "novelty_guard": true,
    "model": "19b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "assign_ids_and_produce_final_output"
  }
}
```

---

## What This Step Does

**Phase 1 — Deterministic assembly:**
- Merge all `04b_generation_review` outputs across categories into a single ordered list
- Apply hallucination risk corrections from `hallucination_report` (override per-problem `hallucination_risk`)
- Assign `problem_id` to each problem: 5-char prefix (E-02) + zero-padded sequential index
- Assign `subdomain_id`, `domain_id`, `parent_domain`, `subdomain_label` from scope
- Assign `created_by`: `pipeline_v1/run_<NNN>` (from `run_id`)
- Assign `created_at`: current ISO 8601 timestamp
- Assign `review_status`: `draft` (all problems start as draft)
- Write output as JSONL — one problem per line, schema-compliant with `atomic_problem.schema.json`

**Phase 2 — LLM run summary (19b):**
- Generate a brief human-readable summary of the run (2–4 sentences)
- Included in `run_audit.json` as `run_summary` field
- Fails gracefully: if LLM times out, `run_summary` is set to `null` — delivery continues

---

## problem_id Assignment (E-02)

```python
def derive_prefix(subdomain_label: str) -> str:
    # Normalize umlauts
    label = label.replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    words = re.split(r"[\s&/]+", label)
    stopwords = {"und", "and", "of", "the"}
    content_words = [w for w in words if w.lower() not in stopwords and w]
    if len(content_words) == 1:
        return content_words[0][:5].upper()
    else:
        initials = "".join(w[0] for w in content_words)
        return initials[:5].upper().ljust(5, content_words[-1][1].upper())

# Collision check at runtime — append -A or -B if prefix already registered
```

---

## Output: final_problems.jsonl

One JSON object per line. Each line is a valid `atomic_problem` instance per `atomic_problem.schema.json`.

```jsonl
{"problem_id":"ALGEB-0001","subdomain_id":"SD-001","domain_id":"D-01","parent_domain":"Mathematics","subdomain_label":"Algebra","title":"...","problem_statement":"...","category":"Equations and Inequalities","difficulty":"basic","answer_type":"factual","canonical_source":"...","verifiable":true,"hallucination_risk":"low","requires_context":false,"tags":["..."],"created_by":"pipeline_v1/run_001","created_at":"2026-03-04T10:00:00Z","review_status":"draft"}
```

## Output: run_audit.json

```json
{
  "run_id": "string",
  "subdomain_id": "SD-001",
  "subdomain_label": "Algebra",
  "kb_snapshot_id": "string",
  "pipeline_status": "validated | partial | insufficient",
  "total_problems": "integer",
  "problems_by_category": { "category_name": "integer" },
  "problems_by_difficulty": { "basic": "integer", "intermediate": "integer", "advanced": "integer", "expert": "integer" },
  "problems_by_hallucination_risk": { "low": "integer", "medium": "integer", "high": "integer" },
  "hallucination_corrections_applied": "integer",
  "clarification_rounds": "integer",
  "generation_retries": "integer",
  "run_summary": "string | null",
  "system_version": "2.0.0",
  "finalized_at": "ISO 8601 timestamp"
}
```

---

## Content State on Completion
All problems in `final_problems.jsonl`: `candidate` → promoted to `verified` after `09_commit` succeeds

## STOP Conditions
- Audit write failure → `audit_write_failure` (hard STOP — do not commit without audit)
- JSONL output unwritable → `deterministic_step_error`
- `problem_id` prefix collision unresolvable (> Z options) → `deterministic_step_error`
