import HydrogenPathway.Witness.Statements
import HydrogenPathway.Scalar
import Mathlib.Tactic.Ring

namespace HydrogenPathway.Witness

theorem four_outcome_law : OutcomeLawStatement := by
  intro r t hr hr1 ht ht1
  have hp : 0 ≤ 1 + r := by linarith
  have hm : 0 ≤ 1 - r := by linarith
  have htp : 0 ≤ 1 + t := by linarith
  have htm : 0 ≤ 1 - t := by linarith
  dsimp [jointWeight]
  constructor
  · convert div_nonneg (mul_nonneg hp htp) (by norm_num : (0 : ℝ) ≤ 4) using 1; ring
  constructor
  · convert div_nonneg (mul_nonneg hm htm) (by norm_num : (0 : ℝ) ≤ 4) using 1; ring
  constructor
  · convert div_nonneg (mul_nonneg hp htm) (by norm_num : (0 : ℝ) ≤ 4) using 1; ring
  constructor
  · convert div_nonneg (mul_nonneg hm htp) (by norm_num : (0 : ℝ) ≤ 4) using 1; ring
  constructor <;> ring

theorem full_response_guess : ResponseGuessStatement := by
  intro pp pm mp mm ep em hpp hpm hmp hmm hep hem hp hm
  dsimp [scoreGuess, contrast]
  exact ⟨by linarith, by positivity, by linarith⟩

theorem expectation_contrast_error : ContrastErrorStatement := by
  intro mp mm target εp εm hp hm
  obtain ⟨hpl, hpu⟩ := abs_le.mp hp
  obtain ⟨hml, hmu⟩ := abs_le.mp hm
  dsimp [contrast]
  exact abs_le.mpr ⟨by linarith, by linarith⟩

theorem calibrated_contrast_lower : CalibrationStatement := by
  intro mp mm v u z c εp εm hv hu hz hp hm
  have herr := expectation_contrast_error mp mm (v * u * z) εp εm hp hm
  have hcal := mul_le_mul_of_nonneg_left hz (mul_nonneg hv hu)
  have hl := (abs_le.mp herr).1
  linarith

theorem loss_false_accept_bounds : LossBoundsStatement := by
  intro q b c f g hq hb hqb hc hc1 hf hf1 hg
  have hqc := mul_le_mul_of_nonneg_left hc hq
  have hqc1 := mul_le_mul_of_nonneg_left hc1 hq
  have hbf := mul_le_mul_of_nonneg_left hf hb
  have hbf1 := mul_le_mul_of_nonneg_left hf1 hb
  rw [hg]
  dsimp [scoreGuess]
  exact ⟨by nlinarith, by nlinarith, by nlinarith, by nlinarith⟩

theorem coincidence_advantage : AdvantageStatement := by
  intro qj qa bj ba cj ca fj fa lj ua gj ga hqj hqa hbj hba hcj hca hfj hfa hgj hga
  have hj := mul_le_mul_of_nonneg_left hcj hqj
  have ha := mul_le_mul_of_nonneg_left hca hqa
  have hfj' := mul_le_mul_of_nonneg_left hfj hbj
  have hfa' := mul_le_mul_of_nonneg_left hfa hba
  rw [hgj, hga]
  dsimp [margin, scoreGuess]
  constructor
  · nlinarith
  · intro hmargin
    nlinarith

theorem ideal_efficiency_threshold : EfficiencyThresholdStatement := by
  intro p ea ec r u hp hea hu
  have hpos : 0 < p * ea * u := mul_pos (mul_pos hp hea) hu
  dsimp [scoreGuess]
  refine ⟨by ring, ?_⟩
  constructor <;> intro h <;> nlinarith

theorem hybrid_advantage : HybridAdvantageStatement := by
  intro qj qa bh ba cj ca fh fa lj ua gh ga hqj hqa hbh hba hcj hca hfh hfa hgh hga
  have hj := mul_le_mul_of_nonneg_left hcj hqj
  have ha := mul_le_mul_of_nonneg_left hca hqj
  have hfh' := mul_le_mul_of_nonneg_left hfh hbh
  have hfa' := mul_le_mul_of_nonneg_left hfa hba
  rw [hgh, hga]
  dsimp [scoreGuess]
  constructor
  · nlinarith
  · intro hmargin
    nlinarith

theorem hybrid_ideal_gain : HybridIdealStatement := by
  intro qa qj r t
  have hid : scoreGuess (qj * t + (qa - qj) * r * t) - scoreGuess (qa * r * t) =
      qj * t * (1 - r) / 2 := by dsimp [scoreGuess]; ring
  refine ⟨hid, ?_⟩
  intro hq ht hr
  have hpos : 0 < qj * t * (1 - r) / 2 := by positivity
  linarith

theorem minus_port_advantage : MinusPortStatement := by
  intro g L f d bnew bold H W gh ga hb hH hW hgh hga
  rw [hgh, hga]
  dsimp [scoreGuess]
  constructor
  · linarith
  · intro hmargin
    linarith

/-- Exact arithmetic for deliberately illustrative, uncertified parameters. -/
theorem illustrative_budget : IllustrativeBudgetStatement := by
  norm_num [IllustrativeBudgetStatement, margin]

end HydrogenPathway.Witness
