# Contract — 03_categories

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "seeds": ["thermodynamics", "heat engines", "..."],
  "seed_sources": {"generated": 3, "curated": 2, "final": 5}
}
```
| Field    | Type         | Required | Source            |
|----------|--------------|----------|-------------------|
| `domain` | string       | yes      | run param         |
| `seeds`  | list[string] | yes      | 02_seed_expansion |

## Forbidden Context
- problems, validation results, rankings, export paths
- any artifact from steps 04–08

## Operation
Load taxonomy from `IngestionLoader.load_taxonomy(domain)`.
If taxonomy exists: use it verbatim (filtered to non-empty strings).
If empty/missing: derive 3 fallback categories from domain slug.

## Output Schema
```json
{
  "domain": "thermodynamics",
  "categories": ["string", "..."],
  "category_source": "ingestion_taxonomy",
  "created_at": "2026-03-11T10:00:00Z"
}
```
| Field             | Type         | Required | Values                              |
|-------------------|--------------|----------|-------------------------------------|
| `domain`          | string       | yes      |                                     |
| `categories`      | list[string] | yes      | min 1                               |
| `category_source` | string       | yes      | `"ingestion_taxonomy"` or `"fallback"` |

## Invariants
- `len(categories) >= 1`
- All category strings are non-empty after strip
- `category_source` reflects actual source used

## Stop Conditions
| Condition                           | Outcome  |
|-------------------------------------|----------|
| `domain` missing                    | FAIL     |
| Category list empty after filtering | FAIL     |
| Taxonomy file malformed             | FALLBACK |

## Example Input / Output
**Input:**
```json
{"domain": "thermodynamics", "seeds": ["thermodynamics", "heat engines"]}
```
**Output:**
```json
{
  "domain": "thermodynamics",
  "categories": ["first_law", "second_law", "heat_transfer", "thermodynamic_cycles"],
  "category_source": "ingestion_taxonomy",
  "created_at": "2026-03-11T10:00:00Z"
}
```
