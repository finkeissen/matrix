#!/usr/bin/env bash
set -euo pipefail

# Generate SHA256 checksums for all files under artefacts/
# Writes to ../checksums.sha256 relative to this script.

cd "$(dirname "$0")/.."

OUT="checksums.sha256"
TMP="$(mktemp)"

echo "# sha256 checksums for artefacts/" > "$TMP"
echo "# Format: <sha256>  <relative_path>" >> "$TMP"

# Use sha256sum if available, otherwise shasum -a 256
if command -v sha256sum >/dev/null 2>&1; then
  HASHCMD=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then
  HASHCMD=(shasum -a 256)
else
  echo "ERROR: Need sha256sum or shasum" >&2
  exit 1
fi

# Find files (exclude .gitkeep)
mapfile -t FILES < <(find artefacts -type f ! -name ".gitkeep" -print | sort)

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "# (no artefacts yet)" >> "$TMP"
else
  for f in "${FILES[@]}"; do
    "${HASHCMD[@]}" "$f" >> "$TMP"
  done
fi

mv "$TMP" "$OUT"
echo "Wrote $OUT"
