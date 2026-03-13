# M02 — Knowledge Store & Versioning
## Storage, Snapshots, and Knowledge Lifecycle Management

**Layer:** Knowledge
**Version:** 2.0.0
**Deterministic:** Yes
**Depends on:** M01 (AKU schema)
**Used by:** M03 (ingestion), M04 (embedding), M05 (retrieval), M06 (validation)
**Pipeline steps:** Authoring time; snapshot ID pinned at query time

---

## Purpose

Provide a **versioned, immutable, queryable store** for all AKUs. The knowledge store is the ground truth of the system. Every query-time operation (retrieval, validation) references a specific, pinned snapshot — never the live mutable state.

---

## Storage Architecture

```
+---------------------+       +----------------------+
|  Mutable Store      |  ──►  |  Snapshot Store      |
|  (authoring)        |       |  (query-time)        |
|                     |       |                      |
|  AKUs in draft,     |       |  Immutable snapshots |
|  review, active     |       |  SNAP-NNNN           |
|  states             |       |  (active AKUs only)  |
+---------------------+       +----------------------+
         |                              |
         ▼                              ▼
  Relational DB                   Vector Index
  (relations, criteria,           (M04 embedding)
   lifecycle, history)
```

The mutable store and snapshot store are separate. Only `active` AKUs are included in snapshots. Query-time components (M04, M05, M06) access the snapshot store exclusively.

---

## Snapshot Contract

A snapshot is an **immutable, versioned point-in-time export** of all active AKUs.

```json
{
  "snapshot_id": "SNAP-00189",
  "kb_version": "2.1.0",
  "created_at": "2025-06-01T00:00:00Z",
  "aku_count": 847,
  "domains": ["endocrinology", "oncology", "legal-compliance"],
  "triggered_by": "kb-release-pipeline",
  "changelog_ref": "CHANGELOG-2.1.0.md"
}
```

### Snapshot Invariants

- A snapshot is never modified after creation.
- A snapshot is never deleted (archived for audit purposes).
- A snapshot contains only `active` AKUs at the moment of creation.
- Every query-time run must declare and pin a `snapshot_id`.

---

## Knowledge Base Versioning

The KB uses semantic versioning (`MAJOR.MINOR.PATCH`) at the **snapshot level**:

| Increment | Trigger | Regression Test Required |
|-----------|---------|--------------------------|
| `PATCH` | Metadata correction, typo fix in non-criteria fields | No |
| `MINOR` | New AKU added; criteria wording clarified | Recommended |
| `MAJOR` | Criteria semantically changed; AKU deprecated/replaced | Required |

A `MAJOR` bump requires a **migration report** identifying which prior validated results may now return a different outcome, and why.

---

## Knowledge Base API

```
GET  /units/{id}                  -> AKU (current active version)
GET  /units/{id}/history          -> version history[]
GET  /units/{id}/relations        -> { parent, children, conflicts_with }
GET  /units/{id}/criteria         -> { required_criteria, exclusion_criteria }
GET  /version                     -> { current_kb_version, latest_snapshot_id }
GET  /snapshots/{id}              -> snapshot metadata
GET  /snapshots/{id}/units        -> all AKUs in snapshot
GET  /snapshots/latest            -> latest active snapshot

SEARCH /units?query=...&domain=...&status=...  -> ranked AKU list

POST /units                       -> create AKU (Contributor role required)
PUT  /units/{id}                  -> update AKU (triggers MINOR or MAJOR bump)
POST /units/{id}/deprecate        -> deprecate AKU (Admin role required)
POST /snapshots                   -> publish new snapshot (triggers CI checks)
```

All write operations require authentication, produce an audit log entry, and are attributed to a named user.

---

## Update Workflow

```
1. Author submits AKU create/update via POST or PUT.
2. Schema validator (M01) runs; rejects on any integrity violation.
3. AKU enters `draft` state.
4. Automated integrity checks run:
     - circular dependency detection
     - conflict symmetry check
     - parent coherence check
5. Domain expert review assigned (required for MINOR and MAJOR changes).
6. Reviewer approves -> AKU transitions to `active`.
7. Snapshot publication triggered:
     - regression test suite executes
     - embedding rebuild triggered in M04 (incremental or full)
     - new snapshot published with version bump
     - changelog entry created
8. Prior version deprecated (if update); backward ID mapping updated.
```

PATCH-level changes skip steps 5–6 (no expert review required) and trigger only incremental embedding updates.

---

## Regression Testing

Every MINOR or MAJOR snapshot release runs against a curated **canonical test set**: known inputs with expected outputs. A test failure blocks the release until resolved.

| Test Type | Trigger | Blocks Release |
|-----------|---------|----------------|
| Schema validation | All changes | Yes |
| Integrity checks | All changes | Yes |
| Canonical case tests | MINOR, MAJOR | Yes |
| Retrieval quality eval | MAJOR | Yes |
| Full regression suite | MAJOR | Yes |

---

## Backward Compatibility

When an AKU ID changes (rare; only on structural reorganization):

- The old ID is deprecated and mapped to the new ID in the backward mapping table.
- All prior audit traces referencing the old ID remain valid and resolvable.
- The retrieval layer resolves deprecated IDs transparently during replay.

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Snapshot write fails | Block release; retry; alert |
| Regression test failure | Block release; open review ticket |
| Integrity check failure on update | Reject update; return violation details |
| Snapshot not found at query time | Block query; return structured error |
