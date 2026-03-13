# Engine Layout

The engine is organized as a sequence of independently executable steps.

Each step has two representations:

1. **Code path** in `pipeline/steps/*.py`
2. **Work package** in `engine/steps/<step>/`

The work package defines the local contract of the step and keeps the context deliberately small:

- `README.md` — purpose and local execution semantics
- `contract.md` — accepted input, operation, output, stop conditions
- `run/` — placeholder for step-local run artifacts during manual or scripted work

## Runtime layout

For every pipeline run, the engine also writes a step-local runtime envelope:

```text
runs/<run-id>/steps/<step>/run/
  input.json
  output.json
