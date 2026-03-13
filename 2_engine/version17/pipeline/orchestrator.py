#!/usr/bin/env python3
"""
orchestrator.py v14 — Atomic Problem Identification Pipeline
Dispatches steps for a single subdomain run.

Key changes from v2:
- Telemetry instance created at run start, finalized at run end
- prompt_versions written into run_record.json before first dispatch
- All step calls pass tel= for measurement
- --prompt-variant flag for A/B testing without code changes

Usage:
  python orchestrator.py --subdomain SD-001 --steps all
  python orchestrator.py --subdomain SD-001 --steps 01_scope,01_scope_confidence
  python orchestrator.py --subdomain SD-001 --from 04a
  python orchestrator.py --subdomain SD-001 --steps all --prompt-variant v2
  python orchestrator.py --subdomain SD-001 --steps all --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR / "steps"))

from config import WORK_DIR, SUBDOMAINS_JSONL, SEEDS_CSV, TELEMETRY_ENABLED, PROMPT_VARIANT
from constants import PIPELINE_VERSION, LLM_STEPS, DETERMINISTIC_STEPS
from common import (
    sha256_file, sha256_str, now_iso, run_dir,
    load_run_record, save_run_record, emit_state,
    read_json, write_json, artifact_dir,
)
from prompt_loader import build_prompt_versions
from telemetry import Telemetry

# ── Step imports ──────────────────────────────────────────────────────────────
from steps.step_01_scope              import run as run_01_scope
from steps.step_01_scope_confidence   import run as run_01_confidence
from steps.step_02_retrieval          import run as run_02_retrieval
from steps.step_03_categories         import run as run_03_categories
from steps.step_03_normalize          import run as run_03_normalize
from steps.step_03_gap_detection      import run as run_03_gap_detection
from steps.step_04a_generation        import run as run_04a
from steps.step_04b_generation_review import run as run_04b
from steps.step_05_validation         import run as run_05_validation
from steps.step_06_clarification      import run as run_06_clarification
from steps.step_07_hallucination_scan import run as run_07_hallucination
from steps.step_07_alternative_check  import run as run_07_alternative
from steps.step_08_finalization       import run as run_08_finalization
from steps.step_09_commit             import run as run_09_commit


ALL_STEPS = [
    "01_scope", "01_scope_confidence", "02_retrieval",
    "03_categories", "03_normalize", "03_gap_detection",
    "04a", "04b",
    "05_validation", "06_clarification",
    "07_hallucination", "07_alternative",
    "08_finalization", "09_commit",
]

STEP_ALIASES = {
    "01_scope":            "01_scope",
    "01_scope_confidence": "01_scope_confidence",
    "01_confidence":       "01_scope_confidence",
    "02_retrieval":        "02_retrieval",
    "02":                  "02_retrieval",
    "03_categories":       "03_categories",
    "03_normalize":        "03_normalize",
    "03_gap_detection":    "03_gap_detection",
    "03_gap":              "03_gap_detection",
    "04a":                 "04a",
    "04b":                 "04b",
    "05_validation":       "05_validation",
    "05":                  "05_validation",
    "06_clarification":    "06_clarification",
    "06":                  "06_clarification",
    "07_hallucination":    "07_hallucination",
    "07_alternative":      "07_alternative",
    "08_finalization":     "08_finalization",
    "08":                  "08_finalization",
    "09_commit":           "09_commit",
    "09":                  "09_commit",
}


# ── Subdomain loader ──────────────────────────────────────────────────────────

def load_subdomain(subdomain_id: str) -> dict:
    if SUBDOMAINS_JSONL.exists():
        with open(SUBDOMAINS_JSONL) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("subdomain_id") == subdomain_id:
                        return rec
                except Exception:
                    pass
    print(f"[warn] {subdomain_id} not found — using stub")
    return _stub_subdomain(subdomain_id)


def _stub_subdomain(subdomain_id: str) -> dict:
    stubs = {
        "SD-001": {"subdomain_id": "SD-001", "subdomain_label": "Algebra",
                   "parent_domain": "Mathematics", "domain_id": "D-01",
                   "score": 93, "tier": 1},
    }
    return stubs.get(subdomain_id, {
        "subdomain_id": subdomain_id, "subdomain_label": subdomain_id,
        "parent_domain": "Unknown", "domain_id": "D-00", "score": 0, "tier": 1,
    })


# ── Run ID ────────────────────────────────────────────────────────────────────

def make_run_id(subdomain_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing = list(WORK_DIR.glob(f"{ts}_*_{subdomain_id}"))
    return f"{ts}_{len(existing) + 1:03d}_{subdomain_id}"


# ── RunState ──────────────────────────────────────────────────────────────────

class RunState:
    def __init__(self, run_id: str, subdomain: dict, kb_snapshot_id: str):
        self.run_id          = run_id
        self.subdomain       = subdomain
        self.kb_snapshot_id  = kb_snapshot_id

        self.scope           = None
        self.scope_hash      = None
        self.confidence      = None
        self.confidence_hash = None
        self.structure       = None
        self.structure_hash  = None
        self.categories      = None
        self.categories_hash = None
        self.normalized      = None
        self.normalized_hash = None
        self.gap_detection   = None
        self.gap_hash        = None

        self.drafts:   list[dict] = []
        self.reviewed: list[dict] = []

        self.validation_report = None
        self.report_hash       = None
        self.hall_report       = None
        self.hall_hash         = None
        self.alt_check         = None
        self.alt_hash          = None
        self.audit             = None
        self.final_path        = None

    def try_restore(self):
        def _load(step, filename):
            p = artifact_dir(WORK_DIR, self.run_id, step) / filename
            if p.exists():
                return read_json(p), str(sha256_file(p))
            return None, None

        self.scope,            self.scope_hash            = _load("01_scope",                       "scope.json")
        self.confidence,       self.confidence_hash       = _load("01_scope_confidence",            "scope_confidence.json")
        self.structure,        self.structure_hash        = _load("02_retrieval",                   "canonical_structure.json")
        self.categories,       self.categories_hash       = _load("03_enrichment_01_categories",    "categories.json")
        self.normalized,       self.normalized_hash       = _load("03_enrichment_02_normalize",     "normalized_categories.json")
        self.gap_detection,    self.gap_hash              = _load("03_enrichment_03_gap_detection", "gap_detection.json")
        self.validation_report, self.report_hash          = _load("05_validation",                  "validation_report.json")
        self.hall_report,      self.hall_hash             = _load("07_examination_01_hallucination_scan", "hallucination_report.json")
        self.alt_check,        self.alt_hash              = _load("07_examination_02_alternative_check",  "alternative_check.json")
        audit, _                                          = _load("08_finalization",                 "run_audit.json")
        self.audit = audit
        fp = artifact_dir(WORK_DIR, self.run_id, "08_finalization") / "final_problems.jsonl"
        self.final_path = fp if fp.exists() else None

        if self.normalized:
            for cat in self.normalized.get("items", []):
                idx = cat["index"]
                rp  = artifact_dir(WORK_DIR, self.run_id,
                                   f"04b_generation_review/cat_{idx:02d}") / "problems_reviewed.json"
                if rp.exists():
                    reviewed = read_json(rp)
                    self.reviewed.append({
                        "problems_reviewed": reviewed,
                        "reviewed_hash":     str(sha256_file(rp)),
                        "reviewed_key":      f"04b_generation_review:cat_{idx:02d}:problems_reviewed",
                        "category_index":    idx,
                    })


# ── Step selector ─────────────────────────────────────────────────────────────

def parse_steps(steps_arg: str, from_arg: str) -> list[str]:
    if steps_arg == "all":
        return ALL_STEPS[:]
    if from_arg:
        resolved = STEP_ALIASES.get(from_arg, from_arg)
        if resolved not in ALL_STEPS:
            raise ValueError(f"Unknown step: {from_arg}")
        return ALL_STEPS[ALL_STEPS.index(resolved):]
    selected = []
    for token in steps_arg.split(","):
        token = token.strip()
        resolved = STEP_ALIASES.get(token, token)
        if resolved not in ALL_STEPS:
            raise ValueError(f"Unknown step: {token}")
        if resolved not in selected:
            selected.append(resolved)
    selected.sort(key=lambda s: ALL_STEPS.index(s))
    return selected


# ── Step dispatcher ───────────────────────────────────────────────────────────

def dispatch(step: str, state: RunState, active_steps: list[str],
             tel: Telemetry) -> bool:
    run_id = state.run_id
    kb     = state.kb_snapshot_id
    sd     = state.subdomain

    print(f"\n{'='*60}")
    print(f"STEP: {step}")
    print(f"{'='*60}")

    with tel.step(step):

        if step == "01_scope":
            res = run_01_scope(run_id, sd, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.scope      = res["scope"]
            state.scope_hash = res["scope_hash"]
            return True

        if step == "01_scope_confidence":
            if not state.scope:
                print("[error] 01_scope_confidence requires scope")
                return False
            res = run_01_confidence(run_id, state.scope, state.scope_hash, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.confidence      = res["confidence"]
            state.confidence_hash = res["confidence_hash"]
            rec = res["recommendation"]
            if rec == "clarify":
                print(f"[routing] scope_confidence → clarify → re-running 01_scope")
                clarification = {
                    **state.scope,
                    "additional_context": state.confidence.get("flagged_ambiguities", []),
                }
                res2 = run_01_scope(run_id, sd, kb, clarification_input=clarification, tel=tel)
                if res2["status"] == "stop":
                    return False
                state.scope      = res2["scope"]
                state.scope_hash = res2["scope_hash"]
            return True

        if step == "02_retrieval":
            if not state.scope:
                print("[error] 02_retrieval requires scope")
                return False
            res = run_02_retrieval(run_id, state.scope, state.scope_hash, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.structure      = res["canonical_structure"]
            state.structure_hash = res["structure_hash"]
            return True

        if step == "03_categories":
            if not state.scope or not state.structure:
                print("[error] 03_categories requires scope + structure")
                return False
            res = run_03_categories(run_id, state.scope, state.scope_hash,
                                    state.structure, state.structure_hash, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.categories      = res["categories"]
            state.categories_hash = res["categories_hash"]
            return True

        if step == "03_normalize":
            if not state.categories:
                print("[error] 03_normalize requires categories")
                return False
            res = run_03_normalize(run_id, state.categories, state.categories_hash, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.normalized      = res["normalized_categories"]
            state.normalized_hash = res["normalized_hash"]
            return True

        if step == "03_gap_detection":
            if not state.scope or not state.structure or not state.normalized:
                print("[error] 03_gap_detection requires scope + structure + normalized")
                return False
            res = run_03_gap_detection(run_id,
                                       state.scope, state.scope_hash,
                                       state.structure, state.structure_hash,
                                       state.normalized, state.normalized_hash,
                                       kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.gap_detection = res["gap_detection"]
            state.gap_hash      = res["gap_hash"]
            return True

        if step in ("04a", "04b"):
            if not state.normalized:
                print("[error] 04a/04b requires normalized_categories")
                return False
            run_04b_flag = ("04b" in active_steps)
            new_reviewed = []

            for cat in state.normalized["items"]:
                if step == "04a" or "04a" in active_steps:
                    res_a = run_04a(run_id, state.scope, state.scope_hash,
                                    cat, state.gap_detection, state.gap_hash, kb, tel=tel)
                    if res_a["status"] == "stop":
                        print(f"[warn] 04a failed cat={cat['index']} — skipping")
                        continue
                    draft      = res_a["problems_draft"]
                    draft_hash = res_a["draft_hash"]
                else:
                    dp = artifact_dir(WORK_DIR, run_id,
                                      f"04a_generation/cat_{cat['index']:02d}") / "problems_draft.json"
                    if not dp.exists():
                        print(f"[warn] No draft cat={cat['index']} — skipping 04b")
                        continue
                    draft      = read_json(dp)
                    draft_hash = str(sha256_file(dp))

                if step == "04b" or run_04b_flag:
                    prior_key = next(
                        (r["reviewed_key"] for r in state.reviewed
                         if r["category_index"] == cat["index"]), None)
                    res_b = run_04b(run_id, state.scope, state.scope_hash,
                                    draft, draft_hash, cat,
                                    state.gap_detection, state.gap_hash, kb,
                                    prior_reviewed_key=prior_key, tel=tel)
                    if res_b["status"] == "stop":
                        print(f"[warn] 04b failed cat={cat['index']} — skipping")
                        continue
                    new_reviewed.append(res_b)

            if new_reviewed:
                state.reviewed = new_reviewed
            return True

        if step == "05_validation":
            if not state.reviewed:
                print("[error] 05_validation requires reviewed problems (04b)")
                return False
            all_rev  = [r["problems_reviewed"] for r in state.reviewed]
            rev_keys = [r["reviewed_key"] for r in state.reviewed]
            res = run_05_validation(run_id, state.scope, state.scope_hash,
                                    all_rev, rev_keys, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.validation_report = res["validation_report"]
            state.report_hash       = res["report_hash"]
            routing = res["routing"]
            print(f"[routing] validation → {routing}")
            tel.record_routing("05_validation", routing)

            if routing == "retry_categories":
                print("[info] retry_categories: re-running 04a+04b")
                state.reviewed = []
                dispatch("04a", state, active_steps, tel)
                dispatch("04b", state, active_steps, tel)
                all_rev  = [r["problems_reviewed"] for r in state.reviewed]
                rev_keys = [r["reviewed_key"] for r in state.reviewed]
                res2 = run_05_validation(run_id, state.scope, state.scope_hash,
                                         all_rev, rev_keys, kb, tel=tel)
                state.validation_report = res2.get("validation_report", state.validation_report)
                state.report_hash       = res2.get("report_hash", state.report_hash)
            return True

        if step == "06_clarification":
            if not state.scope:
                print("[error] 06_clarification requires scope")
                return False
            res = run_06_clarification(run_id, state.scope, state.scope_hash, kb,
                                       validation_report=state.validation_report,
                                       report_hash=state.report_hash,
                                       confidence=state.confidence,
                                       confidence_hash=state.confidence_hash,
                                       tel=tel)
            if res["status"] == "stop":
                return False
            state.scope      = res["refined_scope"]
            state.scope_hash = None
            from common import artifact_dir as _adir, write_json as _wj, register_artifact as _reg, sha256_file as _shf
            sp = _adir(WORK_DIR, run_id, "01_scope") / "scope.json"
            _wj(sp, state.scope)
            state.scope_hash = str(_shf(sp))
            _reg(WORK_DIR, run_id, "01_scope:scope", sp,
                 content_state="candidate", step="01_scope_clarified")
            print("[routing] clarification → re-run from 01_scope_confidence")
            return True

        if step == "07_hallucination":
            if not state.reviewed:
                print("[error] 07_hallucination requires reviewed problems")
                return False
            all_rev    = [r["problems_reviewed"] for r in state.reviewed]
            rev_hashes = [r["reviewed_hash"] for r in state.reviewed]
            res = run_07_hallucination(run_id, state.scope, state.scope_hash,
                                       all_rev, rev_hashes,
                                       state.validation_report or {}, state.report_hash or "",
                                       kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.hall_report = res["hallucination_report"]
            state.hall_hash   = res["hall_hash"]
            tel.record_routing("07_hallucination", res["routing"])
            print(f"[routing] hallucination → {res['routing']}")
            return True

        if step == "07_alternative":
            if not state.normalized or not state.hall_report:
                print("[error] 07_alternative requires normalized_categories + hallucination_report")
                return False
            res = run_07_alternative(run_id, state.scope, state.scope_hash,
                                     state.normalized, state.normalized_hash,
                                     state.gap_detection or {}, state.gap_hash or "",
                                     state.hall_report, state.hall_hash, kb, tel=tel)
            if res["status"] == "stop":
                return False
            state.alt_check = res["alternative_check"]
            state.alt_hash  = res["alt_hash"]
            tel.record_routing("07_alternative", res["routing"])
            print(f"[routing] alternative_check → {res['routing']}")
            return True

        if step == "08_finalization":
            if not state.reviewed:
                print("[error] 08_finalization requires reviewed problems")
                return False
            pipeline_status = "validated"
            if state.validation_report and not state.validation_report.get("valid"):
                pipeline_status = "insufficient"
            all_rev    = [r["problems_reviewed"] for r in state.reviewed]
            rev_hashes = [r["reviewed_hash"] for r in state.reviewed]
            res = run_08_finalization(run_id,
                                      state.scope, state.scope_hash,
                                      all_rev, rev_hashes,
                                      state.hall_report or {"flagged": []}, state.hall_hash or "",
                                      state.alt_check or {}, state.alt_hash or "",
                                      pipeline_status, kb, state.subdomain, tel=tel)
            if res["status"] == "stop":
                return False
            state.audit      = res["audit"]
            state.final_path = res["final_path"]
            return True

        if step == "09_commit":
            if not state.final_path or not state.audit:
                print("[error] 09_commit requires finalization output")
                return False
            res = run_09_commit(run_id, state.final_path, state.audit, kb, tel=tel)
            if res["status"] == "stop":
                return False
            return True

    print(f"[error] Unknown step: {step}")
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Atomic Problem Identification Pipeline v14")
    parser.add_argument("--subdomain",      required=True)
    parser.add_argument("--steps",          default="all")
    parser.add_argument("--from",           dest="from_step", default=None)
    parser.add_argument("--run-id",         default=None)
    parser.add_argument("--prompt-variant", default=PROMPT_VARIANT,
                        help="Prompt variant for A/B testing (e.g. v2)")
    parser.add_argument("--dry-run",        action="store_true")
    args = parser.parse_args()

    # Set prompt variant in env for prompt_loader
    if args.prompt_variant:
        os.environ["PROMPT_VARIANT"] = args.prompt_variant

    try:
        active_steps = parse_steps(args.steps, args.from_step)
    except ValueError as e:
        print(f"[error] {e}")
        print(f"Available steps: {', '.join(ALL_STEPS)}")
        sys.exit(1)

    if args.dry_run:
        print("Steps that would run (in order):")
        for s in active_steps:
            print(f"  {s}")
        sys.exit(0)

    subdomain = load_subdomain(args.subdomain)
    print(f"\nPipeline v{PIPELINE_VERSION}")
    print(f"Subdomain: {subdomain.get('subdomain_label')} ({args.subdomain})")
    print(f"Steps: {', '.join(active_steps)}")
    if args.prompt_variant:
        print(f"Prompt variant: {args.prompt_variant}")

    if SUBDOMAINS_JSONL.exists():
        kb_snapshot_id = sha256_file(SUBDOMAINS_JSONL)
    else:
        kb_snapshot_id = sha256_str(args.subdomain)
        print("[warn] subdomains.jsonl not found — stub kb_snapshot_id")

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or make_run_id(args.subdomain)
    print(f"Run ID: {run_id}")
    print(f"Work dir: {WORK_DIR / run_id}\n")

    # Init run_record with prompt_versions
    prompt_versions = build_prompt_versions(active_steps, variant=args.prompt_variant)
    rec = load_run_record(WORK_DIR, run_id)
    rec.setdefault("subdomain_id", args.subdomain)
    rec.setdefault("kb_snapshot_id", kb_snapshot_id)
    rec["status"]          = "running"
    rec["prompt_versions"] = prompt_versions
    rec["prompt_variant"]  = args.prompt_variant or "active"
    save_run_record(WORK_DIR, run_id, rec)

    emit_state(WORK_DIR, run_id, "run.start", "orchestrator",
               {"subdomain_id":    args.subdomain,
                "active_steps":    active_steps,
                "kb_snapshot_id":  kb_snapshot_id,
                "prompt_versions": prompt_versions})

    # Init telemetry
    tel = Telemetry(WORK_DIR, run_id, enabled=TELEMETRY_ENABLED)

    # Init run state and restore
    state = RunState(run_id, subdomain, kb_snapshot_id)
    state.try_restore()

    # Dispatch steps
    for step in active_steps:
        ok = dispatch(step, state, active_steps, tel)
        if not ok:
            print(f"\n[STOP] Pipeline halted at step: {step}")
            rec = load_run_record(WORK_DIR, run_id)
            rec["status"]          = "stop"
            rec["stopped_at_step"] = step
            save_run_record(WORK_DIR, run_id, rec)
            emit_state(WORK_DIR, run_id, "run.stop", step, {})
            tel.record_stop(step, "dispatch_returned_false")
            tel.finalize()
            sys.exit(1)

    # Finalize telemetry
    summary = tel.finalize()

    print(f"\n{'='*60}")
    print(f"Run complete: {run_id}")
    print(f"Total time:   {summary.get('total_duration_s', '?')}s")
    print(f"LLM calls:    {summary.get('llm', {}).get('total_calls', '?')} "
          f"(error rate: {summary.get('llm', {}).get('error_rate', '?'):.1%})")
    print(f"Telemetry:    {WORK_DIR / run_id / 'telemetry_summary.json'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
