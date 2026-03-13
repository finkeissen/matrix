from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INGESTION_DIR = PROJECT_ROOT / "ingestion"


def slug_to_words(value: str) -> str:
    value = value.replace(".fillet", "")
    value = value.replace(".md", "")
    value = value.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", value).strip().lower()


def build_failure_patterns() -> dict:
    src = INGESTION_DIR / "imports" / "contradictions" / "contradictions"
    patterns = []

    if src.exists():
        for path in sorted(src.glob("*.md")):
            if path.name in {"README.md", "TEMPLATE.md"}:
                continue
            base = path.stem
            phrase = slug_to_words(base)
            patterns.append(
                {
                    "name": base,
                    "triggers": [
                        phrase,
                        phrase.replace(" vs ", " versus "),
                    ],
                    "source_file": str(path.relative_to(PROJECT_ROOT)),
                }
            )

    return {
        "version": "v1",
        "patterns": patterns,
    }


def extract_status(text: str) -> str:
    m = re.search(r"status\s*:\s*([A-Z_]+)", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()
    if "STOP" in text.upper():
        return "STOP"
    if "ALLOW" in text.upper():
        return "ALLOW"
    return "REVIEW"


def build_case_gates() -> dict:
    src = INGESTION_DIR / "imports" / "cases" / "cases"
    gates = []

    if src.exists():
        for case_dir in sorted(src.iterdir()):
            if not case_dir.is_dir() or case_dir.name == "CASE_TEMPLATE":
                continue

            parts = case_dir.name.split("__", 1)
            case_id = parts[0]
            slug = parts[1] if len(parts) > 1 else case_dir.name

            gate_path = case_dir / "gate.md"
            gate_text = gate_path.read_text(encoding="utf-8") if gate_path.exists() else ""
            status = extract_status(gate_text)

            trigger_terms = [slug.replace("-", " ")]
            trigger_terms.extend(slug.split("-"))

            gates.append(
                {
                    "id": case_id,
                    "status": status,
                    "trigger_terms": sorted({t.strip().lower() for t in trigger_terms if t.strip()}),
                    "source_dir": str(case_dir.relative_to(PROJECT_ROOT)),
                }
            )

    return {
        "version": "v1",
        "gates": gates,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    rules_dir = INGESTION_DIR / "rules"
    write_json(rules_dir / "failure_patterns.json", build_failure_patterns())
    write_json(rules_dir / "case_gates.json", build_case_gates())
    print("Built ingestion rule assets.")


if __name__ == "__main__":
    main()
