"""
common.py v14 — Shared utilities for all pipeline steps.

Key change from v2: llm_call() now accepts an optional Telemetry instance
and records all LLM call metrics automatically. Steps pass `tel` through;
if None, behaviour is identical to v2.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests

from config import LM_STUDIO_URL, LM_STUDIO_MODEL, REQUEST_TIMEOUT
from constants import PIPELINE_VERSION


# ── Hashing ────────────────────────────────────────────────────────────────────

def sha256_str(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()

def sha256_obj(obj: Any) -> str:
    return sha256_str(json.dumps(obj, sort_keys=True, ensure_ascii=False))


# ── Timestamp ──────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── LLM call ──────────────────────────────────────────────────────────────────

def llm_call(
    prompt: str,
    system: str = "",
    retries: int = 1,
    tel=None,             # Optional[Telemetry]
    step: str = "",
    prompt_hash: str = "",
    model_class: str = "",
) -> Optional[str]:
    """
    Call LM Studio with a prompt. Returns raw text response or None on failure.

    When `tel` is provided (Telemetry instance), the call is measured and
    recorded. All other parameters are used for telemetry labelling only.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model":       LM_STUDIO_MODEL,
        "messages":    messages,
        "temperature": 0.2,
        "max_tokens":  4096,
    }

    def _call_once() -> Optional[str]:
        try:
            resp = requests.post(
                LM_STUDIO_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return None

    # With telemetry: delegate entirely to tel.llm_call which handles retries + measurement
    if tel is not None:
        raw, _ = tel.llm_call(
            prompt_text  = prompt,
            prompt_hash  = prompt_hash,
            step_name    = step,
            model_class  = model_class,
            call_fn      = _call_once,
            retries      = retries,
        )
        return raw

    # Without telemetry: plain retry loop (v2 behaviour)
    for attempt in range(retries + 1):
        result = _call_once()
        if result is not None:
            return result
        print(f"  [LLM] attempt {attempt + 1}/{retries + 1} failed", file=sys.stderr)
        if attempt < retries:
            time.sleep(2)
    return None


def parse_json_response(text: str) -> Optional[Any]:
    """Parse JSON from LLM response. Strips markdown fences if present."""
    if text is None:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines    = cleaned.split("\n")
        inner    = []
        in_block = False
        for line in lines:
            if line.startswith("```") and not in_block:
                in_block = True; continue
            if line.startswith("```") and in_block:
                break
            if in_block:
                inner.append(line)
        cleaned = "\n".join(inner)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"  [JSON] parse error: {e}", file=sys.stderr)
        print(f"  [JSON] raw: {cleaned[:300]}", file=sys.stderr)
        return None


# ── Run directory helpers ──────────────────────────────────────────────────────

def run_dir(work_dir: Path, run_id: str) -> Path:
    d = work_dir / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d

def artifact_dir(work_dir: Path, run_id: str, step: str) -> Path:
    d = run_dir(work_dir, run_id) / "artifacts" / step
    d.mkdir(parents=True, exist_ok=True)
    return d

def snapshot_dir(work_dir: Path, run_id: str) -> Path:
    d = run_dir(work_dir, run_id) / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_jsonl_line(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ── State events ──────────────────────────────────────────────────────────────

def emit_state(work_dir: Path, run_id: str, event: str, step: str,
               payload: dict = None) -> None:
    state_path = run_dir(work_dir, run_id) / "state.jsonl"
    record = {"ts": now_iso(), "event": event, "step": step, "run_id": run_id}
    if payload:
        record.update(payload)
    write_jsonl_line(state_path, record)


# ── Manifest ───────────────────────────────────────────────────────────────────

def load_manifest(work_dir: Path, run_id: str) -> dict:
    path = run_dir(work_dir, run_id) / "manifest.json"
    if path.exists():
        return read_json(path)
    return {"run_id": run_id, "artifacts": {}}

def save_manifest(work_dir: Path, run_id: str, manifest: dict) -> None:
    """Write manifest.json with schema validation before write. Raises on violation."""
    dest = run_dir(work_dir, run_id) / "manifest.json"
    try:
        from validator import validate_schema
        errors = validate_schema(manifest, "manifest")
        if errors:
            raise ValueError(
                f"manifest.json schema validation failed (run={run_id}): {errors}"
            )
    except (ImportError, RuntimeError):
        # Schema file missing at cold start — warn, do not block
        print(f"  [warn] manifest schema not available — writing without validation",
              file=sys.stderr)
    write_json(dest, manifest)

def register_artifact(work_dir: Path, run_id: str, key: str, path: Path,
                       content_state: str = "candidate", step: str = "") -> str:
    file_hash = sha256_file(path)
    manifest  = load_manifest(work_dir, run_id)
    manifest["artifacts"][key] = {
        "path":          str(path),
        "hash":          file_hash,
        "content_state": content_state,
        "step":          step,
        "registered_at": now_iso(),
    }
    save_manifest(work_dir, run_id, manifest)
    return file_hash

def promote_artifact(work_dir: Path, run_id: str, key: str, new_state: str) -> None:
    manifest = load_manifest(work_dir, run_id)
    if key in manifest["artifacts"]:
        manifest["artifacts"][key]["content_state"] = new_state
        manifest["artifacts"][key]["promoted_at"]   = now_iso()
        save_manifest(work_dir, run_id, manifest)

def supersede_artifact(work_dir: Path, run_id: str, key: str) -> None:
    promote_artifact(work_dir, run_id, key, "superseded")


# ── Snapshot ───────────────────────────────────────────────────────────────────

def create_snapshot(work_dir: Path, run_id: str, label: str) -> str:
    import shutil
    snap_id   = f"{label}_{now_iso().replace(':', '').replace('-', '')}"
    snap_path = snapshot_dir(work_dir, run_id) / snap_id
    snap_path.mkdir(parents=True, exist_ok=True)
    for fname in ("manifest.json", "state.jsonl"):
        src = run_dir(work_dir, run_id) / fname
        if src.exists():
            shutil.copy2(src, snap_path / fname)
    print(f"  [snapshot] {snap_id}")
    return snap_id


# ── Novelty Guard ─────────────────────────────────────────────────────────────

def novelty_guard_check(work_dir: Path, run_id: str, task_id: str) -> bool:
    cache_path = run_dir(work_dir, run_id) / "novelty_cache.jsonl"
    if not cache_path.exists():
        return False
    with open(cache_path) as f:
        for line in f:
            try:
                if json.loads(line).get("task_id") == task_id:
                    return True
            except Exception:
                pass
    return False

def novelty_guard_record(work_dir: Path, run_id: str, task_id: str, step: str) -> None:
    cache_path = run_dir(work_dir, run_id) / "novelty_cache.jsonl"
    write_jsonl_line(cache_path, {
        "task_id":     task_id,
        "step":        step,
        "recorded_at": now_iso(),
    })

def make_task_id(step: str, inputs: dict) -> str:
    """
    v14: task_id includes prompt_hash when present in inputs.
    This makes the Novelty Guard prompt-sensitive: a prompt change
    causes a cache miss even with identical data inputs.
    """
    return sha256_obj({"step": step, "inputs": inputs})


# ── run_record.json ────────────────────────────────────────────────────────────

def load_run_record(work_dir: Path, run_id: str) -> dict:
    path = run_dir(work_dir, run_id) / "run_record.json"
    if path.exists():
        return read_json(path)
    return {
        "run_id":                run_id,
        "status":                "running",
        "clarification_rounds":  0,
        "pipeline_version":      PIPELINE_VERSION,
        "prompt_versions":       {},
        "started_at":            now_iso(),
    }

def save_run_record(work_dir: Path, run_id: str, record: dict) -> None:
    """Write run_record.json with schema validation before write. Raises on violation."""
    dest = run_dir(work_dir, run_id) / "run_record.json"
    try:
        from validator import validate_schema
        errors = validate_schema(record, "run_record")
        if errors:
            raise ValueError(
                f"run_record.json schema validation failed (run={run_id}): {errors}"
            )
    except (ImportError, RuntimeError):
        print(f"  [warn] run_record schema not available — writing without validation",
              file=sys.stderr)
    write_json(dest, record)
