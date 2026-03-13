# version05 config

## Paths
- repo_root: auto-discovered
- runs_root: <repo_root>/2.runs
- ram_root: /home/ef/ram/matrix

## Ephemeral workspace (Ramdisk)
- ram_run_dir: <ram_root>/<run_id>/
  - work/
  - tmp/
  - cache/

## Persistence
- canonical run artifacts go to: <runs_root>/<date>/<run_id>/
- logs: <runs_root>/<date>/<run_id>/logs/

## Lifecycle
- preflight: assert ram_root exists + writable
- start_run: mkdir ram_run_dir/*
- stage policy:
  - stages MAY write temp files to ram_run_dir/work
  - stages MUST write canonical artifacts to the run directory
- finalize_run:
  - flush: ensure required artifacts exist in run dir
  - cleanup: rm -rf ram_run_dir (unless debug_keep=true)

## Backpressure / limits
- max_ram_bytes_per_run:
- max_inflight_tasks:
- behavior on ENOSPC: stop run with STOP record + flush logs
