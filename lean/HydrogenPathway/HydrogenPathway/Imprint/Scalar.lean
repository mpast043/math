import HydrogenPathway.Imprint.Statements
import HydrogenPathway.Scalar
import Mathlib.Tactic.Ring

namespace HydrogenPathway.Imprint

/-- Algebraic identity for two different label ensembles in the illustrative
model, not conservation of the three phase-label marginal distances. -/
theorem overlap_which_mode_identity : ComplementarityStatement := by
  intro r hr hr1
  have hn : 0 ≤ 1 - r ^ 2 := by nlinarith
  dsimp [whichMode]
  rw [Real.sq_sqrt hn]
  ring

theorem scaled_overlap_which_mode_identity : ScaledComplementarityStatement := by
  intro p r hr hr1
  calc
    (p * r) ^ 2 + (p * whichMode r) ^ 2 =
        p ^ 2 * (r ^ 2 + (whichMode r) ^ 2) := by ring
    _ = p ^ 2 := by rw [overlap_which_mode_identity r hr hr1, mul_one]

/-- Once the full flagged distance is known to be `p*d`, its guessing
advantage scales with `p`; conditioning alone cannot remove that cost. -/
theorem equal_acceptance_accounting : AcceptanceStatement := by
  intro p d hp hp1 hd hd1
  have hupper : p * d ≤ p := by nlinarith
  refine ⟨mul_nonneg hp hd, hupper, ?_, ?_⟩
  · dsimp [equalPriorGuess]
    ring
  · dsimp [equalPriorGuess]
    linarith

/-- Bounds for the flagged block formula, conditional on the named bounds on
the success-block norm. No matrix/operator facts are introduced as axioms. -/
theorem flagged_accounting_bounds : FlaggedAccountingStatement := by
  intro p0 p1 n hp0 hp01 hp1 hp11 hnlow hnupper
  have hmax : p0 + p1 + |p0 - p1| = 2 * max p0 p1 := by
    rcases le_total p0 p1 with h | h
    · rw [max_eq_right h, abs_of_nonpos (by linarith)]
      ring
    · rw [max_eq_left h, abs_of_nonneg (by linarith)]
      ring
  have hm1 : max p0 p1 ≤ 1 := max_le hp01 hp11
  dsimp [flaggedValue]
  exact ⟨by linarith, by linarith, by linarith⟩

theorem flagged_guess_bounds : FlaggedGuessStatement := by
  intro p0 p1 n hp0 hp01 hp1 hp11 hnlow hnupper
  obtain ⟨hlow, hupp, _⟩ := flagged_accounting_bounds p0 p1 n hp0 hp01 hp1 hp11 hnlow hnupper
  dsimp [equalPriorGuess]
  exact ⟨by linarith, by linarith⟩

/-- Equal input priors become equal success-conditioned priors exactly when
the two acceptance probabilities coincide. Zero total acceptance is excluded. -/
theorem posterior_weights : PosteriorStatement := by
  intro p0 p1 hp0 hp1 hs
  have hne : p0 + p1 ≠ 0 := ne_of_gt hs
  refine ⟨div_nonneg hp0 hs.le, div_nonneg hp1 hs.le, ?_, ?_⟩
  · rw [← add_div, div_self hne]
  · constructor
    · intro h
      have hh := (div_eq_iff hne).mp h
      linarith
    · intro h
      apply (div_eq_iff hne).mpr
      linarith

/-- Generic triangle-inequality stability with one error per normalized
output. A trace-distance instantiation must use the same flag/register scope. -/
theorem metric_stability : MetricStabilityStatement := by
  intro E _ a0 a1 m0 m1 δ0 δ1 hδ0 hδ1 h0 h1
  have ht0 := dist_triangle m0 a0 m1
  have ht1 := dist_triangle a0 a1 m1
  rw [dist_comm m0 a0] at ht0
  dsimp [stableFloor]
  exact max_le dist_nonneg (by linarith)

/-- Composes metric stability with an explicitly supplied model-distance
equation and an explicitly supplied operational guessing interpretation. -/
theorem stable_flagged_guess : StableFlaggedGuessStatement := by
  intro E _ a0 a1 m0 m1 p r δ0 δ1 g hp hp1 hr hr1 hδ0 hδ1 hmodel h0 h1 hg
  have h := metric_stability E a0 a1 m0 m1 δ0 δ1 hδ0 hδ1 h0 h1
  rw [hmodel] at h
  rw [hg]
  dsimp [equalPriorGuess]
  linarith

end HydrogenPathway.Imprint
