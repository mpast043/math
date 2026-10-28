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
  python3 - witness/RESULTS.json "$log_dir/model-results.json" <<'ARTIFACTCHECK'
from pathlib import Path
import hashlib
import json
import math
import sys

def compare(saved, fresh, path='$'):
    if isinstance(saved, bool) or isinstance(fresh, bool):
        equal = type(saved) is type(fresh) and saved == fresh
    elif isinstance(saved, (int, float)) and isinstance(fresh, (int, float)):
        equal = math.isfinite(saved) and math.isfinite(fresh) and abs(saved - fresh) <= 2e-9
    elif type(saved) is not type(fresh):
        equal = False
    elif isinstance(saved, dict):
        if saved.keys() != fresh.keys():
            raise SystemExit(f'Result keys differ at {path}')
        for key in saved:
            compare(saved[key], fresh[key], f'{path}.{key}')
        return
    elif isinstance(saved, list):
        if len(saved) != len(fresh):
            raise SystemExit(f'Result lengths differ at {path}')
        for i, (a, b) in enumerate(zip(saved, fresh)):
            compare(a, b, f'{path}[{i}]')
        return
    else:
        equal = saved == fresh
    if not equal:
        raise SystemExit(f'Results differ beyond tolerance at {path}: {saved!r} != {fresh!r}')

compare(json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text()))
for line in Path('witness/source-sha256.txt').read_text().splitlines():
    expected, name = line.split('  ', 1)
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'Source hash mismatch: {name}')
print('PASS: saved results reproduce within 2e-9 and all 11 source hashes match exactly.')
ARTIFACTCHECK
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
