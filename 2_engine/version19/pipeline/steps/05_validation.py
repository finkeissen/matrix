from __future__ import annotations
import json
from pipeline.validation.schema_validator import SchemaValidator
from pipeline.validation.business_rules import validate_business_rules
from pipeline.validation.content_checks import run_content_checks
from pipeline.validation.result_quality import run_quality_checks

def _write_errors(path, errors):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding='utf-8')

def run(ctx, domain, config, prompt_loader):
    validator = SchemaValidator(config)
    in_path = ctx.intermediate_dir() / '04_problem_generation.json'
    problems = json.loads(in_path.read_text(encoding='utf-8'))
    schema_errors = []
    business_errors = []
    content_errors = []
    quality_errors = []
    accepted = []
    for p in problems:
        se = validator.validate_artifact(p, 'atomic_problem')
        be = validate_business_rules('05_validation', p)
        ce = run_content_checks('05_validation', p)
        qe = run_quality_checks('05_validation', p)
        if se or be or ce or qe:
            schema_errors.extend(se)
            business_errors.extend(be)
            content_errors.extend(ce)
            quality_errors.extend(qe)
        else:
            accepted.append(p)
    rej = ctx.rejected_dir()
    _write_errors(rej / 'schema_errors.json', schema_errors)
    _write_errors(rej / 'business_rule_failures.json', business_errors)
    _write_errors(rej / 'content_failures.json', content_errors)
    _write_errors(rej / 'quality_errors.json', quality_errors)
    out = ctx.intermediate_dir() / '05_validation.json'
    out.write_text(json.dumps(accepted, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'data': accepted, 'output_path': str(out), 'counts': {'input': len(problems), 'accepted': len(accepted), 'rejected': len(problems) - len(accepted)}}
