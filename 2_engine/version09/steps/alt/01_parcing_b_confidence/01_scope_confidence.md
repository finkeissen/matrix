# Envelope: 01_scope_confidence

**Parent step:** `01_scope`
**Type:** `llm`
**Model:** `19b`
**Upstream:** `01_scope` → `scope`
**Downstream:** `02_retrieval`

---

## TaskEnvelope

```json
{
  "envelope_version": "1.0.0",
  "step": "01_scope_confidence",
  "parent_step": "01_scope",
  "type": "llm",
  "inputs": {
    "scope_hash": "<sha256 of scope.json>",
    "kb_snapshot_id": "<sha256 of subdomains.jsonl>"
  },
  "input_snapshot_id": "<sha256 of subdomains.jsonl>",
  "expected_outputs": [
    {
      "key": "scope_confidence",
      "path": "runs/<run_id>/artifacts/01_scope_confidence/scope_confidence.json",
      "required": true
    }
  ],
  "policy": {
    "retries": 1,
    "timeout_sec": 30,
    "priority": "normal",
    "novelty_guard": true,
    "model": "19b"
  },
  "provenance": {
    "created_by": "orchestrator",
    "reason": "scope_quality_assessment"
  }
}
```

---

## Prompt (Algebra — SD-001)

```
You are a precise academic knowledge engineer. Your task is to assess the quality and clarity of a scope definition for an atomic problem generation pipeline.

You will receive a scope object for the subdomain Algebra (SD-001, Mathematics). Evaluate it on three dimensions and return a structured confidence report.

Input scope:
<SCOPE_JSON>

Evaluate the scope on the following three dimensions. For each, assign a score from 0.0 to 1.0:

1. boundary_clarity (0.0–1.0): Are the boundaries specific enough to decide unambiguously whether a given problem belongs in this subdomain? A score of 1.0 means every boundary item is precise and testable. A score below 0.6 means boundaries are too vague to use as a filter.

2. exclusion_coverage (0.0–1.0): Do the exclusions cover the most likely confusion areas? A score of 1.0 means all adjacent subdomains are explicitly excluded. A score below 0.6 means important adjacent areas are missing.

3. ambiguity_resolution (0.0–1.0): Are the ambiguity resolutions clear and actionable? A score of 1.0 means every boundary case has a decisive, unambiguous resolution. A score below 0.6 means resolutions are vague or missing.

Then compute:
- overall_score: arithmetic mean of the three dimension scores, rounded to 2 decimal places
- recommendation: "proceed" if overall_score >= 0.70, otherwise "clarify"

Flag any specific ambiguities that remain unresolved or any boundaries that are too vague to use as a generation filter.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "scores": {
    "boundary_clarity": <float 0.0–1.0>,
    "exclusion_coverage": <float 0.0–1.0>,
    "ambiguity_resolution": <float 0.0–1.0>
  },
  "overall_score": <float 0.0–1.0>,
  "recommendation": "proceed" | "clarify",
  "flagged_ambiguities": [
    {
      "topic": <string: the ambiguous topic>,
      "issue": <string: what is unclear or missing>,
      "severity": "low" | "medium" | "high"
    }
  ],
  "notes": <string or null: any additional observations>
}
```

---

## Expected Output Schema

```json
{
  "subdomain": "string",
  "subdomain_id": "string",
  "scores": {
    "boundary_clarity": "number (0.0–1.0)",
    "exclusion_coverage": "number (0.0–1.0)",
    "ambiguity_resolution": "number (0.0–1.0)"
  },
  "overall_score": "number (0.0–1.0)",
  "recommendation": "proceed | clarify",
  "flagged_ambiguities": [
    {
      "topic": "string",
      "issue": "string",
      "severity": "low | medium | high"
    }
  ],
  "notes": "string | null"
}
```

## Routing (post-LLM, deterministic)

```
recommendation = "proceed"   → 02_retrieval
recommendation = "clarify"   → 06_clarification (scope refinement loop, max 2 rounds per E-01)
```

Scores outside 0.0–1.0 are clamped and logged as a warning — no STOP.

## Reference Output (for validation and testing)

```json
{
  "subdomain": "Algebra",
  "subdomain_id": "SD-001",
  "scores": {
    "boundary_clarity": 0.92,
    "exclusion_coverage": 0.88,
    "ambiguity_resolution": 0.85
  },
  "overall_score": 0.88,
  "recommendation": "proceed",
  "flagged_ambiguities": [
    {
      "topic": "Linear algebra vs. Functional analysis boundary",
      "issue": "Resolution correctly excludes functional analysis but does not address multilinear algebra (tensors). May generate tensor problems without clear guidance.",
      "severity": "low"
    }
  ],
  "notes": "Scope is well-defined for a Tier-1 subdomain. Canonical source covers undergraduate through graduate level adequately."
}
```

---

## Content State on Completion
`candidate`

## STOP Conditions
- LLM returns non-JSON after 1 retry → `llm_output_invalid`
- `recommendation` field missing or not one of `proceed | clarify` → `llm_output_invalid`
- `overall_score` missing → `llm_output_invalid`
