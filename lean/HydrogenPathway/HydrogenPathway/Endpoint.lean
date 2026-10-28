import HydrogenPathway.Residual

namespace HydrogenPathway

/-- The self-adjoint idempotent operator supplies a valid projection probability. -/
theorem projection_probability_le_one
    {E : Type} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (x : E) (P : E →L[ℂ] E) (hx : ‖x‖ = 1)
    (hP_selfAdjoint : ∀ u v, inner ℂ (P u) v = inner ℂ u (P v))
    (hP_idempotent : ∀ u, P (P u) = P u) : ‖P x‖ ^ 2 ≤ 1 := by
  have hh : RCLike.re (inner ℂ (P x) (P x)) = RCLike.re (inner ℂ x (P x)) := by
    rw [hP_selfAdjoint, hP_idempotent]
  rw [inner_self_eq_norm_sq] at hh
  have hb := re_inner_le_norm (𝕜 := ℂ) x (P x)
  rw [hx, one_mul] at hb
  have hn : 0 ≤ ‖P x‖ := norm_nonneg _
  have hn1 : ‖P x‖ ≤ 1 := by nlinarith
  nlinarith

/-- Composition of the Hilbert-space theorem with the explicitly assumed
incoherent click model. This is conditional on identifying true-click target
probability with the projection probability; it proves no instrument physics. -/
theorem conditional_click_endpoint : EndpointStatement := by
  intro E _ _ x y t P e O S s0 B b Fclick hx hy ht hP hPi hPt
    he he1 hO hO1 hxy hty hs0 hS hB hBb hclick
  have hprojection := projection_bound E x y t P e O hx hy ht hP hPi hPt
    he he1 hO hO1 hxy hty
  have hp1 := projection_probability_le_one x P hx hP hPi
  exact actual_click_bound (probabilityFloor e O) (‖P x‖ ^ 2) S s0 B b Fclick
    (sq_nonneg _) (le_trans hprojection hp1) hprojection hp1 hs0 hS hB hBb hclick

theorem normalized_norm
    {E : Type} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (X : E) (hX : X ≠ 0) : ‖(‖X‖⁻¹ : ℂ) • X‖ = 1 := by
  simp +instances only [norm_smul, norm_inv, Complex.norm_real,
    Real.norm_of_nonneg (norm_nonneg X)]
  exact inv_mul_cancel₀ (norm_ne_zero_iff.mpr hX)

/-- The relative residual-ball input composed all the way to the conditional
actual-click lower bound, with every physical identification still explicit. -/
theorem residual_click_endpoint : ResidualEndpointStatement := by
  intro E _ _ X Y t P e O S s0 B b Fclick hY ht hP hPi hPt
    he he1 hO hO1 hres htarget hs0 hS hB hBb hclick
  obtain ⟨hX, hangle⟩ := residual_normalization E X Y e hY he he1 hres
  exact conditional_click_endpoint E ((‖X‖⁻¹ : ℂ) • X) ((‖Y‖⁻¹ : ℂ) • Y) t
    P e O S s0 B b Fclick (normalized_norm X hX) (normalized_norm Y hY) ht
    hP hPi hPt he he1 hO hO1 hangle htarget hs0 hS hB hBb hclick

end HydrogenPathway
