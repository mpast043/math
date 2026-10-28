# Verification scope

Base: PR #3 at `8da3655da943ca203e5fc56f3f76ea1405e42a44`.
This extension adds files only. The draft PR identifies its final commit and
Linux workflow runs; main and the prior three PR branches are preserved.

Toolchain: Lean 4.34.1, compiler `5045d0056413266e57c625dcd7c365b10e377c52`,
Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`, Lake 5.0.0-src+5045d00.
Local standard-library tests use Python 3.14.3. Existing NumPy 2.4.2 ran the
optional supplement; no new numerical software was installed.

Commands from `lean/HydrogenPathway`:

```sh
lake build HydrogenPathway.Operational
lake env lean HydrogenPathway/Operational/Declarations.lean
python3 -m unittest discover -s operational -p 'test_*.py' -v
python3 operational/model.py --check --output operational/RESULTS.json
bash scripts/verify-operational.sh
```

Sixteen main statements compile and pass independent declaration/axiom audits.
All transitive axiom sets contain only `propext`, `Classical.choice`, and
`Quot.sound`. The finite complex matrix proofs cover arbitrary complete
idempotents, coordinate blocks and actual rectangular branch compression;
the record statements are finite conditional probability bounds. The
approximate theorem is entrywise, not the operator/trace-norm inequality.
No proof holes/custom axioms or supplied trace-equality conclusions.

Twelve standard-library tests pass, including 40 arbitrary complex matrix
pairs and the nonmultiplicative-compression counterexample. Saved reference
results reproduce within `2e-9` with exact JSON structure/labels/booleans.
Source hashes verify exact file identity; placeholder scans fail closed.
Successful output is retained in `verification.log`, without host paths.

The source ZIP was transferred through the current Library helper and its
15435 readable bytes match SHA256
`b83d5013423f99a753f13cbb724cd807081e7497099d76c8cdbb57ba13af0082`.
Library file/version metadata remain on the local archive; public
`PROVENANCE.json` records stable identity and selected original-file hashes.
Original reports are distinct from this executor's NumPy rerun reports.
Both `python3 check_bridge.py` (29 checks) and
`python3 check_single_photon_loss.py` (40 checks) passed from a separate
scratch extraction. The original source scripts are unchanged. Those 69
checks are numerical evidence, not certificates or additional Lean theorems.
CI validates that stored evidence and provenance but does not rerun NumPy.

Density/effect admissibility, actual accessible controls and subspaces,
physical stability, photon instruments, and hydrogen preparation/capture are
caller obligations. The algebra does not select one global outcome, prove
an interpretation, or establish record lifetime. Coarse blocks can retain
within-block quantum coherence; later coherent controls can change access.
