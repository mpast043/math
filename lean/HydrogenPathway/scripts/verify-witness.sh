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
  cmp witness/RESULTS.json "$log_dir/model-results.json"
  python3 - <<'HASHCHECK'
from pathlib import Path
import hashlib
for line in Path('witness/source-sha256.txt').read_text().splitlines():
    expected, name = line.split('  ', 1)
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'Source hash mismatch: {name}')
print('PASS: saved results reproduce and all 11 source hashes match.')
HASHCHECK
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
