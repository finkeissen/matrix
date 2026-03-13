#!/usr/bin/env python3
"""steps/00_atomic_problem_curation.py — Step 00: Curate atomic problem candidates.

Engine step:  run(ctx, step_input, config, prompt_loader)
CLI wrapper:  python 00_atomic_problem_curation.py --domain X --input Y --output-dir Z

Input contract:
    step_input["domain"]              — domain name
    step_input["subdomains_file"]     — path to .jsonl/.json/.txt/.zip with subdomains
    step_input["provider"]            — "lm-studio" | "offline-template"
    step_input["output_dir"]          — where to write candidate batches
    step_input["provider_config"]     — dict with model/base_url/temperature/max_tokens/timeout/seed
    step_input["curation_params"]     — dict with records_per_file/subdomains_per_call/atomic_per_subdomain/sleep_seconds/limit_subdomains

Output (data dict):
    domain, subdomain_count, total_candidates, inserted, updated, unchanged,
    output_files, manifest, output_dir
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterator, Sequence

LOGGER = logging.getLogger("atomic_problem_curation")
JSON_ARRAY_RE = re.compile(r"\[.*\]", flags=re.S)
BATCH_NAME_RE = re.compile(r"^(?P<domain>[a-z0-9_]+)_atomic_candidates_(?P<num>\d{4})\.jsonl$")


# ── Pure utility functions (no I/O) ──────────────────────────────────────────

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()

def slugify(value: str) -> str:
    value = normalize_ws(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")

def chunked(items: Sequence[str], size: int) -> Iterator[list[str]]:
    if size <= 0:
        raise ValueError("chunk size must be > 0")
    for idx in range(0, len(items), size):
        yield list(items[idx: idx + size])

def unique_texts(values) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        if raw is None:
            continue
        value = normalize_ws(str(raw))
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out

def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding=encoding) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)

def safe_int_0_99(value: Any, default: int = 50) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(0, min(99, number))

def candidate_id(domain: str, subdomain: str, atomic_problem: str) -> str:
    return slugify(f"{domain}__{subdomain}__{atomic_problem}")


# ── I/O helpers ──────────────────────────────────────────────────────────────

def read_text_maybe_zip(path: Path) -> list[tuple[str, str]]:
    if path.suffix.lower() != ".zip":
        return [(path.name, path.read_text(encoding="utf-8"))]
    payloads: list[tuple[str, str]] = []
    with zipfile.ZipFile(path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            if not info.filename.lower().endswith((".jsonl", ".json", ".txt")):
                continue
            with zf.open(info, "r") as fh:
                payloads.append((info.filename, fh.read().decode("utf-8", errors="replace")))
    return payloads

def extract_subdomains_from_record(record: Any) -> list[str]:
    if isinstance(record, str):
        return unique_texts([record])
    if not isinstance(record, dict):
        return []
    hits: list[str] = []
    for key in ("subdomain", "sub_domain", "subsubdomain", "topic", "name", "title", "label", "candidate", "item"):
        value = record.get(key)
        if isinstance(value, str):
            hits.append(value)
    for key in ("subdomains", "subsubdomains", "topics", "labels", "items", "candidates"):
        value = record.get(key)
        if isinstance(value, list):
            hits.extend(item for item in value if isinstance(item, str))
    return unique_texts(hits)

def load_subdomains(path: Path) -> list[str]:
    subdomains: list[str] = []
    for name, text in read_text_maybe_zip(path):
        suffix = Path(name).suffix.lower()
        if suffix == ".jsonl":
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    subdomains.extend(unique_texts([line]))
                    continue
                subdomains.extend(extract_subdomains_from_record(record))
        elif suffix == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, list):
                for item in payload:
                    subdomains.extend(extract_subdomains_from_record(item))
            elif isinstance(payload, dict):
                subdomains.extend(extract_subdomains_from_record(payload))
        else:
            for line in text.splitlines():
                subdomains.extend(unique_texts([line]))
    return sorted(unique_texts(subdomains), key=str.casefold)

def batch_path(output_dir: Path, domain: str, number: int) -> Path:
    return output_dir / f"{slugify(domain)}_atomic_candidates_{number:04d}.jsonl"

def iter_existing_batch_paths(output_dir: Path, domain: str) -> list[Path]:
    domain_slug = slugify(domain)
    matches: list[tuple[int, Path]] = []
    for path in output_dir.glob("*_atomic_candidates_*.jsonl"):
        match = BATCH_NAME_RE.match(path.name)
        if not match or match.group("domain") != domain_slug:
            continue
        matches.append((int(match.group("num")), path))
    matches.sort(key=lambda item: item[0])
    return [path for _, path in matches]

def load_existing_candidates(output_dir: Path, domain: str) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    for path in iter_existing_batch_paths(output_dir, domain):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                LOGGER.warning("Skipping invalid JSON line in %s", path)
                continue
            cid = normalize_ws(str(record.get("candidate_id", "")))
            if not cid:
                ap = normalize_ws(str(record.get("atomic_problem", "")))
                sd = normalize_ws(str(record.get("subdomain", "")))
                if ap and sd:
                    cid = candidate_id(domain, sd, ap)
                    record["candidate_id"] = cid
            if cid:
                existing[cid] = record
    return existing

def merge_candidate(existing: dict[str, Any] | None, fresh: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if existing is None:
        record = dict(fresh)
        record.setdefault("status", "candidate")
        record.setdefault("version", 1)
        ts = record.get("created_at") or utc_now()
        record.setdefault("created_at", ts)
        record["updated_at"] = record.get("updated_at") or ts
        return record, "inserted"
    merged = dict(existing)
    changed = False
    for key in ("domain", "subdomain", "atomic_problem"):
        value = normalize_ws(str(fresh.get(key, "")))
        if value and merged.get(key) != value:
            merged[key] = value
            changed = True
    fresh_conf = safe_int_0_99(fresh.get("candidate_confidence"), 0)
    old_conf = safe_int_0_99(merged.get("candidate_confidence"), 0)
    if fresh_conf > old_conf:
        merged["candidate_confidence"] = fresh_conf
        changed = True
    for key in ("possible_parents", "possible_siblings", "possible_children"):
        merged_vals = list(merged.get(key) or [])
        fresh_vals = list(fresh.get(key) or [])
        union = unique_texts([*merged_vals, *fresh_vals])
        if union != merged_vals:
            merged[key] = union
            changed = True
    rationale = normalize_ws(str(fresh.get("family_rationale", "")))
    if rationale and rationale != normalize_ws(str(merged.get("family_rationale", ""))):
        merged["family_rationale"] = rationale
        changed = True
    merged.setdefault("status", "candidate")
    merged.setdefault("version", 1)
    merged.setdefault("created_at", fresh.get("created_at") or existing.get("created_at") or utc_now())
    if changed:
        merged["version"] = int(merged.get("version", 1)) + 1
        merged["updated_at"] = utc_now()
        return merged, "updated"
    merged.setdefault("updated_at", merged.get("created_at") or utc_now())
    return merged, "unchanged"

def write_batches(output_dir: Path, domain: str, records: list[dict[str, Any]], records_per_file: int) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in iter_existing_batch_paths(output_dir, domain):
        path.unlink(missing_ok=True)
    written: list[Path] = []
    records = sorted(records, key=lambda r: (str(r.get("subdomain", "")).casefold(), str(r.get("atomic_problem", "")).casefold()))
    for batch_num, offset in enumerate(range(0, len(records), records_per_file), start=1):
        path = batch_path(output_dir, domain, batch_num)
        payload = "\n".join(json.dumps(rec, ensure_ascii=False) for rec in records[offset: offset + records_per_file])
        if payload:
            payload += "\n"
        atomic_write_text(path, payload)
        written.append(path)
    return written

def write_manifest(output_dir: Path, domain: str, batch_paths: list[Path],
                   subdomain_count: int, counters: dict[str, int], provider: str) -> Path:
    file_counts = [sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip()) for p in batch_paths]
    manifest = {
        "domain": domain, "provider": provider, "subdomain_count": subdomain_count,
        "total_candidates": sum(file_counts), "records_per_file": max([0] + file_counts),
        "files": [p.name for p in batch_paths],
        "inserted": counters.get("inserted", 0), "updated": counters.get("updated", 0),
        "unchanged": counters.get("unchanged", 0), "updated_at": utc_now(),
    }
    path = output_dir / "_latest_manifest.json"
    atomic_write_text(path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return path


# ── LLM providers ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model: str
    base_url: str
    temperature: float
    max_tokens: int
    timeout: int
    seed: int | None

def build_prompt(domain: str, subdomains: Sequence[str], atomic_per_subdomain: int) -> str:
    subdomain_lines = "\n".join(f"- {item}" for item in subdomains)
    return f"""
You are curating atomic problem candidates for the domain '{domain}'.

For each subdomain below, generate up to {atomic_per_subdomain} candidate atomic problems.
For each atomic problem, also provide:
- possible_parents, possible_siblings, possible_children
- candidate_confidence: integer 0-99
- family_rationale: one short sentence

Rules: stay inside the subdomain, return JSON array only.

Expected JSON format:
[{{"subdomain":"...","atomic_problem":"...","possible_parents":[],"possible_siblings":[],"possible_children":[],"candidate_confidence":0,"family_rationale":"..."}}]

Subdomains:
{subdomain_lines}
""".strip()

def call_offline_template(domain: str, subdomains: Sequence[str], atomic_per_subdomain: int, seed: int | None) -> list[dict[str, Any]]:
    rng = random.Random(seed if seed is not None else 0)
    records: list[dict[str, Any]] = []
    for subdomain in subdomains:
        topic = normalize_ws(subdomain)
        base = topic.lower()
        patterns = [
            f"Estimate key state variables in {base}",
            f"Predict transitions and limiting cases in {base}",
            f"Determine governing constraints for {base}",
        ]
        for atomic_problem in patterns[:max(1, atomic_per_subdomain)]:
            records.append({
                "subdomain": topic, "atomic_problem": atomic_problem,
                "possible_parents": [f"Analyze core mechanisms in {base}"],
                "possible_siblings": [f"Compare competing models in {base}", f"Quantify uncertainty in {base}"],
                "possible_children": [f"Solve a simplified benchmark case in {base}", f"Handle parameter sensitivity in {base}"],
                "candidate_confidence": rng.randint(60, 92),
                "family_rationale": f"Concrete candidate within {topic}, but possibly still splittable.",
            })
    return records

def extract_first_json_array(text: str) -> list[dict[str, Any]]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("Empty model response")
    try:
        payload = json.loads(stripped)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(.*?)```", stripped, flags=re.S | re.I)
    if fenced:
        try:
            payload = json.loads(fenced.group(1).strip())
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
        except json.JSONDecodeError:
            pass
    # last resort: find first [...] block
    start = stripped.find("[")
    if start >= 0:
        depth, in_str, escape = 0, False, False
        for idx in range(start, len(stripped)):
            ch = stripped[idx]
            if in_str:
                escape = (not escape and ch == "\\")
                if not escape and ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    try:
                        payload = json.loads(stripped[start: idx + 1])
                        return [item for item in payload if isinstance(item, dict)]
                    except json.JSONDecodeError:
                        break
    raise ValueError(f"No JSON array found in model response: {stripped[:300]}")

def call_lm_studio(config: ProviderConfig, domain: str, subdomains: Sequence[str], atomic_per_subdomain: int) -> list[dict[str, Any]]:
    prompt = build_prompt(domain, subdomains, atomic_per_subdomain)
    body: dict[str, Any] = {
        "model": config.model, "temperature": config.temperature, "max_tokens": config.max_tokens,
        "messages": [
            {"role": "system", "content": "Return valid JSON only. No markdown. No prose."},
            {"role": "user", "content": prompt},
        ],
    }
    if config.seed is not None:
        body["seed"] = config.seed
    request = urllib.request.Request(
        url=config.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LM Studio request failed: {exc}") from exc
    payload = json.loads(raw)
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError(f"LM Studio response had no choices: {raw[:300]}")
    return extract_first_json_array(choices[0].get("message", {}).get("content", ""))

def normalize_record(domain: str, raw: dict[str, Any]) -> dict[str, Any] | None:
    subdomain = normalize_ws(str(raw.get("subdomain") or raw.get("subsubdomain") or ""))
    atomic_problem = normalize_ws(str(raw.get("atomic_problem") or raw.get("title") or raw.get("problem") or ""))
    if not subdomain or not atomic_problem:
        return None
    parents = raw.get("possible_parents")
    siblings = raw.get("possible_siblings")
    children = raw.get("possible_children")
    return {
        "candidate_id": candidate_id(domain, subdomain, atomic_problem),
        "domain": domain, "subdomain": subdomain, "atomic_problem": atomic_problem,
        "possible_parents": unique_texts(parents if isinstance(parents, list) else []),
        "possible_siblings": unique_texts(siblings if isinstance(siblings, list) else []),
        "possible_children": unique_texts(children if isinstance(children, list) else []),
        "candidate_confidence": safe_int_0_99(raw.get("candidate_confidence"), 50),
        "family_rationale": normalize_ws(str(raw.get("family_rationale", ""))),
        "status": "candidate", "version": 1,
        "created_at": utc_now(), "updated_at": utc_now(),
    }


# ── Engine step ───────────────────────────────────────────────────────────────

def run(ctx, step_input: dict, config, prompt_loader) -> dict:
    """Engine entry point — contract-driven, no CLI args needed.

    Reads from step_input:
        domain, subdomains_file, provider, output_dir, provider_config, curation_params
    Returns:
        {"data": {...summary...}, "counts": {...}}
    """
    domain = normalize_ws(step_input["domain"])
    subdomains_file = Path(step_input["subdomains_file"])
    output_dir = Path(step_input.get("output_dir") or str(ctx.run_dir / "ap_candidates" / slugify(domain)))
    provider = step_input.get("provider", "offline-template")
    pc = step_input.get("provider_config", {})
    cp = step_input.get("curation_params", {})

    provider_config = ProviderConfig(
        provider=provider,
        model=pc.get("model", "local-model"),
        base_url=pc.get("base_url", "http://127.0.0.1:1234/v1"),
        temperature=float(pc.get("temperature", 0.2)),
        max_tokens=int(pc.get("max_tokens", 4000)),
        timeout=int(pc.get("timeout", 120)),
        seed=pc.get("seed", 7),
    )
    records_per_file = int(cp.get("records_per_file", 1000))
    subdomains_per_call = int(cp.get("subdomains_per_call", 12))
    atomic_per_subdomain = int(cp.get("atomic_per_subdomain", 6))
    sleep_seconds = float(cp.get("sleep_seconds", 0.0))
    limit_subdomains = int(cp.get("limit_subdomains", 0))

    subdomains = load_subdomains(subdomains_file)
    if limit_subdomains > 0:
        subdomains = subdomains[:limit_subdomains]
    if not subdomains:
        raise ValueError(f"00_atomic_problem_curation: no subdomains found in {subdomains_file}")

    existing = load_existing_candidates(output_dir, domain)
    counters = {"inserted": 0, "updated": 0, "unchanged": 0}

    for batch in chunked(subdomains, subdomains_per_call):
        if provider == "offline-template":
            raw_records = call_offline_template(domain, batch, atomic_per_subdomain, provider_config.seed)
        else:
            raw_records = call_lm_studio(provider_config, domain, batch, atomic_per_subdomain)
        for raw in raw_records:
            record = normalize_record(domain, raw)
            if record is None:
                continue
            cid = record["candidate_id"]
            merged, state = merge_candidate(existing.get(cid), record)
            existing[cid] = merged
            counters[state] += 1
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    records = list(existing.values())
    batch_paths = write_batches(output_dir, domain, records, records_per_file)
    manifest_path = write_manifest(output_dir, domain, batch_paths, len(subdomains), counters, provider)

    data = {
        "domain": domain,
        "subdomain_count": len(subdomains),
        "total_candidates": len(records),
        "inserted": counters["inserted"],
        "updated": counters["updated"],
        "unchanged": counters["unchanged"],
        "output_dir": str(output_dir),
        "output_files": [str(p) for p in batch_paths],
        "manifest": str(manifest_path),
    }
    return {
        "data": data,
        "counts": {
            "total_candidates": len(records),
            "inserted": counters["inserted"],
            "updated": counters["updated"],
            "unchanged": counters["unchanged"],
        },
    }


# ── CLI wrapper ───────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Curate atomic-problem candidates with family hints.")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--input", required=True, help="Subdomains file (.jsonl/.json/.txt/.zip)")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--provider", default="lm-studio", choices=["lm-studio", "offline-template"])
    parser.add_argument("--model", default="local-model")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--records-per-file", type=int, default=1000)
    parser.add_argument("--subdomains-per-call", type=int, default=12)
    parser.add_argument("--atomic-per-subdomain", type=int, default=6)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--limit-subdomains", type=int, default=0)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser


def main(argv=None) -> int:
    """CLI entry point — thin wrapper around run()."""
    args = _build_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    step_input = {
        "domain": args.domain,
        "subdomains_file": args.input,
        "provider": args.provider,
        "output_dir": args.output_dir,
        "provider_config": {
            "model": args.model, "base_url": args.base_url, "temperature": args.temperature,
            "max_tokens": args.max_tokens, "timeout": args.timeout, "seed": args.seed,
        },
        "curation_params": {
            "records_per_file": args.records_per_file,
            "subdomains_per_call": args.subdomains_per_call,
            "atomic_per_subdomain": args.atomic_per_subdomain,
            "sleep_seconds": args.sleep_seconds,
            "limit_subdomains": args.limit_subdomains,
        },
    }

    class _NullCtx:
        run_dir = Path(args.output_dir).parent

    result = run(_NullCtx(), step_input, None, None)
    print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
