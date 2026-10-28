#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
log_dir="${LOG_DIR:-.lake/imprint-verification}"
mkdir -p "$log_dir"
{
  date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
  git rev-parse HEAD
  git branch --show-current
  lean --version
  lake --version
  python3 --version
  cat lean-toolchain
  git -C .lake/packages/mathlib rev-parse HEAD
  lake build HydrogenPathway.Imprint
  lake env lean HydrogenPathway/Imprint/Declarations.lean
  python3 -m unittest discover -s imprint -p 'test_*.py' -v
  python3 imprint/model.py --check --output "$log_dir/model-results.json"
  if grep -En '(^|[^[:alnum:]_])(sorry|admit)([^[:alnum:]_]|$)|^[[:space:]]*(axiom|opaque)[[:space:]]' \
      HydrogenPathway/Imprint.lean HydrogenPathway/Imprint/*.lean; then
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
  echo 'PASS: imprint build, eight declarations/axiom audits, 13 numerical tests, model cases, and source scan.'
} 2>&1 | tee "$log_dir/build-model-and-axioms.log"
