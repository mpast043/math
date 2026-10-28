import HydrogenPathway.Operational.Matrix

namespace HydrogenPathway.Operational
open scoped BigOperators Matrix

theorem encoding_compression : CompressionStatement := by
  intro n e _ _ E M j k
  classical
  simp [Matrix.mul_apply, Matrix.conjTranspose_apply, encoding, localLift,
    Fintype.sum_prod_type, gram, Finset.mul_sum, apply_ite, ite_mul,
    mul_left_comm, mul_assoc]

theorem encoding_isometry : EncodingIsometryStatement := by
  intro n e _ _ _ E hunit
  classical
  have hlift : localLift (e := e) (1 : Matrix n n ℂ) = 1 := by
    ext a b
    by_cases ha : a.1 = b.1 <;> by_cases he : a.2 = b.2 <;>
      simp [localLift, Matrix.one_apply, Prod.ext_iff, ha, he]
  ext j k
  have h := encoding_compression n e E (1 : Matrix n n ℂ) j k
  rw [hlift, Matrix.mul_one] at h
  by_cases heq : j = k
  · simpa [heq, Matrix.one_apply, hunit] using h
  · simpa [heq, Matrix.one_apply] using h

theorem encoding_pairing : EncodingPairingStatement := by
  intro n e _ _ E M ρ
  calc
    Matrix.trace (localLift (e := e) M * (encoding E * ρ * (encoding E)ᴴ)) =
        Matrix.trace ((localLift (e := e) M * encoding E * ρ) * (encoding E)ᴴ) := by
      simp only [Matrix.mul_assoc]
    _ = Matrix.trace ((encoding E)ᴴ * (localLift (e := e) M * encoding E * ρ)) :=
      Matrix.trace_mul_comm _ _
    _ = _ := by simp only [Matrix.mul_assoc]

theorem inaccessible_boundary : InaccessibleBoundaryStatement := by
  intro n e _ _ E M ρ horth
  rw [encoding_pairing n e E M ρ, encoding_pairing n e E M (blockDelta (fun j : n => j) ρ)]
  apply block_boundary n n (fun j => j)
  intro j k hne
  rw [encoding_compression n e E M j k, horth j k hne, mul_zero]

theorem inaccessible_entrywise_bound : InaccessibleEntrywiseStatement := by
  intro n e _ _ E M ρ
  rw [encoding_pairing n e E M ρ, encoding_pairing n e E M (blockDelta (fun j : n => j) ρ)]
  have h := entrywise_bound n n (fun j => j) ((encoding E)ᴴ * localLift (e := e) M * encoding E) ρ
  have hc := encoding_compression n e E M
  simpa only [offBlockBudget, hc, norm_mul] using h

end HydrogenPathway.Operational
