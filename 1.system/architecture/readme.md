# architecture

This directory documents the **matrix-internal architectural view**.

It does not restate the full cross-repository contract.
It does not define epistemic admissibility.
It does not describe MMS implementation details.

Its sole purpose is to clarify:
- what exists in this repository,
- how the major areas relate,
- and where responsibility boundaries lie.

---

## Architecture in One Sentence

> **The Matrix repository is a structured environment for instantiated epistemic artifacts,
> produced by MMS runs, and maintained under explicit boundaries.**

---

## Repository Areas and Roles

This repository distinguishes strictly between:

- `handbook/`  
  Human-readable orientation and explanations.  
  Not normative. Not executable.

- `system/`  
  Matrix-internal specification: schemas, conventions, and constraints.  
  Structural only. Content-agnostic.

- `work/`  
  Non-normative working space: raw material, pre-matrix history, exploration, production preparation.  
  Unstable by design.

- `domains/`  
  The current, referencable Matrix state: structured epistemic artifacts.  
  Provisional. Traceable. Comparable.

- `runs/`  
  Append-only execution records produced by MMS.  
  The provenance backbone and transition record.

- `exports/`  
  Frozen representations of Matrix states for external use.  
  Immutable. Non-authoritative.

---

## Responsibility Boundaries

This repository is responsible for:
- preserving structure under uncertainty
- making provenance and constraints inspectable
- representing conflict and gaps explicitly
- keeping transitions traceable through runs

This repository is not responsible for:
- truth
- resolution
- prioritization
- decisions
- recommendations

---

## Cross-Repository Contract (Reference)

The separation between:
- `research-program`
- `mms`
- `matrix`

is documented in:

`handbook/research-program_mms_matrix.md`

That document is normative at the architectural level.

This `system/architecture/` directory is local documentation only.

---

## Summary

> **This repository provides structure, traceability, and visibility —
> not conclusions.**

Its architecture exists to keep that distinction stable.


---

### Note on Model Construction

Model construction within this ecosystem follows a separate, explicitly
non-ontological **Model Toolkit**.

The toolkit defines:
- how models are specified as artifacts,
- which components must be made explicit,
- and which interpretive upgrades are disallowed.

The toolkit does not:
- define truth,
- privilege any theory,
- or grant semantic authority to models.

All models appearing in `domains/` or produced by `runs/`
are assumed to comply with that toolkit.

