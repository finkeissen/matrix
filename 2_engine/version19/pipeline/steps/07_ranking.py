from __future__ import annotations
import json

def run(ctx, domain, config, prompt_loader):
    in_path = ctx.intermediate_dir() / '06_deduplication.json'
    data = json.loads(in_path.read_text(encoding='utf-8'))
    accepted = data.get('accepted', []) if isinstance(data, dict) else data
    ranked = list(sorted(accepted, key=lambda p: (p.get('difficulty') != 'hard', p.get('category', ''))))
    out = ctx.intermediate_dir() / '07_ranking.json'
    out.write_text(json.dumps(ranked, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'data': ranked, 'output_path': str(out), 'counts': {'ranked': len(ranked)}}
