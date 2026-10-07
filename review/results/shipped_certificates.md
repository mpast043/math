# Re-runs of the repository's own computational certificates

Each bundle was copied to a scratch directory and run with its documented
command (Python 3.13, NumPy 2.5, SciPy 1.18, SymPy 1.14, mpmath 1.3, GCC) on
2026-10-07. These programs check the finite or numerical parts of the
proofs only; the analytic arguments are in the papers.

| Family | Bundle (preprint) | Command | Outcome | Time |
|---|---|---|---|---|
| 087 Mahler conjectures | `The-Mahler-Conjecture-for-General-Convex-Bodies` | the 10 programs in `verification/programs/` in the order fixed by `reproduce.py`, validated by its `check_report` | all 10 pass | ~7 s |
| 090 Triangular-lattice optimality | `An-atomic-certificate-for-triangular-lattice-universal-optimality` | `python3 -I verification/check_certificate.py` | exit 0 (silent pass) | 15 s |
| 107 Matrix multiplication | `Complex-Matrix-Multiplication-Below-2.258-...` | `checks/run_checks.py` (rectangular bounds) | `"status": "passed"`, outputs byte-identical to saved | 1 s |
| 107 Matrix multiplication | `Staggered-extraction-for-exact-matrix-multiplication-over-every-field` | `verify_parameters.py --mode interval --dps 80 --rational-log` | all 13 checks true; exponent enclosed in [2.37105488600674568486, 2.37105488600674568486] < 2.371056 | 14 s |
| 153 Bernoulli convolutions | `Arithmetic-classification-and-non-Pisot-singularity-...` | `verification/verify_degree31.py` | `PASS: all degree-31 finite arithmetic checks passed.` | 22 s |
| 187 Snaky in 21 moves | `Snaky-in-21-Maker-moves` | `route21/primary.py`, `route21/independent.py` | both `PASS` (728 cards, 37,042 reply classes) | <1 s |
| 189 Cycle–clique Ramsey | `Cycle-clique-Ramsey-numbers` | `verification/code/verify.py` | original and independent checkers agree; 3,099 patterns in 42 parameter pairs, 0 unresolved | 98 s |
| 205 Saxl / universal tensor squares | `Universal-Tensor-Squares-for-Symmetric-Groups` | compile `smallcode_submitted.cpp`; `smallcode_verify.py` for n = 1, 3, 5–8, 10–64; both `capacity_checks.py` modes | all 61 degrees status 0; both capacity checks `PASS` | 715 s |
| 210 Foulkes (sixth power) | `Foulkes-Conjecture-for-the-Sixth-Symmetric-Power` | `verify_computations.py --check` | `PASS` on 62 rows (check mode; the C++ certificate programs need Boost and were not executed) | 1 s |
| 266 MUBs in dimension six (companion) | `Exact-Fourier-certificates-for-complex-Hadamard-matrices-of-order-six` | `python3 verification/run.py` | output identical to the three lines printed in the paper (Appendix A) | 89 s |
| 067 Campana–Peternell, dimension 6 | `The-Campana-Peternell-conjecture-in-dimension-six` | `verification/verify.py` | `N done` / `pass` | 72 s |
| 272 Entanglement without secret key | `Entanglement-with-zero-distillable-secret-key-in-local-dimension-ten` | the three exact checkers + `cmp` against recorded outputs | all byte-identical | 1 s |
| 348 Einstein four-manifolds | `Positively-curved-Einstein-four-manifolds` | `verify.py --check` | `PASS` (53 identities, 24 exact values, 21 interval rows) | 3 s |
| 361 Harmonic-dimension counterexample | `A-counterexample-to-integer-degree-harmonic-dimension-comparison` | `verification/counting-check.py` | selected count exceeds the Euclidean count (strict surplus) | 13 s |

## Packaging issue found

* **Mahler conjecture bundle:** `verification/reproduce.py` and the README
  require `verification/SOURCE-MANIFEST.json`, which is not in the
  repository, so the documented command fails immediately with
  `FileNotFoundError`. The ten programs it pins are present and all pass when
  run in the documented order with the runner's own result validator; only the
  source-hash pinning could not be checked.

## Not run (time or dependencies)

Haldane gap (NumPy/SciPy, 27 thermal cases), the boundary-field spin-one gap,
Hellinger contraction, the three- and four-state reconstruction thresholds,
Bernoulli one-phase critical dimension, stable NLS blowup, Calabi flow, circle
packing (needs `python-flint`), the 2.258 square certificate (needs GMP), and
the remaining smaller bundles.
