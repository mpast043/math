# Conditional hydrogen pathway

This small standalone Lake project formalizes a conditional logical spine. It
does not certify a hydrogen source, transport channel, capture process, or
detector. No manuscript or private certificate is included.

The project uses Lean `leanprover/lean4:v4.34.1` and Mathlib commit
`d13f23b723b8a846827a245b89c10fc7d3f11612`, matching `../lean-toolchain`
and the parent project's Mathlib pin. It intentionally does not depend on the
parent library's other research packages. Its manifest pins all transitive
Lean dependencies.

## Mathematical interface

For unit vectors `x`, `y`, `t` in a complex inner product space and real
`0 ≤ e < 1`, `0 ≤ O ≤ 1`, define

```
A(e,O) = max 0 (O * sqrt(1-e²) - e * sqrt(1-O²))
L(e,O) = A(e,O)²
```

The overlap premises are amplitude bounds:

```
sqrt(1-e²) ≤ ‖⟪x,y⟫‖       O ≤ ‖⟪t,y⟫‖.
```

`overlap_bound` concludes `A(e,O) ≤ ‖⟪t,x⟫‖`.
`projection_bound` concludes `L(e,O) ≤ ‖P x‖²` when the explicitly supplied
continuous complex linear map `P` is self-adjoint, idempotent, and fixes `t`.
The result applies in Hilbert spaces; completeness is not needed for this
inequality. The proof derives the perpendicular-component estimates and does
not assume the desired projection lower bound.

`residual_normalization` prepends the relative residual-ball interface:

```
Y ≠ 0,  0 ≤ e < 1,  ‖X-Y‖ ≤ e*‖Y‖
  ⇒ X ≠ 0 and sqrt(1-e²) ≤ ‖⟪X/‖X‖, Y/‖Y‖⟫‖.
```

This does not identify Hilbert distance with sine error. In particular,
`‖x-y‖ ≤ e` is a different premise, and no mixed-state trace-distance theorem
is delivered. Norms of inner products are amplitudes; their squares are
squared overlaps. A projection probability is a single observable's
probability and is not full reduced-state trace-distance control.

`actual_click_bound` takes the named scalar hypotheses
`0 ≤ L ≤ p ≤ 1`, `0 < s0 ≤ S`, `0 ≤ B ≤ b`, and

```
Fclick = p*S/(S+B)
```

and proves `L*s0/(s0+b) ≤ Fclick`. The equation is the external assumption
of incoherently additive signal and false-click masses, with target true-click
mass `p*S`. It is not inferred from a source-state overlap.
`conditional_click_endpoint` composes this theorem with the projection result
under the explicit instrument equation with `p = ‖P x‖²`.
`residual_click_endpoint` additionally composes the residual-ball normalization
step with this conditional endpoint.

## Assumption ledger

| Layer | Status and required input |
| --- | --- |
| Generic Hilbert geometry | Kernel-checked conditional theorem |
| Scalar click arithmetic | Kernel-checked conditional theorem |
| Relative residual estimate | Caller supplies `‖X-Y‖ ≤ e*‖Y‖`; Lean derives normalized amplitude bound |
| Reference-target overlap | Caller supplies amplitude `O ≤ ‖⟪t,y⟫‖`; squared overlap must not be substituted without conversion |
| Operators and domains | Caller supplies bounded complex linear `P`, self-adjointness, idempotence, and `Pt=t`; identifying physical unbounded generators and their domains remains external |
| Signal and instrument | Caller supplies positive lower signal mass, nonnegative additive false-click bound, and the displayed equation for `Fclick` |
| Numerical residual certificate | Not imported or validated; the residual inequality is an externally certified assumption |
| Certificate identity | A hash can bind the identity of supplied bytes; it does not prove a residual estimate or its numerical validity |
| Central-source instance | Open: new certificate, normalization convention, and instantiation hypotheses |
| Inherited accepted-state instance | Separate open instantiation; not identified with the central-source certificate |
| Full pathway | Transport, return, capture, efficiency, and detector physics remain open |

No source, operator, domain, or instrument fact is introduced as a global
axiom. Independent proposition definitions live in `Statements.lean`;
solution declarations are checked against them in `Declarations.lean`.
This is a comparator-style declaration and transitive axiom test using the
standard Lean kernel. The external Comparator/nanoda workflow is not claimed.

## Exact numerical regression

Lean arithmetic checks the equality and strict inequality

```
1 - (294780/1000000)² = 9131047516/10000000000 < 913105/1000000.
```

Thus `0.913105` is not a justified lower bound from those rounded data. The
generic endpoint also contains the target overlap and click dilution; it does
not silently set either to its ideal value.

## Build

With the pinned Lean distribution on `PATH`:

```sh
cd lean/HydrogenPathway
MATHLIB_NO_CACHE_ON_UPDATE=1 lake update
lake exe cache get Mathlib.Analysis.InnerProductSpace.Basic Mathlib.Analysis.SpecialFunctions.Sqrt Mathlib.Tactic.NormNum Mathlib.Tactic.Linarith Mathlib.Tactic.Positivity Mathlib.Tactic.Ring
bash scripts/verify.sh
```

Only this standalone project is built. `scripts/verify.sh` preserves the exact
base commit, branch, compiler, Mathlib revision, build output, and transitive
axiom results in `.lake/verification/build-and-axioms.log`. The permitted axioms are
`propext`, `Quot.sound`, and `Classical.choice`; an extra axiom, including a
proof placeholder, fails the test.

## Verification status

The local ARM64 build, independent declaration tests, 15-theorem transitive
axiom audit, exact numeric regressions, source scan, and whitespace checks
passed. See [verification/RESULTS.md](verification/RESULTS.md) and the sanitized
[verification log](verification/build-and-axioms.log) for commands and scope.
The path-scoped GitHub workflow repeats the build and audit on Linux with a
checksum-verified official compiler. Local verification does not assert that
GitHub CI has run; its status is reported on the draft PR.
