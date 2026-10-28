# Two-source phase imprint: a controlled finite model

This is a standard illustrative quantum-information calculation, not a novel
law, experimental result, or established hydrogen channel. It extends the
pinned project from PR #1 on a separate stacked branch; that PR is unchanged.
Python uses only the standard library. Lean checks the scalar/metric lemmas
listed below, not the matrix spectral or trace-class results.

## Sources and isometry

Use orthogonal modes `|0⟩,|1⟩` and `|±⟩=(|0⟩±|1⟩)/√2`. Their **mode
populations** coincide. Equal pointwise momentum distributions additionally
require, for example, mode functions with disjoint momentum support. Merely
orthogonal overlapping mode functions need not work: the interference term
can differ. Tests include both a disjoint finite momentum-bin construction
and an overlapping orthogonal counterexample. None of these idealized modes
is automatically an admissible preparation for the certified hydrogen source.

Take unit photon states `e0=(1,0)`, `e1=(k,√(1−|k|²))`, with `|k|≤1` and
`k=⟨e0|e1⟩` (conjugate-linear first argument). Define
`V|j⟩=|j⟩_A|ej⟩_P`. Its columns are orthonormal because the atom modes are
orthogonal, so `V†V=I` for every allowed complex `k`.

The atom states are `ρA±=½[[1,±conj(k)],[±k,1]]`; their difference has
eigenvalues `±|k|`. The photon states are both
`½(|e0⟩⟨e0|+|e1⟩⟨e1|)`. The two joint pure states are orthogonal.
With `D(ρ,σ)=½‖ρ−σ‖₁` and equal source priors:

| Phase-label access | D | Optimal guessing probability |
| --- | --- | --- |
| Atom | `|k|` | `(1+|k|)/2` |
| Photon | `0` | `1/2` |
| Joint atom–photon | `1` | `1` |

For the **different which-mode ensemble** `e0` versus `e1`, photon
distinguishability is `√(1−|k|²)`. The identity between its square and the
atom phase-distance square concerns two different encodings. The three
phase-label marginal distances must not be added as a conserved quantity.
An optimal Helstrom measurement is a mathematical optimum, not an assumed
physically accessible readout. The code checks the correctly phase-rotated
atom POVM for complex `k`.

## Capture instrument and explicit failure

Accessible output space is `(A⊗P) ⊕ span{|f⟩}`, so success and failure have
orthogonal flags. For source-independent yield `p`, the success operator is
`Ks=√p V` embedded in the success block. Failure Kraus operators are
`K+=√(1−p)|f⟩⟨+|`, `K−=√(1−p)|f⟩⟨−|`. Then
`ΣK†K=pI+(1−p)I=I`. A Kraus sum is completely positive; the complete map
is trace-preserving, while the success branch is trace-nonincreasing.

The code also constructs the isometry
`W|±⟩=√p |s,V±⟩|vac⟩+√(1−p)|f⟩|±mem⟩`, where all three memory
states are orthogonal. Thus `W†W=I`. Tracing out this inaccessible memory
gives the Kraus channel. Conditional failure memory states remain orthogonal
when failure occurs, although accessible failure states are identical. Global
preservation of input information does not imply accessible retention.

For the normalized accessible flagged states
`σ±=pρ± ⊕ (1−p)τ`, with common normalized failure state `τ`, blockwise
trace-norm additivity gives `Dflag=p Dsuccess`. Hence flagged distances are
`p|k|,0,p`, and guessing advantages above `1/2` scale with `p`. At `p=0`
there is no conditional success ensemble; the script returns `null`.
For `|k|=.6,p=.25`, the full-attempt atom distance is `.15` and its optimum
guessing probability is `.575`; joint flagged distance is `.25`, despite
perfect distinguishability within the success-only joint ensemble.

For unequal yields, a common valid instrument uses
`A=√p0|+⟩⟨+|+√p1|−⟩⟨−|`, `Ks=VA`, and
`K±=√(1−p±)|f⟩⟨±|`. Orthogonal source projectors again give `ΣK†K=I`.
For any normalized success states `ρ0,ρ1` and **the same normalized** `τ`,

`Dflag = ½(‖p0ρ0−p1ρ1‖₁ + |p0−p1|)`.

This follows from the two orthogonal flag blocks and `‖τ‖₁=1`; it need not
hold for distinct failure states. The success-block norm `n` obeys
`|p0−p1|≤n≤p0+p1`, giving `|p0−p1|≤Dflag≤max(p0,p1)`.
In this particular model, with `r=|k|`, the flagged atom distance is
`½(max(|p0−p1|,(p0+p1)r)+|p0−p1|)`, photon distance is `|p0−p1|`, and
joint distance is `max(p0,p1)`. Yield flags alone can identify the source.

After success, the priors are `qi=pi/(p0+p1)` if the denominator is positive.
The appropriate conditional optimum is
`½(1+‖q0ρ0−q1ρ1‖₁)`, not the equal-prior formula for the conditional pair.
For example, `k=0,p0=1,p1=0` gives identical conditional photon states but
certainty about the accepted label from the prior. The original source priors
are equal throughout the reported full-attempt guessing probabilities.

## Collection and unobserved modes

An explicitly factorized toy variant uses `ei=ci⊗ui`, with unit factors and
overlaps `kC,kU`. The calculation checks
`D_A=|kC*kU|`, `D_C=0`, `D_AC=|kU|`, `D_ACU=1`; equal-yield flagged
`D_AC=p|kU|`. For `kC=.8,kU=.6i,p=.25`, these are `.48,0,.6,1` and `.15`.
Factorization, collection access, and a realizable joint witness remain
additional hypotheses, not facts about the actual source.

## Checked scope and error budget

Eight Lean theorems check: the overlap/which-mode square identity and its
scaled form; equal-acceptance distance/guessing accounting; flagged bounds
from explicit success-block norm bounds; posterior normalization/equality;
and generic metric stability plus its guessing consequence. Independent
declarations and transitive axiom audits permit only `propext`,
`Classical.choice`, and `Quot.sound`. There are no proof placeholders or
new custom axioms.

For normalized outputs in one metric and the same register/flag scope,
`dist(actual_i,model_i)≤δi` implies
`Dactual≥max(0,Dmodel−δ0−δ1)`. Lean proves this from metric triangle
inequalities and composes it with explicit model-distance and operational
guessing equations. Applying it to trace distance requires a trace-distance
metric instance; that matrix/trace-class instantiation is **not** formalized
here. Conditional success errors cannot silently replace full flagged errors.

Missing hydrogen bridges: two admissible preparations (including the momentum
claim), their common capture instrument and source-dependent yields, accepted
joint output errors plus failure behavior, photon collection/resolution and
coarse graining, and a physically realizable readout. This extension does not
instantiate PR #1's endpoint or validate either physical source certificate.

## Reproduce

From `lean/HydrogenPathway`, with the pinned Lean on `PATH`:

```sh
bash scripts/verify-imprint.sh
python3 imprint/model.py --k-real .3 --k-imag .4 --p0 .8 --p1 .2 --check
```

`RESULTS.json` records ten reference cases and the collected-mode example;
floating-point checks use tolerance `2e-9` and are not certified intervals.
`VERIFICATION.md` records scope and commands. No extra numerical package is
needed. This is a stacked extension based on PR #1's branch; merging either
PR is outside this task.

Standard references: Watrous, *The Theory of Quantum Information*,
[Theorem 3.4](https://cs.uwaterloo.ca/~watrous/TQI/TQI.3.pdf) for binary
state discrimination, and
[Theorem 2.22](https://cs.uwaterloo.ca/~watrous/TQI/TQI.2.pdf) for finite
Kraus/Stinespring characterizations. The calculations above are direct
finite-model derivations, not a novelty claim.
