import HydrogenPathway.Operational.Statements

namespace HydrogenPathway.Operational
open scoped BigOperators Matrix

theorem pinch_pairing : PinchPairingStatement := by
  intro n J _ _ P M X
  dsimp [pinch]
  rw [Matrix.mul_sum, Matrix.sum_mul]
  simp only [Matrix.trace_sum]
  apply Finset.sum_congr rfl
  intro j _
  calc
    Matrix.trace (M * (P j * X * P j)) = Matrix.trace ((M * P j * X) * P j) := by
      simp only [Matrix.mul_assoc]
    _ = Matrix.trace (P j * (M * P j * X)) := Matrix.trace_mul_comm _ _
    _ = Matrix.trace (P j * M * P j * X) := by simp only [Matrix.mul_assoc]

theorem commuting_fixed : CommutingFixedStatement := by
  intro n J _ _ _ P M hid hsum hcomm
  dsimp [pinch]
  calc
    ∑ j, P j * M * P j = ∑ j, M * P j := by
      apply Finset.sum_congr rfl
      intro j _
      rw [← hcomm j, Matrix.mul_assoc, hid j]
    _ = M * ∑ j, P j := by rw [Matrix.mul_sum]
    _ = M := by rw [hsum, Matrix.mul_one]

theorem operational_boundary : OperationalBoundaryStatement := by
  intro n J _ _ _ P M ρ hid hsum hcomm
  rw [pinch_pairing n J P M ρ, commuting_fixed n J P M hid hsum hcomm]

theorem block_idempotent : BlockIdempotentStatement := by
  intro n B label X
  classical
  ext i j
  by_cases h : label i = label j
  · simp only [blockDelta, ite_eq_left h]
  · simp only [blockDelta, ite_eq_right h]

theorem off_block_expansion : OffBlockExpansionStatement := by
  intro n B _ label M ρ
  classical
  simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  by_cases h : label i = label j
  · simp only [blockDelta, ite_eq_left h.symm, ite_eq_left h, sub_self]
  · simp only [blockDelta, ite_eq_right (Ne.symm h), ite_eq_right h, mul_zero, sub_zero]

theorem entrywise_bound : EntrywiseBoundStatement := by
  intro n B _ label M ρ
  classical
  rw [off_block_expansion n B label M ρ]
  dsimp [offBlockBudget]
  apply (norm_sum_le _ _).trans
  apply Finset.sum_le_sum
  intro i _
  apply (norm_sum_le _ _).trans
  apply Finset.sum_le_sum
  intro j _
  by_cases h : label i = label j
  · simp only [ite_eq_left h, norm_zero, le_refl]
  · simp only [ite_eq_right h, norm_mul, le_refl]

theorem block_boundary : BlockBoundaryStatement := by
  intro n B _ label M ρ hoff
  classical
  apply sub_eq_zero.mp
  rw [off_block_expansion n B label M ρ]
  apply Finset.sum_eq_zero
  intro i _
  apply Finset.sum_eq_zero
  intro j _
  by_cases h : label i = label j
  · simp only [ite_eq_left h]
  · simp only [ite_eq_right h, hoff i j h, zero_mul]

theorem pinch_trace : PinchTraceStatement := by
  intro n J _ _ _ P ρ hid hsum
  have h := operational_boundary n J P (1 : Matrix n n ℂ) ρ hid hsum (by intro j; simp)
  simpa only [Matrix.one_mul] using h.symm

theorem block_trace : BlockTraceStatement := by
  intro n B _ label X
  classical
  simp [Matrix.trace, blockDelta]

end HydrogenPathway.Operational
