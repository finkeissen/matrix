#!/usr/bin/env bash
set -euo pipefail
mkdir -p out
echo "hello from engine run $(date -Is)" | tee out/hello.txt
