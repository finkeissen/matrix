from pathlib import Path

def run(run_dir: Path) -> Path:
    src = run_dir / "extractions.jsonl"
    out = run_dir / "canonical_claims.jsonl"
    out.write_text(src.read_text(encoding="utf-8") if src.exists() else "", encoding="utf-8")
    return out
