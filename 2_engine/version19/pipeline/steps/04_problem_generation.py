from __future__ import annotations
import json
from datetime import datetime, timezone

def run(ctx, domain, config, prompt_loader):
    cats_path = ctx.intermediate_dir() / '03_categories.json'
    categories = json.loads(cats_path.read_text(encoding='utf-8')) if cats_path.exists() else [{'category': domain}]
    problems = []
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for idx, item in enumerate(categories, start=1):
        cat = item['category']
        problems.append({
            'problem_id': f'ap_{idx:03d}',
            'title': f'{cat.replace("_", " ").title()} scenario {idx}',
            'problem_statement': f'Analyze a representative {domain} problem in category {cat} and determine the governing result with a justified solution path.',
            'category': cat,
            'difficulty': 'medium' if idx % 3 else 'hard',
            'source_run_id': ctx.manifest.run_id,
            'created_at': now,
        })
    out = ctx.intermediate_dir() / '04_problem_generation.json'
    out.write_text(json.dumps(problems, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'data': problems, 'output_path': str(out), 'counts': {'generated': len(problems)}}
