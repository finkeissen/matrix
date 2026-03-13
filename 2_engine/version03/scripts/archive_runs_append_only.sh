#!/usr/bin/env bash
set -euo pipefail

# Load central config if available.
# Priority: explicit MATRIX_CONFIG -> repo-local config -> /etc default.
MATRIX_CONFIG="${MATRIX_CONFIG:-}"
if [ -n "${MATRIX_CONFIG}" ] && [ -f "${MATRIX_CONFIG}" ]; then
  # shellcheck disable=SC1090
  source "${MATRIX_CONFIG}"
elif [ -f "$(dirname "$0")/../config/matrix-engine.env" ]; then
  # shellcheck disable=SC1091
  source "$(dirname "$0")/../config/matrix-engine.env"
elif [ -f "/etc/matrix-engine/matrix-engine.env" ]; then
  # shellcheck disable=SC1091
  source "/etc/matrix-engine/matrix-engine.env"
fi

RUNS_ROOT="${MATRIX_RUNS_ROOT:-${RUNS_ROOT:-/home/ef/ram/runs}}"
ARCHIVE_ROOT="${MATRIX_ARCHIVE_ROOT:-${ARCHIVE_ROOT:-/home/ef/Beruflich/GitHub/3.matrix (artifacts)/2.runs}}"

today="$(date +%F)"
dest_root="$ARCHIVE_ROOT/$today"
mkdir -p "$dest_root"

for bucket in done failed; do
  src="$RUNS_ROOT/$bucket"
  [ -d "$src" ] || continue
  find "$src" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' d; do
    name="$(basename "$d")"
    dest="$dest_root/$name"

    if [ -e "$dest" ]; then
      echo "ERROR: archive target already exists (append-only): $dest" >&2
      exit 2
    fi

    mkdir -p "$dest"
    rsync -a "$d/" "$dest/"

    rm -rf "$d"
  done
done
