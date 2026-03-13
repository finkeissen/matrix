# Matrix Engine (v0.2.0)

Local, reproducible run pipeline that enforces **structural admissibility** and **STOP propagation**.
It does **not** evaluate truth, correctness, usefulness, or authority.

## Single source of constraints
All engine-enforced constraints are summarized in:
- `CONSTRAINTS.md`

The engine is designed so that it does **not** require external normative documents at runtime.

## Runtime vs Archive
- Runtime (RAM): `/home/ef/ram/runs/`
- Archive (append-only): `/home/ef/Beruflich/GitHub/3.matrix (artifacts)/2.runs/`

## Commands
- Run once: `python3 engine/cli.py run /path/to/run`
- Daemon:   `python3 engine/cli.py daemon --runs-root /home/ef/ram/runs`

See `QUICKSTART.md`.
