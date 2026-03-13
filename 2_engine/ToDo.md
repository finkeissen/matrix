# Umbau: Step-orientierte Engine mit separaten `run/`-Ordnern

## Ziel

Die Engine wird so umgestellt, dass jeder Step als **eigene Arbeitseinheit** gedacht ist:

Input -> Step -> Output

Dafür gibt es jetzt zwei Ebenen:

1. **Statische Step-Arbeitspakete im Repo**
   - `engine/steps/<step>/README.md`
   - `engine/steps/<step>/contract.md`
   - `engine/steps/<step>/run/`

2. **Konkrete Laufzeit-Artefakte pro Run**
   - `data/runs/<run-id>/steps/<step>/run/input.json`
   - `data/runs/<run-id>/steps/<step>/run/output.json`

---

## Neue Struktur

```text
engine/
  steps/
    01_scope/
      README.md
      contract.md
      run/
    02_seed_expansion/
      README.md
      contract.md
      run/
    03_categories/
      README.md
      contract.md
      run/
    04_problem_generation/
      README.md
      contract.md
      run/
    05_validation/
      README.md
      contract.md
      run/
    06_deduplication/
      README.md
      contract.md
      run/
    07_ranking/
      README.md
      contract.md
      run/
    08_export/
      README.md
      contract.md
      run/


Input -> 01_scope -> Output
Output -> 02_seed_expansion -> Output
Output -> 03_categories -> Output
Output -> 04_problem_generation -> Output
Output -> 05_validation -> Output
Output -> 06_deduplication -> Output
Output -> 07_ranking -> Output
Output -> 08_export -> Output



---

## Beispiel-Step: `engine/steps/01_scope/README.md`

```md
# 01_scope

## Purpose
Local work package for `01_scope`.

## Boundary
This step should be executable from its declared input alone. It must not rely on hidden knowledge from later steps.

## Local flow
`domain` -> `01_scope` -> `scope`

## Runtime
During execution, step-local artifacts are written to:

```text
runs/<run-id>/steps/01_scope/run/
  input.json
  output.json



---

## Beispiel-Step: `engine/steps/01_scope/contract.md`

```md
# Contract — 01_scope

## Accepted Input
- `domain`
- explicit upstream artifact only

## Rejected Input
- hidden assumptions from downstream steps
- undeclared side-channel context

## Operation
Transform the declared input into `scope` without expanding scope.

## Output
- `scope`
- machine-readable artifact in `run/output.json` at runtime

## Stop Conditions
- missing required upstream artifact
- invalid or structurally inadmissible payload
- explicit quality gate failure


engine/steps/02_seed_expansion/
engine/steps/03_categories/
engine/steps/04_problem_generation/
engine/steps/05_validation/
engine/steps/06_deduplication/
engine/steps/07_ranking/
engine/steps/08_export/


from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepSpec:
    name: str
    module_path: str
    input_label: str
    output_label: str

    @property
    def slug(self) -> str:
        return self.name


STEP_SPECS: tuple[StepSpec, ...] = (
    StepSpec('01_scope', 'pipeline.steps.01_scope', 'domain', 'scope'),
    StepSpec('02_seed_expansion', 'pipeline.steps.02_seed_expansion', 'scope+domain', 'seed_set'),
    StepSpec('03_categories', 'pipeline.steps.03_categories', 'scope+seed_set', 'categories'),
    StepSpec('04_problem_generation', 'pipeline.steps.04_problem_generation', 'categories', 'generated_problems'),
    StepSpec('05_validation', 'pipeline.steps.05_validation', 'generated_problems', 'validated_problems'),
    StepSpec('06_deduplication', 'pipeline.steps.06_deduplication', 'validated_problems', 'deduplicated_problems'),
    StepSpec('07_ranking', 'pipeline.steps.07_ranking', 'deduplicated_problems', 'ranked_problems'),
    StepSpec('08_export', 'pipeline.steps.08_export', 'ranked_problems', 'export_bundle'),
)

STEP_MAP = {spec.name: spec for spec in STEP_SPECS}


def all_step_names() -> list[str]:
    return [spec.name for spec in STEP_SPECS]


def get_step_spec(step_name: str) -> StepSpec:
    return STEP_MAP[step_name]



from .step_registry import get_step_spec

class RunContext:
    ...

    def step_dir(self, step_name: str) -> Path:
        spec = get_step_spec(step_name)
        p = self.run_dir / "steps" / spec.slug
        p.mkdir(parents=True, exist_ok=True)
        return p

    def step_run_dir(self, step_name: str) -> Path:
        p = self.step_dir(step_name) / "run"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def step_input_path(self, step_name: str) -> Path:
        return self.step_run_dir(step_name) / "input.json"

    def step_output_path(self, step_name: str) -> Path:
        return self.step_run_dir(step_name) / "output.json"

    def step_meta_path(self, step_name: str) -> Path:
        return self.step_run_dir(step_name) / "meta.json"

    def write_step_payload(self, step_name: str, kind: str, payload) -> Path:
        if kind not in {"input", "output", "meta"}:
            raise ValueError(f"Unsupported step payload kind: {kind}")
        path = getattr(self, f"step_{kind}_path")(step_name)
        data = payload if isinstance(payload, str) else json.dumps(payload, indent=2, ensure_ascii=False)
        path.write_text(data, encoding="utf-8")
        return path

def _run_step_with_retry(self, ctx: RunContext, step_name: str, domain: str) -> bool:
    existing = ctx.manifest.get_step(step_name)
    retry_count = existing.retry_count if existing else 0
    while retry_count <= self.max_retries:
        try:
            input_path = str(ctx.step_input_path(step_name))
            ctx.start_step(step_name, input_path=input_path)
            step_fn = self._load_step(step_name)
            result = step_fn(ctx, domain, self.config, self.prompt_loader)
            errors = self._validate_result(step_name, result)
            if errors:
                raise ValueError('; '.join(errors))
            ctx.complete_step(step_name, output_path=result.get('output_path'), counts=result.get('counts', {}))
            logger.info('step.completed', step=step_name, counts=result.get('counts', {}))
            return True
        except Exception as exc:
            retry_count += 1
            ctx.fail_step(step_name, type(exc).__name__, str(exc))
            if retry_count > self.max_retries:
                logger.error('step.failed_permanently', step=step_name, error=str(exc))
                return False
            record = ctx.manifest.get_step(step_name)
            if record:
                record.status = 'pending'
                ctx.manifest.status = 'running'
                ctx.manifest.upsert_step(record)
                ctx.save()
    return False



data/runs/<run-id>/steps/<step>/run/
  input.json
  output.json
  meta.json



def run(ctx, domain, config, prompt_loader):
    step_name = "01_scope"

    input_payload = {
        "domain": domain
    }
    ctx.write_step_payload(step_name, "input", input_payload)

    output_payload = {
        "scope": {
            "domain": domain
        }
    }
    output_path = ctx.write_step_payload(step_name, "output", output_payload)

    return {
        "data": output_payload,
        "output_path": str(output_path),
        "counts": {"scope_items": 1},
    }



Input_A -> Step1 -> Output_A
Output_A -> Step2 -> Output_B
Output_B -> Step3 -> Output_C


Nächster sinnvoller Ausbau

Als nächstes sollte jeder Step inhaltlich präzisiert werden:

Accepted Input

Rejected Input

Operation

Output Schema

Stop Conditions

Invariants

Example input/output

Dann wird aus der bloßen Ordnerstruktur echte Information-Hiding.


Wenn du willst, formatiere ich dir daraus im nächsten Schritt noch eine **vollständige Zielstruktur für alle 8 Steps** mit konkreten `contract.md`-Vorlagen pro Step.



