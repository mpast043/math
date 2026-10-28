import HydrogenPathway.Scalar
import Mathlib.Tactic.Ring

namespace HydrogenPathway

section Geometry
variable {E : Type} [NormedAddCommGroup E] [InnerProductSpace ℂ E]

/-- Component perpendicular to the unit reference vector `y`. -/
noncomputable def perpendicular (y v : E) : E := v - inner ℂ y v • y

theorem inner_perpendicular (y v : E) (hy : ‖y‖ = 1) :
    inner ℂ y (perpendicular y v) = 0 := by
  simp [perpendicular, inner_sub_right, inner_smul_right, inner_self_eq_norm_sq_to_K, hy]

theorem perpendicular_norm_sq (y v : E) (hy : ‖y‖ = 1) :
    ‖perpendicular y v‖ ^ 2 = ‖v‖ ^ 2 - ‖inner ℂ y v‖ ^ 2 := by
  have hprod : RCLike.re (inner ℂ v (inner ℂ y v • y)) = ‖inner ℂ y v‖ ^ 2 := by
    rw [inner_smul_right, ← inner_conj_symm v y, RCLike.mul_conj]
    exact RCLike.re_ofReal_pow _ _
  rw [perpendicular, norm_sub_sq (𝕜 := ℂ), norm_smul, hy, mul_one, hprod]
  ring

theorem perpendicular_inner (y t x : E) (hy : ‖y‖ = 1) :
    inner ℂ (perpendicular y t) (perpendicular y x) =
      inner ℂ t x - inner ℂ t y * inner ℂ y x := by
  simp only [perpendicular, inner_sub_left, inner_sub_right, inner_smul_left,
    inner_smul_right, inner_self_eq_norm_sq_to_K, hy, RCLike.ofReal_one, one_pow, mul_one,
    inner_conj_symm]
  ring

/-- Phase-free triangle/Cauchy–Schwarz lower bound. -/
theorem overlap_from_perpendicular (y t x : E) (hy : ‖y‖ = 1) :
    ‖inner ℂ t y‖ * ‖inner ℂ y x‖ -
      ‖perpendicular y t‖ * ‖perpendicular y x‖ ≤ ‖inner ℂ t x‖ := by
  have htri := norm_le_norm_add_norm_sub' (inner ℂ t y * inner ℂ y x) (inner ℂ t x)
  have hcs := norm_inner_le_norm (𝕜 := ℂ) (perpendicular y t) (perpendicular y x)
  rw [perpendicular_inner y t x hy] at hcs
  rw [norm_mul, norm_sub_rev] at htri
  linarith

/-- The requested angle-to-amplitude statement. No operator or physical model
is used in this purely Hilbert-space step. -/
theorem overlap_bound : OverlapStatement := by
  intro E _ _ x y t e O hx hy ht he he1 hO hO1 hxy hty
  have hsqe : 0 ≤ 1 - e ^ 2 := by nlinarith
  have hsqO : 0 ≤ 1 - O ^ 2 := by nlinarith
  have hqa := Real.sq_sqrt hsqe
  have hqb := Real.sq_sqrt hsqO
  have hxy' : Real.sqrt (1 - e ^ 2) ≤ ‖inner ℂ y x‖ := by
    simpa only [norm_inner_symm x y] using hxy
  have hperpx : ‖perpendicular y x‖ ≤ e := by
    have hn := perpendicular_norm_sq y x hy
    rw [hx] at hn
    have hs := square_bound (Real.sqrt_nonneg _) hxy'
    nlinarith [norm_nonneg (perpendicular y x)]
  have hperpt : ‖perpendicular y t‖ ≤ Real.sqrt (1 - O ^ 2) := by
    have hn := perpendicular_norm_sq y t hy
    rw [ht, norm_inner_symm y t] at hn
    have hs := square_bound hO hty
    nlinarith [norm_nonneg (perpendicular y t), Real.sqrt_nonneg (1 - O ^ 2)]
  have hmain := overlap_from_perpendicular y t x hy
  have hprod := mul_le_mul hty hxy' (Real.sqrt_nonneg _) (norm_nonneg _)
  have herr := mul_le_mul hperpt hperpx (norm_nonneg _) (Real.sqrt_nonneg _)
  apply max_le (norm_nonneg _)
  nlinarith

/-- Self-adjointness and `P t = t` move the target inner product through `P`.
Idempotence records the projection model, although this estimate only needs
those two properties. Completeness is unnecessary for the estimate. -/
theorem projection_bound : ProjectionStatement := by
  intro E _ _ x y t P e O hx hy ht hP_selfAdjoint hP_idempotent hPt
    he he1 hO hO1 hxy hty
  have ha := overlap_bound E x y t e O hx hy ht he he1 hO hO1 hxy hty
  have hp : inner ℂ t x = inner ℂ t (P x) := by
    simpa only [hPt] using hP_selfAdjoint t x
  have hcs := norm_inner_le_norm (𝕜 := ℂ) t (P x)
  rw [ht, one_mul, ← hp] at hcs
  exact square_bound (le_max_left _ _) (le_trans ha hcs)

end Geometry
end HydrogenPathway
