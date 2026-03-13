# M07 — LLM Orchestrator
## Constrained Language Model Interface

**Layer:** Orchestration
**Version:** 2.0.0
**Deterministic:** No (LLM-based)
**Depends on:** M05 (retrieval), M06 (validation)
**Used by:** Pipeline stages 01, 03, 04, 06, 08
**Pipeline steps:** 01_parsing, 03_enrichment, 04_hypothesis, 06_clarification, 08_finalization

---

## Purpose

Provide a **strictly constrained interface** through which language models contribute to the pipeline. The LLM orchestrator enforces that every model invocation operates within declared boundaries: it may only use knowledge from the retrieved context, must cite AKU IDs, and must produce structured output.

The LLM is the language interface of the system — not its decision-maker. Every consequential decision (validation, acceptance, rejection) is made by deterministic modules.

---

## LLM Responsibilities

| Allowed | Prohibited |
|---------|------------|
| Extract structured case facts from user input | Access the knowledge base directly |
| Normalize terminology and units | Override validation results |
| Map case facts to AKU criteria | Introduce criteria not present in context |
| Propose candidate AKU IDs with citations | Make final accept/reject decisions |
| Generate targeted clarification questions | Express uncertainty as prose hedging |
| Produce user-facing natural language explanations | Fabricate AKU IDs or criteria |

---

## Invocation Roles

The orchestrator manages five distinct LLM roles. Each has a separate system prompt, input schema, and output contract.

### Role 1 — Parser

**Invoked by:** `01_parsing`
**Task:** Extract structured case facts from raw user input.

Prompt constraints:
```
Extract only facts explicitly stated in the input. Do not infer.
Assign a confidence score (0.0-1.0) to each extracted field.
Output as JSON. List unparseable fragments separately.
```

Output: `ParsedFacts` (see `01_parsing.md`)

### Role 2 — Enricher

**Invoked by:** `03_enrichment`
**Task:** Resolve terminology ambiguities; map colloquial terms to ontology-canonical field names.

Prompt constraints:
```
Use only the ontology terms provided in the context.
Map each ambiguous fact to exactly one canonical field.
Record all unit conversions with conversion factor.
```

Output: `EnrichedContext` (see `03_enrichment.md`)

### Role 3 — Generator

**Invoked by:** `04_hypothesis`
**Task:** Propose candidate AKU IDs based on case facts and retrieved context.

Prompt constraints (minimum, non-negotiable):
```
1. Use only the AKUs provided in this context. Do not introduce external knowledge.
2. Cite the AKU ID for every claim you make.
3. List matched criteria and missing criteria separately and explicitly.
4. Do not validate -- propose candidates only. Validation happens downstream.
5. If no AKU in the context is a plausible match, respond with status: NO_MATCH.
6. Express uncertainty as a structured field, not as hedging language.
```

Output: `HypothesisResult` (see `04_hypothesis.md`)

### Role 4 — Clarifier

**Invoked by:** `06_clarification`
**Task:** Generate targeted questions for missing required facts.

Prompt constraints:
```
One question per missing criterion. No more.
Each question must be answerable with structured data (yes/no, numeric, date, enum).
Use domain-canonical terminology. Do not reveal AKU IDs or system internals.
```

Output: `ClarificationRequest` (see `06_clarification.md`)

### Role 5 — Explainer

**Invoked by:** `08_finalization`
**Task:** Translate the validation result into a user-facing natural language explanation.

Prompt constraints:
```
Explain only what the validation report confirms. Do not add claims.
Use plain language appropriate for the domain and user type.
Mention weak points transparently but without alarming language.
Do not expose AKU IDs, internal scores, or pipeline structure.
```

Output: `explanation` field in `FinalAnswer`

---

## Required Output Schema (All Roles)

Every LLM response must include a structured `uncertainty` field:

```json
{
  "uncertainty": {
    "level": "none | low | medium | high",
    "reason": "string or null"
  }
}
```

Responses with prose hedging ("it may be...", "possibly...", "it is likely that...") instead of a structured `uncertainty` field are treated as schema violations and trigger a retry.

---

## Non-Determinism Handling

Every LLM invocation must be logged with:

```json
{
  "model_id": "claude-sonnet-4-20250514",
  "temperature": 0.0,
  "seed": null,
  "prompt_hash": "sha256:...",
  "raw_response": "...",
  "prompt_tokens": 1840,
  "completion_tokens": 412
}
```

The `raw_response` is stored verbatim in the run record. For replay, the stored response is returned instead of re-invoking the LLM.

---

## Prompt Construction Rules

1. **Context window budgeting:** Retrieved AKUs are included in order of rank until the context window budget is consumed. Lower-ranked AKUs are truncated before ancestor-path AKUs.
2. **Instruction block always first:** Constraints and output schema appear before any context or user data.
3. **No instruction-data mixing:** Context (AKUs, case facts) is in a clearly delimited block, separate from instructions.
4. **Schema in prompt:** The expected output JSON schema is always included in the prompt to enforce structure.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Malformed JSON output | Retry once; then return `status: error`; block pipeline |
| AKU ID cited not in context | Strip invalid citation; add warning to report; proceed |
| Prose hedging instead of structured uncertainty | Treat as schema violation; retry once |
| Context window exceeded | Trim lowest-ranked AKUs; log truncation; proceed |
| LLM unavailable | Return cached result if available for replay; else `status: degraded` |
| Max retries exceeded | Return `status: error`; route to finalization |
