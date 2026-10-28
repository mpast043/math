import HydrogenPathway.Statements
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

namespace HydrogenPathway

/-- Incoherent click dilution. The equation for `Fclick` is an explicit
instrument assumption: target true-click mass is `p*S`, and total mass is `S+B`.
The background contributes no target mass in this conservative model. -/
theorem actual_click_bound : ClickStatement := by
  intro L p S s0 B b Fclick hL hL1 hLp hp1 hs0 hS hB hBb hclick
  have hp : 0 ≤ p := le_trans hL hLp
  have hS0 : 0 ≤ S := le_trans hs0.le hS
  have hb : 0 ≤ b := le_trans hB hBb
  have hden : 0 < S + B := by linarith
  have hden0 : 0 < s0 + b := by linarith
  have hmass : L * s0 ≤ p * S := mul_le_mul hLp hS hs0.le hp
  have hsignal := mul_le_mul_of_nonneg_right hLp (mul_nonneg hs0.le hS0)
  have hbackground : L * s0 * B ≤ p * S * b := calc
    L * s0 * B ≤ p * S * B := mul_le_mul_of_nonneg_right hmass hB
    _ ≤ p * S * b := mul_le_mul_of_nonneg_left hBb (mul_nonneg hp hS0)
  rw [hclick]
  apply (div_le_div_iff₀ hden0 hden).2
  nlinarith

/-- Squaring preserves a nonnegative amplitude lower bound. -/
theorem square_bound {a r : ℝ} (ha : 0 ≤ a) (har : a ≤ r) : a ^ 2 ≤ r ^ 2 := by
  have hr : 0 ≤ r := le_trans ha har
  nlinarith [mul_nonneg (sub_nonneg.mpr har) (add_nonneg hr ha)]

/-- This exact rational identity is checked by Lean arithmetic, independently
of any external residual certificate. -/
theorem residual_numeric_exact :
    1 - (294780 / 1000000 : ℝ) ^ 2 = 9131047516 / 10000000000 := by
  norm_num

/-- The rounded-up endpoint is strictly stronger than the exact bound. -/
theorem residual_numeric_below_rounded :
    1 - (294780 / 1000000 : ℝ) ^ 2 < 913105 / 1000000 := by
  norm_num

end HydrogenPathway
