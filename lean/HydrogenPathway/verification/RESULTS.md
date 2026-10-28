# Conditional pathway verification

Verified locally with Lean 4.34.1 (compiler commit
`5045d0056413266e57c625dcd7c365b10e377c52`) and Lake 5.0.0-src+5045d00
on ARM64 macOS. Mathlib is pinned at
`d13f23b723b8a846827a245b89c10fc7d3f11612`.

Base repository commit: `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
Feature branch: `codex/hydrogen-conditional-spine`.
The sanitized log records the checkout commit at test time; uncommitted
source identity is additionally bound by `source-sha256.txt`. These hashes
identify the tested bytes; they are not mathematical evidence for an external
physical residual certificate.

From `lean/HydrogenPathway`:

```sh
lake build HydrogenPathway
lake env lean HydrogenPathway/Declarations.lean
bash scripts/verify.sh
```

All three commands exited **0**. The project build completed successfully
with 2135 jobs (including cached dependency jobs). All six independent
statement checks passed: overlap, projection, residual normalization, scalar
click dilution, projection-to-click composition, and residual-to-click
composition. Regression examples cover perfect overlap, a nontrivial rational
square-root case, zero-clamped overlap, and nonzero false clicks.

The transitive audit covers all **15** named theorems. Each uses only the
repository's permitted standard axioms:

```
[propext, Classical.choice, Quot.sound]
```

The source scan finds no proof placeholders or custom axiom declarations.
The shell script syntax and whitespace checks pass. The scoped workflow's
YAML syntax parses successfully. No external Comparator, landrun, lean4export,
or independent kernel recheck is claimed; this is a Lean declaration test
against separately defined propositions plus a transitive axiom audit.

A separate read-only review repeated elaboration of the five implementation
modules and declaration tests with exit 0 and found no critical or important
issues. Its minor source-scanner hardening finding was fixed: scanner errors
now fail verification. A local regression injected scanner exit status 2;
the verification command propagated exit 2 and emitted no PASS marker.

Lean checks the exact arithmetic

```
1 - (294780/1000000)² = 9131047516/10000000000 < 913105/1000000.
```

There is therefore no claimed `F ≥ 0.913105` corollary from those rounded data.

## External obligations

No physical source certificate is validated by these proofs. The residual
inequality, reference-target overlap, physical operator/domain identification,
incoherent click model, signal mass, and false-click bound remain explicit
caller inputs. The new central-source certificate and inherited accepted-state
endpoint remain separate open instances. Transport, return, capture,
efficiency, and reduced-state trace-distance control remain open. See the
README assumption ledger for the complete boundary.

## Remote verification

The new path-scoped GitHub Actions workflow is supporting test infrastructure.
Its actual run status is reported on the draft PR; a local pass is not a
claim that remote CI passed.
