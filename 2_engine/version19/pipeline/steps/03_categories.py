from __future__ import annotations
import json

def run(ctx, domain, config, prompt_loader):
    out = ctx.intermediate_dir() / '03_categories.json'
    categories = [
        {'category': f'{domain}_foundations'},
        {'category': f'{domain}_applications'},
        {'category': f'{domain}_analysis'},
    ]
    out.write_text(json.dumps(categories, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'data': categories, 'output_path': str(out), 'counts': {'categories': len(categories)}}
