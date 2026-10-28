#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
log_dir="${LOG_DIR:-.lake/verification}"
mkdir -p "$log_dir"
{
  date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
  git rev-parse HEAD
  git branch --show-current
  lean --version
  lake --version
  cat lean-toolchain
  git -C .lake/packages/mathlib rev-parse HEAD
  lake build HydrogenPathway
  lake env lean HydrogenPathway/Declarations.lean
  if grep -En '(^|[^[:alnum:]_])(sorry|admit)([^[:alnum:]_]|$)|^[[:space:]]*(axiom|opaque)[[:space:]]' \
      HydrogenPathway.lean HydrogenPathway/*.lean; then
    echo 'Forbidden proof placeholder or axiom declaration found.' >&2
    exit 1
  else
    scan_status=$?
    if [ "$scan_status" -ne 1 ]; then
      echo 'Proof source scan failed.' >&2
      exit "$scan_status"
    fi
  fi
  git diff --check
  git diff --cached --check
  echo 'PASS: build, declaration checks, axiom allowlist, source scan, and whitespace checks.'
} 2>&1 | tee "$log_dir/build-and-axioms.log"
