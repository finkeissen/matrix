# Update Contract (Normative)

This contract binds all update modules, independent of implementation (human, script, model, successor).

---

## 1) Conceptual signature

`update(state, inputs, params) -> (patches, report)`

The module MUST:
- read from `state`,
- emit append-only patch events,
- produce a report.

The module MUST NOT:
- rewrite past runs,
- silently delete records,
- rely on hidden global state.

---

## 2) Required properties

### 2.1 Re-entry
Runnable at any time; must skip unchanged work units.

### 2.2 Determinism (or declared non-determinism)
Given identical `(state, inputs, params, module_version)`, output must be identical OR module records:
- provider identity and version,
- seed (if applicable),
- prompt/spec hash (if applicable).

### 2.3 Append-only change
All changes are emitted as events. Materialized state is derived.

---

## 3) Patch Event (minimal)

Required fields:
- `event_id` (unique)
- `created_at`
- `module_id`, `module_version`
- `params_hash`
- `inputs_fingerprint`
- `ops[]`
- `provenance` (producer identity/version)
- optional: `evidence_refs[]`

### 3.1 Allowed op set (minimal)
- `upsert_entity`
- `upsert_assertion` (or `upsert_relation`)
- `attach_evidence`
- `deprecate` (never silent delete)

---

## 4) Fingerprinting

Modules compute fingerprints over the *work unit* they process (e.g. per source excerpt, per candidate cluster):
- normalize input
- hash it
- combine with module_version + params_hash

If unchanged → emit skip in report.

---

## 5) Reports

Reports MUST include:
- counts: created/updated/skipped/flagged
- warnings
- produced artifacts list
- optional references to review queues / STOP artifacts

Reports are descriptive, not authoritative.
