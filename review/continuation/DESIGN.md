# Scientific use continuation

Current application focus, clarified 7 October 2026: start with solutions
already documented in the factual handoff, identify concrete decisions they
enable, and explain their benefits. The report prioritizes optical provisioning,
reaction-system design and known material reference structures. The rare-group
example illustrates the supplied stability result; developing a general
rare-cell reliability method is outside the present application. Further direct
uses cover periodic-box interfaces, gas-model selection and plasma simulation
diagnosis. Existing numerical demonstrations are retained.

User objective: take `claude/math-repo-review` as a factual handoff, use its
results to answer scientific questions, and explain useful new consequences.
The source is pinned to `80b50443f73da7934815df0973231b13666890f6`.
The continuation branch is `codex/scientific-use-continuation`.

## Deliverables

Five reproducible extensions: a qubit encoding decision rule including
dephasing and ordinary X-basis readout; a photon budget optimizer comparing
superposition against power-optimized time sharing; rare-group assignment
stability metrics from the supplied transport construction; minimum-cost
reaction graph repairs with quantitative abundance constraints; and multi-motif
degree-preserving network inference with sampling diagnostics.

An illustrated research note explains the computed results and derivations,
connects them to real research uses, and gives a concrete next experiment for
all 12 applications in the handoff. New calculations, existing results,
proposed applications, and claims of world-first novelty are distinct.
Global novelty is not asserted from a limited literature search.

## Scientific constraints

- Source theorems are premises. No proof auditing or Lean reruns.
- Only the new calculations and implementations are tested.
- Qubit quantities are classical information, not preservation of unknown
  quantum states. Added dephasing gives achievable strategy rates, not a newly
  established channel capacity. Ideal GAD capacity is explicitly separate.
- Optical rates are bits per mode; energy is mean photons per mode. Compare
  against time sharing with optimized fractions AND powers.
- Transport assignment formulas use a uniform square source and three atoms,
  with `0 < m < 1`, `0 <= b <= min(m, 1-m)`. Biological transfer is a proposal.
- Reaction nodes are complexes. Repairs use permitted reactions among existing
  complexes in the same linkage class; physical realizability still requires
  domain input. Permanence does not give a rate-independent abundance floor.
- Network samples preserve the labeled simple-graph degree sequence and
  retain state after burn-in. Practical diagnostics are not a mixing proof;
  empirical tail probabilities are Monte Carlo estimates.
- All random seeds and parameters are recorded; existing handoff files remain
  intact. Outputs are finite JSON, editable text, figures, and a portable PDF.

## Success

Run the new suite and the complete demo command, inspect the figures and PDF,
commit and push the continuation, verify its remote SHA and ancestry, and
explain the strongest findings with their practical significance.
