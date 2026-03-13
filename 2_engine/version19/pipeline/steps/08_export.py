from __future__ import annotations
import json

def run(ctx, domain, config, prompt_loader):
    in_path = ctx.intermediate_dir() / '07_ranking.json'
    ranked = json.loads(in_path.read_text(encoding='utf-8'))
    out = ctx.exports_dir() / 'atomic_problems.jsonl'
    with out.open('w', encoding='utf-8') as f:
        for item in ranked:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    return {'data': {'exported': len(ranked)}, 'output_path': str(out), 'counts': {'exported': len(ranked)}}
