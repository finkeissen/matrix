from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def find_latest_run(runs_dir: Path, *, after_mtime: float | None = None) -> Path | None:
    candidates = [p for p in runs_dir.iterdir() if p.is_dir()] if runs_dir.exists() else []
    if after_mtime is not None:
        filtered = []
        for path in candidates:
            try:
                if path.stat().st_mtime >= after_mtime:
                    filtered.append(path)
            except FileNotFoundError:
                continue
        candidates = filtered
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: (p.stat().st_mtime, p.name))[-1]


def load_run_artifacts(run_dir: Path) -> dict[str, Any]:
    exports = run_dir / "exports"
    manifest_name = "manifest.json" if (run_dir / "manifest.json").exists() else "run_manifest.json"
    manifest = load_json(run_dir / manifest_name)
    metrics = load_json(exports / "metrics.json") if (exports / "metrics.json").exists() else {}
    run_health = load_json(exports / "run_health.json") if (exports / "run_health.json").exists() else {}
    summary = load_json(exports / "summary_report.json") if (exports / "summary_report.json").exists() else {}
    return {
        "manifest": manifest,
        "metrics": metrics,
        "run_health": run_health,
        "summary_report": summary,
    }
