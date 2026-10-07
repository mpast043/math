import OAI.Combinatorics.SecondNeighborhood.Main

/-!
Independent restatement of the Comparator challenge
`lean/ComparatorChallenges/SeymourSecondNeighborhood.lean`, copied verbatim into a
fresh namespace `ReviewCheck`, and derived from the repository's compiled proof.
If this file compiles and `#print axioms` shows only the standard axioms, the
challenge statement is a theorem of Lean + Mathlib.
-/

namespace ReviewCheck

variable {V : Type*}

structure IsOriented (r : V → V → Prop) : Prop where
  loopless : ∀ v, ¬ r v v
  asymmetric : ∀ {u v}, r u v → ¬ r v u

variable [Fintype V] [DecidableEq V]

noncomputable section

def firstNeighbors (r : V → V → Prop) (v : V) : Finset V := by
  classical
  exact Finset.univ.filter (r v)

def secondNeighbors (r : V → V → Prop) (v : V) : Finset V := by
  classical
  exact Finset.univ.filter (fun w =>
    w ≠ v ∧ ¬ r v w ∧ ∃ u, r v u ∧ r u w)

def GoodVertex (r : V → V → Prop) (v : V) : Prop :=
  (firstNeighbors r v).card ≤ (secondNeighbors r v).card

end

variable [Nonempty V]

theorem exists_goodVertex (r : V → V → Prop) (hr : IsOriented r) :
    ∃ v, GoodVertex r v := by
  obtain ⟨v, hv⟩ := OAI.SeymourSecondNeighborhood.exists_goodVertex r
    ⟨hr.loopless, fun h => hr.asymmetric h⟩
  exact ⟨v, hv⟩

end ReviewCheck

#check @OAI.SeymourSecondNeighborhood.exists_goodVertex
#print axioms OAI.SeymourSecondNeighborhood.exists_goodVertex
#print axioms ReviewCheck.exists_goodVertex
