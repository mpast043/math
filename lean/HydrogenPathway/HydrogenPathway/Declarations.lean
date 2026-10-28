import HydrogenPathway
import Lean.Util.CollectAxioms

/-! Comparator-style checks against independent statement definitions.
The tests fail to elaborate if a solution's declaration does not have the
required type. The command below fails on any transitive axiom outside the
repository comparator's three standard axioms. No external comparator binary
is required, and this does not claim an independent kernel recheck. -/

namespace HydrogenPathway

example : OverlapStatement := overlap_bound
example : ProjectionStatement := projection_bound
example : ResidualStatement := residual_normalization
example : ClickStatement := actual_click_bound
example : EndpointStatement := conditional_click_endpoint
example : ResidualEndpointStatement := residual_click_endpoint

example : probabilityFloor 0 1 = 1 := by
  norm_num [probabilityFloor, amplitudeFloor]

example : probabilityFloor (3 / 5) (4 / 5) = 49 / 625 := by
  have he : Real.sqrt (1 - (3 / 5 : ℝ) ^ 2) = 4 / 5 := by
    rw [show (1 - (3 / 5 : ℝ) ^ 2) = (4 / 5 : ℝ) ^ 2 by norm_num]
    exact Real.sqrt_sq (by norm_num)
  have hO : Real.sqrt (1 - (4 / 5 : ℝ) ^ 2) = 3 / 5 := by
    rw [show (1 - (4 / 5 : ℝ) ^ 2) = (3 / 5 : ℝ) ^ 2 by norm_num]
    exact Real.sqrt_sq (by norm_num)
  unfold probabilityFloor amplitudeFloor
  rw [he, hO]
  norm_num

example : probabilityFloor (3 / 5) 0 = 0 := by
  norm_num [probabilityFloor, amplitudeFloor]

example (Fclick : ℝ) (hclick : Fclick = ((9 / 10 : ℝ) * 2) / (2 + 1 / 2)) :
    (18 / 25 : ℝ) ≤ Fclick := by
  have h := actual_click_bound (9 / 10) (9 / 10) 2 2 (1 / 2) (1 / 2) Fclick
    (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) hclick
  norm_num at h ⊢
  exact h

run_cmd do
  let permitted : Array Lean.Name := #[``propext, ``Quot.sound, ``Classical.choice]
  for decl in #[``square_bound, ``inner_perpendicular, ``perpendicular_norm_sq, ``perpendicular_inner,
      ``overlap_from_perpendicular, ``overlap_bound, ``projection_bound,
      ``projection_probability_le_one, ``residual_normalization, ``actual_click_bound,
      ``conditional_click_endpoint, ``normalized_norm, ``residual_click_endpoint,
      ``residual_numeric_exact,
      ``residual_numeric_below_rounded] do
    let axioms ← Lean.collectAxioms decl
    for ax in axioms do
      unless permitted.contains ax do
        throwError "Forbidden axiom {ax} in {decl}"
    Lean.logInfo m!"AXIOMS {decl}: {axioms}"

end HydrogenPathway
