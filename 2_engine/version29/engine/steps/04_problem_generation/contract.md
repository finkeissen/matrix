# Contract — 04_problem_generation

## Accepted Input
- `domain` (string, required)
- `categories` (list[str], from 03_categories)

## Rejected Input
- validation results, dedup results, ranking artifacts

## Operation
For each category, call LLM with problem-style variants.
Parse and hash each problem. Apply style rotation.

## Output
- list of problem objects, each with:
  - `title`, `problem_statement`, `category`, `difficulty`
  - `problem_hash` (sha1)
  - `_prompt_version`, `_prompt_hash`

## Stop Conditions
- categories list empty
- LLM returns no parseable problems for any category
- problem_hash collision within same batch
