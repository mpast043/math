import Lake
open Lake DSL

package seymourcheck where
  leanOptions := #[⟨`autoImplicit, false⟩]

require mathlib from "../mathlib4"

lean_lib OAI where
  globs := #[`OAI.+]

lean_lib ComparatorChallenges where
  globs := #[`ComparatorChallenges.+]
