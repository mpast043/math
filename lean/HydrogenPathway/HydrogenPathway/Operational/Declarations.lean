import HydrogenPathway.Operational
import Mathlib.Tactic.NormNum
import Lean.Util.CollectAxioms

namespace HydrogenPathway.Operational
open scoped Matrix
example : PinchPairingStatement := pinch_pairing
example : CommutingFixedStatement := commuting_fixed
example : OperationalBoundaryStatement := operational_boundary
example : BlockIdempotentStatement := block_idempotent
example : OffBlockExpansionStatement := off_block_expansion
example : EntrywiseBoundStatement := entrywise_bound
example : BlockBoundaryStatement := block_boundary
example : PinchTraceStatement := pinch_trace
example : BlockTraceStatement := block_trace
example : CompressionStatement := encoding_compression
example : EncodingIsometryStatement := encoding_isometry
example : EncodingPairingStatement := encoding_pairing
example : InaccessibleBoundaryStatement := inaccessible_boundary
example : InaccessibleEntrywiseStatement := inaccessible_entrywise_bound
example : ConditionalUnionStatement := conditional_union
example : RecordErrorStatement := conditional_record_error

/-- The algebra does not require a density matrix. -/
example : Matrix.trace ((!![5, 0; 0, 6] : Matrix (Fin 2) (Fin 2) ℂ) * !![1, 2; 3, 4]) = 29 := by
  norm_num [Matrix.trace, Matrix.mul_apply, Fin.sum_univ_succ]

run_cmd do
  let permitted : Array Lean.Name := #[``propext, ``Quot.sound, ``Classical.choice]
  for decl in #[``pinch_pairing, ``commuting_fixed, ``operational_boundary,
      ``block_idempotent, ``off_block_expansion, ``entrywise_bound, ``block_boundary,
      ``pinch_trace, ``block_trace, ``encoding_compression, ``encoding_isometry,
      ``encoding_pairing, ``inaccessible_boundary, ``inaccessible_entrywise_bound,
      ``conditional_union, ``conditional_record_error] do
    let axioms ← Lean.collectAxioms decl
    for ax in axioms do
      unless permitted.contains ax do
        throwError "Forbidden axiom {ax} in {decl}"
    Lean.logInfo m!"AXIOMS {decl}: {axioms}"
end HydrogenPathway.Operational
