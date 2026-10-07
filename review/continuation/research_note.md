# Scientific uses of the mathematical catalogue

The catalogue supplies tools for designing systems and deciding which scientific inference can be trusted. Its strongest immediate uses are coherent encoding of classical information, photon-efficient communication, stability assessment of rare-population assignments, constrained reaction-network repair, and degree-preserving network inference.

The Claude branch is accepted as the factual handoff [1](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/review/applications/README.md). This continuation develops its consequences and tests the new computations. A potential wider discovery is a mass-dependent criterion for accepting rare-population transport assignments; establishing that criterion beyond the supplied construction requires the proposed data experiments.

Rare-population inference is the strongest next research project because aggregate agreement can coexist with substantial changes in inferred membership. Quantum encoding is the most direct hardware experiment. Optical allocation gives the clearest ideal resource saving.

| Use | Computed result | What it makes possible |
| --- | --- | --- |
| Qubit storage | 37.9% local-readout gain | Choose encoding from measured coherence; use ordinary classical decoding. |
| Optical broadcast | 12.2% to 38.9% fewer photons | Meet two user-rate demands with a smaller ideal optical budget. |
| Rare-group transport | 12.5% of original members replaced | Assess subgroup assignment stability alongside aggregate fit. |
| Reaction repair | 1 added reaction rather than 4 reverse arrows | Find a minimal permitted repair, then impose an abundance floor. |
| Network inference | Assortativity estimated tail p = 0.00125 | Identify a high-to-low-degree pattern missed by triangle-only analysis. |

Original results, new computations and proposed experiments are distinguished throughout. Superposition coding, optimal transport, weak reversibility and assortativity are established methods. No world-first theorem or experimental discovery is asserted from these demonstrations.

## Classical qubit storage with measured coherence

For a 5 GHz qubit stored for 100 microseconds, with T1 = 100 microseconds and effective temperature 50 mK, optimized Z-basis encoding carries 0.206424 bit per qubit. Prepare equally likely |+> and |-> and read in the X basis: with T2 = 200 microseconds the achievable rate is 0.284651, a 37.9% gain.

A basis rotation followed by the usual measurement implements X readout. Long classical error-correcting codes attain the resulting binary-channel rate; this demonstrated gain does not require a collective quantum measurement. It concerns classical messages, not storage of unknown quantum states.

Transverse contrast is exp(-t/T2), with 1/T2 = 1/(2 T1) + 1/Tphi in the relaxation-plus-dephasing model. Thus R_X = 1 - h2((1 - exp(-t/T2))/2). Thermal effects enter through measured T1 and T2; X contrast has no additional thermal-population term.

At the stated temperature and delay, X readout beats the optimized Z code when T2 exceeds 153.72 microseconds. Pure relaxation has ideal capacity 0.361375 bit. Added dephasing is a different channel: the plotted symmetric-pair Holevo value is an achievable collective-decoding rate, not an exact capacity theorem.

![Classical qubit storage with measured coherence](figures/quantum_encoding.png)

The next experiment tests whether preparation, rotation and readout errors leave a positive gain. Measure X and Z confusion matrices on the same qubits over idle time, then compare mutual information and encoded-block error. Standard coherence characterization supplies the model inputs [2](https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.030202).

## Minimum optical resources for two receivers

The accepted broadcast region [1](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/review/applications/README.md) becomes a provisioning rule. For pure-loss efficiencies eta_B >= eta_C, let g(x) = (x+1) log2(x+1) - x log2(x). Budget N and superposition fraction beta support r_B <= g(eta_B beta N), r_C <= g(eta_C N) - g(eta_C beta N). Coherent-state broadcast coding has a prior literature [3](https://arxiv.org/abs/0706.3416).

For requested rates, reserve x = g_inverse(r_B)/eta_B photons for the near user. Then N_superposition = g_inverse(r_C + g(eta_C x))/eta_C and beta = x/N_superposition. This inverts the accepted boundary.

The fair baseline allows different active powers. Minimize N_TS(f) = f g_inverse(r_B/f)/eta_B + (1-f) g_inverse(r_C/(1-f))/eta_C over the near-user fraction f. Comparing only equal active powers would overstate the saving.

![Minimum optical resources for two receivers](figures/optical_budget.png)

| Demand B,C | Superposition photons | Optimized TS photons | Saving |
| --- | --- | --- | --- |
| 1, 0.5 | 2.021 | 2.302 | 12.2% |
| 2, 1 | 7.226 | 9.323 | 22.5% |
| 3, 1 | 12.448 | 16.857 | 26.2% |
| 4, 2 | 49.804 | 81.560 | 38.9% |

At efficiencies 0.6/0.1 and demands 3/1 bits per mode, the budget is 12.448 versus 16.857 photons per mode. Requiring service throughout loss intervals with efficiency lower endpoints 0.5/0.08 raises the superposition budget to 15.130 photons per mode.

These are mean-photon budgets per mode, assuming ideal joint-detection receivers, pure loss and long codes. The useful open question is how much saving survives a specific finite-block receiver. Detector hardware and added thermal noise are not simulated.

## Rare population assignments need their own error budget

Optimal transport infers cellular responses from unpaired populations [5](https://www.nature.com/articles/s41592-023-01969-x), with conditional modelling continuing to develop [9](https://www.nature.com/articles/s42256-026-01242-8). The supplied construction [4](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/preprints/Sharp-One-Third-Stability-of-Brenier-Maps-September-25-2026/build/source/sections/sharpness.tex) gives an exact assignment stress test. Its source is uniform on [-1,1]^2; targets are (-1,0), (1,0) and a central atom of mass m.

Move the central atom upward by b without changing its mass. Its source cell changes from |x1| < m to |x1| < m + b x2. For 0 <= b <= min(m,1-m), the triangular differences give lost mass = gained mass = b/4, target W2 = b sqrt(m), and map L2 squared = b/2 + m b^2.

The membership calculation is retained fraction = 1 - b/(4m), with Jaccard similarity (m - b/4)/(m + b/4). At b = m/2, 12.5% of original members leave and an equal mass enters. Jaccard similarity stays at 7/9, about 0.778, at every rarity level. The symmetric difference relative to group mass is 25%; that is distinct from 12.5% original-member replacement.

For m = 0.001 and b = 0.0005, target W2 is only 0.00001581 while map L2 is 0.01581. Aggregate W2 tends to zero as rarity increases, without improving relative membership stability. Distribution agreement alone cannot certify assignments in this model.

![Rare population assignments need their own error budget](figures/rare_transport.png)

A derived rule in this construction is W2 <= 4 delta m^(3/2) for original-member replacement below delta. For a 0.1% group and 5% replacement tolerance, the budget is 0.000006325 in model units. The mass scaling motivates adaptive validation.

This is a new use of the supplied construction, whose geometry and transport distances were already in the manuscript. Test broader usefulness by reweighting held-out rare cell types, bootstrapping learned maps and scoring membership overlap. A biological guarantee and superiority of any proposed regularizer remain open.

## Repair reaction structure and set usable abundance

The accepted permanence result [1](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/review/applications/README.md) gives a structural guarantee for weakly reversible deterministic mass-action networks. Structural design has a prior literature [6](https://pmc.ncbi.nlm.nih.gov/articles/PMC3086454/). The continuation solves a small-instance optimization: select the lowest-cost permitted reactions that make every linkage class strongly connected.

In A -> B, A -> C, B -> D, C -> D, one permitted reaction D -> A creates return paths for all four reactions. Adding every reverse arrow takes four additions. Forbid D -> A and the enumerator finds a two-reaction repair. Nodes are complexes; this example uses single-species complexes. Chemistry determines which candidate reactions are feasible.

Permanence alone gives no useful rate-independent abundance floor. For A -> B -> C -> A with rates 1, 1, epsilon and total concentration 1, stationary fractions are (epsilon, epsilon, 1)/(1 + 2 epsilon). Epsilon = 0.000001 closes the cycle, yet A and B each have only about one part per million of the total concentration.

Requiring all three stationary fractions >= delta gives delta/(1-2 delta) <= epsilon <= (1-delta)/(2 delta), for 0 < delta <= 1/3. A 1% floor requires 0.010204 <= epsilon <= 49.5. The lower endpoint gives fractions 0.01, 0.01, 0.98.

![Repair reaction structure and set usable abundance](figures/reaction_design.png)

Scaling all rates downward leaves stationary fractions unchanged while stretching recovery time. Structural persistence, operational abundance and timely recovery are separate requirements; the exact trajectories conserve total concentration.

The broader question is whether minimum chemically feasible repairs meet abundance and recovery targets when stoichiometry, thermodynamics and cost restrict candidates. Stochastic extinction at low molecule counts requires a separate model.

## A network signal beyond triangle enrichment

The null preserves every labeled vertex's degree. The accepted switch-chain result supplies the general mixing foundation [1](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/review/applications/README.md). Practical sampling uses four lazy chains, each with 6,240 burn-in attempts and 1,200 graphs recorded every 78 attempts. State is retained throughout. All motif counts are unweighted.

Triangles and four-cycles have no strong upper-tail enrichment in this sampled null. Assortativity is much more negative than the degree-matched expectation: high-degree nodes connect to low-degree nodes more strongly than their degrees alone predict.

Assortativity is established [8](https://arxiv.org/abs/cond-mat/0205405); this is a worked inference on a known dataset, not a first discovery of disassortativity. Null-model choice also matters in biological motif interpretation [7](https://pmc.ncbi.nlm.nih.gov/articles/PMC3481585/).

![A network signal beyond triangle enrichment](figures/network_motifs.png)

| Statistic | Observed | Null mean | Estimated tail p | BY transformed |
| --- | --- | --- | --- | --- |
| triangles | 45 | 39.32 | 0.12122 | 0.33337 |
| four cycles | 154 | 148.2 | 0.35909 | 0.65834 |
| assortativity | -0.4756 | -0.3019 | 0.00125 | 0.00687 |

The assortativity tail's batch-means Monte Carlo standard error is about 0.00045. Motif effective sample sizes are about 2,070-2,212, with split R-hat 1.002-1.003. The completely enumerated 70-graph reference has exact triangle upper-tail probability 1/7.

Tails and Benjamini-Yekutieli transformations are Monte Carlo estimates, not finite-run error guarantees. Diagnostics do not prove mixing. A hypothesis selected after seeing the data needs independent confirmation. Extra constraints, such as compartments or connectedness, change the state space and need their own sampling justification.

## Further uses in materials and atomic physics

Anderson localization. The accepted two-dimensional infinite-volume result determines the limiting interpretation; finite samples can still appear metallic. Use the supplied size-dependent statistics to plan a localization-length study, not to infer the infinite phase from one sample. The next question is where sample length and coherence scale produce an observable crossover within the stated Anderson model.

Spin-chain boundaries. At L = 16, accepted open-chain edge splitting is 8.28% of the reported bulk excitation gap. Extrapolating the supplied edge-decay length places a 1% ratio near even L = 30. This is a design projection beyond the data, not a new gap theorem. Longer-chain calculations and symmetry-preserving perturbations test useful edge isolation.

Cold atoms. A 2% leading-order depletion signal at density 10^14 cm^-3 requires scattering length 228.5 Bohr radii and rho a^3 = 0.000177. This is a concrete scattering-length target. Measure the momentum tail and a temperature series to distinguish quantum depletion from thermal and trap effects.

Fermion density bounds. The accepted kinetic constant 8.2821, compared with 7.0960, strengthens the lower kinetic-energy bound by 16.72%. For an assumed uniform spherical density at fixed particle count and kinetic budget, the derived minimum-radius bound strengthens by 8.03% because the density integral scales as R^-2. Spin convention and hbar^2/(2m) normalization must match.

Apply the tighter bound to exclude inadmissible trial densities or narrow variational energy intervals. The three-dimensional equality question remains open in the handoff; this calculation does not settle it.

## Further uses in crystals dynamics and algorithms

Screened-charge crystals. Use the triangular reference to quantify competing geometries before adding substrate pinning or attraction. At kappa = 0.5, the accepted square-triangular energy difference is 0.22294%. If both absolute energy errors are normalized to the triangular energy, each must be below about 0.11147% to distinguish ordering by that gap alone. At kappa = 4 the corresponding threshold is 3.80995%. Separate errors relative to each structure's own energy require the slightly stricter gap/(2 + gap/100) bound. These are numerical planning rules, not melting predictions.

Chaotic forecasts. An initial error of 10^-10 reaching tolerance 10^-3 needs log(10^7) growth. The accepted area-average entropy gives heuristic horizons of 9.95 kicks at K = 10, 6.99 kicks at K = 20, 4.12 kicks at K = 100. The useful question is the distribution of orbitwise horizons near stable islands. Positive metric entropy alone does not provide those quantiles, ensure rapid mixing or predict an individual orbit's error.

Smooth-number algorithms. Joint and prime-predecessor laws can guide finite benchmark ensembles and parameters. Asymptotic forecasts are ranking priors, not certificates for an integer or key. Pollard stage 1 depends on prime powers dividing its exponent, a stronger operational condition than bounding only the largest prime factor. Compare random and structured ensembles and measure finite-size model error.

These seven additional uses translate inherited demonstrations into operational targets. The machine-readable twelve-use agenda supplies a specific next experiment for every application.

## Candidate discoveries worth pursuing

First priority: a mass-adaptive criterion for accepting inferred rare-cell transitions. The new calculation is membership overlap and its m^(3/2) error budget in the supplied family. The broader hypothesis is that overlap conditioned on group mass detects unstable biological predictions missed by aggregate losses.

Keep aggregate fit similar while changing rare-group prevalence. Compare standard validation with stratified overlap validation on held-out populations and paired or lineage-informed references where available. Success means fewer unsupported rare-cell assignments at matched predictive performance; a possible tradeoff is more bias or less sensitivity to real transitions.

Second priority: coherence-aware classical storage. The new use is an accessible encoding switch based on measured T2. Test whether preparation and readout overhead leave a positive mutual-information gain. Success could reduce physical-qubit requirements or extend the refresh interval for a classical message under observed device noise.

Third priority: minimum feasible reaction repairs with operating targets. The repair is exact for its permitted candidates. Wider usefulness needs feasibility constraints, abundance floors and transient targets in one optimization. Success means fewer added reactions while preserving a specified concentration over a specified time.

The optical optimizer and network inference are usable calculations under their declared models. The significance is resource allocation and improved scientific interpretation. The coding scheme, transport construction, graph concepts and statistical observables are not presented as inventions of this continuation.

## Reproducibility and source context

Source: claude/math-repo-review at 80b50443f73da7934815df0973231b13666890f6. Continuation: codex/scientific-use-continuation. The source manuscripts and Claude application files remain intact. Results record Python and dependency versions, numerical parameters and all four network seeds.

Tests check new entropy calculations, dephasing inputs, optical inversion and rate demands, independent polygon overlaps, exact reaction repairs, conserved dynamics, labeled degrees, unweighted motifs and a completely enumerated null. Regression checks cover small optical demands and the quantum threshold's numerical endpoint.

From the repository root, run python3 -m pytest review/continuation/tests -q and python3 -m review.continuation.run. Rebuild with python3 -m review.continuation.build_report using ReportLab. results/results.json contains outputs and the twelve-use experiment agenda. Figures are supplied as PNG and SVG.

External sources establish application context and prior methods. They do not audit or replace the factual handoff. The computations establish consequences within stated models; laboratory outcomes and global novelty require the proposed research.

1. [Claude factual handoff, pinned source](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/review/applications/README.md)
2. [Hashim et al. Practical Introduction to Benchmarking and Characterization of Quantum Computers, PRX Quantum (2025)](https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.030202)
3. [Guha, Shapiro and Erkmen. Classical capacity of bosonic broadcast communication, Physical Review A (2007)](https://arxiv.org/abs/0706.3416)
4. [Supplied three-atom transport construction](https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/preprints/Sharp-One-Third-Stability-of-Brenier-Maps-September-25-2026/build/source/sections/sharpness.tex)
5. [Bunne et al. Learning single-cell perturbation responses using neural optimal transport, Nature Methods (2023)](https://www.nature.com/articles/s41592-023-01969-x)
6. [Shinar and Feinberg. Design principles for robust biochemical reaction networks, Mathematical Biosciences (2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3086454/)
7. [Beber et al. Artefacts in statistical analyses of network motifs, Journal of the Royal Society Interface (2012)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3481585/)
8. [Newman. Assortative mixing in networks, Physical Review Letters (2002)](https://arxiv.org/abs/cond-mat/0205405)
9. [Bunne et al. Conditional Monge Gap enables generalizable single-cell perturbation modelling, Nature Machine Intelligence (2026)](https://www.nature.com/articles/s42256-026-01242-8)
