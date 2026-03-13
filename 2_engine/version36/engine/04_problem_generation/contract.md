# Contract — 04_problem_generation

## Accepted Input
```json
{
  "domain": "thermodynamics",
  "categories": ["first_law", "second_law", "heat_transfer"],
  "category_source": "ingestion_taxonomy"
}
```
| Field             | Type         | Required | Source        |
|-------------------|--------------|----------|---------------|
| `domain`          | string       | yes      | run param     |
| `categories`      | list[string] | yes      | 03_categories |
| `category_source` | string       | no       | 03_categories |

## Forbidden Context
- validation results, dedup hashes, rankings
- registry state, export paths
- any artifact from steps 05–08

## Operation
For each category × style combination, call LLM with problem template.
Hash each problem with SHA1 over (title + problem_statement + category).
Deduplicate by hash within batch.

## Output Schema
```json
[
  {
    "title": "Analyze Heat Transfer",
    "problem_statement": "Given a steady-state heat conduction problem ...",
    "category": "heat_transfer",
    "difficulty": "medium",
    "problem_hash": "a1b2c3...",
    "_prompt_version": "v1",
    "_prompt_hash": "d4e5f6..."
  }
]
```
| Field               | Type   | Required |
|---------------------|--------|----------|
| `title`             | string | yes      |
| `problem_statement` | string | yes      |
| `category`          | string | yes      |
| `difficulty`        | string | yes — one of: `easy`, `medium`, `hard`, `expert` |
| `problem_hash`      | string | yes      |
| `_prompt_version`   | string | yes      |
| `_prompt_hash`      | string | yes      |

## Invariants
- `problem_hash` unique within this step's output
- `category` must be a value from input `categories`
- `difficulty` must be one of the four allowed values

## Stop Conditions
| Condition                                   | Outcome  |
|---------------------------------------------|----------|
| `categories` empty                          | FAIL     |
| LLM returns no parseable problems           | FAIL     |
| Hash collision within batch (same content)  | DEDUPE (silent drop) |
