from pathlib import Path

def run(run_dir: Path) -> Path:
    out = run_dir / "extractions.jsonl"
    if not out.exists():
        out.write_text("", encoding="utf-8")
    return out
