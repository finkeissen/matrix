#!/usr/bin/env bash
set -euo pipefail

## archive_runs_append_only.sh
#
# Append-only Archiver: moves completed runs from RAM (RUNS_ROOT/{done,failed})
# to SSD (ARCHIVE_ROOT/YYYY-MM-DD/<run_id>/) and deletes the RAM copy afterwards.
#
# Key properties (based on lessons learned from earlier archived runs):
# - Append-only: never overwrite an existing archived run directory.
# - Self-contained artifacts: archive includes README.md, manifest.json, outputs, and logs/.
# - Date bucketing follows the run's manifest.json created_at (if available),
#   otherwise it falls back to today's date.
#
# Config loading order:
#   1) MATRIX_CONFIG=/path/to/matrix-engine.env
#   2) ./config/matrix-engine.env (repo-local)
#   3) /etc/matrix-engine/matrix-engine.env (system default)
#
# Environment variables (preferred via central config):
#   MATRIX_RUNS_ROOT              default: /home/ef/ram/runs
#   MATRIX_ARCHIVE_ROOT           default: /home/ef/.../2.runs
#   MATRIX_PYTHON                 default: /usr/bin/env python3
#   MATRIX_ARCHIVE_RSYNC_OPTS     default: -a
#
# Exit codes:
#   0 success
#   2 append-only violation (target exists)
#
# Notes on "no tmp-files":
#   rsync may create temporary files depending on options and filesystem.
#   If you need stricter behavior, set MATRIX_ARCHIVE_RSYNC_OPTS="--inplace -a"
#   (tradeoff: partially-written files are possible on power loss).
#

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load central config if available.
MATRIX_CONFIG="${MATRIX_CONFIG:-}"
if [ -n "${MATRIX_CONFIG}" ] && [ -f "${MATRIX_CONFIG}" ]; then
  # shellcheck disable=SC1090
  source "${MATRIX_CONFIG}"
elif [ -f "${script_dir}/../config/matrix-engine.env" ]; then
  # shellcheck disable=SC1091
  source "${script_dir}/../config/matrix-engine.env"
elif [ -f "/etc/matrix-engine/matrix-engine.env" ]; then
  # shellcheck disable=SC1091
  source "/etc/matrix-engine/matrix-engine.env"
fi

RUNS_ROOT="${MATRIX_RUNS_ROOT:-${RUNS_ROOT:-/home/ef/ram/runs}}"
ARCHIVE_ROOT="${MATRIX_ARCHIVE_ROOT:-${ARCHIVE_ROOT:-/home/ef/Beruflich/GitHub/3.matrix (artifacts)/2.runs}}"
PY="${MATRIX_PYTHON:-/usr/bin/env python3}"

# rsync options (see header docs)
if [ -n "${MATRIX_ARCHIVE_RSYNC_OPTS:-}" ]; then
  RSYNC_OPTS="${MATRIX_ARCHIVE_RSYNC_OPTS}"
else
  RSYNC_OPTS="-a"
fi

# Determine YYYY-MM-DD bucket for a run.
# Prefer manifest.json created_at (epoch seconds) to mirror historical archives.
run_bucket_date() {
  local run_dir="$1"
  local manifest="$run_dir/manifest.json"
  if [ -f "$manifest" ]; then
    "$PY" - "$manifest" <<'PY'
import json, sys, datetime, os
p=sys.argv[1]
try:
    with open(p,'r',encoding='utf-8') as f:
        m=json.load(f)
    ts=float(m.get('created_at', 0))
    if ts>0:
        d=datetime.datetime.fromtimestamp(ts).date()
        print(d.isoformat())
    else:
        raise ValueError("missing created_at")
except Exception:
    print(datetime.date.today().isoformat())
PY
  else
    date +%F
  fi
}

mkdir -p "$ARCHIVE_ROOT"

echo "[archive] RUNS_ROOT=$RUNS_ROOT"
echo "[archive] ARCHIVE_ROOT=$ARCHIVE_ROOT"

for bucket in done failed; do
  src="$RUNS_ROOT/$bucket"
  [ -d "$src" ] || continue

  find "$src" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' d; do
    name="$(basename "$d")"
    day="$(run_bucket_date "$d")"
    dest_root="$ARCHIVE_ROOT/$day"
    dest="$dest_root/$name"

    mkdir -p "$dest_root"

    if [ -e "$dest" ]; then
      echo "ERROR: archive target already exists (append-only): $dest" >&2
      exit 2
    fi

    echo "[archive] $bucket/$name -> $day/$name"
    mkdir -p "$dest"

    # Copy *all* run contents, including logs/ and out/
    rsync $RSYNC_OPTS "$d/" "$dest/"

    # Remove RAM copy only after successful sync
    rm -rf "$d"
  done
done
