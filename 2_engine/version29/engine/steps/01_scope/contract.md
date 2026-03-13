# Contract — 01_scope

## Accepted Input
- `domain` (string, required)

## Rejected Input
- any downstream artifact (seed_set, categories, problems)
- hidden assumptions about problem style or difficulty

## Operation
Transform `domain` into a scoped boundary description.
Do not expand scope beyond explicit domain definition.

## Output
- `boundaries` (list[str]) — in-scope topic areas
- `exclusions` (list[str]) — explicitly out-of-scope areas
- `confidence_score` (float)

## Stop Conditions
- missing `domain`
- LLM response contains no parseable JSON object
- explicit quality gate failure
