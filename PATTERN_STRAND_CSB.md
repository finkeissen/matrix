# PATTERN_STRAND_CSB.md — Pattern Strand: Full Proof Chain (US CSB Recommendations)

## Purpose

This document shows **one complete chain** from public source material to admitted
knowledge artifacts, for the domain "US Chemical Safety Board (CSB) investigation
recommendations". It is the reference pattern ("Musterstrang") for every future
domain ingestion.

It demonstrates **form and traceability**, not truth, completeness, or real-world
validity (see `PUBLIC_SCOPE.md`). All numbers below were measured between
2026-11-22 and 2026-11-23 and are recorded with their stage.

## The chain, stage by stage

```
source (csb.gov, HTML)
   → extraction (anchor-based, 3 iterations)
   → mapping (problem atom + solution atom + `solves` edge)
   → admission (gatekeeper script, classes SUCCESS/NOCLAIM/CONFLICT/STOP)
   → ingestion (delta write path: intake → check → apply)
   → verification (proof chain per sample atom)
```

| # | Stage | What was done | Measured result |
|---|---|---|---|
| 1 | Source | Crawl of csb.gov investigation pages (HTML); pair-density measured **before** building the extractor | 697 files counted; 88 carry recommendation numbers (728 distinct numbers, 508 block-stable) |
| 2 | Extraction | Anchor-based block extraction (number / recommendation text / status); three iterations: anchor-window fix, HTML end-tag fix, position-based head assignment | final: 677 sentences, 677/677 with recipient, 0 without |
| 3 | Mapping | Per recommendation: problem atom + solution atom + `solves` edge; heads > 96 chars excluded (identity stability over completeness) | 311 + 311 atoms, 311 `solves` edges (first pass); 301 excluded (missing recipient); license check: 0 errors |
| 4 | Admission | First **executed** gatekeeper run (the role existed in architecture only, until this date). DE/EN treated separately | 554 problems SUCCESS, 554 solutions SUCCESS, 0 CONFLICT, 0 STOP |
| 5 | Ingestion | Delta-based write path on the test instance, dry-run first, one ledger/manifest line per stage | 4 deltas per phase; final stock: 571 problem/solution pairs, 571 `solves` edges |
| 6 | Verification | Sample proof chain resolved end-to-end: solution → recipient → raw-file sha256 → local file → source URL | verified OK on the example atom; cross-mark duplicate check: 0 hits |

## Distilled rules (transferable to any new domain)

1. **Measure pair density first.** Names and boilerplate say nothing: only 88 of
   697 CSB pages carried usable recommendation numbers. Build extractors only
   after counting.
2. **Anchor windows:** take the *last* end of all non-overlapping matches before
   the identifier — never the first match, never `max()` over all matches.
3. **Closing tags lie.** Real-world HTML has unclosed tags; position logic
   (nearest heading before the identifier) beats range logic (first `</li>`).
4. **Validate your own counting method against one real object** before
   counting (a prototype that kept a list part produced a phantom gap of 664
   atoms that did not exist).
5. **Identity stability over completeness:** exclude over-long heads with
   reason recorded; never truncate — a truncated name would be a false root.
6. **Every stage leaves a manifest/ledger line.** A run without a write flag
   produces a report but no ledger entry — never claim "manifest current"
   without a write receipt.
7. **License gate before mapping,** never after; unlicensed or "unverified"
   licensed material does not enter, no matter how good the anchors are.
8. **No claim without admission.** Atoms without a passed gatekeeper run are
   not "admissible", regardless of how they were produced.

## What this strand does not claim

- Not that CSB recommendations are complete, current, or correct.
- Not that admitted atoms are true or useful (see `PUBLIC_SCOPE.md`).
- The aggregate/synthesis layer (E4) is out of scope here and not built yet.
