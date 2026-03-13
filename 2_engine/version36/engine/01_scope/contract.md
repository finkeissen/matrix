# Contract — 01_scope

## Accepted Input
```json
{
  "domain": "thermodynamics"
}
```
| Field    | Type   | Required | Description                  |
|----------|--------|----------|------------------------------|
| `domain` | string | yes      | Target domain for this run   |

## Forbidden Context
- seed_set, categories, problems, validation results, or any step 02–08 artifact
- implicit assumptions about problem difficulty or style

## Operation
Call LLM with `domain` to produce scope boundaries.
Strip `<think>` reasoning blocks. Parse first JSON object from response.
On LLM failure: apply deterministic fallback (3 boundaries, 2 exclusions).

## Output Schema
```json
{
  "boundaries": ["string", "..."],
  "exclusions": ["string", "..."],
  "confidence_score": 0.8,
  "_domain": "thermodynamics",
  "_prompt_version": "v1",
  "_prompt_hash": "abc123..."
}
```
| Field               | Type          | Required |
|---------------------|---------------|----------|
| `boundaries`        | list[string]  | yes      |
| `exclusions`        | list[string]  | yes      |
| `confidence_score`  | float 0..1    | no       |
| `_domain`           | string        | yes      |
| `_prompt_version`   | string        | yes      |
| `_prompt_hash`      | string        | yes      |

## Invariants
- `len(boundaries) >= 1`
- `len(exclusions) >= 0`
- `_domain` == input `domain`

## Stop Conditions
| Condition                          | Outcome |
|------------------------------------|---------|
| `domain` missing or empty          | FAIL    |
| LLM returns no parseable JSON      | FALLBACK (not FAIL) |
| Quality gate: boundaries empty     | FAIL    |

## Example Input / Output
**Input:**
```json
{"domain": "thermodynamics"}
```
**Output:**
```json
{
  "boundaries": ["heat transfer", "thermodynamic cycles", "entropy and irreversibility"],
  "exclusions": ["history of thermodynamics", "biographical content"],
  "confidence_score": 0.85,
  "_domain": "thermodynamics",
  "_prompt_version": "v1",
  "_prompt_hash": "d4e5f6..."
}
```
