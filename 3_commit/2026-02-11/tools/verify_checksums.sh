#!/usr/bin/env bash
set -euo pipefail

# Verify checksums in ../checksums.sha256

cd "$(dirname "$0")/.."

FILE="checksums.sha256"

if [ ! -f "$FILE" ]; then
  echo "ERROR: $FILE not found" >&2
  exit 1
fi

# Use sha256sum if available, otherwise shasum -a 256 -c
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c <(grep -vE '^#' "$FILE" | sed '/^\s*$/d') || exit 1
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 -c <(grep -vE '^#' "$FILE" | sed '/^\s*$/d') || exit 1
else
  echo "ERROR: Need sha256sum or shasum" >&2
  exit 1
fi

echo "OK: checksums verified"
