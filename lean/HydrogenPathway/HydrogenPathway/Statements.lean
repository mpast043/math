import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-! Independent statement definitions used by the declaration tests.
No solution module is imported here. Inner products are complex amplitudes;
their squared norms and squared projection norms are probabilities. -/

namespace HydrogenPathway

noncomputable def amplitudeFloor (e O : ℝ) : ℝ :=
  max 0 (O * Real.sqrt (1 - e ^ 2) - e * Real.sqrt (1 - O ^ 2))

noncomputable def probabilityFloor (e O : ℝ) : ℝ := (amplitudeFloor e O) ^ 2

def OverlapStatement : Prop :=
  ∀ (E : Type) [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (x y t : E) (e O : ℝ),
    ‖x‖ = 1 → ‖y‖ = 1 → ‖t‖ = 1 →
    0 ≤ e → e < 1 → 0 ≤ O → O ≤ 1 →
    Real.sqrt (1 - e ^ 2) ≤ ‖inner ℂ x y‖ →
    O ≤ ‖inner ℂ t y‖ →
    amplitudeFloor e O ≤ ‖inner ℂ t x‖

def ProjectionStatement : Prop :=
  ∀ (E : Type) [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (x y t : E) (P : E →L[ℂ] E) (e O : ℝ),
    ‖x‖ = 1 → ‖y‖ = 1 → ‖t‖ = 1 →
    (∀ u v, inner ℂ (P u) v = inner ℂ u (P v)) →
    (∀ u, P (P u) = P u) → P t = t →
    0 ≤ e → e < 1 → 0 ≤ O → O ≤ 1 →
    Real.sqrt (1 - e ^ 2) ≤ ‖inner ℂ x y‖ →
    O ≤ ‖inner ℂ t y‖ →
    probabilityFloor e O ≤ ‖P x‖ ^ 2

def ResidualStatement : Prop :=
  ∀ (E : Type) [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (X Y : E) (e : ℝ),
    Y ≠ 0 → 0 ≤ e → e < 1 → ‖X - Y‖ ≤ e * ‖Y‖ →
    X ≠ 0 ∧ Real.sqrt (1 - e ^ 2) ≤
      ‖inner ℂ ((‖X‖⁻¹ : ℂ) • X) ((‖Y‖⁻¹ : ℂ) • Y)‖

def ClickStatement : Prop :=
  ∀ (L p S s0 B b Fclick : ℝ),
    0 ≤ L → L ≤ 1 → L ≤ p → p ≤ 1 →
    0 < s0 → s0 ≤ S → 0 ≤ B → B ≤ b →
    Fclick = (p * S) / (S + B) →
    L * s0 / (s0 + b) ≤ Fclick

def EndpointStatement : Prop :=
  ∀ (E : Type) [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (x y t : E) (P : E →L[ℂ] E) (e O S s0 B b Fclick : ℝ),
    ‖x‖ = 1 → ‖y‖ = 1 → ‖t‖ = 1 →
    (∀ u v, inner ℂ (P u) v = inner ℂ u (P v)) →
    (∀ u, P (P u) = P u) → P t = t →
    0 ≤ e → e < 1 → 0 ≤ O → O ≤ 1 →
    Real.sqrt (1 - e ^ 2) ≤ ‖inner ℂ x y‖ →
    O ≤ ‖inner ℂ t y‖ →
    0 < s0 → s0 ≤ S → 0 ≤ B → B ≤ b →
    Fclick = (‖P x‖ ^ 2 * S) / (S + B) →
    probabilityFloor e O * s0 / (s0 + b) ≤ Fclick

def ResidualEndpointStatement : Prop :=
  ∀ (E : Type) [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (X Y t : E) (P : E →L[ℂ] E) (e O S s0 B b Fclick : ℝ),
    Y ≠ 0 → ‖t‖ = 1 →
    (∀ u v, inner ℂ (P u) v = inner ℂ u (P v)) →
    (∀ u, P (P u) = P u) → P t = t →
    0 ≤ e → e < 1 → 0 ≤ O → O ≤ 1 →
    ‖X - Y‖ ≤ e * ‖Y‖ →
    O ≤ ‖inner ℂ t ((‖Y‖⁻¹ : ℂ) • Y)‖ →
    0 < s0 → s0 ≤ S → 0 ≤ B → B ≤ b →
    Fclick = (‖P ((‖X‖⁻¹ : ℂ) • X)‖ ^ 2 * S) / (S + B) →
    probabilityFloor e O * s0 / (s0 + b) ≤ Fclick

end HydrogenPathway
