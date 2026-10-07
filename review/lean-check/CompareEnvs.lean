import Lean
open Lean

/-!
Comparator-style check (independent re-implementation of its core idea).

Loads the compiled challenge module and the compiled solution module as two separate
environments. For every constant declared under the challenge's namespace it checks
that the solution environment has a constant of the same name and kind, with an
identical type, and (for definitions, inductives and structures) an identical value or
shape. Theorems are compared by type only, since the challenge proves them with
`sorry`. Finally it reports the axioms used by each target theorem in the solution.

Usage: lake env lean --run Check/CompareEnvs.lean <ChallengeModule> <SolutionModule> <Namespace> <Theorem>...
-/

def kindOf : ConstantInfo → String
  | .axiomInfo _ => "axiom" | .defnInfo _ => "def" | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque" | .quotInfo _ => "quot" | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor" | .recInfo _ => "recursor"

/-- Body comparison; theorems (proofs) are deliberately not compared. -/
def sameBody : ConstantInfo → ConstantInfo → Bool
  | .defnInfo a, .defnInfo b => a.value == b.value
  | .opaqueInfo a, .opaqueInfo b => a.value == b.value
  | .inductInfo a, .inductInfo b => a.numParams == b.numParams && a.numIndices == b.numIndices && a.ctors == b.ctors && a.all == b.all
  | .ctorInfo a, .ctorInfo b => a.induct == b.induct && a.cidx == b.cidx && a.numFields == b.numFields
  | .recInfo a, .recInfo b => a.numMotives == b.numMotives && a.numMinors == b.numMinors
  | .thmInfo _, .thmInfo _ => true
  | .axiomInfo _, .axiomInfo _ => true
  | _, _ => true

partial def axiomsOf (env : Environment) (n : Name) : StateT NameSet (Except String) Unit := do
  if (← get).contains n then return
  modify (·.insert n)
  match env.find? n with
  | none => throw s!"unknown constant {n}"
  | some ci =>
    let deps := ci.type.getUsedConstants ++ (match ci.value? (allowOpaque := true) with | some v => v.getUsedConstants | none => #[])
    for d in deps do axiomsOf env d

def main (args : List String) : IO UInt32 := do
  let [chalMod, solMod, ns] := args.take 3 | do IO.eprintln "usage"; return 2
  let thms := (args.drop 3).map String.toName
  initSearchPath (← findSysroot)
  let chal ← importModules #[{ module := chalMod.toName }] {}
  let sol ← importModules #[{ module := solMod.toName }] {}
  let pre := ns.toName
  let mut checked := 0
  let mut bad := 0
  let names := chal.constants.fold (init := (#[] : Array Name)) fun acc n _ =>
    if pre.isPrefixOf n && !n.isInternalDetail then acc.push n else acc
  for n in names.qsort Name.lt do
    let some c := chal.find? n | continue
    -- only declarations introduced by the challenge module itself
    unless (chal.getModuleIdxFor? n).map (fun i => chal.header.moduleNames[i.toNat]! == chalMod.toName) |>.getD false do continue
    checked := checked + 1
    match sol.find? n with
    | none => IO.println s!"MISSING in solution: {n}"; bad := bad + 1
    | some s =>
      let okKind := kindOf c == kindOf s
      let okLvl := c.levelParams == s.levelParams
      let okType := c.type == s.type
      let okBody := sameBody c s
      if okKind && okLvl && okType && okBody then pure ()
      else
        IO.println s!"MISMATCH {n}: kind {okKind} levels {okLvl} type {okType} body {okBody}"
        bad := bad + 1
  IO.println s!"compared {checked} challenge declarations under {ns}: {bad} mismatches"
  for t in thms do
    match (axiomsOf sol t).run {} with
    | .error e => IO.println s!"axiom scan failed for {t}: {e}"; bad := bad + 1
    | .ok ((), seen) =>
      let axs := seen.toList.filter fun n => match sol.find? n with | some (.axiomInfo _) => true | _ => false
      IO.println s!"{t} uses axioms: {axs}"
      for a in axs do
        unless a == ``propext || a == ``Classical.choice || a == ``Quot.sound do
          IO.println s!"  NON-STANDARD AXIOM {a}"; bad := bad + 1
  return (if bad == 0 then 0 else 1)
