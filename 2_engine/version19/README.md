# Atomic Problem Identification Pipeline — Version 19

**Version:** 19.0.0
**Replaces:** v14.0.0 (v17)
**Architecture revision date:** 2026-03-07

---

## Leitprinzip

Version 19 löst das Versprechen von Version 14 ein: Jeder Run ist nachvollziehbar, reproduzierbar, validiert und wiederaufnehmbar. Der Schritt von v14→v18 ist kein Architektur-Entwurf mehr, sondern ein belastbares Ausführungssystem.

**v14 war:** Gute Architekturidee — zwei Lebenszyklen, Prompt-Hashing, Telemetrie.
**v18 ist:** Echte Datenverträge, echte Zustandsverwaltung, echte Fehlertoleranz, echte Vergleichbarkeit zwischen Runs.

---

## Die drei Kernversprechen von v18

### 1. Reproduzierbarkeit
Jeder Run enthält in `manifest.json` vollständig:
- Prompt-Version + SHA256-Hash jedes genutzten Prompts
- Modell-Konfiguration (Modell, URL, Timeout)
- Schritt-für-Schritt-Timing und Output-Pfade
- Finale Metriken (generated / accepted / duplicates / acceptance_rate)

Zwei Runs mit identischen Inputs aber unterschiedlichem `prompt_hash` sind direkt vergleichbar — die Grundlage für systematische Prompt-Optimierung via `pipeline compare`.

### 2. Robustheit
- **Atomare Schreibvorgänge**: `manifest.json` wird nie halb geschrieben (tmp → fsync → rename)
- **Resume**: Abgebrochene Runs nehmen genau dort wieder auf, wo sie gestoppt haben
- **Retry**: Jeder Step wird bis zu 2-mal wiederholt bevor der Run abbricht
- **Harte Validierung**: Nach **jedem** Step wird das Output gegen das JSON Schema validiert — Fehler werden sofort gemeldet, nicht erst am Ende

### 3. Qualitätssicherung
- **3-stufige Deduplication**: Exact Match → Normalized Match → Semantic Match (opt-in)
- **FormatChecker aktiv**: `date-time`, `uri` etc. werden wirklich geprüft, nicht ignoriert
- **Automatischer Report**: Jeder Run erzeugt `exports/summary_report.json` ohne zusätzlichen Aufruf
- **Cross-Run Vergleich**: `pipeline compare` zeigt Metrik- und Prompt-Diffs zweier Runs nebeneinander

---

## Änderungen gegenüber v14 (v17)

| Bereich | v14 / v17 | v18 |
|---------|-----------|-----|
| Run-Manifest | Im Orchestrator zusammengebaut | `RunManifest` + `RunContext` als eigenständige Klassen |
| Schreibsicherheit | Direktes `write_json()` | Atomares tmp → fsync → rename Pattern |
| Schema-Validierung | Nur beim Schreiben von manifest/run_record | **Nach jedem Step** auf dem Output |
| Resume | `try_restore()` lädt Artefakte, kein Skip-Check | Steps werden übersprungen wenn `status=completed` |
| Deduplication | Einzelner Validator-Check | Eigener Step (06) mit 3 Ebenen + Registry-Abgleich |
| CLI | Nur `orchestrator.py --subdomain` | `pipeline run / resume / validate / report / compare` |
| Logging | `print()` + Telemetry-JSONL | Strukturiertes JSON-Logging + per-Run Logdatei |
| Tests | Keine | 4 Test-Module mit 25+ Tests |
| Prompt-Struktur | `prompts/<step>.md` (flat) | `prompts/templates/<step>/v1.md`, `v2.md` (per-Step-Verzeichnis) |
| Metrics | In `telemetry_summary.json` | In `manifest.metrics` + `exports/summary_report.json` |

---

## Architektur

```
src/pipeline/
├── cli.py                    ← Entry point: pipeline run / resume / report / compare
├── config.py                 ← Alle Parameter via .env, keine Hardcodes
├── orchestrator.py           ← Dispatch, Retry, Validation-Hook nach jedem Step
├── run_context.py            ← RunManifest + RunContext (atomares IO)
├── logging_setup.py          ← Strukturiertes JSON-Logging (Datei + Console)
│
├── prompts/
│   ├── loader.py             ← Load + SHA256-Hash + Variant-Resolution
│   └── templates/
│       ├── 01_scope/
│       │   ├── v1.md         ← Aktive Version
│       │   └── v2.md         ← A/B-Test Variante
│       ├── 03_categories/
│       │   └── v1.md
│       └── 04_problem_generation/
│           └── v1.md
│
├── steps/
│   ├── 01_scope.py           ← Einheitliches Muster: load_prompt → LLM → return {data, output_path, counts}
│   ├── 02_seed_expansion.py
│   ├── 03_categories.py
│   ├── 04_problem_generation.py
│   ├── 05_validation.py
│   ├── 06_deduplication.py   ← Deterministisch, kein LLM, 3-stufige Dedup
│   ├── 07_ranking.py
│   └── 08_export.py
│
├── schema/                   ← JSON Schema Draft-07 für alle Artefakte
│   ├── atomic_problem.schema.json
│   ├── category.schema.json
│   ├── scope.schema.json
│   └── run_manifest.schema.json
│
├── validation/
│   ├── schema_validator.py   ← Draft7Validator + FormatChecker (date-time, uri)
│   ├── business_rules.py     ← Domänen-Constraints (Pflichtfelder, Enum-Werte)
│   └── content_checks.py     ← Inhaltliche Prüfung (Atomizität, Scope-Verletzungen)
│
├── dedup/
│   └── __init__.py           ← Level A (exact), B (normalized), C (semantic stub)
│
├── storage/
│   └── manifest_store.py     ← Atomares Lesen/Schreiben von manifest.json
│
└── eval/
    ├── metrics.py            ← Metriken aus Run-Verzeichnis aggregieren
    └── reports.py            ← summary_report.json + compare_runs()
```

---

## Run-Verzeichnisstruktur

```
data/runs/<run_id>/
├── manifest.json             ← Einzige Quelle der Wahrheit (atomar geschrieben)
├── logs/
│   └── run.log               ← Strukturiertes JSON-Log dieses Runs
├── intermediate/
│   ├── 01_scope.json
│   ├── 02_seed_expansion.json
│   ├── 03_categories.json
│   ├── 04_problem_generation.json
│   ├── 05_validation.json
│   └── 06_deduplication.json
├── rejected/
│   ├── schema_errors.json    ← Schema-Validierungsfehler
│   ├── business_rule_failures.json
│   └── duplicates.json       ← Von Dedup abgelehnte Probleme
└── exports/
    ├── atomic_problems.jsonl ← Finales Output
    └── summary_report.json   ← Automatisch generierter Run-Report
```

---

## manifest.json — Einzige Wahrheit pro Run

```json
{
  "run_id": "2026-03-07_001_thermodynamics",
  "created_at": "2026-03-07T10:15:00Z",
  "finished_at": "2026-03-07T10:47:22Z",
  "status": "completed",
  "domain": "thermodynamics",
  "pipeline_version": "18.0.0",
  "model_config": {
    "model": "qwen2.5-72b",
    "url": "http://localhost:1234/v1/chat/completions",
    "timeout": 120
  },
  "prompt_versions": {
    "01_scope": "v1",
    "03_categories": "v2",
    "04_problem_generation": "v1"
  },
  "prompt_hashes": {
    "01_scope": "sha256:b0ba1a8c...",
    "03_categories": "sha256:3bfd160e...",
    "04_problem_generation": "sha256:ce4994e2..."
  },
  "steps": [
    {
      "name": "01_scope",
      "status": "completed",
      "started_at": "2026-03-07T10:15:02Z",
      "finished_at": "2026-03-07T10:15:18Z",
      "duration_ms": 16000,
      "output_path": "intermediate/01_scope.json",
      "counts": { "boundaries": 8, "exclusions": 3 }
    },
    {
      "name": "06_deduplication",
      "status": "completed",
      "duration_ms": 240,
      "counts": {
        "input": 128,
        "accepted": 112,
        "rejected_exact": 9,
        "rejected_normalized": 7,
        "rejected_semantic": 0
      }
    }
  ],
  "metrics": {
    "generated": 128,
    "accepted": 112,
    "duplicates": 16,
    "acceptance_rate": 0.875,
    "by_difficulty": { "easy": 28, "medium": 54, "hard": 30 },
    "by_category": { "heat_transfer": 32, "thermodynamic_cycles": 44, "entropy": 36 }
  }
}
```

---

## CLI

```bash
# Neuen Run starten
pipeline run --domain thermodynamics

# A/B-Test mit alternativer Prompt-Variante
pipeline run --domain algebra --prompt-variant v2

# Unterbrochenen Run fortsetzen
pipeline resume --run-id 2026-03-07_001_thermodynamics

# Run-Status anzeigen
pipeline validate --run-id 2026-03-07_001_thermodynamics

# Report ausgeben
pipeline report --run-id 2026-03-07_001_thermodynamics

# Zwei Runs vergleichen
pipeline compare \
  --run-a 2026-03-07_001_thermodynamics \
  --run-b 2026-03-07_002_thermodynamics
```

---

## Deduplication — 3 Ebenen

```
Input
  │
  ▼
Level A: Exact Match
  SHA256(problem_statement) ∈ known_hashes?
  └─ JA → rejected/duplicates.json (_dedup_reason: exact_match)
  │
  ▼
Level B: Normalized Match
  lowercase + punctuation strip + whitespace collapse
  └─ JA → rejected/duplicates.json (_dedup_reason: normalized_match)
  │
  ▼
Level C: Semantic Match (opt-in via SEMANTIC_DEDUP_ENABLED=true)
  Embedding cosine similarity > threshold (default: 0.92)
  └─ JA → rejected/duplicates.json (_dedup_reason: semantic_match)
  │
  ▼
accepted → intermediate/06_deduplication.json
```

Level A und B sind in v18 vollständig implementiert. Level C ist ein dokumentierter Stub, aktivierbar ab v19 durch Hinzufügen von `sentence-transformers`.

---

## Validierung nach jedem Step

Der Orchestrator ruft nach **jedem** Step `SchemaValidator.validate_step_output()` auf:

```
execute step
    │
    ▼
validate output against JSON Schema (FormatChecker aktiv)
    │ fehler?
    ├─ JA → retry (bis zu 2x) → fail_step() → HALT
    └─ NEIN → complete_step() → next step
```

Ohne diesen Hook war es in v14 möglich, dass ein Step ein malformiertes JSON-Artefakt schreibt und der Fehler erst 3 Steps später beim Lesen auffällt.

---

## Prompt-Versionierung

Jeder Prompt liegt als `prompts/templates/<step>/v1.md` (aktiv) und optional `v2.md`, `v3.md` (Varianten für A/B-Tests).

Beim Run-Start werden alle Prompt-Hashes berechnet und ins Manifest geschrieben. `pipeline compare` zeigt dann, welche Prompt-Version bei welchem Step geändert wurde.

```bash
# Beispiel: compare Output
pipeline compare --run-a run_A --run-b run_B

  Step                    Prompt A        Prompt B
  ---------------------------------------------------
  01_scope                      v1              v1
  03_categories                 v1              v2  ←   (geändert)
  04_problem_generation         v1              v1
```

---

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=pipeline --cov-report=term-missing
```

Test-Module:
- `test_run_context.py` — RunManifest, atomare Schreibvorgänge, Resume-Logic
- `test_schema_validation.py` — FormatChecker, Pflichtfelder, Enum-Prüfung
- `test_deduplication.py` — Alle 3 Ebenen, Within-Batch-Duplikate, Normalisierung
- `test_prompt_loader.py` — Varianten-Auflösung, Caching, Invalidierung

---

## Konfigurationsparameter

Alle Parameter über `.env` steuerbar. Keine Hardcodes.

| Parameter | Default | Bedeutung |
|-----------|---------|-----------|
| `LM_STUDIO_URL` | `http://localhost:1234/v1/chat/completions` | LLM-Endpoint |
| `LM_STUDIO_MODEL` | `loaded` | Modell-ID |
| `REQUEST_TIMEOUT` | `120` | LLM-Timeout (Sekunden) |
| `DEFAULT_RETRIES` | `2` | Max. Retries pro Step |
| `SCOPE_CONFIDENCE_THRESHOLD` | `0.70` | Unter diesem Wert → Clarification |
| `ATOMICITY_FAILURE_THRESHOLD` | `0.20` | Über diesem Wert → Retry |
| `PROMPT_VARIANT` | `""` | A/B-Test Variante (z.B. `v2`) |
| `SEMANTIC_DEDUP_ENABLED` | `false` | Level-C Dedup aktivieren |
| `TELEMETRY_ENABLED` | `true` | Telemetrie ein/aus |

---

## Was v18 noch nicht löst (bewusste Entscheidungen)

**Semantic Dedup (Level C):** Stub in v18. Benötigt Embedding-Endpoint. Wird in v19 aktiviert wenn ausreichend Runs zur Kalibrierung des Schwellenwerts vorliegen.

**`validate_output()` als Kontrakt-Datei:** In v14 als nächster Schritt angekündigt. In v18 weiterhin in der Step-Datei. Die Auslagerung als `prompts/<step>.contract.json` ist der logisch nächste Schritt für v19.

**Parallele Step-Ausführung:** Steps 04a/04b (Generation pro Kategorie) könnten parallelisiert werden. Bewusst nicht in v18, um die Manifest-Konsistenz zu stabilisieren bevor Concurrency eingeführt wird.

---

*Version 19.0.0 — Atomic Problem Identification Pipeline*


## Neu in v19

- Smoke-Tests (`pipeline smoke`, `pipeline doctor`)
- Mehrstufige Quality Gates (Schema, Business Rules, Content, Quality)
- Run Health Scoring + Invariants
- Observability-Artefakte (`exports/metrics.json`, `run_timeline.json`, `dashboard.html`)
- Drift-Analyse (`pipeline drift`)
