# Verification record

The extension is based on PR #2 commit
`8f94c4f9ff2ff0e50e91d2410b363866a8c31002`; it adds files only.
The draft PR and its CI record identify the final published commit.

- Lean: `leanprover/lean4:v4.34.1`, compiler commit
  `5045d0056413266e57c625dcd7c365b10e377c52` (official arm64 macOS binary).
- Lake: `5.0.0-src+5045d00`.
- Mathlib: `d13f23b723b8a846827a245b89c10fc7d3f11612`.
- Python: existing 3.14.3; no external numerical packages required or installed.

Commands, from `lean/HydrogenPathway`:

```sh
lake build HydrogenPathway.Witness
lake env lean HydrogenPathway/Witness/Declarations.lean
python3 -m unittest discover -s witness -p 'test_*.py' -v
python3 witness/model.py --check --output witness/RESULTS.json
bash scripts/verify-witness.sh
```

Local results: build and 11 expected-statement/axiom checks exit 0; 13 numerical
tests pass; eight illustrative scenarios and the port-dependent detection
counterexample reproduce. The complete response/POVM tests keep erasures,
all photon ports, and the unchanged atomic fallback. `verification.log` is
the sanitized output. The placeholder/custom-axiom scan fails closed.

All 11 named theorems have only `propext`, `Classical.choice`, and `Quot.sound`
in their transitive axiom sets. The new Lean statements are scalar arithmetic
consequences of explicit response and error hypotheses. They do not prove the
matrix construction, cosine bound, an optical control sequence, source
admissibility, or an actual hydrogen instrument. The illustrative rational
budget is an arithmetic check, not certification of its inputs.

Numerical tolerance is `2e-9`; matrices use double precision and the unchanged
PR #2 standard-library helpers. Numerical checks are not interval-certified or
Lean proofs. `source-sha256.txt` binds the listed source/result files, excluding
itself and the log; hashes alone do not validate their contents.

The new GitHub Actions workflow uses the existing pinned Linux Lean archive
and scoped Mathlib cache. It runs the same verification script. The inherited
pathway and imprint workflows remain unchanged and are regression checks on
this PR. CI success is to be read from the final draft-PR checks, not inferred
from this local record.
