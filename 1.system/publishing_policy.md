# Publishing Policy
## What May Be Released From the Matrix (Binding)

---

## Status

This document is **normative**.

It defines:
- what Matrix material may be exported/published,
- what must never be published,
- how publication decisions are represented as artifacts,
- and how releases are produced as reproducible runs.

---

## 1. Core Principle

Publication is not truth.
Publication is not endorsement.
Publication is not prioritization.

Publication is a **controlled export** of selected artifacts
under explicit constraints.

---

## 2. Publication Units

Everything published must be produced as an **export snapshot**
via an explicit run.

A publication output is an **export artifact** (external format permitted)
that is:
- versioned,
- reproducible in principle,
- accompanied by an export manifest.

No ad-hoc release is allowed.

---

## 3. Default Stance

Default is **non-public**.

Nothing is public unless explicitly included
by a publication policy and a release run.

---

## 4. Absolute Non-Publishable Material (Hard Block)

The following must never be published in any form:

1) **Secrets / credentials / tokens**
2) **Personal data** (direct identifiers)
3) **Sensitive personal data** (health, biometrics, etc.)
4) **Private communications** unless explicit permission is recorded
5) **Internal safety or abuse-sensitive operational details**
6) **Anything covered by legal confidentiality**
7) **Material that creates actionable harm in high-stakes contexts**
8) **Unredacted provenance that exposes private individuals**
9) **Any artifact marked with STOP: privacy/security/harm risk**

Hard block is enforced by structure.
If present, release must emit STOP and fail.

---

## 5. Conditionally Publishable Material (Allowed With Constraints)

The following may be published only if constraints are satisfied:

### 5.1 Raw Sources
Publishable only if:
- license permits,
- access is public,
- retrieval metadata does not expose private identities,
- content is not confidential.

Otherwise publish:
- citation only,
- or a non-sensitive excerpt within license limits,
- or a derived observation.

### 5.2 Claims / Problems
Publishable if:
- provenance does not expose private individuals,
- scope is explicit,
- no high-stakes action guidance is embedded,
- no implicit endorsement is introduced.

### 5.3 Runs / Manifests
Publishable if:
- no private paths, credentials, or internal endpoints appear,
- tooling metadata is scrubbed of secrets,
- nondeterminism is documented without disclosing sensitive prompts.

### 5.4 Observations / Similarity Outputs
Publishable if:
- metric registry is included (versioned),
- no private content is leaked via payloads,
- outputs are non-authoritative.

---

## 6. Redaction and Anonymization Rules (Structural)

Redaction and anonymization must be represented explicitly as:

- a run (`R_transform` or `R_export_prepare`)
- producing a new export snapshot
- with a manifest describing the applied transformations.

No manual or silent redaction is permitted.

Redaction must be:
- reversible only in internal history,
- non-reversible in the exported artifact,
- auditable by declared transformation rules.

---

## 7. Publication Policy Objects

Publication rules must exist as explicit **policy artifacts**.

A publication policy must define:
- inclusion criteria (types/domains/scopes),
- exclusion criteria (STOP flags, risk tags),
- required transformations (redaction/anonymization),
- required manifests and audit metadata.

Policy is versioned.
Changing policy changes what may be published.

---

## 8. Export Manifest (Required for Every Release)

Every exported release must include an export manifest that records:

- release_id
- policy_version
- input snapshot or commit refs
- included artifact types and counts
- excluded sets and reasons (aggregated)
- applied transformations (redaction/anonymization)
- timestamp and authorship
- validation results

---

## 9. Validation Gates (Required)

A release run must validate:

- schema validity of all included artifacts
- policy compliance (publishability checks)
- hard-block absence (secrets/PII/STOP reasons)
- license/access constraints (for sources)

If any gate fails:
- release fails
- STOP record is produced
- no partial export is published

---

## 10. Architectural Invariant (Binding)

> Publishing is an explicit, policy-bound export.
> The default is non-public.
> Nothing sensitive leaves the system.


## Scope of Application (Binding)

This publishing policy applies to **all artifacts and files
managed by the Matrix**, regardless of their location.

This explicitly includes material under:
- `system/`
- `domains/`
- `runs/`
- `exports/`
- any future repository areas

No directory is exempt by default.

Placement of this document under `system/`
indicates **normative authority**, not limited scope.


Export outputs must reside under `exports/`.
Exports are immutable snapshots and are not part of the canonical Matrix state.

