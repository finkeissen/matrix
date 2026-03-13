from __future__ import annotations
import json, uuid
from typing import Any, Dict, List

from lib.io import sha256_str
from lib.ids import stable_problem_id

MODULE_VERSION = "v1"

def _event_id() -> str:
    return "evt_" + uuid.uuid4().hex[:16]

def update_problem_atomize(*, state: Dict[str, Any], inputs: Dict[str, Any], params: Dict[str, Any], cfg: Dict[str, Any], provider):
    candidates = inputs.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return [], {"created":0,"updated":0,"skipped":0,"flagged":1,"warnings":["No inputs.candidates provided"]}

    prompt_cfg = cfg.get("prompts", {})
    sys_t = prompt_cfg.get("problem_atomize_system", "")
    user_t = prompt_cfg.get("problem_atomize_user", "")

    prov = cfg.get("provider", {})
    model = prov.get("model","local-model")
    temperature = float(prov.get("temperature",0.0))
    max_tokens = int(prov.get("max_tokens",2000))

    candidates_json = json.dumps(candidates, ensure_ascii=False)
    user_msg = user_t.replace("{{candidates_json}}", candidates_json)

    content = provider.chat(
        [{"role":"system","content":sys_t},{"role":"user","content":user_msg}],
        model=model, temperature=temperature, max_tokens=max_tokens
    )

    try:
        obj = json.loads(content)
        atomic = obj.get("atomic_problems", [])
    except Exception as e:
        ev = {
            "event_id": _event_id(),
            "provenance": {"provider":"lm_studio", "note":"json_parse_failed"},
            "ops": [{
                "op":"upsert_entity",
                "record":{
                    "entity_id":"atomize_parse_error_"+uuid.uuid4().hex[:8],
                    "type":"ontology.problem/Problem",
                    "problem_id":"prob_error_"+uuid.uuid4().hex[:8],
                    "atomic": True,
                    "label":"ATOMIZE_PARSE_ERROR",
                    "description":f"Provider returned non-JSON: {str(e)}",
                    "scope":"unknown",
                    "status":"needs_review",
                    "attributes":{"raw_output":content[:2000]},
                    "evidence_refs":[]
                }
            }]
        }
        return [ev], {"created":1,"updated":0,"skipped":0,"flagged":1,"warnings":["Atomize parse failed; created placeholder problem."]}

    patch_events = []
    created = 0
    for p in atomic:
        label = (p.get("label") or "").strip()
        if not label:
            continue
        scope = (p.get("scope") or "unknown").strip()
        desc = (p.get("description") or "").strip()
        primary_symptom = (p.get("primary_symptom") or "").strip()
        derived_idx = p.get("derived_from_index", [])
        if not isinstance(derived_idx, list):
            derived_idx = []

        pid = stable_problem_id(label, scope, primary_symptom or label)
        ent_id = pid
        derived_ids = []
        for i in derived_idx:
            if isinstance(i,int) and 0 <= i < len(candidates):
                cid = candidates[i].get("entity_id")
                if cid:
                    derived_ids.append(cid)

        rec = {
            "entity_id": ent_id,
            "type": "ontology.problem/Problem",
            "problem_id": pid,
            "atomic": True,
            "label": label,
            "description": desc,
            "scope": scope,
            "status": "draft",
            "attributes": {"primary_symptom": primary_symptom, "derived_from_candidate_ids": derived_ids},
            "evidence_refs": []
        }

        ops = [{"op":"upsert_entity","record":rec}]
        for cid in derived_ids:
            asrt_id = "asrt_" + sha256_str(pid+"|derived_from|"+cid)[7:31]
            ops.append({
                "op":"upsert_assertion",
                "record":{
                    "assertion_id": asrt_id,
                    "type":"relation/derived_from",
                    "subject_ref": ent_id,
                    "object_ref": cid,
                    "qualifiers": {},
                    "scope": scope,
                    "evidence_refs": []
                }
            })

        patch_events.append({
            "event_id": _event_id(),
            "provenance": {"provider":"lm_studio", "model":model, "temperature":temperature},
            "ops": ops
        })
        created += 1

    return patch_events, {"created":created,"updated":0,"skipped":0,"flagged":0,"warnings":[]}
