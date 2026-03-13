"""
storage/manifest_store.py — Safe read/write access to manifest.json.
All writes are atomic (tmp → rename) to prevent partial-write corruption.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional


class ManifestStore:
    def __init__(self, run_dir: Path):
        self._path = run_dir / "manifest.json"

    def load(self) -> Optional[dict]:
        if not self._path.exists():
            return None
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        """Atomically write manifest.json using tmp → rename."""
        text = json.dumps(data, indent=2, ensure_ascii=False)
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=self._path.parent, prefix=".manifest_", suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def exists(self) -> bool:
        return self._path.exists()
