"""Structural admissibility + STOP trigger scan.

This stage intentionally performs only *shallow* checks:
- required files/dirs exist
- README/stress_test contain a few required keys (as lightweight guardrails)
- scan for authority-claim phrasing that would violate the engine's "non-claims"

Output:
  - validation_report.json
  - decision.json  (approved/outcome + reasons)
"""
import time, re
from pathlib import Path
from engine.utils.fs import write_json

REQUIRED_FILES = ["README.md", "stress_test.md", "job.json"]
REQUIRED_DIRS = ["raw"]

AUTHORITY_PATTERNS = [
    r"\b(proven|proof|true|truth|correct|validated|guarantee|must be)\b",
    r"\b(therefore|hence|thus)\s+.*\b(true|correct|valid)\b",
    r"\b(authority|authoritative|endorsed|official)\b",
]

REQUIRED_README_KEYS = ["purpose", "scope", "non-goals", "roles", "constraints"]
REQUIRED_STRESS_KEYS = ["illegitimate transfer", "counterfactual"]

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def run(run_dir: Path) -> Path:
    ts = time.time()
    reasons = []
    stop_triggers = []
    text_blobs = ""

    for d in REQUIRED_DIRS:
        if not (run_dir / d).exists():
            reasons.append(f"missing required dir: {d}")

    for f in REQUIRED_FILES:
        if not (run_dir / f).exists():
            reasons.append(f"missing required file: {f}")

    readme = run_dir / "README.md"
    stress = run_dir / "stress_test.md"

    if readme.exists():
        t = _read_text(readme).lower()
        text_blobs += "\n" + t
        missing = [k for k in REQUIRED_README_KEYS if k not in t]
        if missing:
            reasons.append(f"README.md missing keys: {', '.join(missing)}")

    if stress.exists():
        t = _read_text(stress).lower()
        text_blobs += "\n" + t
        missing = [k for k in REQUIRED_STRESS_KEYS if k not in t]
        if missing:
            reasons.append(f"stress_test.md missing keys: {', '.join(missing)}")

    for pat in AUTHORITY_PATTERNS:
        if re.search(pat, text_blobs, flags=re.IGNORECASE):
            stop_triggers.append(f"SR-01/SR-03 heuristic match: /{pat}/")

    if stress.exists() and "counterfactual" not in _read_text(stress).lower():
        stop_triggers.append("SR-02 heuristic: missing counterfactual marker")

    if reasons:
        outcome = "inadmissible"
        approved = False
    else:
        if stop_triggers:
            outcome = "STOP"
            approved = False
        else:
            outcome = "admissible"
            approved = True

    report = {
        "run_id": run_dir.name,
        "ts": ts,
        "approved": approved,
        "outcome": outcome,
        "reasons": reasons,
        "stop_triggers": stop_triggers,
        "required_files": REQUIRED_FILES,
        "required_dirs": REQUIRED_DIRS,
    }
    write_json(run_dir / "validation_report.json", report)
    write_json(run_dir / "decision.json", {"approved": approved, "outcome": outcome, "reasons": reasons, "stop_triggers": stop_triggers})
    return run_dir / "validation_report.json"