# Scientific Use Continuation Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this
> research continuation. The user has directly requested execution.

**Goal:** Turn the accepted Claude handoff into five usable, reproducible
scientific extensions, plus a research plan covering all 12 proposed uses.

**Architecture:** Small computational modules write deterministic results.
One runner records provenance and produces figures. A separate report builder
uses those exact results for an illustrated note.

**Tech Stack:** Python 3.11+, NumPy, SciPy, NetworkX, Matplotlib, ReportLab, pytest.

**Spec:** `review/continuation/DESIGN.md`.

## Global Constraints

Apply every scientific constraint in the spec. Pin source SHA
`80b50443f73da7934815df0973231b13666890f6`; do not change the source documents.
Only claim properties of the new models within their stated assumptions.

## Review Focus

1. Added qubit dephasing must not inherit the pure-GAD capacity theorem.
2. Both optical schemes must meet the same rates and mean photon constraint.
3. Rare-cell membership metrics must distinguish lost members from symmetric
   difference and Jaccard distance.
4. Structural reaction repairs must not be called quantitative or physical
   guarantees; missing candidates must be reported infeasible.
5. Burn-in must carry state forward; constant tail indicators must not be
   assigned a misleading zero uncertainty.

## Tasks

- [x] Task 1: Write `review/continuation/tests/test_calculations.py` with
  independent density-matrix entropy, photon-demand, polygon-overlap,
  conservation, graph-enumeration and degree-preservation tests. Run
  `python3 -m pytest review/continuation/tests -q`; expect missing-module
  failures. Implement `quantum.py`, `optical.py`, `transport.py`, `reactions.py`,
  and `networks.py`; rerun to green.
- [x] Task 2: Add `run.py`, fixed parameters and seeds, JSON outputs and five
  figures. Run `python3 -m review.continuation.run`; expect finite results,
  degree preservation and correct rate constraints. Add a smoke check before
  implementing the runner.
- [x] Task 3: Write the research note and all-12-use roadmap, with primary
  sources for application context, explicit derivations and candidate research
  questions. Build the PDF with `build_report.py`; render and visually inspect.
- [ ] Task 4: Review scientific applicability and new code, run the suite and
  reproducibility checks, commit, push, and use `git ls-remote` to verify the
  remote continuation SHA. The continuation must descend from the source SHA.
