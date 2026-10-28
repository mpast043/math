#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
log_dir="${LOG_DIR:-.lake/witness-verification}"
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
  lake build HydrogenPathway.Witness
  lake env lean HydrogenPathway/Witness/Declarations.lean
  python3 -m unittest discover -s witness -p 'test_*.py' -v
  python3 witness/model.py --check --output "$log_dir/model-results.json"
  if grep -En '(^|[^[:alnum:]_])(sorry|admit)([^[:alnum:]_]|$)|^[[:space:]]*(axiom|opaque)[[:space:]]' \
      HydrogenPathway/Witness.lean HydrogenPathway/Witness/*.lean; then
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
  echo 'PASS: witness build, 11 declarations/axiom audits, 13 numerical tests, model cases, and source scan.'
} 2>&1 | tee "$log_dir/build-model-and-axioms.log"
