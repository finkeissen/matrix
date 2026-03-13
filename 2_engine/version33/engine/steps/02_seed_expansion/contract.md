# Contract — 02_seed_expansion

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "scope": {
    "boundaries": ["..."],
    "exclusions": ["..."]
  }
}
```
| Field    | Type   | Required | Source    |
|----------|--------|----------|-----------|
| `domain` | string | yes      | run param |
| `scope`  | object | yes      | 01_scope  |

## Forbidden Context
- categories, problems, validation results, dedup state
- any artifact from steps 03–08

## Operation
1. Generate LLM seeds from domain + scope (3 minimal seeds as baseline).
2. Load curated seeds from ingestion knowledge base (`IngestionLoader`).
3. Merge and deduplicate, preserving insertion order (generated first).

## Output Schema
```json
{
  "domain": "thermodynamics",
  "seeds": ["string", "..."],
  "seed_sources": {
    "generated": 3,
    "curated": 12,
    "final": 14
  },
  "created_at": "2026-03-11T10:00:00Z"
}
```
| Field                    | Type         | Required |
|--------------------------|--------------|----------|
| `domain`                 | string       | yes      |
| `seeds`                  | list[string] | yes      |
| `seed_sources.generated` | int          | yes      |
| `seed_sources.curated`   | int          | yes      |
| `seed_sources.final`     | int          | yes      |

## Invariants
- `seed_sources.final == len(seeds)`
- `len(seeds) >= 1`
- No duplicate seeds (case-insensitive, stripped)

## Stop Conditions
| Condition                        | Outcome  |
|----------------------------------|----------|
| `domain` missing                 | FAIL     |
| Final seed list empty after dedup | FAIL    |

## Example Input / Output
**Input:**
```json
{"domain": "thermodynamics", "scope": {"boundaries": ["heat transfer", "cycles"]}}
```
**Output:**
```json
{
  "domain": "thermodynamics",
  "seeds": ["thermodynamics", "thermodynamics workflows", "thermodynamics edge cases", "heat engines", "Carnot cycle"],
  "seed_sources": {"generated": 3, "curated": 2, "final": 5},
  "created_at": "2026-03-11T10:00:00Z"
}
```
