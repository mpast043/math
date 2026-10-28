import HydrogenPathway.Witness
import Lean.Util.CollectAxioms

namespace HydrogenPathway.Witness
example : OutcomeLawStatement := four_outcome_law
example : ResponseGuessStatement := full_response_guess
example : ContrastErrorStatement := expectation_contrast_error
example : CalibrationStatement := calibrated_contrast_lower
example : LossBoundsStatement := loss_false_accept_bounds
example : AdvantageStatement := coincidence_advantage
example : EfficiencyThresholdStatement := ideal_efficiency_threshold
example : HybridAdvantageStatement := hybrid_advantage
example : HybridIdealStatement := hybrid_ideal_gain
example : MinusPortStatement := minus_port_advantage
example : IllustrativeBudgetStatement := illustrative_budget

example : scoreGuess ((1 / 1000 : ℝ) * 1) = 1001 / 2000 := by norm_num [scoreGuess]
example : jointWeight (1 : ℝ) (4 / 5) 1 (-1) = 0 := by norm_num [jointWeight]
example : scoreGuess (-4 / 5 : ℝ) = 1 / 10 := by norm_num [scoreGuess]

run_cmd do
  let permitted : Array Lean.Name := #[``propext, ``Quot.sound, ``Classical.choice]
  for decl in #[``four_outcome_law, ``full_response_guess, ``expectation_contrast_error,
      ``calibrated_contrast_lower, ``loss_false_accept_bounds, ``coincidence_advantage,
      ``ideal_efficiency_threshold, ``hybrid_advantage, ``hybrid_ideal_gain, ``minus_port_advantage, ``illustrative_budget] do
    let axioms ← Lean.collectAxioms decl
    for ax in axioms do
      unless permitted.contains ax do
        throwError "Forbidden axiom {ax} in {decl}"
    Lean.logInfo m!"AXIOMS {decl}: {axioms}"
end HydrogenPathway.Witness
