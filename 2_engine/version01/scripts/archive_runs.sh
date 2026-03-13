#!/usr/bin/env bash
set -euo pipefail
RUNS_ROOT="${RUNS_ROOT:-/home/ef/ram/runs}"
ARCHIVE_ROOT="${ARCHIVE_ROOT:-/home/ef/Beruflich/GitHub/3.matrix (artifacts)/2.runs}"
mkdir -p "$ARCHIVE_ROOT"

for bucket in done failed; do
  src="$RUNS_ROOT/$bucket"
  [ -d "$src" ] || continue
  find "$src" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' d; do
    name="$(basename "$d")"
    dest="$ARCHIVE_ROOT/$name"
    rsync -a --delete "$d/" "$dest/"
    rm -rf "$d"
  done
done
