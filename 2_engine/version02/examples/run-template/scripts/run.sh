#!/usr/bin/env bash
set -euo pipefail
mkdir -p out
echo "hello from engine v0.2 run $(date -Is)" | tee out/hello.txt
