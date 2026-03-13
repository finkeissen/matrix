# Step 07_examination_01 — Weakness Scan
## Identify Weakly Supported Matched Criteria

**Version:** 2.0.0
**Parent step:** `07_examination` (v1)
**Track:** All tracks
**Deterministic:** No (LLM — adversarial role)
**Upstream:** `05_validation.md` → `validation_report` (valid candidate only)
**Downstream:** `07_examination_02_alternative_check.md`

---

## Why This Was Split

In v1, `07_examination` asked the LLM to simultaneously scan for weak criteria, identify alternative AKUs, check low-confidence facts, and produce a combined accept/reject decision. For small LLMs this produces shallow analysis on all fronts. Weakness scanning is now isolated: focus entirely on whether each matched criterion is robustly supported.

---

## Single LLM Task

> **For each matched criterion, determine whether the supporting case fact is strong, ambiguous, or weak. Assign a severity. Do not look for alternatives yet.**

---

## Contract

```
update(state, inputs={ candidate, validation_report, facts_normalized, confidence }, params) -> (patches, report)
```

### Inputs

| Field | Type | Required |
|-------|------|----------|
| `candidate` | `HypothesisResult` | Yes |
| `validation_report` | `ValidationReport` | Yes — must have `valid: true` |
| `facts_normalized` | key-value object | Yes |
| `confidence` | `{ field: score }` | Yes — from `01_parsing_02` |

### Prompt (Full Template)

```
You are a strict criteria examiner. Assess the strength of each matched criterion.

CANDIDATE: {candidate_id}

MATCHED CRITERIA AND SUPPORTING FACTS:
{matched_criteria_with_fact_values}

CONFIDENCE SCORES FOR FACTS USED:
{confidence_subset}

RULES:
1. For each matched criterion, assess the supporting evidence:
   - "strong": fact value clearly and unambiguously satisfies the criterion
   - "ambiguous": value satisfies criterion but measurement method, timing, or context is unclear
   - "weak": value barely meets threshold, or supporting fact has confidence < 0.75
2. Output one entry per criterion.
3. Flat JSON only. No explanation outside the "issue" field.

OUTPUT FORMAT:
{
  "assessments": [
    {
      "criterion": "<criterion_string>",
      "strength": "strong | ambiguous | weak",
      "issue": "<brief description or null>"
    }
  ]
}
```

### Output Schema

```json
{
  "candidate_id": "AKU-00123",
  "assessments": [
    {
      "criterion": "Fasting plasma glucose >= 7.0 mmol/L on two separate occasions",
      "strength": "ambiguous",
      "issue": "Value confirmed (8.21 mmol/L) but separate-day requirement not documented in facts."
    },
    {
      "criterion": "autoimmune_markers_present == false",
      "strength": "strong",
      "issue": null
    }
  ],
  "weak_or_ambiguous_count": 1
}
```

### Severity Mapping (Post-LLM)

Applied deterministically after LLM output:

| LLM Strength | Severity | Action in 07_02 |
|-------------|----------|-----------------|
| `strong` | none | No action |
| `ambiguous` | medium | Flag; accept unless 07_02 finds better alternative |
| `weak` | high | Reject candidate; retry 04_hypothesis |

### Patches Produced

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `WeaknessScanResult` | Always |
| `create` | `ReviewQueueEntry` | If any `ambiguous` or `weak` assessments |

### Report Fields

```json
{
  "status": "ok | warn | reject",
  "criteria_assessed": 2,
  "strong_count": 1,
  "ambiguous_count": 1,
  "weak_count": 0,
  "routing": "proceed_to_alternative_check | reject"
}
```

If any `weak` assessment exists → `routing: reject` → pipeline returns to `04_hypothesis` without proceeding to `07_examination_02`.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| LLM returns non-JSON | Retry once; then treat all criteria as `ambiguous` |
| LLM omits a matched criterion | Treat omitted criterion as `ambiguous`; log warning |
| All criteria `strong` | `status: ok`; routing: proceed |

---

## Example

**Matched criteria:** 
1. `fasting_plasma_glucose >= 7.0 mmol/L (×2)` — value: 8.21, confidence: 0.98
2. `autoimmune_markers_present == false` — value: false, confidence: 0.91

**LLM assessment:**
- Criterion 1: `ambiguous` — separate-day timing not documented
- Criterion 2: `strong` — explicitly stated

**Routing:** proceed to `07_examination_02` (no `weak` criteria found).
