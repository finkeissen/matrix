from __future__ import annotations
import json, uuid
from typing import Any, Dict, List
from lib.io import sha256_str

MODULE_VERSION = "v1"

def _event_id() -> str:
    return "evt_" + uuid.uuid4().hex[:16]

def update_problem_seed(*, state: Dict[str, Any], inputs: Dict[str, Any], params: Dict[str, Any], cfg: Dict[str, Any], provider):
    texts = inputs.get("texts", [])
    if not isinstance(texts, list) or not texts:
        return [], {"created":0,"updated":0,"skipped":0,"flagged":1,"warnings":["No inputs.texts provided"]}

    prompt_cfg = cfg.get("prompts", {})
    sys_t = prompt_cfg.get("problem_seed_system", "")
    user_t = prompt_cfg.get("problem_seed_user", "")

    prov = cfg.get("provider", {})
    model = prov.get("model","local-model")
    temperature = float(prov.get("temperature",0.0))
    max_tokens = int(prov.get("max_tokens",2000))

    patch_events = []
    created = 0

    for item in texts:
        text = item.get("text","")
        if not text.strip():
            continue
        user_msg = user_t.replace("{{text}}", text)

        content = provider.chat(
            [{"role":"system","content":sys_t},{"role":"user","content":user_msg}],
            model=model, temperature=temperature, max_tokens=max_tokens
        )

        try:
            candidates = json.loads(content)
        except Exception as e:
            patch_events.append({
                "event_id": _event_id(),
                "provenance": {"provider":"lm_studio", "note":"json_parse_failed"},
                "ops": [{
                    "op":"upsert_entity",
                    "record":{
                        "entity_id":"pcand_parse_error_"+uuid.uuid4().hex[:8],
                        "type":"ontology.problem/ProblemCandidate",
                        "label":"PARSE_ERROR",
                        "description":f"Provider returned non-JSON: {str(e)}",
                        "scope":"unknown",
                        "status":"needs_review",
                        "attributes":{"raw_output":content[:2000]},
                        "evidence_refs":[]
                    }
                }]
            })
            continue

        for c in candidates:
            label = (c.get("label") or "").strip()
            if not label:
                continue
            subtype = (c.get("subtype") or "inferred_issue").strip()
            scope = (c.get("scope") or "unknown").strip()
            desc = (c.get("description") or "").strip()
            excerpt = (c.get("evidence_excerpt") or "").strip()

            cid = "pcand_" + sha256_str(label+"|"+scope+"|"+excerpt)[7:31]
            rec = {
                "entity_id": cid,
                "type": "ontology.problem/ProblemCandidate",
                "label": label,
                "description": desc,
                "scope": scope,
                "status": "draft",
                "attributes": {
                    "subtype": subtype,
                    "evidence_excerpt": excerpt,
                    "source_id": item.get("source_id","unknown"),
                },
                "evidence_refs": []
            }
            patch_events.append({
                "event_id": _event_id(),
                "provenance": {"provider":"lm_studio", "model":model, "temperature":temperature},
                "ops": [{"op":"upsert_entity","record":rec}]
            })
            created += 1

    return patch_events, {"created":created,"updated":0,"skipped":0,"flagged":0,"warnings":[]}
