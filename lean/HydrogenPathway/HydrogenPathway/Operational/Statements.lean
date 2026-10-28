import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Analysis.Complex.Basic

/-! Finite complex matrix interfaces. Positivity, effect admissibility and
physical access are not needed for the algebra and are separate hypotheses
for a Born-probability interpretation. -/
namespace HydrogenPathway.Operational
open Classical
open scoped BigOperators Matrix

noncomputable def pinch {n J : Type*} [Fintype n] [Fintype J]
    (P : J → Matrix n n ℂ) (X : Matrix n n ℂ) : Matrix n n ℂ := ∑ j, P j * X * P j

noncomputable def blockDelta {n B : Type*} (label : n → B) (X : Matrix n n ℂ) : Matrix n n ℂ := by
  classical
  exact fun i j => if label i = label j then X i j else 0

noncomputable def offBlockBudget {n B : Type*} [Fintype n]
    (label : n → B) (M ρ : Matrix n n ℂ) : ℝ := by
  classical
  exact ∑ i, ∑ j, if label i = label j then 0 else ‖M i j‖ * ‖ρ j i‖

def PinchPairingStatement : Prop :=
  ∀ (n J : Type) [Fintype n] [Fintype J] (P : J → Matrix n n ℂ) (M X : Matrix n n ℂ),
    Matrix.trace (M * pinch P X) = Matrix.trace (pinch P M * X)

/-- Complete idempotents suffice; orthogonal Hermitian pointer projections
are a special case. These assumptions do not contain the trace conclusion. -/
def CommutingFixedStatement : Prop :=
  ∀ (n J : Type) [Fintype n] [DecidableEq n] [Fintype J]
    (P : J → Matrix n n ℂ) (M : Matrix n n ℂ),
    (∀ j, P j * P j = P j) → (∑ j, P j) = 1 →
    (∀ j, M * P j = P j * M) → pinch P M = M

def OperationalBoundaryStatement : Prop :=
  ∀ (n J : Type) [Fintype n] [DecidableEq n] [Fintype J]
    (P : J → Matrix n n ℂ) (M ρ : Matrix n n ℂ),
    (∀ j, P j * P j = P j) → (∑ j, P j) = 1 →
    (∀ j, M * P j = P j * M) →
    Matrix.trace (M * ρ) = Matrix.trace (M * pinch P ρ)

def BlockIdempotentStatement : Prop :=
  ∀ (n B : Type) (label : n → B) (X : Matrix n n ℂ),
    blockDelta label (blockDelta label X) = blockDelta label X

def OffBlockExpansionStatement : Prop :=
  ∀ (n B : Type) [Fintype n] (label : n → B) (M ρ : Matrix n n ℂ),
    Matrix.trace (M * ρ) - Matrix.trace (M * blockDelta label ρ) =
      ∑ i, ∑ j, if label i = label j then 0 else M i j * ρ j i

/-- Entrywise sufficient bound, not an operator-norm/trace-norm bound. -/
def EntrywiseBoundStatement : Prop :=
  ∀ (n B : Type) [Fintype n] (label : n → B) (M ρ : Matrix n n ℂ),
    ‖Matrix.trace (M * ρ) - Matrix.trace (M * blockDelta label ρ)‖ ≤ offBlockBudget label M ρ

def BlockBoundaryStatement : Prop :=
  ∀ (n B : Type) [Fintype n] (label : n → B) (M ρ : Matrix n n ℂ),
    (∀ i j, label i ≠ label j → M i j = 0) →
    Matrix.trace (M * ρ) = Matrix.trace (M * blockDelta label ρ)

/-- Actual rectangular branch encoding and lifted local matrix. -/
noncomputable def encoding {n e : Type*} (E : n → e → ℂ) : Matrix (n × e) n ℂ := by
  classical
  exact fun a j => if a.1 = j then E j a.2 else 0

noncomputable def localLift {n e : Type*} (M : Matrix n n ℂ) : Matrix (n × e) (n × e) ℂ := by
  classical
  exact fun a b => if a.2 = b.2 then M a.1 b.1 else 0

noncomputable def gram {n e : Type*} [Fintype e] (E : n → e → ℂ) (j k : n) : ℂ :=
  ∑ a, star (E j a) * E k a

def CompressionStatement : Prop :=
  ∀ (n e : Type) [Fintype n] [Fintype e] (E : n → e → ℂ) (M : Matrix n n ℂ) (j k : n),
    ((encoding E)ᴴ * localLift (e := e) M * encoding E) j k = M j k * gram E j k

def PinchTraceStatement : Prop :=
  ∀ (n J : Type) [Fintype n] [DecidableEq n] [Fintype J]
    (P : J → Matrix n n ℂ) (ρ : Matrix n n ℂ),
    (∀ j, P j * P j = P j) → (∑ j, P j) = 1 → Matrix.trace (pinch P ρ) = Matrix.trace ρ

def BlockTraceStatement : Prop :=
  ∀ (n B : Type) [Fintype n] (label : n → B) (X : Matrix n n ℂ),
    Matrix.trace (blockDelta label X) = Matrix.trace X

def EncodingIsometryStatement : Prop :=
  ∀ (n e : Type) [Fintype n] [DecidableEq n] [Fintype e] (E : n → e → ℂ),
    (∀ j, gram E j j = 1) → (encoding E)ᴴ * encoding E = 1

def EncodingPairingStatement : Prop :=
  ∀ (n e : Type) [Fintype n] [Fintype e] (E : n → e → ℂ) (M ρ : Matrix n n ℂ),
    Matrix.trace (localLift (e := e) M * (encoding E * ρ * (encoding E)ᴴ)) =
      Matrix.trace (((encoding E)ᴴ * localLift (e := e) M * encoding E) * ρ)

/-- Every local atom matrix is allowed in this algebraic statement. Vanishing
inaccessible overlaps, rather than a ban on atom interference, remove the
branch off-diagonal contribution. Unit vectors are needed for an isometry. -/
def InaccessibleBoundaryStatement : Prop :=
  ∀ (n e : Type) [Fintype n] [Fintype e] (E : n → e → ℂ) (M ρ : Matrix n n ℂ),
    (∀ j k, j ≠ k → gram E j k = 0) →
    Matrix.trace (localLift (e := e) M * (encoding E * ρ * (encoding E)ᴴ)) =
      Matrix.trace (localLift (e := e) M *
        (encoding E * blockDelta (fun j : n => j) ρ * (encoding E)ᴴ))

/-- Quantitative finite entrywise access bound. This is not the operator/trace
norm Holder inequality. It explicitly contains inaccessible Gram overlaps. -/
def InaccessibleEntrywiseStatement : Prop :=
  ∀ (n e : Type) [Fintype n] [Fintype e] (E : n → e → ℂ) (M ρ : Matrix n n ℂ),
    ‖Matrix.trace (localLift (e := e) M * (encoding E * ρ * (encoding E)ᴴ)) -
      Matrix.trace (localLift (e := e) M *
        (encoding E * blockDelta (fun j : n => j) ρ * (encoding E)ᴴ))‖ ≤
      ∑ j, ∑ k, if j = k then 0 else ‖M j k‖ * ‖gram E j k‖ * ‖ρ k j‖

noncomputable def eventMass {Ω : Type*} [Fintype Ω] (w : Ω → ℝ) (E : Ω → Prop) : ℝ := by
  classical
  exact ∑ ω, if E ω then w ω else 0

def ConditionalUnionStatement : Prop :=
  ∀ (Ω : Type) [Fintype Ω] (w : Ω → ℝ) (C E A B : Ω → Prop),
    (∀ ω, 0 ≤ w ω) → 0 < eventMass w C → (∀ ω, E ω → A ω ∨ B ω) →
    eventMass w (fun ω => C ω ∧ E ω) / eventMass w C ≤
      (eventMass w (fun ω => C ω ∧ A ω) + eventMass w (fun ω => C ω ∧ B ω)) / eventMass w C

def RecordErrorStatement : Prop :=
  ∀ (Ω R : Type) [Fintype Ω] (w : Ω → ℝ) (C : Ω → Prop) (initial later truth : Ω → R),
    (∀ ω, 0 ≤ w ω) → 0 < eventMass w C →
    eventMass w (fun ω => C ω ∧ later ω ≠ truth ω) / eventMass w C ≤
      (eventMass w (fun ω => C ω ∧ initial ω ≠ truth ω) +
       eventMass w (fun ω => C ω ∧ later ω ≠ initial ω)) / eventMass w C

end HydrogenPathway.Operational
