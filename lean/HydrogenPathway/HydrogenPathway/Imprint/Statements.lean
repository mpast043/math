import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Topology.MetricSpace.Basic

/-! Independent scalar/metric interfaces. These definitions do not assert a
matrix trace-norm identity, complete positivity, or a physical hydrogen model. -/

namespace HydrogenPathway.Imprint

noncomputable def whichMode (r : ℝ) : ℝ := Real.sqrt (1 - r ^ 2)
noncomputable def equalPriorGuess (d : ℝ) : ℝ := (1 + d) / 2
noncomputable def flaggedValue (p0 p1 n : ℝ) : ℝ := (n + |p0 - p1|) / 2
noncomputable def stableFloor (d δ0 δ1 : ℝ) : ℝ := max 0 (d - δ0 - δ1)

def ComplementarityStatement : Prop :=
  ∀ (r : ℝ), 0 ≤ r → r ≤ 1 → r ^ 2 + (whichMode r) ^ 2 = 1

def ScaledComplementarityStatement : Prop :=
  ∀ (p r : ℝ), 0 ≤ r → r ≤ 1 →
    (p * r) ^ 2 + (p * whichMode r) ^ 2 = p ^ 2

def AcceptanceStatement : Prop :=
  ∀ (p d : ℝ), 0 ≤ p → p ≤ 1 → 0 ≤ d → d ≤ 1 →
    0 ≤ p * d ∧ p * d ≤ p ∧
    equalPriorGuess (p * d) - 1 / 2 = p * (equalPriorGuess d - 1 / 2) ∧
    equalPriorGuess (p * d) ≤ (1 + p) / 2

/-- `n` models the success-block trace norm. Its two bounds and its connection
to any matrix/operator norm are separate obligations of the caller. -/
def FlaggedAccountingStatement : Prop :=
  ∀ (p0 p1 n : ℝ), 0 ≤ p0 → p0 ≤ 1 → 0 ≤ p1 → p1 ≤ 1 →
    |p0 - p1| ≤ n → n ≤ p0 + p1 →
    |p0 - p1| ≤ flaggedValue p0 p1 n ∧
    flaggedValue p0 p1 n ≤ max p0 p1 ∧ flaggedValue p0 p1 n ≤ 1

def FlaggedGuessStatement : Prop :=
  ∀ (p0 p1 n : ℝ), 0 ≤ p0 → p0 ≤ 1 → 0 ≤ p1 → p1 ≤ 1 →
    |p0 - p1| ≤ n → n ≤ p0 + p1 →
    (1 + |p0 - p1|) / 2 ≤ equalPriorGuess (flaggedValue p0 p1 n) ∧
    equalPriorGuess (flaggedValue p0 p1 n) ≤ (1 + max p0 p1) / 2

def PosteriorStatement : Prop :=
  ∀ (p0 p1 : ℝ), 0 ≤ p0 → 0 ≤ p1 → 0 < p0 + p1 →
    0 ≤ p0 / (p0 + p1) ∧ 0 ≤ p1 / (p0 + p1) ∧
    p0 / (p0 + p1) + p1 / (p0 + p1) = 1 ∧
    (p0 / (p0 + p1) = 1 / 2 ↔ p0 = p1)

def MetricStabilityStatement : Prop :=
  ∀ (E : Type) [PseudoMetricSpace E] (a0 a1 m0 m1 : E) (δ0 δ1 : ℝ),
    0 ≤ δ0 → 0 ≤ δ1 → dist a0 m0 ≤ δ0 → dist a1 m1 ≤ δ1 →
    stableFloor (dist m0 m1) δ0 δ1 ≤ dist a0 a1

/-- The metric, model-distance equation, and operational guessing equation are
explicit inputs. Instantiating the metric as normalized flagged trace distance
is not proved by this statement. -/
def StableFlaggedGuessStatement : Prop :=
  ∀ (E : Type) [PseudoMetricSpace E] (a0 a1 m0 m1 : E)
    (p r δ0 δ1 g : ℝ),
    0 ≤ p → p ≤ 1 → 0 ≤ r → r ≤ 1 → 0 ≤ δ0 → 0 ≤ δ1 →
    dist m0 m1 = p * r → dist a0 m0 ≤ δ0 → dist a1 m1 ≤ δ1 →
    g = equalPriorGuess (dist a0 a1) →
    equalPriorGuess (stableFloor (p * r) δ0 δ1) ≤ g

end HydrogenPathway.Imprint
