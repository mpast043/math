import HydrogenPathway.Operational.Statements

namespace HydrogenPathway.Operational
open scoped BigOperators

theorem conditional_union : ConditionalUnionStatement := by
  intro Ω _ w C E A B hw hC hcover
  apply div_le_div_of_nonneg_right _ hC.le
  dsimp [eventMass]
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro ω _
  by_cases hc : C ω
  · by_cases he : E ω
    · rcases hcover ω he with ha | hb
      · by_cases hb : B ω <;> simp [hc, he, ha, hb, hw ω]
      · by_cases ha : A ω <;> simp [hc, he, ha, hb, hw ω]
    · by_cases ha : A ω <;> by_cases hb : B ω <;> simp [hc, he, ha, hb, hw ω]
  · simp [hc]

theorem conditional_record_error : RecordErrorStatement := by
  intro Ω R _ w C initial later truth hw hC
  apply conditional_union Ω w C (fun ω => later ω ≠ truth ω)
    (fun ω => initial ω ≠ truth ω) (fun ω => later ω ≠ initial ω) hw hC
  intro ω hwrong
  by_cases h : initial ω = truth ω
  · right
    intro hsame
    exact hwrong (hsame.trans h)
  · exact Or.inl h

end HydrogenPathway.Operational
