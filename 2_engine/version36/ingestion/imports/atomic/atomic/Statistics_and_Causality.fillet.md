# Statistics and Causality — Fillet

## 1. Core Formal Structure
Statistics provides tools for inference from data:
- estimators, confidence intervals,
- hypothesis tests,
- likelihood/posterior inference,
- model selection and prediction.

Causality frameworks (e.g., DAGs, potential outcomes) add:
- intervention semantics,
- identifiability conditions,
- causal effect estimands.

## 2. Standard Interpretation
Statistical outputs are commonly treated as:
- direct evidence of causal truth,
- objective measures of “importance,”
- or proof of real effects independent of modeling choices.

## 3. Illicit Upgrades
- **Correlation → causation**: interpreting association as causal effect without an intervention model.
- **Significance → importance**: converting p-values into epistemic or practical weight.
- **Fit → truth**: treating predictive success as ontological confirmation.
- **Model assumptions → reality**: forgetting that identifiability hinges on untestable structural assumptions.

## 4. Failure Modes
- P-hacking and garden-of-forking-paths as hidden flexibility.
- Confusing frequentist long-run guarantees with single-study claims.
- Treating “no evidence” as “evidence of no effect.”
- Reifying latent variables introduced for convenience.

## 5. What Survives
- Statistical claims as **conditional**: valid given a model, sampling process, and error structure.
- Causal claims as **intervention-relative**: valid given an explicit causal graph or potential outcomes assumptions.
- Robustness checks, sensitivity analysis, and preregistration as practical guardrails.

## 6. How It Reconnects
- Connects as: **Inference and Interface Layer** between data and models in the Matrix.
- Requires explicit metadata: data-generating assumptions, estimand, identification strategy, and uncertainty interpretation.
- Guardrail: never treat statistical formalisms as metaphysical truth-makers.
