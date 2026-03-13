# Resume — Algorithm and Skip Rules

**Version:** 1.0.0

---

## Guarantee

> Using only the run directory, the system must be able to reconstruct execution state and continue — without re-running completed steps and without re-invoking LLMs for completed tasks.

---

## When Resume Is Triggered

- Explicit: `run.py --resume <run_id>`
- Automatic: orchestrator detects an existing run directory with `status: running` at startup

---

## Resume Algorithm

```
1. Read run_record.json
   └─ if status == done | stop → nothing to resume; return

2. Verify manifest integrity
   for each artifact in manifest.artifacts:
       actual_hash = sha256(read(path))
       if actual_hash != stored_hash:
           → STOP: manifest_integrity_mismatch

3. Read state.jsonl
   └─ reconstruct which task_ids are in state complete

4. Load all envelopes from envelopes/
   └─ for each envelope:
       if task_id in completed_tasks:
           → skip (do not dispatch)
       else:
           → add to pending queue

5. Check for orphaned .tmp files
   └─ if manifest.json.tmp exists → retry atomic rename → verify

6. Resume execution from pending queue
   └─ deterministic steps first, then LLM steps
   └─ dispatch in original step order (01 → 09)
```

---

## Skip Rules

A task is skipped on resume if **all** of the following are true:

| Condition | Check |
|-----------|-------|
| `task_id` appears in `state.jsonl` with event `task.complete` | Yes |
| All `required: true` expected_outputs exist at declared paths | Yes |
| All output hashes match manifest entries | Yes |

If any condition fails, the task is **re-run**, not skipped.

---

## LLM Steps on Resume

For LLM steps that are skipped (already complete):

1. The executor reads the raw response from `logs/llm_calls.jsonl`
2. Re-parses the response
3. Verifies output hash
4. Returns the parsed output — **no LLM call**

This is transparent to downstream steps: they receive the same output as in the original run.

---

## Clarification Rounds on Resume

If a run was interrupted during a clarification round (step 06), the resume algorithm:

1. Checks `state.jsonl` for the last `clarification.round_N.complete` event
2. If the user's answer was already parsed (01_parsing_01 completed for round N), resume from 02_retrieval
3. If the user's answer was not yet received, re-emit the clarification questions and wait

---

## Partial Run Recovery

If the run was interrupted mid-step (e.g. process killed during `04_hypothesis`):

- The task's `.tmp` output file may exist — this is discarded (not renamed to final path)
- The task is re-run from scratch
- The manifest is checked: if no hash was registered, no conflict exists

---

## State Reconstruction Example

```
state.jsonl contains:
  task.complete  task_id=sha256:aaa (01_parsing_01_extraction)
  task.complete  task_id=sha256:bbb (01_parsing_02_confidence)
  task.complete  task_id=sha256:ccc (02_retrieval)
  task.claimed   task_id=sha256:ddd (03_enrichment_01_terminology)   ← interrupted here

Resume result:
  01_parsing_01  → skip ✓
  01_parsing_02  → skip ✓
  02_retrieval   → skip ✓
  03_enrichment_01 → re-run (claimed but not complete)
  03_enrichment_02 → pending
  03_enrichment_03 → pending
  04_hypothesis    → pending
  ...
```
