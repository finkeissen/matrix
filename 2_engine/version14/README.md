# Atomic Problem Identification Pipeline — Version 14

**Version:** 14.0.0  
**Replaces:** v2.1.0  
**Architecture revision date:** 2026-03-07

---

## Leitprinzip

Eine Pipeline, die Wissen erzeugt, muss sich selbst beobachten können — nicht nur was sie erzeugt, sondern *wie* und *womit* sie es erzeugt. Version 14 führt daher zwei vollständige, unabhängige Lebenszyklen ein: einen für **Artefakte** (die generierten Inhalte) und einen für **Prompts** (die Anweisungen, die diese Inhalte erzeugen). Beide Lebenszyklen sind messbar, versioniert und vergleichbar.

---

## Die zwei Lebenszyklen

### Lebenszyklus 1: Artefakt-Lebenszyklus (Inhalte)

Jedes von der Pipeline erzeugte Datenobjekt durchläuft definierte Zustände:

```
candidate → verified → accepted
                ↓           ↓
           superseded    disputed → rejected
```

| Zustand | Bedeutung |
|---------|-----------|
| `candidate` | Frisch generiert, noch nicht geprüft |
| `verified` | Besteht Schema-, Duplikat- und Atomizitätsprüfung |
| `accepted` | Menschlich oder extern bestätigt |
| `superseded` | Durch neuere Generation ersetzt |
| `disputed` | Qualitätszweifel markiert, Review ausstehend |
| `rejected` | Endgültig ausgeschlossen |

**Gespeichert in:** `manifest.json` pro Run, `content_state_at_commit` in jedem Problem-Record.

---

### Lebenszyklus 2: Prompt-Lebenszyklus (Anweisungen)

Prompts sind selbst versionierte Artefakte. Jede Änderung an einem Prompt erzeugt eine neue Version mit eigenem Hash. Die Pipeline zeichnet auf, welche Prompt-Version jeden Artefakt erzeugt hat.

```
draft → active → deprecated
                     ↓
               archived (nach N runs ohne Nutzung)
```

| Zustand | Bedeutung |
|---------|-----------|
| `draft` | In Entwicklung, noch nicht in Produktion |
| `active` | Aktuell aktive Version für diesen Step |
| `deprecated` | Von neuerer Version ersetzt, noch referenziert |
| `archived` | Nicht mehr genutzt, historisch dokumentiert |

**Gespeichert in:** `pipeline/prompts/<step_name>.md` (Text), `pipeline/prompt_registry.json` (Metadaten).

**Kernprinzip:** Ein Run-Record enthält `prompt_versions: {step: {version, hash}}`. Zwei Runs mit identischen Inputs aber unterschiedlichem `prompt_hash` sind direkt vergleichbar — das ist die Grundlage für systematische Prompt-Optimierung.

**Novelty Guard ist prompt-sensitiv:** Cache-Hit nur wenn `prompt_hash` + Inputs identisch. Prompt-Änderung → neue Generation, auch wenn dieselben Daten vorliegen.

---

## Trennung der Schichten

Jede Step-Datei in v13 und früher vermischte vier verschiedene Schichten in einer Datei. Version 14 trennt sie strikt:

```
Schicht 1: Prompt-Text       → pipeline/prompts/<step>.md
Schicht 2: Output-Kontrakt   → pipeline/prompts/<step>.contract.json
Schicht 3: Step-Logik        → pipeline/steps/step_<name>.py  (nur run() + validate())
Schicht 4: Infrastruktur     → pipeline/common.py, prompt_loader.py, telemetry.py
```

**Was das bedeutet:**
- Prompt-Verbesserungen berühren nie den Python-Code
- Step-Refactorings berühren nie den Prompt-Text
- Beide Dimensionen haben eigene Git-History
- A/B-Tests zwischen Prompts sind mit `--prompt-variant` ohne Code-Änderung möglich

---

## Messpunkte (Armaturen)

Version 14 implementiert ein vollständiges Telemetrie-System, das jeden Aspekt des Prozesses messbar macht. Alle Messpunkte schreiben in `telemetry.jsonl` (pro Run) und werden nach Run-Abschluss in `telemetry_summary.json` aggregiert.

### Technische Messpunkte

| Metrik | Wo gemessen | Bedeutung |
|--------|-------------|-----------|
| `llm_latency_ms` | Jeder LLM-Call | Modell-Performance, Timeout-Kalibrierung |
| `llm_tokens_in` / `llm_tokens_out` | Jeder LLM-Call | Kosten, Kontext-Nutzung |
| `llm_retry_count` | Pro Step | Zuverlässigkeit der Modell-Antworten |
| `json_parse_success` | Jeder LLM-Call | Prompt-Qualität (strukturierte Ausgabe) |
| `step_duration_ms` | Pro Step | Bottleneck-Analyse |
| `novelty_cache_hits` | Pro Run | Cache-Effizienz |

### Inhaltliche Messpunkte

| Metrik | Wo gemessen | Bedeutung |
|--------|-------------|-----------|
| `scope_confidence_score` | Step 01_confidence | Scope-Qualität |
| `boundary_count` / `exclusion_count` | Step 01_scope | Scope-Vollständigkeit |
| `category_count` | Step 03_normalize | Granularität der Generation |
| `problems_per_category` | Step 04a/04b | Dichte-Verteilung |
| `atomicity_failure_rate` | Step 05_validation | Kern-Qualitätsmetrik |
| `hallucination_flagged_rate` | Step 07_hallucination | Fakten-Zuverlässigkeit |
| `problems_added_by_review` | Step 04b | Review-Mehrwert |
| `problems_removed_by_review` | Step 04b | Filter-Schärfe |
| `scope_violations_count` | Step 05_validation | Scope-Disziplin |
| `duplication_rate` | Step 05_validation | Generierungs-Redundanz |

### Prompt-Leistungsmesspunkte

| Metrik | Wo gemessen | Bedeutung |
|--------|-------------|-----------|
| `prompt_hash` | Jeder LLM-Call | Welche Version hat dieses Artefakt erzeugt |
| `validation_pass_rate_by_prompt` | Aggregiert | Welcher Prompt erzeugt valide Outputs |
| `avg_score_by_prompt_version` | Aggregiert | Prompt-A/B Vergleich |
| `json_parse_rate_by_prompt` | Aggregiert | Strukturtreue pro Prompt-Version |

### Dashboard-Queries (aus `telemetry_summary.json`)

```bash
# Welcher Step ist der Bottleneck?
jq '.steps | to_entries | sort_by(.value.avg_duration_ms) | reverse' telemetry_summary.json

# Atomizitätsrate über alle Runs für SD-001
jq 'select(.subdomain_id=="SD-001") | .atomicity_failure_rate' runs/*/telemetry_summary.json

# Prompt-Vergleich: welche Version erzeugt mehr valide Outputs?
jq '.prompt_performance' runs/*/telemetry_summary.json | jq -s 'group_by(.prompt_hash)'

# LLM-Fehlerrate pro Modell-Klasse
jq '.llm_calls | group_by(.model_class) | map({model: .[0].model_class, error_rate: (map(.success) | (map(select(. == false)) | length) / length)})' telemetry_summary.json
```

---

## Architektur-Übersicht

```
pipeline/
├── README.md                    ← dieses Dokument
├── prompt_registry.json         ← aktive Prompt-Versionen + Hashes
├── config.py                    ← alle Parameter via env / .env
├── constants.py                 ← Enums, Codes, Versionen
├── common.py                    ← Infrastruktur: IO, Hashing, LLM-Call
├── prompt_loader.py             ← NEU: lädt/hasht Prompts, löst Versionen auf
├── telemetry.py                 ← NEU: Messpunkte, Aggregation, Summary
├── validator.py                 ← Schema-, Duplikat-, Scope-Prüfung
├── orchestrator.py              ← Sequenz-Dispatcher, RunState
│
├── prompts/                     ← NEU: Prompts als versionierte Textdateien
│   ├── 01_scope.md
│   ├── 01_scope_confidence.md
│   ├── 03_categories.md
│   ├── 03_gap_detection.md
│   ├── 04a_generation.md
│   ├── 04b_generation_review.md
│   ├── 05_validation_atomicity.md
│   ├── 06_clarification.md
│   ├── 07_hallucination_scan.md
│   ├── 07_alternative_check.md
│   └── 08_finalization_summary.md
│
├── steps/                       ← nur run() + validate_output()
│   ├── step_01_scope.py
│   ├── step_01_scope_confidence.py
│   ├── step_02_retrieval.py
│   ├── step_03_categories.py
│   ├── step_03_normalize.py
│   ├── step_03_gap_detection.py
│   ├── step_04a_generation.py
│   ├── step_04b_generation_review.py
│   ├── step_05_validation.py
│   ├── step_06_clarification.py
│   ├── step_07_hallucination_scan.py
│   ├── step_07_alternative_check.py
│   ├── step_08_finalization.py
│   └── step_09_commit.py
│
├── schema/                      ← JSON Schema für alle Artefakte
│   ├── atomic_problem.schema.json
│   ├── manifest.schema.json
│   ├── normalized_categories.schema.json
│   ├── problems_reviewed.schema.json
│   ├── run_record.schema.json
│   ├── scope.schema.json
│   └── validation_report.schema.json
│
├── spec/                        ← Step-Spezifikationen (unverändert)
│   └── *.md
│
└── data/
    ├── input/
    │   ├── subdomains.jsonl
    │   └── seeds/
    ├── runs/
    │   └── <run_id>/
    │       ├── run_record.json      ← enthält prompt_versions{}
    │       ├── manifest.json        ← Artefakt-Lebenszyklus
    │       ├── state.jsonl          ← Event-Log
    │       ├── novelty_cache.jsonl
    │       ├── telemetry.jsonl      ← NEU: Rohmessdaten
    │       ├── telemetry_summary.json ← NEU: aggregierte Metriken
    │       ├── artifacts/
    │       └── snapshots/
    ├── registry/
    │   ├── problems.jsonl
    │   └── run_log.jsonl
    └── archive/
```

---

## Konfigurationsparameter (`.env`)

Alle Parameter sind über Umgebungsvariablen steuerbar. Keine Hardcodes im Code.

| Parameter | Default | Bedeutung |
|-----------|---------|-----------|
| `LM_STUDIO_URL` | `http://localhost:1234/v1/chat/completions` | LLM-Endpoint |
| `LM_STUDIO_MODEL` | `loaded` | Modell-ID (oder `loaded` für das geladene) |
| `REQUEST_TIMEOUT` | `120` | LLM-Timeout in Sekunden |
| `SCOPE_CONFIDENCE_THRESHOLD` | `0.70` | Unter diesem Wert → Clarification |
| `ATOMICITY_FAILURE_THRESHOLD` | `0.20` | Über diesem Wert → Retry |
| `MAX_CLARIFICATION_ROUNDS` | `2` | Max. Scope-Refinement-Loops |
| `HALLUCINATION_SAMPLE_MAX` | `60` | Max. Probleme für Hallucination Scan |
| `DEFAULT_RETRIES` | `1` | LLM-Retry-Versuche pro Call |
| `PROMPT_VARIANT` | `` | Optional: Prompt-Variante für A/B-Tests |
| `TELEMETRY_ENABLED` | `true` | Telemetrie ein/aus |

---

## Prompt-Varianten und A/B-Tests

```bash
# Standard-Run mit aktiver Prompt-Version
python orchestrator.py --subdomain SD-001 --steps all

# Run mit einer alternativen Prompt-Variante
python orchestrator.py --subdomain SD-001 --steps 04a --prompt-variant v2

# Vergleich zweier Runs
python telemetry/compare_runs.py --run-a 2026-03-07_001_SD-001 --run-b 2026-03-07_002_SD-001
```

Prompt-Varianten liegen als `<step_name>.v2.md`, `<step_name>.v3.md` etc. im `prompts/`-Verzeichnis.

---

## Erweiterungen gegenüber v2.1

1. **`prompt_loader.py`** — Lädt Prompts aus `prompts/*.md`, berechnet SHA256, löst Varianten auf
2. **`telemetry.py`** — Schreibt Messpunkte in `telemetry.jsonl`, aggregiert in `telemetry_summary.json`
3. **Prompt-sensitiver Novelty Guard** — `task_id = sha256(step + inputs + prompt_hash)`
4. **`run_record.json`** enthält `prompt_versions: {step: {file, version, hash}}`
5. **Validation-Symmetrie** — `validate_output()` prüft dieselben Constraints wie der Prompt fordert
6. **`clarification_input`-Validation** — Re-Entry-Scope wird re-validiert bevor er akzeptiert wird
7. **Schicht-Trennung** — Prompts, Kontrakte, Step-Logik, Infrastruktur in separaten Dateien

---

*Version 14.0.0 — Atomic Problem Identification Pipeline*
