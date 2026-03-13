# M10 — Security & Governance
## Access Control, Provenance, and Operational Governance

**Layer:** Governance
**Version:** 2.0.0
**Deterministic:** Yes
**Depends on:** M02 (knowledge store), M09 (audit layer)
**Used by:** All modules (enforces access decisions)
**Pipeline steps:** Operational layer (not invoked per query; enforced continuously)

---

## Purpose

Define the **access model, provenance requirements, and operational governance policies** for the system. This module does not process knowledge or answer questions — it determines who may do what, ensures every action is attributed, and enforces safe-fail behavior when the system cannot produce a validated answer.

---

## Access Control Model

### Roles and Permissions

| Role | Knowledge Base | Retrieval/Query | Ingestion | Review/Approve | Admin |
|------|---------------|-----------------|-----------|---------------|-------|
| **Reader** | Read active AKUs | Yes | No | No | No |
| **Contributor** | Read + submit draft AKUs | Yes | Yes (draft only) | No | No |
| **Reviewer** | Read + approve/reject drafts | Yes | No | Yes | No |
| **Administrator** | Full access | Yes | Yes | Yes | Yes |
| **Auditor** | Read audit logs only | Read-only | No | No | No |

Role assignment is explicit (no implicit role inheritance). A user may hold multiple roles in different domains.

### Domain-Scoped Permissions

Roles are scoped per domain. A Reviewer for `endocrinology` cannot approve AKUs in `legal-compliance` without a separate role assignment.

```json
{
  "user_id": "u-00042",
  "roles": [
    { "role": "Reviewer", "domain": "endocrinology" },
    { "role": "Reader", "domain": "legal-compliance" }
  ]
}
```

---

## Provenance Requirements

Every AKU in the system must declare:

| Field | Requirement |
|-------|-------------|
| `source` | Non-empty string; names the authoritative external document or regulation. |
| `reviewed_by` | User ID of the domain expert who approved activation. |
| `review_date` | ISO 8601 date of most recent review. |
| `created_by` | User ID of the contributor who submitted the AKU. |
| `created_at` | ISO 8601 timestamp. |

An AKU may not transition to `active` state without all provenance fields populated.

---

## Domain Boundary Enforcement

AKUs are tagged with a `domain` field. The system enforces:

1. **Retrieval isolation:** A query scoped to domain X does not return AKUs from domain Y by default.
2. **Cross-domain flag:** Cross-domain retrieval requires `allow_cross_domain: true` and is logged as a warning.
3. **Authoring isolation:** A Contributor in domain X cannot submit AKUs to domain Y.
4. **No cross-domain leakage:** AKU relations (`parent`, `children`, `conflicts_with`) may not reference AKUs from a different domain unless explicitly allowed by a declared cross-domain policy in `policies/`.

---

## Safe-Fail Behavior

When the system cannot produce a validated answer, it must return a **structured uncertainty response** — never a fabricated result. The default failure mode is transparent refusal.

### Safe-Fail Response Schema

```json
{
  "status": "insufficient | no_knowledge | no_match | error",
  "reason": "string",
  "safe_fail": true,
  "available_actions": [
    "Provide additional case facts",
    "Expand domain scope",
    "Contact domain expert"
  ],
  "trace_id": "TRACE-20250601-00291"
}
```

Safe-fail responses are logged identically to successful responses — they are full audit trace entries.

---

## Immutable Audit Log

The audit log (M09) must satisfy:

| Property | Specification |
|----------|--------------|
| Append-only | No DELETE or UPDATE operations permitted on log entries |
| Tamper-evident | Hash-chained entries or immutable log service (e.g., CloudTrail, Loki with WORM storage) |
| Separation | Stored independently from the operational database and KB store |
| Retention | Minimum 7 years for regulated domains; indefinite preferred |
| Access | Read access: Auditor role + Administrator; No write access from application layer |

---

## Security Controls

| Control | Implementation |
|---------|---------------|
| Authentication | OAuth 2.0 / OIDC; no API key-only access for write operations |
| Authorization | RBAC enforced at API gateway; domain scoping at service layer |
| Transport | TLS 1.3 minimum for all API calls |
| Secrets | LLM API keys and DB credentials in secrets manager; never in code or config files |
| Input validation | All user inputs validated against declared schemas before processing |
| Dependency scanning | Automated CVE scanning on all dependencies; blocking on critical severity |
| Penetration testing | Annual third-party pen test; quarterly internal red team for regulated deployments |

---

## Governance Workflow

```
AKU Change Proposed
    |
    v
Automated integrity + schema checks (M01, M02)
    |
    v
Domain expert review (Reviewer role)
    |
    +--> Rejected: return to Contributor with rejection rationale
    |
    +--> Approved: transition to active
              |
              v
         Snapshot publication pipeline
              |
              v
         Regression tests (M02)
              |
              +--> Fail: block release; notify Administrator
              |
              +--> Pass: publish; version bump; changelog entry
```

---

## Compliance Considerations

For regulated domains (medical, legal, financial):

| Requirement | Mechanism |
|-------------|-----------|
| Explainability | Mandatory audit trace + AKU citation per output (M09) |
| Data minimization | Case facts contain only what is required for the query; no persistence beyond trace |
| Right to explanation | Trace replay produces human-readable decision record |
| Audit trail | Immutable append-only log with full provenance (M09) |
| Role segregation | No single user can both submit and approve an AKU (Contributor != Reviewer) |

---

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Authentication failure | Reject request; return 401; log attempt |
| Authorization failure | Reject request; return 403; log with user + action |
| Domain boundary violation attempt | Reject; log as security event; alert Administrator |
| Audit log write failure | Block all pipeline operations; alert immediately |
| Safe-fail unavailable (system error) | Return HTTP 503 with retry-after header; never return fabricated content |
