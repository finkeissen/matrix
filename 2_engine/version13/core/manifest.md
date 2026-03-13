# Manifest — Artifact Registry

**Version:** 1.0.0

---

## Purpose

The manifest is the **authoritative registry of all artifacts** produced in a run. It maps every output path to its SHA-256 hash and content state. It is updated atomically after each task completes.

The manifest is the source of truth for:
- Resume skip logic (output exists + hash matches → skip)
- Audit trace (what was produced, when, by which task)
- Content state tracking (candidate → verified → disputed)

---

## manifest.json Schema

```json
{
  "run_id": "2026-03-03_001",
  "manifest_version": "1.0.0",
  "kb_snapshot_id": "SNAP-00189",
  "last_updated_at": "2026-03-03T09:14:00Z",
  "artifacts": {
    "sha256:a1b2c3...": {
      "path": "runs/2026-03-03_001/artifacts/01_parsing_01_extraction/raw_facts.json",
      "step": "01_parsing_01_extraction",
      "task_id": "sha256:...",
      "output_key": "raw_facts",
      "content_state": "candidate",
      "created_at": "2026-03-03T09:01:22Z",
      "size_bytes": 312
    }
  }
}
```

---

## Atomic Update Rule

The manifest is **never edited in-place**. Updates follow write-then-rename:

```
1. Read current manifest.json
2. Apply new artifact entries (additive only)
3. Write to manifest.json.tmp
4. Atomic rename: manifest.json.tmp → manifest.json
```

If the process dies between steps 3 and 4, `manifest.json.tmp` is detected on resume and the rename is retried.

---

## Content States

Content state is tracked per artifact in the manifest. It is separate from task state.

```
candidate
    │
    ▼
verified          ← passed deterministic validation (05_validation)
    │
    ├──► disputed     ← examination found weak criteria (07_examination_01)
    │         │
    │         ▼
    │       superseded ← replaced by result of retry with stronger mapping
    │
    └──► accepted     ← passed examination (07_examination_02 decision=accept)
```

### State Definitions

| State | Meaning | Who Sets It |
|-------|---------|-------------|
| `candidate` | Produced; not yet validated | executor (on task.complete) |
| `verified` | Passed deterministic validation | 05_validation (valid=true) |
| `disputed` | Weak criteria found | 07_examination_01 (ambiguous/weak) |
| `superseded` | Replaced by newer result in same run | orchestrator (on retry) |
| `accepted` | Passed full examination | 07_examination_02 (decision=accept) |
| `rejected` | Failed examination; not used | 07_examination_02 (decision=reject) |

### Transition Log

Every content state transition is recorded in `state.jsonl` as:

```json
{
  "event": "artifact.state_change",
  "artifact_hash": "sha256:a1b2c3...",
  "from_state": "candidate",
  "to_state": "verified",
  "task_id": "sha256:...",
  "reason": "validation_passed"
}
```

History is never deleted. Superseded artifacts remain in the manifest with `content_state: superseded`.

---

## Manifest Integrity Check

On resume, before any envelope is dispatched:

```
for each artifact in manifest.artifacts:
    actual_hash = sha256(read(artifact.path))
    if actual_hash != artifact_hash:
        → STOP: manifest_integrity_mismatch
```

If a file is missing but its hash is in the manifest:
- Required output: STOP
- Optional output: warn; mark as `missing` in manifest

---

## Artifact Lookup for Downstream Steps

Steps reference prior outputs by `output_key`, not by path:

```python
def get_artifact(run_id: str, output_key: str) -> dict:
    # Reads manifest, resolves path, returns parsed JSON
    ...
```

This decouples step logic from path structure and enables replay with different run IDs.
