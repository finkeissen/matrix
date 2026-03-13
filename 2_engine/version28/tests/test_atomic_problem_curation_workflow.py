import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pipeline" / "steps" / "00_atomic_problem_curation.py"
FIXTURE = ROOT / "data" / "test_fixtures" / "subdomains_fixture.jsonl"


def test_cli_help_runs():
    result = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert "--mode" in result.stdout
    assert "--records-per-file" in result.stdout


def test_offline_smoke_run_is_update_safe(tmp_path: Path):
    out_dir = tmp_path / "ap_out"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--domain",
        "thermodynamics",
        "--input",
        str(FIXTURE),
        "--output-dir",
        str(out_dir),
        "--mode",
        "offline-template",
        "--max-subdomains",
        "6",
        "--subdomains-per-call",
        "3",
        "--atomic-per-subdomain",
        "3",
    ]
    first = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    first_manifest = json.loads(first.stdout)
    assert first_manifest["stats"]["inserted"] == 18
    second = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    second_manifest = json.loads(second.stdout)
    assert second_manifest["stats"]["inserted"] == 0
    assert second_manifest["stats"]["unchanged"] == 18
    ap_files = sorted(out_dir.glob("ap_*.jsonl"))
    assert len(ap_files) == 1
    assert ap_files[0].name == "ap_000001.jsonl"
