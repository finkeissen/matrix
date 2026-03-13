# M01 — AKU Schema & Integrity
## The Formal Definition of an Atomic Knowledge Unit

**Layer:** Knowledge
**Version:** 2.0.0
**Deterministic:** Yes
**Depends on:** —
**Used by:** M02 (store), M03 (ingestion), M06 (validation)
**Pipeline steps:** Authoring time only (not invoked at query time)

---

## Purpose

Define the canonical structure, required properties, and integrity constraints for every Atomic Knowledge Unit (AKU) in the system. This module is a **schema contract** — it does not process data, it defines what valid data looks like.

All other modules that create, read, or validate AKUs depend on this definition.

---

## What an AKU Is

An AKU is the **smallest independently verifiable unit of structured knowledge** required to resolve an atomic problem. It is not a document, not a chunk, not a paragraph.

An AKU is a **formalized, versioned, relational entity** with:
- an explicit definition
- machine-readable inclusion criteria
- machine-readable exclusion criteria
- declared structural relationships to other AKUs
- full provenance metadata

---

## Full Schema

```json
{
  "id": "AKU-00123",
  "title": "Type 2 Diabetes Mellitus -- Diagnostic Criteria",
  "definition": "A metabolic disorder characterized by chronic hyperglycemia resulting from insulin resistance, with or without relative insulin deficiency.",
  "required_criteria": [
    "Fasting plasma glucose >= 7.0 mmol/L on two separate occasions",
    "OR HbA1c >= 48 mmol/mol (6.5%) confirmed by repeat test",
    "OR 2-hour plasma glucose >= 11.1 mmol/L during OGTT"
  ],
  "exclusion_criteria": [
    "Confirmed autoimmune beta-cell destruction (Type 1 indicator)",
    "Secondary diabetes due to exocrine pancreatic pathology"
  ],
  "relations": {
    "parent": "AKU-00100",
    "children": ["AKU-00124", "AKU-00125"],
    "conflicts_with": ["AKU-00130"]
  },
  "metadata": {
    "domain": "endocrinology",
    "version": "2.1.0",
    "created_at": "2024-01-15T00:00:00Z",
    "updated_at": "2025-03-01T00:00:00Z",
    "source": "WHO Diabetes Diagnostic Criteria 2023",
    "reviewed_by": "domain-expert-id-42",
    "review_date": "2025-02-28",
    "status": "draft | review | active | deprecated | archived"
  }
}
```

---

## Required Properties

Every AKU must declare all of the following. Ingestion is blocked if any are absent.

| Field | Type | Constraint |
|-------|------|------------|
| `id` | string | Globally unique; never reused after deprecation; format: `AKU-NNNNN` |
| `title` | string | Non-empty; human-readable |
| `definition` | string | Non-empty; formal definition of the concept |
| `required_criteria` | string[] | At least one entry; no implicit criteria allowed |
| `exclusion_criteria` | string[] | May be empty `[]`; must be explicitly declared (not omitted) |
| `relations.parent` | string or null | If non-null, must reference an existing active AKU |
| `relations.children` | string[] | All entries must reference existing AKUs |
| `relations.conflicts_with` | string[] | All entries must reference existing AKUs |
| `metadata.domain` | string | Must match a registered domain in the ontology |
| `metadata.version` | semver | `MAJOR.MINOR.PATCH` |
| `metadata.source` | string | Non-empty; authoritative source document |
| `metadata.reviewed_by` | string | User ID of approving domain expert |
| `metadata.status` | enum | One of: `draft`, `review`, `active`, `deprecated`, `archived` |

---

## Lifecycle States

```
draft ──► review ──► active ──► deprecated ──► archived
                        │
                        └──► superseded (replaced by new AKU version)
```

| State | Retrievable | Usable in Validation | Editable |
|-------|-------------|---------------------|----------|
| `draft` | No | No | Yes |
| `review` | No | No | Yes (reviewer only) |
| `active` | Yes | Yes | No (requires new version) |
| `deprecated` | No (audit only) | No | No |
| `archived` | No | No | No |

Only `active` AKUs are returned by the retrieval layer or used by the validation engine.

---

## Integrity Constraints

The schema validator (enforced at ingestion) must reject any AKU that violates:

| Constraint | Rule |
|------------|------|
| **No circular definitions** | AKU-A's ancestor path may not include AKU-A itself. |
| **No implicit criteria** | Every decision condition must be a machine-readable string in `required_criteria` or `exclusion_criteria`. Prose-only definitions are not valid criteria. |
| **No hidden dependencies** | All structural relationships (parent, children, conflicts) must be explicitly declared. |
| **Conflict symmetry** | If AKU-A declares `conflicts_with: [AKU-B]`, then AKU-B must also declare `conflicts_with: [AKU-A]`. |
| **Parent coherence** | A declared `parent` ID must reference an existing, active AKU. |
| **ID immutability** | An AKU's `id` may never change after creation. |
| **No criteria duplication** | A criterion string may not appear in both `required_criteria` and `exclusion_criteria`. |

---

## Versioning Rules

| Version Increment | Trigger | Behavioral Impact |
|-------------------|---------|-------------------|
| `PATCH` | Typo, metadata correction | No change to criteria or relations |
| `MINOR` | Criteria clarified (wording only), metadata added | Additive; existing validations unaffected |
| `MAJOR` | Criteria added, removed, or semantically changed; relations changed | May change validation results; regression test required |

A `MAJOR` version change requires creating a new AKU version (new `id` entry in version history) and deprecating the prior version. Prior audit traces referencing the old version remain valid.

---

## Embedding Representation

For retrieval (M04), each AKU is embedded as a single rich text chunk combining:

```
{title} | {definition} | criteria: {required_criteria joined} | excludes: {exclusion_criteria joined} | path: {breadcrumb titles}
```

Embedding isolated fields (e.g., only `definition`) is explicitly prohibited — see Design Anti-Patterns in `grounded_intelligence_architecture_v2.md §18`.

---

## Failure Modes at Authoring Time

| Violation | Action |
|-----------|--------|
| Missing required field | Reject ingestion; return field list |
| Circular dependency detected | Reject ingestion; return cycle path |
| Conflict asymmetry | Reject ingestion; name the asymmetric pair |
| Parent ID not found | Reject ingestion; suggest valid parent candidates |
| Duplicate ID | Reject ingestion; reference existing AKU |
