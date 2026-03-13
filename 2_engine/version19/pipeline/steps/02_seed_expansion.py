from __future__ import annotations
import json
from datetime import datetime, timezone

def run(ctx, domain, config, prompt_loader):
    out = ctx.intermediate_dir() / '02_seed_expansion.json'
    data = {
        'domain': domain,
        'seeds': [domain, f'intro_to_{domain}', f'advanced_{domain}'],
        'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'data': data, 'output_path': str(out), 'counts': {'seeds': len(data['seeds'])}}
