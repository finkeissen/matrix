# Step 09 — Commit Gate
## Validate and Publish State Patches

**Version:** 1.0.0
**Track:** All tracks
**Deterministic:** Yes (rule-based integrity checks)
**Upstream:** All steps that produce patches
**Downstream:** State snapshot (queryable materialized view)

---

## Purpose

The commit gate is the **single point of state mutation** in the pipeline. It receives proposed patches from all upstream steps and applies only those that pass structural validity and policy checks. Rejected patches are logged and queued for review — they do not block other patches in the same batch.

The commit gate enforces **structural correctness**, not domain correctness. Domain correctness is the responsibility of the validation and examination steps.

---

## Contract

```
update(state, inputs={ patches[] }, params) -> (committed_patches[], report)
```

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patches` | `PatchEvent[]` | Yes | All proposed patches from the current pipeline run. |
| `policy_set_id` | string | Yes | Version of the active policy set to apply. |
| `kb_snapshot_id` | string | Yes | State snapshot against which patches are evaluated. |

### Commit Checks (Executed Per Patch)

| # | Check | Failure Action |
|---|-------|---------------|
| 1 | **Schema validity** | Does the patch conform to the PatchEvent schema? | Reject; log schema error. |
| 2 | **Entity existence** | For `update`/`deprecate` ops: does the target entity exist in the current snapshot? | Reject; log missing entity. |
| 3 | **Policy compliance** | Does the patch violate any rule in the active policy set? | Reject; log policy ID violated. |
| 4 | **Circular dependency** | Does the patch create a circular relation in the entity graph? | Reject; log cycle path. |
| 5 | **Constraint integrity** | Does the patch violate declared field constraints (type, range, uniqueness)? | Reject; log constraint name. |
| 6 | **Author authorization** | Is the `author` (module ID + version) registered and authorized for this op type? | Reject; log unauthorized module. |

Checks are evaluated in order. The first failure rejects the patch; remaining checks are not evaluated for that patch.

### Patch Application (Accepted Only)

Accepted patches are applied atomically to the current state snapshot:

```
new_snapshot = apply(current_snapshot, accepted_patches)
new_snapshot_id = SNAP-{timestamp}-{run_id}
```

The new snapshot is published and becomes the `current_snapshot` for subsequent pipeline steps.

### Patches Produced by This Step

This step does not produce AKU or domain patches. It produces:

| Op | Entity Type | Condition |
|----|------------|-----------|
| `create` | `CommitRecord` | Always |
| `create` | `ReviewQueueEntry` | For each rejected patch |

### Output Schema — Commit Record

```json
{
  "commit_id": "COMMIT-20250601-0088",
  "run_id": "RUN-20250601-0042",
  "policy_set_id": "policies-v1.4.0",
  "snapshot_before": "SNAP-00188",
  "snapshot_after": "SNAP-00189",
  "patches_proposed": 14,
  "patches_accepted": 12,
  "patches_rejected": 2,
  "rejected_patch_ids": ["PATCH-0011", "PATCH-0014"],
  "rejection_reasons": [
    { "patch_id": "PATCH-0011", "check": "policy_compliance", "policy": "no-status-downgrade" },
    { "patch_id": "PATCH-0014", "check": "entity_existence", "entity_id": "AKU-99999" }
  ],
  "committed_at": "2025-06-01T14:22:45Z"
}
```

### Report Fields

```json
{
  "status": "ok | partial | blocked",
  "patches_proposed": 14,
  "patches_accepted": 12,
  "patches_rejected": 2,
  "new_snapshot_id": "SNAP-00189",
  "review_queue_entries_created": 2
}
```

---

## Status Codes

| Status | Meaning |
|--------|---------|
| `ok` | All patches accepted and committed. |
| `partial` | Some patches rejected; accepted patches committed; rejected patches queued for review. |
| `blocked` | Zero patches accepted (all rejected or schema error on all). No state change. |

A `partial` status does not halt the pipeline. Downstream steps proceed with the committed snapshot.

---

## Policy Set

Policies are declared in `policies/` and versioned independently. Each policy is a named rule applied during check #3. Examples:

| Policy ID | Rule |
|-----------|------|
| `no-status-downgrade` | An entity's `status` may not move from `active` to `draft`. |
| `immutable-id` | An entity's `id` field may not be changed after creation. |
| `source-required-on-create` | A `create` patch for an AKU entity must include a non-empty `source` field. |
| `reviewed-required-for-active` | An AKU may not transition to `active` status without a `reviewed_by` field. |

New policies are additive — adding a policy file never changes the commit gate logic, only its inputs.

---

## State Reconstruction

The full state at any point in time is reconstructible from the commit log:

```
state(t) = apply(empty_state, all_commits where committed_at <= t)
```

This property is maintained by:

- Immutable commit records (no deletions, no edits).
- Append-only patch log.
- Deterministic `apply()` function (same patches always produce same state).

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Policy set not found | `status: blocked`; halt run; alert. |
| Snapshot write fails | `status: blocked`; retry with backoff; alert after 3 failures. |
| All patches rejected | `status: blocked`; no state change; full review queue population. |
| Circular dependency detected | Reject offending patch; log full cycle path for review. |

---

## Performance Targets

| Operation | Target |
|-----------|--------|
| Per-patch check latency | < 10ms |
| Commit gate evaluation (100 patches) | < 100ms |
| Snapshot write latency | < 50ms |
| Full state reconstruction (100k patches) | < 60s |
