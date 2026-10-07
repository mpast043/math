# Scientific use continuation

Start with the [illustrated research note](output/pdf/scientific_uses.pdf)
or its [editable text](research_note.md). Both explain the results, derivations,
scientific uses and proposed discoveries.

This continuation starts at claude/math-repo-review, commit
80b50443f73da7934815df0973231b13666890f6, and accepts it as a factual handoff.
The work develops applications; it does not audit source proofs.

| Extension | Result under the stated model |
|---|---|
| [Classical qubit encoding](quantum.py) | Ordinary X readout gains 37.9% at one T1; the T2 threshold is 153.72 us. |
| [Optical allocation](optical.py) | 12.2-38.9% fewer mean photons than time sharing with optimized fractions and powers. |
| [Rare population inference](transport.py) | Arbitrarily small aggregate target error can replace 12.5% of a rare group's original members. |
| [Reaction design](reactions.py) | One permitted reaction repairs a four-edge diamond; a separate rate condition enforces a stationary floor. |
| [Network inference](networks.py) | Triangle enrichment is weak; degree disassortativity has estimated tail p = 0.00125. |

The report also develops design rules and experiments for Anderson localization,
Haldane boundaries, cold-atom depletion, fermion kinetic bounds, screened crystals,
chaotic forecasts and smooth-number algorithms.
The [twelve-use experiment agenda](results/results.json) is machine readable.

## Reproduce

From the repository root, using Python 3.11+:

    python3 -m venv .venv-scientific-uses
    .venv-scientific-uses/bin/python -m pip install -r review/continuation/requirements.txt
    .venv-scientific-uses/bin/python -m pytest review/continuation/tests -q
    .venv-scientific-uses/bin/python -m review.continuation.run
    .venv-scientific-uses/bin/python -m review.continuation.build_report

The run takes a few seconds on the development machine. Results record tested
dependency versions and fixed seeds. The PDF generator uses Arial on macOS
when available, otherwise Helvetica. Figures are PNG and SVG.

The graph runner accepts --network-draws; smaller runs have weaker tail estimates.
--output selects a results directory. The report builder accepts --results and --pdf.

## Scope

Tests check new computations within stated models. Qubit rates concern classical
information, and added dephasing gives achievable rates. Optical budgets assume
pure loss and ideal receivers. The rare-group rule is exact in the supplied square
construction. Repair uses permitted candidate complexes. Network tails and
multiplicity transformations are Monte Carlo estimates; diagnostics do not prove
finite-run convergence.

The overlap error budget, coherence-aware encoding rule and constrained repair
workflow are useful continuations. Wider novelty is framed as testable research.
