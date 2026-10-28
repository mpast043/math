import HydrogenPathway.Imprint
import Lean.Util.CollectAxioms

namespace HydrogenPathway.Imprint

example : ComplementarityStatement := overlap_which_mode_identity
example : ScaledComplementarityStatement := scaled_overlap_which_mode_identity
example : AcceptanceStatement := equal_acceptance_accounting
example : FlaggedAccountingStatement := flagged_accounting_bounds
example : FlaggedGuessStatement := flagged_guess_bounds
example : PosteriorStatement := posterior_weights
example : MetricStabilityStatement := metric_stability
example : StableFlaggedGuessStatement := stable_flagged_guess

example : equalPriorGuess ((1 / 4 : ℝ) * (3 / 5)) = 23 / 40 := by
  norm_num [equalPriorGuess]

example : flaggedValue (4 / 5) (1 / 5) (3 / 5) = (3 / 5 : ℝ) := by
  norm_num [flaggedValue]

example : stableFloor (1 / 10) (1 / 5) (1 / 5) = 0 := by
  norm_num [stableFloor]

example : (4 / 5 : ℝ) / (4 / 5 + 1 / 5) ≠ 1 / 2 := by norm_num

run_cmd do
  let permitted : Array Lean.Name := #[``propext, ``Quot.sound, ``Classical.choice]
  for decl in #[``overlap_which_mode_identity, ``scaled_overlap_which_mode_identity,
      ``equal_acceptance_accounting, ``flagged_accounting_bounds, ``flagged_guess_bounds,
      ``posterior_weights, ``metric_stability, ``stable_flagged_guess] do
    let axioms ← Lean.collectAxioms decl
    for ax in axioms do
      unless permitted.contains ax do
        throwError "Forbidden axiom {ax} in {decl}"
    Lean.logInfo m!"AXIOMS {decl}: {axioms}"

end HydrogenPathway.Imprint
