# Verification scope

Base: `2f3158f48dc4e557851a8d188796147dca1f94cd` on
`codex/hydrogen-conditional-spine` (PR #1). Extension branch:
`codex/hydrogen-two-source-imprint`. All PR #1 files are preserved unchanged;
the extension adds files only. No manuscript or private certificate is used.

Lean is `leanprover/lean4:v4.34.1`, compiler commit
`5045d0056413266e57c625dcd7c365b10e377c52`; Mathlib is
`d13f23b723b8a846827a245b89c10fc7d3f11612`.

The following commands exited **0** locally from `lean/HydrogenPathway`:

```sh
lake build HydrogenPathway.Imprint
lake env lean HydrogenPathway/Imprint/Declarations.lean
python3 -m unittest discover -s imprint -p 'test_*.py' -v
python3 imprint/model.py --check --output imprint/RESULTS.json
bash scripts/verify-imprint.sh
```

The generated report checks ten reference cases and one collected/unobserved
case. The model suite contains 13 tests, including a 30-case phase/capture grid,
30 random mixed-state unequal-yield identities, complex phase conventions,
Kraus completeness, Choi positivity, Stinespring partial traces, zero success,
posterior priors, the common-failure assumption, momentum-support precision,
and normalized flagged error budgets. These are double-precision checks,
not formal matrix proofs. A separate local comparison with already-installed
NumPy 2.4.2 on 50 Hermitian matrices (dimensions 1,2,4,5,10) gave maximum
trace-norm discrepancy `8.88e-15`; NumPy is not a project dependency.

Eight named Lean scalar/metric theorems have independent declaration tests
and transitive axiom checks. Only `propext`, `Classical.choice`, and
`Quot.sound` are permitted. This does not claim a Lean proof of the matrix
trace-norm identity, Helstrom theorem, complete positivity, or a general
trace-class result. Those model calculations are analytically derived in the
README and numerically checked using the explicit finite matrices.

The sanitized local log and `source-sha256.txt` bind the tested source bytes.
Hashes identify those bytes; they do not prove physical certificate validity.
Actual final-commit CI status is recorded in the stacked draft PR; local
verification alone does not imply remote CI success.
