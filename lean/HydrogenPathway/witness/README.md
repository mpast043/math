# A specified joint phase witness, conditional on controls

This extension replaces an unspecified optimal measurement with a finite
product measurement in PR #2's toy model. It is a standard quantum-information
calculation, not new physics, an experimental result, or a realized hydrogen
measurement. The branch is stacked on PR #2. PRs #1/#2 and `main` are unchanged.
No physical source certificate is instantiated.

## Observable and all four outcomes

Keep the same equally likely sources `|s⟩=(|0⟩+s|1⟩)/√2`, `s=±1`, and
`V|j⟩=|j⟩A |cj⟩C |uj⟩U`. All environment factors are unit vectors; `U` is
unobserved. Define `kC=⟨c0|c1⟩=r exp(iθ)` and `kU=⟨u0|u1⟩=u exp(iφ)`,
with `r,u∈[0,1]`. Inner products conjugate their first argument. These are
explicit toy assumptions. Orthogonal source modes alone give equal mode
populations, not equal pointwise momentum distributions (see PR #2).

Put `d1=exp(-iθ)c1`, so `⟨c0|d1⟩=r` is real. For `r<1`, the normalized
minus vector `h−=(c0−d1)/√(2(1−r))` defines the reflection
`R=I−2|h−⟩⟨h−|`. It is Hermitian, `R²=I`, and
`R c0=exp(-iθ)c1`, `R c1=exp(iθ)c0`. Equivalently its occupied eigenmodes
are `h±=(c0±d1)/√(2(1±r))`. At `r=1` take `R=I`; the minus outcome has
zero probability on the occupied state. At `r=0` set `θ=0` explicitly.

Measure `Xα=exp(-iα)|0⟩⟨1|+exp(iα)|1⟩⟨0|` on the atom and `R` on C.
The four effects are `Ea,b=(I+a Xα)/2 ⊗ (I+b R)/2`, `a,b=±1`. They are
positive projectors summing to identity. The bounded observable
`M=Xα⊗R` has norm one. Directly expanding the two source branches gives

`⟨M⟩s=s t`, `t=Re[exp(i(θ−α))kU]`,

`Prs(a,b)=(1+b r)(1+s a b t)/4`.

Thus `Pr(b)=(1+b r)/2` is label-independent. **Retain both photon outcomes**
and guess `s=a*b`. Then `Prs(w)=(1+s w t)/2`, contrast is `t`, and the
fixed decoder succeeds with `(1+t)/2`. At a known aligned phase
`α=θ+φ`, it attains `(1+u)/2`, the ideal AC optimum from PR #2.
Atom-only readout of the **same** `Xα` has contrast `r t` and guess
`(1+r t)/2`. The baseline is also optimal atom-only at exact alignment.

The apparatus must know/calibrate `θ+φ`. With actual phase offset `δ`,
`t=u cos δ`. The code reports the fixed decoder, including success below
one half for a wrong phase; the separately labeled best relabeling is not
silently substituted. At `kU=0` there is no phase signal and `φ=0` is a
convention. If only `|δ|≤Δ` is certified, `cos δ≥1−Δ²/2` gives a sufficient
bound; no phase knowledge gives no uniformly positive fixed-witness guarantee.

## Losses, complete records and a fair baseline

Let capture probability `p`, atomic readout efficiency `ηA`, and photon
readout efficiency `ηC` be **independent of label, local outcome and state**.
This includes a scalar no-click effect on the occupied photon support, and
unchanged atomic readout when the photon is missing. Set `qA=p ηA` and
`qJ=p ηA ηC`. The factors multiply only under these independence premises.

For the coincidence protocol, true four-outcome effects are `qJ Ea,b`.
Capture failure, atomic no-click and photon no-click have probabilities
`1−p`, `p(1−ηA)`, `p ηA(1−ηC)`. Each erasure gets a fair random guess;
none is dropped. The script also constructs a complete positive POVM with
these effects. A finite positive POVM admits Kraus operators `√E`; this is
an abstract measurement construction, not a hardware implementation.

Independent symmetric readout flips give visibility `vA` for the atomic
record and `vC` for the photon bit, so `vJ=vA vC≤vA`. True contrasts are
`cA=vA r t`, `cJ=vJ t`. The code requires `vJ≤vA`; the two protocols share
the atomic readout. With perfect visibility and no false accepts,

`Gcoinc−Gatom = qA*u*cosδ*(ηC−r)/2`.

For positive `t` and nonzero `qA`, coincidence-only needs `ηC>r`. Having
more allowed access cannot worsen an optimum (one can ignore C), but this
particular fixed coincidence protocol can be worse than atom-only.

A stronger **hybrid** uses the same atomic result even without a photon:
if a photon is detected, guess `a*b`; otherwise guess `a`. Its true signed
bias is `qJ cJ+(qA−qJ)cA`. At perfect visibility its advantage is

`Ghybrid−Gatom = qJ*t*(1−r)/2`.

This counts every attempt and is positive for `qJ>0,t>0,r<1`, even when
`ηC≤r`. It requires an atomic record without a photon herald. A hydrogen
setup that cannot provide this record does not implement the hybrid.
The POVM includes two fallback atomic outcomes with weights
`(qA−qJ)(I+a Xα)/2⊗I` (or the noisy atomic effects); only capture/atom
failure remains an unscored erasure. `loss_povm` checks positivity and
completeness with the same atomic noise for both protocols.

## False accepts and direct observable error budgets

`bJ,bA,bH` are **unconditional per-attempt** false-accept rates, disjoint
from true events. For coincidence require `qJ+bJ≤1`; atom/hybrid require
`qA+b≤1`. The response model replaces a fraction `b/(1−q)` of otherwise
failed attempts with false guesses, preserving the remaining distinct
failure flags. False signed contrasts `f∈[−1,1]` may be adversarial:

`GJ=(1+qJ cJ+bJ fJ)/2`, `GA=(1+qA cA+bA fA)/2`,

`GH=(1+qJ cJ+(qA−qJ)cA+bH fH)/2`.

Arbitrary source-correlated false responses are a conservative classical
uncertainty envelope; the code does not assert that every extreme is a
photon-only quantum instrument. A label-independent false source has `f=0`.
Source-dependent capture/detection or no-click probabilities require their
full conditional response tables, not these scalar efficiencies. In
particular, a zero-rate accepted ensemble is never assigned a posterior.
All reported guessing probabilities use equal **input** priors, without
renormalizing the click subset.

For the specified observable, let per-label expectation errors be
`|m+−vJ*u*z|≤ε+`, `|m−+vJ*u*z|≤ε−`, where `z≥1−c` is a separately
certified phase factor. Then the signed contrast `(m+−m−)/2` is at least
`LJ=vJ*u*(1−c)−εJ`, with `εJ=(ε++ε−)/2`. This uses direct expectation
bounds, not a full trace-distance assumption. An atom upper bound
`UA=r*u+εA` even allows the ideally phased atom-only baseline.

The sufficient coincidence certificate is

`qJ*LJ−qA*UA−bJ−bA > 0`.

Its half is a lower bound on `GJ−GA`. If `qA>0,LJ>0`, this is equivalent
to `ηC > [UA+(bJ+bA)/qA]/LJ`. A threshold above one is infeasible.
For the hybrid with the shared actual atomic contrast, a sufficient bound is

`GH−GA ≥ [qJ*(LJ−UA)−bH−bA]/2`.

The Python `eps` inputs are supplied tolerance allowances, not estimates
learned from data: the generated response uses the displayed ideal/noisy
model; its robustness claims remain conditional on those expectation bounds.
The analytic cosine bound is not formalized in Lean; Lean takes `z≥1−c`
as an explicit input. Floating-point checks are not certified intervals.

## Outcome-selective detection and the minus-port certificate

The independence premise matters. With photon-port efficiencies `η+,η−`,
a compatible instrument has `Kb=√ηb Πb` and
`Kempty=√(1−η+)Π+ + √(1−η−)Π−`. These Kraus operators are complete;
the no-click effect is generally not scalar. Keeping the same atom record,
only a detected **minus** port changes the guess. With ideal controls,

`Ghybrid−GA=qA*η−*(1−r)*t/2`,

while total photon rate is `qA[η+(1+r)+η−(1−r)]/2`.
For `r=.6,u=.8,η+=1,η−=0,qA=1`, photon rate is `.8` and gain is zero;
plugging that rate into the scalar-erasure formula would incorrectly give
`.128`. This is an explicit regression, not an efficiency estimate.

A more general, unnormalized certificate avoids conditioning on a rare or
zero minus event. For source sign `s` and atomic guess `a`, let
`H=−E[s*a*1(genuine minus flip)]≥gMinus*L` and let the false/wrong-port
contribution `W≥−fMinus`. Let added-apparatus atomic signed bias degrade
by at most `dA`. Then

`Ghybrid−GA ≥ gMinus*L−fMinus−dA/2`.

The flip event classes must be disjoint and every no-click/positive-port
record keeps the baseline guess. At ideal controls
`gMinus=qA η−(1−r)/2`, `L=t`. No conditional expectation is used when
`gMinus=0`. Lean proves this bookkeeping implication from the named signed
correlations and response equations; their experimental bounds remain open.

## Illustrative budget and the hydrogen gap

**Illustrative only:** `r=.4,u=.8,p=.2,ηA=.9,ηC=.85,vJ=.95,vA=1,Δ=.1`,
`εJ=.02,εA=.01,bJ=bH=.002,bA=.001`. With worst false signs,
`LJ=.7362,UA=.33`. The coincidence efficiency threshold is about `.470887`.
The guaranteed guessing advantages are `.0251193` (coincidence) and
`.0295743` (hybrid); Lean checks those exact rational budget values.
The generated model gives about `.0276934` and `.0319918`, respectively.
These are probabilities above the atom baseline, not efficiencies or a
prediction for hydrogen. PR #1's fidelity threshold is unrelated here.

To implement this for hydrogen, still needed are two admissible source
preparations; their capture instrument, yields and accepted output errors;
atomic interferometric recombination of the two accepted modes and stable
phase calibration; coherent collected-photon mode mixing into `h±` and
resolution of **both** ports; detector response including false/wrong-port
events; and atomic records without a photon if the hybrid is proposed.
Time/frequency/spatial mode mismatch and unobserved recoil may change these
requirements. Photon counting in an arbitrary existing basis is not this
reflection measurement, and the code supplies no control pulse sequence.

Also, `ej=cj⊗uj` is an environment-factorization toy, not generically one
photon split into collected and lost paths. A one-photon collection model
instead typically has branches like
`√η|cj⟩C|vac⟩U+√(1−η)|vac⟩C|uj⟩U`, possibly with recoil/environment
factors. Its detected/missed atom states must be derived from the actual
instrument. Adding scalar erasure to this factorized toy does not establish
that bridge. No actual hydrogen yield, coupling or efficiency is certified.

## Checked scope and reproduction

From `lean/HydrogenPathway` with the pinned Lean on `PATH`:

```sh
bash scripts/verify-witness.sh
python3 witness/model.py --check --output witness/RESULTS.json
```

The standard-library matrix calculation tests 13 cases/groups, including 160
complex/endpoint/phase combinations, positive complete product/loss POVMs,
wrong-phase decoding, false extremes, full erasure tables, rare successes,
hybrid fallback and the outcome-dependent-efficiency counterexample.
`RESULTS.json` contains eight labeled scenarios plus the counterexample.

Eleven Lean theorems check four scalar outcome weights, full-response
normalization/guessing, expectation perturbations, calibration consequences,
loss/false bounds, coincidence and hybrid advantage, efficiency threshold,
minus-port accounting, and the exact illustrative budget. Declaration tests
use separate expected propositions and audit transitive axioms against only
`propext`, `Classical.choice`, `Quot.sound`. No custom axioms or proof holes.
The matrix/PVM/Kraus realization, trigonometric bound, Helstrom optimum,
and physical apparatus are not formalized in Lean. Source hashes identify
these files; they do not validate numerical arithmetic or physical inputs.

Standard background: Watrous, *The Theory of Quantum Information*,
[Chapter 2](https://cs.uwaterloo.ca/~watrous/TQI/TQI.2.pdf) for finite
measurements/channels and [Theorem 3.4](https://cs.uwaterloo.ca/~watrous/TQI/TQI.3.pdf)
for binary state discrimination. The formulas here are direct derivations
for the specified toy and measurement restrictions.
