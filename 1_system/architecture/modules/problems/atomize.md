# Problems Track: Atomization (v2)

## Atomization criteria
An atomic problem must be:
- single scope (or explicit unknown, not mixed)
- single primary symptom class
- single failure mode family
- coherent intervention family

If not, split.

---

## Split protocol (normative)

When splitting candidate C into atomic problems A, B, ...:

1) C is preserved (no deletion).
2) For each child problem Pi:
   - create `Problem` with `atomic=true`
   - add `relation/derived_from`: Pi → C
3) Mark C as decomposed:
   - either `status=deprecated` with reason `decomposed`
   - or keep as candidate and add `relation/supersedes`: [P1,P2...] supersede C (preferred)
4) Add `relation/related_to` between children if there is coupling (shared boundary).

This ensures re-entry and auditability.

---

## Ambiguity handling
If split is ambiguous:
- create tentative children with `status=needs_review`
- emit review items describing ambiguity and missing evidence
