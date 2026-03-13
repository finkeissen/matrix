"""
step_08_finalization.py — Assign IDs, produce final JSONL.
Type: deterministic + 1 LLM call (run summary only)
Snapshot after: yes
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WORK_DIR, DEFAULT_RETRIES, SYSTEM_VERSION
from common import (
    llm_call, parse_json_response, sha256_file, now_iso,
    artifact_dir, write_json, write_jsonl_line, register_artifact,
    emit_state, create_snapshot,
)

STEP = "08_finalization"

SUMMARY_PROMPT = """In 2-4 sentences, summarize this atomic problem generation run for the subdomain {subdomain_label}.
Total problems: {total}
Categories: {categories}
Pipeline status: {status}
Hallucination risk distribution: low={low} medium={medium} high={high}

Return only the summary text. No JSON, no preamble."""


# ── problem_id prefix derivation (E-02) ──────────────────────────────────────

_STOPWORDS = {"und", "and", "of", "the"}

def derive_prefix(subdomain_label: str) -> str:
    label = (subdomain_label
             .replace("ä", "ae").replace("ö", "oe")
             .replace("ü", "ue").replace("ß", "ss"))
    words = [w for w in re.split(r"[\s&/]+", label) if w]
    content = [w for w in words if w.lower() not in _STOPWORDS]
    if not content:
        content = words
    if len(content) == 1:
        return content[0][:5].upper()
    initials = "".join(w[0] for w in content)
    prefix   = initials[:5].upper()
    if len(prefix) < 5:
        # Pad with next chars of last content word
        last = content[-1].upper()
        prefix = (prefix + last[1:])[:5]
    return prefix.ljust(5, "X")


def _check_prefix_collision(prefix: str, run_id: str) -> str:
    """Append -A or -B if prefix is already registered in this run's collision table."""
    collision_path = artifact_dir(WORK_DIR, run_id, STEP) / "prefix_collisions.json"
    if collision_path.exists():
        table = json.loads(collision_path.read_text())
    else:
        table = {}
    if prefix not in table:
        table[prefix] = run_id
        write_json(collision_path, table)
        return prefix
    # Collision: find suffix
    for suffix in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        candidate = f"{prefix}-{suffix}"
        if candidate not in table:
            table[candidate] = run_id
            write_json(collision_path, table)
            return candidate
    raise RuntimeError(f"Cannot resolve prefix collision for {prefix}")


def run(run_id: str, scope: dict, scope_hash: str,
        all_reviewed: list[dict],
        reviewed_hashes: list[str],
        hallucination_report: dict, hall_hash: str,
        alternative_check: dict, alt_hash: str,
        pipeline_status: str,
        kb_snapshot_id: str,
        subdomain: dict) -> dict:
    """
    pipeline_status: "validated" | "partial" | "insufficient"
    Returns: {"status": "ok"|"stop", "final_count": int, "final_path": Path}
    """
    print(f"[{STEP}] run={run_id} status={pipeline_status}")
    emit_state(WORK_DIR, run_id, "step.start", STEP, {"pipeline_status": pipeline_status})

    out_dir       = artifact_dir(WORK_DIR, run_id, STEP)
    final_path    = out_dir / "final_problems.jsonl"
    audit_path    = out_dir / "run_audit.json"

    # ── Build hallucination correction map ────────────────────────────────────
    hall_corrections: dict[str, str] = {}
    for flag in hallucination_report.get("flagged", []):
        title   = flag.get("title", "")
        corrected = flag.get("corrected_hallucination_risk")
        if title and corrected:
            hall_corrections[title] = corrected

    # ── Derive problem_id prefix ───────────────────────────────────────────────
    subdomain_label = scope.get("subdomain", "Unknown")
    prefix = derive_prefix(subdomain_label)
    prefix = _check_prefix_collision(prefix, run_id)

    domain_id   = subdomain.get("domain_id", "D-00")
    subdomain_id = scope.get("subdomain_id", "SD-000")
    parent_domain = scope.get("parent_domain", "Unknown")
    created_by   = f"pipeline_v2/run_{run_id}"
    created_at   = now_iso()

    # ── Write final_problems.jsonl ────────────────────────────────────────────
    counter = 1
    problems_by_category: dict[str, int] = {}
    problems_by_difficulty = {"basic": 0, "intermediate": 0, "advanced": 0, "expert": 0}
    problems_by_risk       = {"low": 0, "medium": 0, "high": 0}
    hall_corrections_applied = 0

    if final_path.exists():
        final_path.unlink()

    for rev in all_reviewed:
        cat_name = rev.get("category", "unknown")
        problems_by_category[cat_name] = 0
        for p in rev.get("problems", []):
            problem_id = f"{prefix}-{counter:04d}"
            # Apply hallucination correction
            hall_risk = p.get("hallucination_risk", "medium")
            if p.get("title") in hall_corrections:
                hall_risk = hall_corrections[p["title"]]
                hall_corrections_applied += 1

            record = {
                "problem_id":       problem_id,
                "subdomain_id":     subdomain_id,
                "domain_id":        domain_id,
                "parent_domain":    parent_domain,
                "subdomain_label":  subdomain_label,
                "title":            p.get("title", ""),
                "problem_statement": p.get("problem_statement", ""),
                "category":         cat_name,
                "difficulty":       p.get("difficulty", "intermediate"),
                "answer_type":      p.get("answer_type", "factual"),
                "canonical_source": p.get("canonical_source", ""),
                "verifiable":       p.get("verifiable", False),
                "hallucination_risk": hall_risk,
                "requires_context": p.get("requires_context", False),
                "tags":             p.get("tags", []),
                "created_by":       created_by,
                "created_at":       created_at,
                "review_status":    "draft",
            }
            write_jsonl_line(final_path, record)
            counter += 1
            problems_by_category[cat_name] = problems_by_category.get(cat_name, 0) + 1
            diff = record["difficulty"]
            if diff in problems_by_difficulty:
                problems_by_difficulty[diff] += 1
            risk = record["hallucination_risk"]
            if risk in problems_by_risk:
                problems_by_risk[risk] += 1

    total_problems = counter - 1

    if total_problems == 0:
        emit_state(WORK_DIR, run_id, "step.stop", STEP,
                   {"stop_code": "deterministic_step_error",
                    "reason": "zero problems in final output"})
        return {"status": "stop", "stop_code": "deterministic_step_error"}

    register_artifact(WORK_DIR, run_id, f"{STEP}:final_problems",
                      final_path, content_state="verified", step=STEP)

    # ── LLM run summary (graceful degradation) ────────────────────────────────
    from common import load_run_record
    rec = load_run_record(WORK_DIR, run_id)

    summary_prompt = SUMMARY_PROMPT.format(
        subdomain_label=subdomain_label,
        total=total_problems,
        categories=", ".join(problems_by_category.keys()),
        status=pipeline_status,
        low=problems_by_risk["low"],
        medium=problems_by_risk["medium"],
        high=problems_by_risk["high"],
    )
    raw_summary = llm_call(summary_prompt, retries=0)
    run_summary = raw_summary.strip() if raw_summary else None

    # ── Write run_audit.json ──────────────────────────────────────────────────
    audit = {
        "run_id":                       run_id,
        "subdomain_id":                 subdomain_id,
        "subdomain_label":              subdomain_label,
        "kb_snapshot_id":               kb_snapshot_id,
        "pipeline_status":              pipeline_status,
        "total_problems":               total_problems,
        "problems_by_category":         problems_by_category,
        "problems_by_difficulty":       problems_by_difficulty,
        "problems_by_hallucination_risk": problems_by_risk,
        "hallucination_corrections_applied": hall_corrections_applied,
        "clarification_rounds":         rec.get("clarification_rounds", 0),
        "generation_retries":           0,   # orchestrator can fill
        "run_summary":                  run_summary,
        "system_version":               SYSTEM_VERSION,
        "finalized_at":                 now_iso(),
    }
    write_json(audit_path, audit)
    register_artifact(WORK_DIR, run_id, f"{STEP}:run_audit",
                      audit_path, content_state="verified", step=STEP)

    snap_id = create_snapshot(WORK_DIR, run_id, "pre_commit")
    emit_state(WORK_DIR, run_id, "step.done", STEP,
               {"total_problems": total_problems, "prefix": prefix,
                "hall_corrections": hall_corrections_applied,
                "snapshot_id": snap_id})

    print(f"  [done] {total_problems} problems written → {final_path}")
    print(f"  prefix={prefix} corrections={hall_corrections_applied}")
    return {"status": "ok", "final_count": total_problems,
            "final_path": final_path, "audit": audit}
