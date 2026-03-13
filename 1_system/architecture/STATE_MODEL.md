# State Model (Substrate)

A stable substrate that survives ontology changes.

This model is **structural**:
- no truth,
- no correctness,
- no implicit privilege.

---

## 1) Core record types

### Entity
- `entity_id`
- `type` (namespaced)
- `label`
- `scope`
- `status` (active/deprecated/superseded)
- `provenance` (run/module refs)
- optional: `attributes` (type-specific)

### Assertion (typed statement)
- `assertion_id`
- `type` (namespaced; e.g. `relation/has_symptom`)
- `subject_ref`
- `object_ref` (or value)
- `qualifiers` (confidence, modality, conditions)
- `scope`
- `evidence_refs[]`

### Evidence
- `evidence_id`
- `source_ref`
- `extract_ref` (pointer into source)
- `notes`
- `scope`

---

## 2) Namespaces and evolution
- all types are namespaced: `ontology.problem/Problem`
- schema evolution via new types or `schema_version` fields (no silent mutation)
- multiple ontologies may coexist

---

## 3) Materialization
Either:
- event-sourcing-first (events canonical), or
- graph-first (state canonical)

Repository policy: **runs are canonical provenance**; state is derived.
