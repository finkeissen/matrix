# QUICKSTART (v03)

## 1) Zentrale Konfiguration

Alle absoluten Pfade und Parameter liegen in:

- `config/matrix-engine.env` (im Repo)
- empfohlen produktiv: `/etc/matrix-engine/matrix-engine.env`

Für systemd wird die Datei via `EnvironmentFile=` geladen.

## 2) Run starten (manuell)

```bash
cp -a examples/run-template "${MATRIX_RUNS_ROOT:-/home/ef/ram/runs}/incoming/run-$(date +%Y%m%d-%H%M%S)"
python3 -m engine.cli run "${MATRIX_RUNS_ROOT:-/home/ef/ram/runs}/incoming/<run-id>"
```

## 3) Daemon starten (manuell)

```bash
MATRIX_RUNS_ROOT=/home/ef/ram/runs python3 -m engine.cli daemon --runs-root /home/ef/ram/runs
```

## 4) Archivieren (append-only)

```bash
MATRIX_CONFIG=./config/matrix-engine.env ./scripts/archive_runs_append_only.sh
```
