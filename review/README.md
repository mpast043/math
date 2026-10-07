# Review materials

Supporting files for a review of this repository: which results are
machine-checked, which shipped certificates pass, and independent tests of
selected claims. Everything here was produced on 2026-10-07 in a 4-core Linux
container. None of it referees the mathematics.

The written review is `report.html` (open it in a browser). It is also
published at https://claude.ai/artifact/124hrmVkDbQw7YEGmSi7nt, which is
private until its owner shares it.

## Contents

| Path | What it is |
|---|---|
| `report.html` | The review: verdict, evidence levels, my checks, headline claims, scope gaps, uses by field, and a filterable catalogue of all 372 families |
| `lean-check/SeymourCheck.lean` | Challenge statement for Seymour's conjecture (family 173), copied verbatim into a fresh namespace and derived from the repository's compiled proof; prints the axioms used |
| `lean-check/CompareEnvs.lean` | Comparator-style check: loads the compiled challenge and the compiled proof as two environments and compares every challenge declaration (type and definition body), then lists the axioms of the target theorems |
| `lean-check/seymour_*.txt`, `*.log` | Build, axiom, kernel-replay and comparison outputs, including a negative control with a mutated statement |
| `lean-check/ThompsonAxioms.lean`, `lean-check/thompson_*` | The same checks for Thompson's group F (family 248): build log, axioms, comparison of all 61 challenge declarations, and a fresh kernel replay |
| `lean-check/MutatedSeymour_negative_control.lean` | Seymour challenge with one condition removed; `CompareEnvs.lean` must flag it, and does |
| `results/shipped_certificates.md` | Outcomes of re-running 14 of the repository's own verification bundles |
| `demos/seymour_exhaustive.c` | All oriented graphs on up to 6 vertices, plus random larger ones |
| `demos/cycle_clique_ramsey_sat.py` | SAT check of small cases of R(C_m, K_n) = (m-1)(n-1)+1 (family 189) |
| `demos/gad_capacity.py` | Generalized amplitude-damping capacity: King's theorem, brute-force Holevo optimum, two-use additivity search (family 276) |
| `demos/epni_random_test.py` | Entropy photon-number inequality on random non-Gaussian inputs, exact in Fock space (family 273) |
| `demos/lienard_limit_cycles.py` | Limit cycles of the quintic Liénard sharpness example and a random scan (family 143) |
| `results/*.txt` | Outputs of the demos |

## Reproducing the Lean checks

1. Download the Lean toolchain `lean-4.34.1-linux.tar.zst` from the
   `leanprover/lean4` GitHub release and put its `bin/` on `PATH`.
2. Clone Mathlib at commit `d13f23b723b8a846827a245b89c10fc7d3f11612`
   (the pin in `lean/lake-manifest.json`).
3. Create a Lake project with `lean-check/lakefile.lean` next to that Mathlib
   checkout. Copy the import closure of the target module from `lean/OAI/`
   and the challenge file from `lean/ComparatorChallenges/` into it, keeping
   module paths.
4. `MATHLIB_NO_CACHE_ON_UPDATE=1 lake build OAI.Combinatorics.SecondNeighborhood.Main ComparatorChallenges.SeymourSecondNeighborhood`
   (about 25 minutes on 4 cores without the Mathlib cache).
5. `lake env lean Check/Seymour.lean` (restated statement and `#print axioms`).
6. `lake env leanchecker --fresh OAI.Combinatorics.SecondNeighborhood.Main` (full kernel replay).
7. `lake env lean --run Check/CompareEnvs.lean ComparatorChallenges.SeymourSecondNeighborhood OAI.Combinatorics.SecondNeighborhood.Main OAI.SeymourSecondNeighborhood OAI.SeymourSecondNeighborhood.exists_goodVertex`

The official route is the Comparator tool (`lean/ComparatorChallenges/README.md`),
which also needs `lean4export` and `landrun`; it was not run here.

## Reproducing the demos

Python 3.11+ with `numpy`, `scipy` and `python-sat`:

```sh
cc -O2 demos/seymour_exhaustive.c -o seymour_exhaustive && ./seymour_exhaustive 6
python3 demos/cycle_clique_ramsey_sat.py 4,3 5,3 6,3 7,3 4,4
python3 demos/gad_capacity.py
python3 demos/epni_random_test.py
python3 demos/lienard_limit_cycles.py 60
```

Numerical searches can find counterexamples but cannot prove a theorem. A pass
means no violation was found.
