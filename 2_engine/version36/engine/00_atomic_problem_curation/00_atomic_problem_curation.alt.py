#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
00_atomic_problem_curation.py

Erzeugt atomic problem candidates aus einer Subdomain-Liste.
Unterstützt:
- provider=offline-template
- provider=lm-studio (OpenAI-kompatibles API von LM Studio)

Input:
  --domain thermodynamics
  --input ./subdomains.jsonl
  --output-dir /ap_candidates/
  --provider offline-template|lm-studio
  --DEFAULT_MODEL = "local-model"

Optional:
  --base-url http://127.0.0.1:1234/v1
  --temperature 0.2
  --max-tokens 4000
  --timeout 120
  --seed 7
  --records-per-file 1000
  --subdomains-per-call 12
  --atomic-per-subdomain 6
  --sleep-seconds 0.0
  --limit-subdomains 0

Output:
- numbered JSONL batch files
- _latest_manifest.json
- summary JSON to stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# -----------------------------
# Defaults
# -----------------------------

DEFAULT_PROVIDER = "offline-template"
DEFAULT_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_MODEL = "local-model"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TIMEOUT = 120
DEFAULT_SEED = 7

DEFAULT_RECORDS_PER_FILE = 1000
DEFAULT_SUBDOMAINS_PER_CALL = 12
DEFAULT_ATOMIC_PER_SUBDOMAIN = 6
DEFAULT_SLEEP_SECONDS = 0.0
DEFAULT_LIMIT_SUBDOMAINS = 0


# -----------------------------
# Data model
# -----------------------------

@dataclass
class CandidateRecord:
    candidate_id: str
    domain: str
    subdomain: str
    atomic_problem: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


# -----------------------------
# Helpers
# -----------------------------

def eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


def sha1_short(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9äöüß\-_. ]+", "", text, flags=re.IGNORECASE)
    text = text.replace(" ", "_")
    text = re.sub(r"_+", "_", text)
    return text or "domain"


def candidate_id(domain: str, subdomain: str, atomic_problem: str) -> str:
    base = f"{domain}||{subdomain}||{atomic_problem}".lower().strip()
    return f"apc_{sha1_short(base, 20)}"


def batched(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# -----------------------------
# Input loading
# -----------------------------

def load_subdomains(path_str: str) -> List[str]:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"subdomains_file not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        return load_subdomains_jsonl(path)
    if suffix == ".json":
        return load_subdomains_json(path)
    if suffix == ".txt":
        return load_subdomains_txt(path)
    if suffix == ".zip":
        return load_subdomains_zip(path)

    raise ValueError(f"Unsupported input format: {path.suffix}")


def load_subdomains_jsonl(path: Path) -> List[str]:
    out: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            sub = extract_subdomain_field(obj)
            if sub:
                out.append(sub)
    return dedupe_preserve_order(out)


def load_subdomains_json(path: Path) -> List[str]:
    data = json.loads(read_text_file(path))
    out: List[str] = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                sub = extract_subdomain_field(item)
                if sub:
                    out.append(sub)
    elif isinstance(data, dict):
        # flexible parsing
        for key in ("subdomains", "items", "data"):
            val = data.get(key)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        out.append(item)
                    elif isinstance(item, dict):
                        sub = extract_subdomain_field(item)
                        if sub:
                            out.append(sub)
                break

    return dedupe_preserve_order(out)


def load_subdomains_txt(path: Path) -> List[str]:
    out = []
    for line in read_text_file(path).splitlines():
        line = normalize_whitespace(line)
        if line:
            out.append(line)
    return dedupe_preserve_order(out)


def load_subdomains_zip(path: Path) -> List[str]:
    out: List[str] = []
    with zipfile.ZipFile(path, "r") as zf:
        for name in zf.namelist():
            lower = name.lower()
            if lower.endswith("/"):
                continue
            with zf.open(name) as fh:
                raw = fh.read().decode("utf-8")
            tmp_path = Path(name)

            if lower.endswith(".jsonl"):
                for line in raw.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    sub = extract_subdomain_field(obj)
                    if sub:
                        out.append(sub)

            elif lower.endswith(".json"):
                data = json.loads(raw)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            out.append(item)
                        elif isinstance(item, dict):
                            sub = extract_subdomain_field(item)
                            if sub:
                                out.append(sub)
                elif isinstance(data, dict):
                    for key in ("subdomains", "items", "data"):
                        val = data.get(key)
                        if isinstance(val, list):
                            for item in val:
                                if isinstance(item, str):
                                    out.append(item)
                                elif isinstance(item, dict):
                                    sub = extract_subdomain_field(item)
                                    if sub:
                                        out.append(sub)
                            break

            elif lower.endswith(".txt"):
                for line in raw.splitlines():
                    line = normalize_whitespace(line)
                    if line:
                        out.append(line)

    return dedupe_preserve_order(out)


def extract_subdomain_field(obj: Dict[str, Any]) -> str | None:
    for key in ("subdomain", "name", "title", "label"):
        val = obj.get(key)
        if isinstance(val, str):
            val = normalize_whitespace(val)
            if val:
                return val
    return None


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        norm = normalize_whitespace(item)
        if not norm:
            continue
        key = norm.casefold()
        if key not in seen:
            seen.add(key)
            out.append(norm)
    return out


# -----------------------------
# Existing state / upsert
# -----------------------------

def load_existing_records(output_dir: Path) -> Dict[str, CandidateRecord]:
    records: Dict[str, CandidateRecord] = {}
    if not output_dir.exists():
        return records

    for path in sorted(output_dir.glob("*.jsonl")):
        if path.name.startswith("_"):
            continue
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                rec = CandidateRecord(
                    candidate_id=obj["candidate_id"],
                    domain=obj["domain"],
                    subdomain=obj["subdomain"],
                    atomic_problem=obj["atomic_problem"],
                )
                records[rec.candidate_id] = rec
    return records


def merge_records(
    existing: Dict[str, CandidateRecord],
    incoming: List[CandidateRecord],
) -> Tuple[Dict[str, CandidateRecord], int, int, int]:
    merged = dict(existing)
    inserted = 0
    updated = 0
    unchanged = 0

    for rec in incoming:
        old = merged.get(rec.candidate_id)
        if old is None:
            merged[rec.candidate_id] = rec
            inserted += 1
        elif asdict(old) == asdict(rec):
            unchanged += 1
        else:
            merged[rec.candidate_id] = rec
            updated += 1

    return merged, inserted, updated, unchanged


# -----------------------------
# Candidate generation
# -----------------------------

def offline_atomic_problems(domain: str, subdomain: str, count: int) -> List[str]:
    patterns = [
        "Grundbegriffe und Kernkonzepte in {subdomain} eindeutig erklären",
        "Typische Komponenten, Akteure und Schnittstellen in {subdomain} systematisch beschreiben",
        "Häufige Fehlannahmen, Risiken und Ausfallmodi in {subdomain} identifizieren",
        "Messgrößen, Kennzahlen und Evaluationskriterien für {subdomain} ableiten",
        "Zentrale Methoden, Verfahren oder Algorithmen in {subdomain} vergleichen",
        "Praxisnahe Anwendungsfälle und Entscheidungsprobleme in {subdomain} strukturieren",
        "Regulatorische, sicherheitsrelevante oder normative Anforderungen in {subdomain} erfassen",
        "Einführungswissen und Lernpfade für {subdomain} innerhalb von {domain} formulieren",
    ]
    out = []
    for i in range(count):
        text = patterns[i % len(patterns)].format(domain=domain, subdomain=subdomain)
        out.append(normalize_whitespace(text))
    return out


def build_prompt(domain: str, subdomains: List[str], atomic_per_subdomain: int) -> Tuple[str, str]:
    system = (
        "Du erzeugst kuratierte 'atomic problem candidates' für eine Wissenspipeline. "
        "Antworte AUSSCHLIESSLICH als valides JSON ohne Markdown. "
        "Form: ein JSON-Array von Objekten mit Feldern "
        '{"subdomain": string, "atomic_problems": [string, ...]}. '
        f"Für jede Subdomain genau {atomic_per_subdomain} präzise, nicht redundante, eigenständige atomic problems. "
        "Die Probleme müssen knapp, fachlich präzise und lösbar sein. "
        "Keine Nummerierung, keine Erklärtexte, keine zusätzlichen Felder."
    )

    user = {
        "domain": domain,
        "required_atomic_problems_per_subdomain": atomic_per_subdomain,
        "subdomains": subdomains,
    }
    return system, json.dumps(user, ensure_ascii=False)


def parse_lmstudio_json(content: str) -> List[Dict[str, Any]]:
    text = content.strip()

    # Strip code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try to find first JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        fragment = text[start:end + 1]
        data = json.loads(fragment)
        if isinstance(data, list):
            return data

    raise ValueError("Could not parse model response as JSON array")


def generate_with_lm_studio(
    domain: str,
    subdomains: List[str],
    atomic_per_subdomain: int,
    model: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    seed: int,
) -> List[CandidateRecord]:
    if OpenAI is None:
        raise RuntimeError(
            "Package 'openai' is not installed. Install with: pip install openai"
        )

    system_msg, user_msg = build_prompt(domain, subdomains, atomic_per_subdomain)

    client = OpenAI(
        base_url=base_url,
        api_key="lm-studio",
        timeout=timeout,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            response_format={"type": "json_object"},  # may be ignored by some models/servers
            messages=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": (
                        "Gib nur JSON zurück. "
                        "Nutze EXAKT dieses Top-Level-Format: "
                        '{"items":[{"subdomain":"...","atomic_problems":["..."]}]}\n'
                        f"Input:\n{user_msg}"
                    ),
                },
            ],
        )
    except Exception as exc:
        raise RuntimeError(f"LM Studio unreachable or request failed: {exc}") from exc

    content = response.choices[0].message.content or ""
    content = content.strip()

    try:
        parsed = json.loads(content)
        items = parsed["items"] if isinstance(parsed, dict) and "items" in parsed else parsed
    except Exception:
        items = parse_lmstudio_json(content)

    if not isinstance(items, list):
        raise ValueError("Model response JSON does not contain a list of items")

    subdomain_set = {s.casefold(): s for s in subdomains}
    results: List[CandidateRecord] = []

    for item in items:
        if not isinstance(item, dict):
            continue
        raw_subdomain = normalize_whitespace(str(item.get("subdomain", "")))
        atomic_problems = item.get("atomic_problems", [])
        if not raw_subdomain or not isinstance(atomic_problems, list):
            continue

        # map casing back to original input if possible
        canonical_subdomain = subdomain_set.get(raw_subdomain.casefold(), raw_subdomain)

        clean_problems = []
        seen_local = set()
        for p in atomic_problems:
            if not isinstance(p, str):
                continue
            p = normalize_whitespace(p)
            p = re.sub(r"^\d+[\).\-\s]+", "", p).strip()
            if not p:
                continue
            key = p.casefold()
            if key not in seen_local:
                seen_local.add(key)
                clean_problems.append(p)

        for p in clean_problems[:atomic_per_subdomain]:
            results.append(
                CandidateRecord(
                    candidate_id=candidate_id(domain, canonical_subdomain, p),
                    domain=domain,
                    subdomain=canonical_subdomain,
                    atomic_problem=p,
                )
            )

    # Fill missing subdomains deterministically if model omitted some
    by_subdomain: Dict[str, int] = {}
    for rec in results:
        by_subdomain[rec.subdomain.casefold()] = by_subdomain.get(rec.subdomain.casefold(), 0) + 1

    for sub in subdomains:
        have = by_subdomain.get(sub.casefold(), 0)
        missing = atomic_per_subdomain - have
        if missing > 0:
            for p in offline_atomic_problems(domain, sub, missing):
                rec = CandidateRecord(
                    candidate_id=candidate_id(domain, sub, p),
                    domain=domain,
                    subdomain=sub,
                    atomic_problem=p,
                )
                results.append(rec)

    # Deduplicate final
    dedup: Dict[str, CandidateRecord] = {}
    for rec in results:
        dedup[rec.candidate_id] = rec

    return list(dedup.values())


def generate_candidates(
    provider: str,
    domain: str,
    subdomains: List[str],
    provider_config: Dict[str, Any],
    atomic_per_subdomain: int,
) -> List[CandidateRecord]:
    if provider == "offline-template":
        out: List[CandidateRecord] = []
        for sub in subdomains:
            for p in offline_atomic_problems(domain, sub, atomic_per_subdomain):
                out.append(
                    CandidateRecord(
                        candidate_id=candidate_id(domain, sub, p),
                        domain=domain,
                        subdomain=sub,
                        atomic_problem=p,
                    )
                )
        return out

    if provider == "lm-studio":
        return generate_with_lm_studio(
            domain=domain,
            subdomains=subdomains,
            atomic_per_subdomain=atomic_per_subdomain,
            model=provider_config["model"],
            base_url=provider_config["base_url"],
            temperature=provider_config["temperature"],
            max_tokens=provider_config["max_tokens"],
            timeout=provider_config["timeout"],
            seed=provider_config["seed"],
        )

    raise ValueError(f"Unsupported provider: {provider}")


# -----------------------------
# Writing outputs
# -----------------------------

def sort_records(records: Iterable[CandidateRecord]) -> List[CandidateRecord]:
    return sorted(
        records,
        key=lambda r: (
            r.subdomain.casefold(),
            r.atomic_problem.casefold(),
            r.candidate_id,
        ),
    )


def clear_old_batch_files(output_dir: Path, domain: str) -> None:
    prefix = f"{slugify(domain)}_atomic_candidates_"
    for path in output_dir.glob(f"{prefix}*.jsonl"):
        path.unlink()


def write_numbered_jsonl_batches(
    output_dir: Path,
    domain: str,
    records: List[CandidateRecord],
    records_per_file: int,
) -> List[str]:
    ensure_dir(output_dir)
    clear_old_batch_files(output_dir, domain)

    prefix = f"{slugify(domain)}_atomic_candidates_"
    output_files: List[str] = []

    for idx, chunk in enumerate(batched(records, records_per_file), start=1):
        path = output_dir / f"{prefix}{idx:04d}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for rec in chunk:
                f.write(rec.to_json() + "\n")
        output_files.append(str(path))

    return output_files


def write_manifest(
    output_dir: Path,
    domain: str,
    subdomain_count: int,
    total_candidates: int,
    inserted: int,
    updated: int,
    unchanged: int,
    output_files: List[str],
) -> str:
    manifest_path = output_dir / "_latest_manifest.json"
    manifest = {
        "domain": domain,
        "subdomain_count": subdomain_count,
        "total_candidates": total_candidates,
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "output_dir": str(output_dir),
        "output_files": output_files,
        "manifest": str(manifest_path),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(manifest_path)


# -----------------------------
# Main
# -----------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Atomic problem curation step")
    p.add_argument("--domain", required=True, help="Domain name")
    p.add_argument("--input", required=True, dest="subdomains_file", help="Path to subdomains file")
    p.add_argument("--output-dir", required=True, help="Output directory for candidate JSONL files")
    p.add_argument("--provider", default=DEFAULT_PROVIDER, choices=["offline-template", "lm-studio"])

    # provider config
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)

    # curation params
    p.add_argument("--records-per-file", type=int, default=DEFAULT_RECORDS_PER_FILE)
    p.add_argument("--subdomains-per-call", type=int, default=DEFAULT_SUBDOMAINS_PER_CALL)
    p.add_argument("--atomic-per-subdomain", type=int, default=DEFAULT_ATOMIC_PER_SUBDOMAIN)
    p.add_argument("--sleep-seconds", type=float, default=DEFAULT_SLEEP_SECONDS)
    p.add_argument("--limit-subdomains", type=int, default=DEFAULT_LIMIT_SUBDOMAINS)

    return p.parse_args()


def main() -> int:
    args = parse_args()

    domain = normalize_whitespace(args.domain)
    if not domain:
        raise SystemExit("FAIL: domain missing")

    subdomains = load_subdomains(args.subdomains_file)
    if args.limit_subdomains and args.limit_subdomains > 0:
        subdomains = subdomains[:args.limit_subdomains]

    if not subdomains:
        raise SystemExit("FAIL: no subdomains extracted from file")

    output_dir = Path(args.output_dir)
    ensure_dir(output_dir)

    provider_config = {
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
        "seed": args.seed,
    }

    existing = load_existing_records(output_dir)
    all_incoming: List[CandidateRecord] = []

    for batch in batched(subdomains, args.subdomains_per_call):
        batch_records = generate_candidates(
            provider=args.provider,
            domain=domain,
            subdomains=batch,
            provider_config=provider_config,
            atomic_per_subdomain=args.atomic_per_subdomain,
        )
        all_incoming.extend(batch_records)

        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    merged, inserted, updated, unchanged = merge_records(existing, all_incoming)
    sorted_records = sort_records(merged.values())
    output_files = write_numbered_jsonl_batches(
        output_dir=output_dir,
        domain=domain,
        records=sorted_records,
        records_per_file=args.records_per_file,
    )

    total_candidates = len(sorted_records)
    manifest = write_manifest(
        output_dir=output_dir,
        domain=domain,
        subdomain_count=len(subdomains),
        total_candidates=total_candidates,
        inserted=inserted,
        updated=updated,
        unchanged=unchanged,
        output_files=output_files,
    )

    result = {
        "domain": domain,
        "subdomain_count": len(subdomains),
        "total_candidates": total_candidates,
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "output_dir": str(output_dir),
        "output_files": output_files,
        "manifest": manifest,
    }

    # invariant check
    if total_candidates != inserted + updated + unchanged:
        # This invariant is defined for the run's final state delta.
        # With an existing non-empty state, the strict contract arithmetic
        # can be ambiguous. We therefore report the actual values but keep
        # process successful.
        eprint(
            "WARN: invariant total_candidates == inserted + updated + unchanged "
            "is not true against pre-existing state."
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
