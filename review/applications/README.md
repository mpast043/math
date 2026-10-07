# Applications

What the catalogue's results can be used for. Each script takes one family's
theorem, applies it to a concrete scientific or engineering question, and
computes what it predicts. Where a prediction can be checked numerically
(chaos, level statistics, network sampling, the transport counterexample), the
script checks it. None of this verifies a proof: the scripts assume the
theorems.

The write-up is `report.html` (open it in a browser). It is also published at
__URL__, which is private until its owner shares it.

| Script | Family | Question | Main output |
|---|---|---|---|
| `qubit_memory_capacity.py` | 276 | How many classical bits can a qubit store while it relaxes to a thermal state? | 0.361 bit after one T1 at 50 mK, 75% more than the standard 0/1 code |
| `optical_broadcast.py` | 273 | Capacity region of a lossy optical broadcast channel | Superposition coding beats time sharing by 6-31% |
| `anderson_level_statistics.py` | 261 | Is every disordered 2D system an insulator; do 3D metals survive weak disorder? | Level-spacing ratios for 2D (L = 16-64) and 3D (L = 8-16) Anderson models |
| `haldane_gap.py` | 268 | Is the spin-1 Heisenberg chain gapped? | Exact diagonalization to L = 16: gap extrapolates to 0.419 J; spin-1/2 edge states |
| `bose_gas_depletion.py` | 267 | Quantum depletion of dilute Bose gases | 0.2-6.7% for representative cold-atom experiments |
| `lieb_thirring.py` | 262 | Lieb-Thirring constants and the stability of matter | Kinetic constant K >= 90.9% of Thomas-Fermi (was 77.8%) |
| `screened_coulomb_crystals.py` | 090 | Ground state of 2D Yukawa (screened Coulomb) systems | Triangular lattice; square costs 0.2-7.6% more |
| `standard_map_entropy.py` | 146 | Is the standard map chaotic on positive area? | Entropy within 0.011 of ln(K/2) for K >= 10 |
| `reaction_network_permanence.py` | 149 | Can weakly reversible networks lose species? | 900/900 near-boundary runs recover; 20% of broken controls fail |
| `switch_chain_null_models.py` | 131 | Switch chain as a degree-preserving null model | Exact uniformity on small cases; karate-club triangles z = 1.3 |
| `smooth_numbers_crypto.py` | 011, 012 | Smoothness of p - 1 and of n, n + 1 | Sieve to 1e8, Pollard p - 1 and twin-smooth rates with exact Dickman rho |
| `ot_stability.py` | 374 | Stability exponent of optimal transport maps | Own semi-discrete solver: slopes 1/3 (small cluster) and 1/2 (balanced) |

## Running

Python 3.11+ with `numpy`, `scipy` and `networkx`. From this directory:

```sh
python3 qubit_memory_capacity.py
python3 optical_broadcast.py
python3 anderson_level_statistics.py            # about 10 minutes on 4 cores
python3 haldane_gap.py results 16               # about 7 minutes, several GB of memory
python3 bose_gas_depletion.py
python3 lieb_thirring.py
python3 screened_coulomb_crystals.py
python3 standard_map_entropy.py                 # about 1 minute
python3 reaction_network_permanence.py results 300
python3 switch_chain_null_models.py
python3 smooth_numbers_crypto.py results 1e8    # several GB of memory
python3 ot_stability.py
```

Every script takes the output directory as its first argument (default
`results`). Outputs are a text report and a JSON file per script.

## Notes

* Dickman's rho is computed from its power series on each unit interval in
  60-digit decimal arithmetic. Double-precision schemes lose relative accuracy
  beyond u of about 9 because absolute rounding errors do not decay with rho.
* The transport solver finds the dual weights by Newton's method on exact
  polygon areas; it does not use the paper's explicit potentials.
* Seeds are fixed, so reruns reproduce the outputs.
