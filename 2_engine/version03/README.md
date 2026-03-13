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
