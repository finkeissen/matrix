# 2.engine/version06/shared/hashing.py
from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_normalize(obj: Any) -> bytes:
    # Stable JSON: UTF-8, sorted keys, no trailing whitespace
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return s.encode("utf-8")


def sha256_json_normalized(obj: Any) -> str:
    return sha256_bytes(_json_normalize(obj))
