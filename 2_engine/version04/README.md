# Matrix Engine (v03)

v03 bündelt **alle absoluten Pfade und Parameter** in einer zentralen Config-Datei.

## Pfade

- Runtime (RAM, tmpfs empfohlen): `${MATRIX_RUNS_ROOT}`
- Archive (append-only, SSD): `${MATRIX_ARCHIVE_ROOT}`

Die Defaults stehen in `config/matrix-engine.env`.

## systemd

- Service: `systemd/matrix-engine.service`
  - lädt `/etc/matrix-engine/matrix-engine.env`
  - nutzt `WorkingDirectory=${MATRIX_ENGINE_ROOT}`
  - startet via `python -m engine.cli ...`

- optional: tmpfs Mount Unit: `systemd/home-ef-ram-runs.mount`

## CLI

- Daemon: `python3 -m engine.cli daemon --runs-root <runs-root>`
- Single run: `python3 -m engine.cli run <run-dir>`

## Archivierung

`scripts/archive_runs_append_only.sh` liest Config in dieser Reihenfolge:

1) `MATRIX_CONFIG=/pfad/zur/env`
2) `./config/matrix-engine.env`
3) `/etc/matrix-engine/matrix-engine.env`


## Erfahrungen aus früheren Runs (in v03 übernommen)

Aus dem Archiv `2.runs/YYYY-MM-DD/<run_id>/` hat sich bewährt:

- **Datum pro Run**: die Archivierung buckettet nach `manifest.json.created_at` (nicht nach „Archiv-Tag“).
- **Self-contained Runs**: ein Run soll sich offline lesen lassen (README.md + manifest.json + Outputs + Logs).
- **Logs gehören zum Run**: Engine schreibt nach `logs/engine.log` und der Execute-Stage nach `logs/job.*.log`.
- **Append-only Archiv**: niemals überschreiben; wenn `<run_id>` schon existiert → Abbruch.

## Logging

- pro Run: `logs/engine.log`
- pro Job: `logs/job.<timestamp>.log` und `logs/job.<timestamp>.status.json`
