# 3.commit/2026-02-11

This folder is the canonical commit package for **Foundation v1 / Production-line v1**.

## Contents

- `manifest.json`  
  v1 commit manifest. Must remain JSON-valid. Populate:
  - `run_manifests` once you have per-run manifests (or explicitly keep empty if your contract allows).
  - `artefacts` with each committed artefact + `checksum` (sha256) + `source_run`.

- `artefacts/`  
  Place the artefact files that are part of this commit here **only if** they are:
  1) byte-identical to a run output, OR  
  2) produced by a dedicated consolidation run that is itself listed in `source_runs`.

- `checksums.sha256`  
  SHA256 list for all files under `artefacts/` (and any other files you choose to lock).

- `tools/`  
  Helper scripts to (re)generate and verify checksums.

## Minimal workflow

1) Put artefacts into `artefacts/`
2) Run: `tools/generate_checksums.sh`
3) Copy the sha256 values into `manifest.json -> artefacts[].checksum`
4) Run: `tools/verify_checksums.sh`
