# Operational quantum-to-classical boundary

This extension proves a finite complex-matrix boundary between coherent states
and their block-dephased statistics. Retaining global alternatives is not a
failure. The goal is stable, consistent relative records for specified access,
not selection of exactly one global outcome. The work is conditional linear
algebra and finite probability accounting, not a new physical law, an
interpretation of quantum mechanics, or a hydrogen apparatus certificate.
The branch stacks on verified PR #3; main and PRs #1–#3 are unchanged.

## Exact matrix result

For finite square matrices define `pinch P X = Σj Pj X Pj`. Lean proves

`Tr(M pinch(P,X)) = Tr(pinch(P,M) X)`.

It then proves `pinch(P,M)=M` from the concrete hypotheses `Pj²=Pj`,
`Σj Pj=I`, and `M Pj=Pj M`. Combining these yields

`Tr(M ρ) = Tr(M pinch(P,ρ))`.

The proof expands finite matrix sums and uses trace cyclicity; the trace
identity is not supplied as a premise. The algebra needs neither positivity
nor orthogonality, so complete idempotents suffice. Mutually orthogonal
Hermitian pointer projections are the physical special case. Their
self-adjointness/orthogonality, the state being PSD with trace one, and every
measurement effect satisfying `0≤M≤I` are separate requirements for the
Born-probability interpretation. The Lean theorem is deliberately stronger
as an algebraic statement, and does not certify any supplied apparatus effect.
Applied separately to every effect of a specified finite measurement, it gives
identical outcome distributions. Commutation is sufficient, not necessary:
a noncommuting effect may still have zero state-specific trace difference.

A separate coordinate version uses `blockDelta label X` with entry `Xij`
when `label i=label j`, and zero otherwise. It preserves trace and is
idempotent. Matrices with no entries between distinct labels have equal
traces on `ρ` and this dephasing. Coarse labels retain **within-block quantum
coherence**; only distinct-label interference is removed. This coordinate
map is the pinching by the corresponding diagonal label projectors; that
identification is explained here, while the two Lean results are proved
independently rather than relying on an unproved basis-conversion lemma.

The full state need not equal its dephasing. For `ρ=|+⟩⟨+|`, diagonal effects
give the same statistics as `I/2`, yet the effect `|+⟩⟨+|` gives probabilities
`1` and `1/2`; trace distance is `1/2`. Allowing a coherent Hadamard control
before a diagonal measurement changes the effective Heisenberg effect and
restores this distinction. The instantaneous boundary alone proves no
persistence against later controls or dynamics.

## Checked approximate bound

Direct trace expansion and two finite triangle inequalities give the exact
identity and sufficient bound

`Tr(Mρ)−Tr(M blockDelta(ρ)) = Σi,j:label i≠label j Mij ρji`,

`|Tr(Mρ)−Tr(M blockDelta(ρ))| ≤ Σi,j:label i≠label j |Mij| |ρji|`.

Complex absolute values are complex norms. No spurious factor `1/2` appears.
This is a basis-dependent **entrywise** bound, not the operator-norm times
trace-norm Hölder inequality. The stronger norm statement and general
basis-conversion machinery are not formalized or claimed here.

## Local access after branch encoding

Lean constructs the actual rectangular matrix
`W_(i,e),j = [i=j] Ej(e)` and local lift `(M⊗I)_(i,e),(j,f)=[e=f] Mij`.
Writing `Gjk=Σe conj(Ej(e)) Ek(e)`, it proves

`[W†(M⊗I)W]jk = Mjk Gjk`.

Unit diagonal Gram entries imply `W†W=I`; thus normalized environment
vectors give a branch isometry. A second actual matrix trace identity relates
measurement on `WρW†` to its compressed effect. If every off-diagonal `Gjk`
vanishes, **every local atom matrix M**, including `X`, has the same trace
on the coherent encoding and the encoding of the branch-dephased input.
Losing environmental access does not forbid atom interference measurements;
the inaccessible overlaps suppress their branch matrix elements.

A quantitative theorem also proves

`|Tr[(M⊗I)W(ρ−blockDelta_id(ρ))W†]| ≤ Σj≠k |Mjk| |Gjk| |ρkj|`.

This finite entrywise consequence is genuine matrix algebra in Lean. It
requires no assumption of its own conclusion. Physical effect admissibility
and a normalized encoded state still require the conditions above.
Compression is not generally multiplicative: with orthogonal environment
records, `W†(X⊗I)W=0` but `W†(X²⊗I)W=I`. The code tests this, and does not
assume compressed accessible effects form an algebra.

## Relative-record errors without independence

For nonnegative finite weights and an explicitly named condition `C` of
positive weight, define conditional probabilities by division by that weight.
If a failure event is contained in `A∪B`, Lean proves

`Pr(failure | C) ≤ Pr(A | C)+Pr(B | C)`.

Apply this to a later record, its initial value and the target label:

`Pr(later≠target | C) ≤ Pr(initial≠target | C)+Pr(later≠initial | C)`.

The target is a specified calibration/reference variable or relative-record
label, not an assumed hidden pointer value in a coherent preparation.
No independence, product state, or exponential improvement is assumed. The
weights need not already sum to one because conditioning normalizes them.
A zero-weight condition is excluded. An erasure can be included as an
explicit record value; any conditioning or attempt selection must be named.
Consistently copying a shared wrong decision does not improve source accuracy.
A storage-time change bound must be supplied separately; neither record
agreement nor the instantaneous trace theorem proves a lifetime.

## Verification and supplement provenance

Sixteen named Lean theorems have separate statement interfaces and declaration
checks. Transitive axiom audits allow only `propext`, `Classical.choice`, and
`Quot.sound`; proof modules contain no placeholders/custom axioms. Twelve
standard-library numerical tests cover rotated projections, 40 complex matrix
pairs, constant/injective/coarse labels, tight complex bounds, non-density
matrices, retained coherence, later controls, rectangular compression and
conditional/correlated record errors. Numerical tolerance is `2e-9`, not an
interval certificate. The declarations include the exact non-density trace
regression `Tr(diag(5,6) [[1,2],[3,4]])=29`.

The authorized project supplement was materialized to this Mac through the
current Library transfer route, with readable bytes and metadata verified:

- `Quantum_Classical_Records_Bridge_2026-10-28.zip`, version 1, 15435 bytes.
- Library ID `libfile_c46d65898a00819186320a4544fcdd6c`.
- SHA256 `b83d5013423f99a753f13cbb724cd807081e7497099d76c8cdbb57ba13af0082`.

Four selected files in `supplement/` retain their exact original archive bytes:
two NumPy scripts and their results. Originally 29 bridge checks were
independently rerun, while the 40 single-photon checks had only the original
primary run. **This executor now reran both: 29+40 passed**, using existing
NumPy 2.4.2 without installing software. New reports are separately retained
in `supplement-rerun/`; `PROVENANCE.json` records identities and hashes. These
69 checks remain floating-point evidence, not Lean proofs or certificates.
Only selected relevant project-authored material is published; no old private
manuscript is included. The original supplement's broader amplifier,
fragment-independence and single-photon models are not all formalized here.

The required CI uses standard-library numerical tests and Lean. It validates
the original/rerun report provenance and source hashes; it **does not claim to
execute the NumPy supplement in CI**. To rerun that optional evidence with an
existing NumPy installation, copy the two scripts to a scratch directory and
run each there (they write adjacent results), preserving the original reports.

From `lean/HydrogenPathway`, with pinned Lean 4.34.1 on PATH:

```sh
bash scripts/verify-operational.sh
python3 operational/model.py --check --output operational/RESULTS.json
```

`VERIFICATION.md`, `verification.log`, source hashes, and the final draft PR's
CI links record exact scope. Hashes bind identity, not physical or numerical
validity. Remaining physical bridges are the accessible effect set and its
controls, normalized source preparations, photon instrument, hydrogen source
and capture, record storage dynamics and uniform stability over a time window.
No biology analogy or subjective-experience claim is part of this PR.
