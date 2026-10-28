import HydrogenPathway.Imprint.Statements

/-! Scalar response statements only. The finite matrix realization and the
physical meaning of every parameter must be checked separately. -/
namespace HydrogenPathway.Witness

noncomputable def scoreGuess (c : ℝ) : ℝ := (1 + c) / 2
noncomputable def contrast (mplus mminus : ℝ) : ℝ := (mplus - mminus) / 2
noncomputable def jointWeight (r t a b : ℝ) : ℝ := (1 + b * r) * (1 + a * b * t) / 4
noncomputable def margin (qj qa lj ua bj ba : ℝ) : ℝ := qj * lj - qa * ua - bj - ba

/-- `t` includes the source sign. All four photon/atom outcomes are kept. -/
def OutcomeLawStatement : Prop :=
  ∀ (r t : ℝ), 0 ≤ r → r ≤ 1 → -1 ≤ t → t ≤ 1 →
    0 ≤ jointWeight r t 1 1 ∧ 0 ≤ jointWeight r t 1 (-1) ∧
    0 ≤ jointWeight r t (-1) 1 ∧ 0 ≤ jointWeight r t (-1) (-1) ∧
    jointWeight r t 1 1 + jointWeight r t 1 (-1) +
      jointWeight r t (-1) 1 + jointWeight r t (-1) (-1) = 1 ∧
    jointWeight r t 1 1 - jointWeight r t 1 (-1) -
      jointWeight r t (-1) 1 + jointWeight r t (-1) (-1) = t

/-- Each row is a complete per-attempt response for one source label.
Erasures receive a fair random guess, without conditioning on acceptance. -/
def ResponseGuessStatement : Prop :=
  ∀ (pp pm mp mm ep em : ℝ),
    0 ≤ pp → 0 ≤ pm → 0 ≤ mp → 0 ≤ mm → 0 ≤ ep → 0 ≤ em →
    pp + pm + ep = 1 → mp + mm + em = 1 →
    let g := (pp + mm) / 2 + (ep + em) / 4
    g = scoreGuess (contrast (pp - pm) (mp - mm)) ∧ 0 ≤ g ∧ g ≤ 1

/-- Direct errors on expectations of the specified bounded observable.
No trace-norm premise or metric instance is used. -/
def ContrastErrorStatement : Prop :=
  ∀ (mp mm target εp εm : ℝ),
    |mp - target| ≤ εp → |mm + target| ≤ εm →
    |contrast mp mm - target| ≤ (εp + εm) / 2

/-- `z` is the measured phase cosine, with separately supplied calibration
cost `c`. Visibility and coherence are nonnegative. -/
def CalibrationStatement : Prop :=
  ∀ (mp mm v u z c εp εm : ℝ),
    0 ≤ v → 0 ≤ u → 1 - c ≤ z →
    |mp - v * u * z| ≤ εp → |mm + v * u * z| ≤ εm →
    v * u * (1 - c) - (εp + εm) / 2 ≤ contrast mp mm

/-- Disjoint true/false events; unscored erasures are already included in g.
False contrast may depend adversarially on the source label. -/
def LossBoundsStatement : Prop :=
  ∀ (q b c f g : ℝ), 0 ≤ q → 0 ≤ b → q + b ≤ 1 →
    -1 ≤ c → c ≤ 1 → -1 ≤ f → f ≤ 1 →
    g = scoreGuess (q * c + b * f) →
    0 ≤ g ∧ g ≤ 1 ∧ (1 + q * c - b) / 2 ≤ g ∧
    g ≤ (1 + q * c + b) / 2

def AdvantageStatement : Prop :=
  ∀ (qj qa bj ba cj ca fj fa lj ua gj ga : ℝ),
    0 ≤ qj → 0 ≤ qa → 0 ≤ bj → 0 ≤ ba →
    lj ≤ cj → ca ≤ ua → -1 ≤ fj → fa ≤ 1 →
    gj = scoreGuess (qj * cj + bj * fj) →
    ga = scoreGuess (qa * ca + ba * fa) →
    margin qj qa lj ua bj ba / 2 ≤ gj - ga ∧
    (0 < margin qj qa lj ua bj ba → ga < gj)

def EfficiencyThresholdStatement : Prop :=
  ∀ (p ea ec r u : ℝ), 0 < p → 0 < ea → 0 < u →
    scoreGuess (p * ea * ec * u) - scoreGuess (p * ea * r * u) =
      p * ea * u * (ec - r) / 2 ∧
    (scoreGuess (p * ea * r * u) < scoreGuess (p * ea * ec * u) ↔ r < ec)

/-- Same atomic readout on photon erasure, and state/outcome-independent
photon detection, are needed to supply the shared `ca` in both equations. -/
def HybridAdvantageStatement : Prop :=
  ∀ (qj qa bh ba cj ca fh fa lj ua gh ga : ℝ),
    0 ≤ qj → qj ≤ qa → 0 ≤ bh → 0 ≤ ba →
    lj ≤ cj → ca ≤ ua → -1 ≤ fh → fa ≤ 1 →
    gh = scoreGuess (qj * cj + (qa - qj) * ca + bh * fh) →
    ga = scoreGuess (qa * ca + ba * fa) →
    (qj * (lj - ua) - bh - ba) / 2 ≤ gh - ga ∧
    (0 < qj * (lj - ua) - bh - ba → ga < gh)

def HybridIdealStatement : Prop :=
  ∀ (qa qj r t : ℝ),
    scoreGuess (qj * t + (qa - qj) * r * t) - scoreGuess (qa * r * t) =
      qj * t * (1 - r) / 2 ∧
    (0 < qj → 0 < t → r < 1 →
      scoreGuess (qa * r * t) < scoreGuess (qj * t + (qa - qj) * r * t))

/-- Unnormalized flip accounting: H is minus the source/atom signed
correlation on genuine minus-port events; W is its wrong/false-flip counterpart.
No conditional expectation is needed when the genuine event has zero rate. -/
def MinusPortStatement : Prop :=
  ∀ (g L f d bnew bold H W gh ga : ℝ),
    bold - d ≤ bnew → g * L ≤ H → -f ≤ W →
    gh = scoreGuess bnew + H + W → ga = scoreGuess bold →
    g * L - f - d / 2 ≤ gh - ga ∧
    (0 < g * L - f - d / 2 → ga < gh)


def IllustrativeBudgetStatement : Prop :=
  let lj : ℝ := (95 / 100) * (8 / 10) * (1 - 1 / 200) - 2 / 100
  let ua : ℝ := (4 / 10) * (8 / 10) + 1 / 100
  let qj : ℝ := (2 / 10) * (9 / 10) * (85 / 100)
  let qa : ℝ := (2 / 10) * (9 / 10)
  margin qj qa lj ua (2 / 1000) (1 / 1000) / 2 = 251193 / 10000000 ∧
    0 < margin qj qa lj ua (2 / 1000) (1 / 1000) ∧
    (qj * (lj - ua) - 2 / 1000 - 1 / 1000) / 2 = 295743 / 10000000 ∧
    0 < qj * (lj - ua) - 2 / 1000 - 1 / 1000

end HydrogenPathway.Witness
