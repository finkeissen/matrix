import json
from pathlib import Path

from pipeline.ap_store import APStore, canonical_ap_id


def test_canonical_ap_id_is_stable():
    a = canonical_ap_id(domain="thermodynamics", subdomain="A", problem_group="B", atomic_problem="C")
    b = canonical_ap_id(domain="thermodynamics", subdomain="A", problem_group="B", atomic_problem="C")
    assert a == b
    assert a.startswith("ap_")


def test_store_upsert_and_file_split(tmp_path: Path):
    store = APStore(tmp_path, records_per_file=2)
    recs = []
    for idx in range(5):
        recs.append({
            "ap_id": f"ap_{idx:04d}",
            "domain": "thermodynamics",
            "subdomain": f"s{idx}",
            "problem_group": "g",
            "atomic_problem": f"p{idx}",
        })
    stats = store.upsert_many(recs)
    assert stats["inserted"] == 5
    assert len(sorted(tmp_path.glob("ap_*.jsonl"))) == 3
    lines = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in tmp_path.glob("ap_*.jsonl"))
    assert lines == 5
