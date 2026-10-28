import HydrogenPathway.Geometry

namespace HydrogenPathway

/-- A relative residual ball controls the sine of the angle after normalization.
It does not assert that the normalized Hilbert-space distance is at most `e`.
Both nonzero denominators are established in the proof. -/
theorem residual_normalization : ResidualStatement := by
  intro E _ _ X Y e hY he he1 hres
  have hYn : 0 < ‖Y‖ := norm_pos_iff.mpr hY
  have hX : X ≠ 0 := by
    intro hzero
    have hh : ‖Y‖ ≤ e * ‖Y‖ := by simpa [hzero] using hres
    nlinarith
  refine ⟨hX, ?_⟩
  have hXn : 0 < ‖X‖ := norm_pos_iff.mpr hX
  have hsqe : 0 ≤ 1 - e ^ 2 := by nlinarith
  have hres2 := square_bound (norm_nonneg (X - Y)) hres
  rw [norm_sub_sq (𝕜 := ℂ)] at hres2
  have hsq := sq_nonneg (‖X‖ - Real.sqrt (1 - e ^ 2) * ‖Y‖)
  simp only [sub_sq, mul_pow, Real.sq_sqrt hsqe] at hsq
  have hre : Real.sqrt (1 - e ^ 2) * ‖X‖ * ‖Y‖ ≤ RCLike.re (inner ℂ X Y) := by
    nlinarith
  have habs : Real.sqrt (1 - e ^ 2) * (‖X‖ * ‖Y‖) ≤ ‖inner ℂ X Y‖ := by
    have hh := RCLike.re_le_norm (inner ℂ X Y)
    nlinarith
  have hnormalized :
      ‖inner ℂ ((‖X‖⁻¹ : ℂ) • X) ((‖Y‖⁻¹ : ℂ) • Y)‖ =
        ‖inner ℂ X Y‖ / (‖X‖ * ‖Y‖) := by
    simp +instances only [inner_smul_left, inner_smul_right, norm_mul, RCLike.norm_conj,
      norm_inv, Complex.norm_real, Real.norm_of_nonneg (norm_nonneg X),
      Real.norm_of_nonneg (norm_nonneg Y)]
    simp only [div_eq_mul_inv, mul_inv_rev]
    ring
  rw [hnormalized]
  exact (le_div_iff₀ (mul_pos hXn hYn)).2 habs

end HydrogenPathway
