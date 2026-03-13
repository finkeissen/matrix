#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
00_atomic_problem_curation.py

Generate atomic problem candidates from a subdomain list.

Supported providers:
- offline-template
- lm-studio (direct HTTP request to LM Studio, no openai dependency)

Input:
  --domain thermodynamics
  --input /path/to/subdomains.jsonl
  --output-dir /path/to/ap_candidates
  --provider offline-template|lm-studio

Optional:
  --model local-model
  --base-url http://127.0.0.1:1234/v1
  --temperature 0.0
  --max-tokens 2000
  --timeout 120
  --seed 7
  --records-per-file 1000
  --subdomains-per-call 4
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
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


# -----------------------------
# Defaults
# -----------------------------

DEFAULT_PROVIDER = "offline-template"
DEFAULT_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_MODEL = "local-model"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TIMEOUT = 120
DEFAULT_SEED = 7

DEFAULT_RECORDS_PER_FILE = 1000
DEFAULT_SUBDOMAINS_PER_CALL = 4
DEFAULT_ATOMIC_PER_SUBDOMAIN = 6
DEFAULT_SLEEP_SECONDS = 0.0
DEFAULT_LIMIT_SUBDOMAINS = 0

LM_STUDIO_MAX_RETRIES = 4
LM_STUDIO_MIN_BATCH_SIZE = 1


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
    return re.sub(r"\s+", " ", text or "").strip()


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


def chunk_list(items: List[str], size: int) -> List[List[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


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
    out: List[str] = []
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
    out: List[str] = []
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
        "Explain the core concepts and foundational ideas in {subdomain}.",
        "Describe the typical components, actors, and interfaces in {subdomain}.",
        "Identify common misconceptions, risks, and failure modes in {subdomain}.",
        "Define the main metrics, measurements, and evaluation criteria for {subdomain}.",
        "Compare central methods, procedures, or algorithms used in {subdomain}.",
        "Structure practical use cases and decision problems in {subdomain}.",
        "Capture regulatory, safety-related, or normative requirements in {subdomain}.",
        "Formulate an introductory learning path for {subdomain} within {domain}.",
    ]
    out: List[str] = []
    for i in range(count):
        text = patterns[i % len(patterns)].format(domain=domain, subdomain=subdomain)
        out.append(normalize_whitespace(text))
    return out


def build_prompt(domain: str, subdomains: List[str], atomic_per_subdomain: int) -> Tuple[str, str]:
    system = (
        "You generate curated atomic problem candidates for a knowledge pipeline. "
        "Return only valid JSON. "
        "Do not reveal reasoning. Do not include chain-of-thought. Do not explain. "
        "No markdown. No prose. No comments. No extra fields. "
        'Return exactly one JSON object with the field "items". '
        'Each element in "items" must be an object with the fields '
        '{"subdomain": string, "atomic_problems": [string, ...]}. '
        f"For each subdomain, produce exactly {atomic_per_subdomain} precise, non-redundant, self-contained atomic problems. "
        "If you cannot comply, still return only a valid JSON object."
    )

    user = {
        "domain": domain,
        "required_atomic_problems_per_subdomain": atomic_per_subdomain,
        "subdomains": subdomains,
    }
    return system, json.dumps(user, ensure_ascii=False)


def build_user_message(user_msg: str) -> str:
    return (
        "Return only one valid JSON object.\n"
        "Do not think aloud.\n"
        "Do not output a thinking process.\n"
        "Do not output notes.\n"
        "Do not output analysis.\n"
        "Do not output any text before or after the JSON.\n"
        'Use exactly this top-level format:\n'
        '{"items":[{"subdomain":"...","atomic_problems":["..."]}]}\n'
        "Each subdomain must have exactly the requested number of atomic problems.\n"
        "Input:\n"
        f"{user_msg}"
    )


def extract_balanced_json_fragment(text: str) -> str | None:
    """
    Extract the first balanced JSON object or array from arbitrary text.
    Handles strings and escapes correctly.
    """
    start_positions: List[int] = []
    for i, ch in enumerate(text):
        if ch == "{" or ch == "[":
            start_positions.append(i)

    for start in start_positions:
        stack: List[str] = []
        in_string = False
        escape = False

        for i in range(start, len(text)):
            ch = text[i]

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if not stack:
                    break
                opening = stack.pop()
                if (opening == "{" and ch != "}") or (opening == "[" and ch != "]"):
                    break
                if not stack:
                    return text[start:i + 1]

    return None


def extract_items_json_fragment(text: str) -> str | None:
    """
    Prefer a JSON object that starts with {"items": ...} or contains an "items" field.
    This avoids accidentally parsing unrelated brace fragments from reasoning text.
    """
    if not text:
        return None

    candidates: List[int] = []

    for match in re.finditer(r'\{\s*"items"\s*:', text):
        candidates.append(match.start())

    for start in candidates:
        stack: List[str] = []
        in_string = False
        escape = False

        for i in range(start, len(text)):
            ch = text[i]

            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if not stack:
                    break
                opening = stack.pop()
                if (opening == "{" and ch != "}") or (opening == "[" and ch != "]"):
                    break
                if not stack:
                    return text[start:i + 1]

    return None


def parse_lmstudio_json(content: str) -> List[Dict[str, Any]]:
    text = (content or "").strip()

    if not text:
        raise ValueError("Model response is empty")

    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # 1) Direct parse
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]
    except json.JSONDecodeError:
        pass

    # 2) Prefer an object that explicitly starts with {"items": ...}
    fragment = extract_items_json_fragment(text)
    if fragment is not None:
        data = json.loads(fragment)
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data["items"]

    # 3) Fallback to any balanced JSON fragment
    fragment = extract_balanced_json_fragment(text)
    if fragment is None:
        raise ValueError(f"Could not find balanced JSON in model response: {text[:800]}")

    data = json.loads(fragment)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]

    raise ValueError(f"Balanced JSON found, but format is invalid: {fragment[:800]}")


def lmstudio_chat_completion(
    base_url: str,
    model: str,
    system_msg: str,
    user_msg: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    seed: int,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model or "local-model",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "seed": seed,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": build_user_message(user_msg)},
        ],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer lm-studio",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LM Studio HTTP error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LM Studio not reachable at {url}: {exc}") from exc

    try:
        return json.loads(raw)
    except Exception as exc:
        raise RuntimeError(f"Unexpected LM Studio response format: {raw[:1000]}") from exc


def parse_lmstudio_response(response: Dict[str, Any]) -> Tuple[str, str]:
    try:
        choice = response["choices"][0]
        message = choice["message"]
        content = message.get("content", "") or ""
        finish_reason = choice.get("finish_reason", "") or ""
        return content.strip(), finish_reason
    except Exception as exc:
        raw = json.dumps(response, ensure_ascii=False)[:1000]
        raise RuntimeError(f"Unexpected LM Studio response schema: {raw}") from exc


def clean_atomic_problem(problem: str) -> str:
    problem = normalize_whitespace(problem)
    problem = re.sub(r"^\d+[\).\-\s]+", "", problem).strip()
    problem = re.sub(r"^[-*]\s+", "", problem).strip()
    return problem


def normalize_lmstudio_items(
    domain: str,
    subdomains: List[str],
    items: List[Dict[str, Any]],
    atomic_per_subdomain: int,
) -> List[CandidateRecord]:
    subdomain_set = {s.casefold(): s for s in subdomains}
    results: List[CandidateRecord] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        raw_subdomain = normalize_whitespace(str(item.get("subdomain", "")))
        atomic_problems = item.get("atomic_problems", [])

        if not raw_subdomain or not isinstance(atomic_problems, list):
            continue

        canonical_subdomain = subdomain_set.get(raw_subdomain.casefold(), raw_subdomain)

        clean_problems: List[str] = []
        seen_local = set()

        for problem in atomic_problems:
            if not isinstance(problem, str):
                continue
            problem = clean_atomic_problem(problem)
            if not problem:
                continue
            key = problem.casefold()
            if key not in seen_local:
                seen_local.add(key)
                clean_problems.append(problem)

        for problem in clean_problems[:atomic_per_subdomain]:
            results.append(
                CandidateRecord(
                    candidate_id=candidate_id(domain, canonical_subdomain, problem),
                    domain=domain,
                    subdomain=canonical_subdomain,
                    atomic_problem=problem,
                )
            )

    by_subdomain: Dict[str, int] = {}
    for rec in results:
        by_subdomain[rec.subdomain.casefold()] = by_subdomain.get(rec.subdomain.casefold(), 0) + 1

    for sub in subdomains:
        have = by_subdomain.get(sub.casefold(), 0)
        missing = atomic_per_subdomain - have
        if missing > 0:
            for problem in offline_atomic_problems(domain, sub, missing):
                results.append(
                    CandidateRecord(
                        candidate_id=candidate_id(domain, sub, problem),
                        domain=domain,
                        subdomain=sub,
                        atomic_problem=problem,
                    )
                )

    dedup: Dict[str, CandidateRecord] = {}
    for rec in results:
        dedup[rec.candidate_id] = rec

    return list(dedup.values())


def generate_with_lm_studio_single_batch(
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
    system_msg, user_msg = build_prompt(domain, subdomains, atomic_per_subdomain)

    response = lmstudio_chat_completion(
        base_url=base_url,
        model=model,
        system_msg=system_msg,
        user_msg=user_msg,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        seed=seed,
    )

    content, finish_reason = parse_lmstudio_response(response)

    if finish_reason == "length":
        raise RuntimeError(
            "LM Studio truncated the response before valid JSON was completed. "
            "The model likely produced reasoning text instead of the requested JSON."
        )

    if not content:
        raise RuntimeError(
            f"LM Studio returned empty message content. Full response: "
            f"{json.dumps(response, ensure_ascii=False)[:1000]}"
        )

    items = parse_lmstudio_json(content)
    return normalize_lmstudio_items(domain, subdomains, items, atomic_per_subdomain)


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
    """
    Robust LM Studio generation:
    - tries the whole batch first
    - if the model truncates or refuses JSON, recursively splits the batch
    - falls back to deterministic offline generation only for the smallest failing unit
    """
    def _generate_recursive(batch_subdomains: List[str], attempt: int = 1) -> List[CandidateRecord]:
        try:
            return generate_with_lm_studio_single_batch(
                domain=domain,
                subdomains=batch_subdomains,
                atomic_per_subdomain=atomic_per_subdomain,
                model=model,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                seed=seed,
            )
        except Exception as exc:
            batch_size = len(batch_subdomains)
            if batch_size <= LM_STUDIO_MIN_BATCH_SIZE or attempt >= LM_STUDIO_MAX_RETRIES:
                eprint(
                    f"WARN: LM Studio failed for subdomains {batch_subdomains}. "
                    f"Falling back to offline-template for this unit. Error: {exc}"
                )
                fallback: List[CandidateRecord] = []
                for sub in batch_subdomains:
                    for problem in offline_atomic_problems(domain, sub, atomic_per_subdomain):
                        fallback.append(
                            CandidateRecord(
                                candidate_id=candidate_id(domain, sub, problem),
                                domain=domain,
                                subdomain=sub,
                                atomic_problem=problem,
                            )
                        )
                return fallback

            split_size = max(LM_STUDIO_MIN_BATCH_SIZE, batch_size // 2)
            halves = chunk_list(batch_subdomains, split_size)

            eprint(
                f"WARN: LM Studio failed for batch of size {batch_size}. "
                f"Retrying with smaller batches. Error: {exc}"
            )

            out: List[CandidateRecord] = []
            for part in halves:
                out.extend(_generate_recursive(part, attempt + 1))
            return out

    return _generate_recursive(subdomains, attempt=1)


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
            for problem in offline_atomic_problems(domain, sub, atomic_per_subdomain):
                out.append(
                    CandidateRecord(
                        candidate_id=candidate_id(domain, sub, problem),
                        domain=domain,
                        subdomain=sub,
                        atomic_problem=problem,
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
    parser = argparse.ArgumentParser(description="Atomic problem curation step")
    parser.add_argument("--domain", required=True, help="Domain name")
    parser.add_argument("--input", required=True, dest="subdomains_file", help="Path to subdomains file")
    parser.add_argument("--output-dir", required=True, help="Output directory for candidate JSONL files")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER, choices=["offline-template", "lm-studio"])

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Optional model identifier. For LM Studio, the currently loaded local model is typically used.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)

    parser.add_argument("--records-per-file", type=int, default=DEFAULT_RECORDS_PER_FILE)
    parser.add_argument("--subdomains-per-call", type=int, default=DEFAULT_SUBDOMAINS_PER_CALL)
    parser.add_argument("--atomic-per-subdomain", type=int, default=DEFAULT_ATOMIC_PER_SUBDOMAIN)
    parser.add_argument("--sleep-seconds", type=float, default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument("--limit-subdomains", type=int, default=DEFAULT_LIMIT_SUBDOMAINS)

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    domain = normalize_whitespace(args.domain)
    if not domain:
        raise SystemExit("FAIL: domain is missing")

    subdomains = load_subdomains(args.subdomains_file)
    if args.limit_subdomains and args.limit_subdomains > 0:
        subdomains = subdomains[:args.limit_subdomains]

    if not subdomains:
        raise SystemExit("FAIL: no subdomains extracted from input file")

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

    if total_candidates != inserted + updated + unchanged:
        eprint(
            "WARN: invariant total_candidates == inserted + updated + unchanged "
            "is not true against a pre-existing output state."
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
