# 2.engine/version06/shared/fs.py
from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any


def mkdirp(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def is_writable_dir(path: str) -> bool:
    return os.path.isdir(path) and os.access(path, os.W_OK)


def _fsync_dir(dir_path: str) -> None:
    # Best effort. On some systems, fsync on dir may fail.
    try:
        fd = os.open(dir_path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except Exception:
        pass


def atomic_rename(src: str, dst: str) -> None:
    # os.replace is atomic on POSIX for same filesystem.
    os.replace(src, dst)


def atomic_write_text(path: str, text: str) -> None:
    mkdirp(os.path.dirname(path) or ".")
    dir_path = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=dir_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        atomic_rename(tmp_path, path)
        _fsync_dir(dir_path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def atomic_write_json(path: str, obj: Any) -> None:
    # Stable JSON formatting for hashing/reproducibility
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    atomic_write_text(path, s)


def rm_rf(path: str) -> None:
    if not path:
        return
    if os.path.isfile(path) or os.path.islink(path):
        try:
            os.remove(path)
        except FileNotFoundError:
            return
        return
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def write_delete_test(dir_path: str) -> bool:
    if not os.path.isdir(dir_path):
        return False
    try:
        fd, tmp_path = tempfile.mkstemp(prefix=".writetest_", dir=dir_path)
        try:
            os.write(fd, b"ok")
            os.fsync(fd)
        finally:
            os.close(fd)
        os.remove(tmp_path)
        return True
    except Exception:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False
