from __future__ import annotations
import re, hashlib

def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "x"

def stable_problem_id(label: str, scope: str, primary_symptom: str) -> str:
    canon = f"{label.strip().lower()}|{scope.strip().lower()}|{primary_symptom.strip().lower()}"
    h = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]
    return f"prob_{h}"
