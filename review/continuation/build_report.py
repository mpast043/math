"""Build an editable research note and an illustrated PDF from computed results."""
import argparse
from html import escape
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCES=[
    ("Claude factual handoff, pinned source",
     "https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/review/applications/README.md"),
    ("Hashim et al. Practical Introduction to Benchmarking and Characterization of Quantum Computers, PRX Quantum (2025)",
     "https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.030202"),
    ("Guha, Shapiro and Erkmen. Classical capacity of bosonic broadcast communication, Physical Review A (2007)",
     "https://arxiv.org/abs/0706.3416"),
    ("Supplied three-atom transport construction",
     "https://github.com/mpast043/math/blob/80b50443f73da7934815df0973231b13666890f6/preprints/Sharp-One-Third-Stability-of-Brenier-Maps-September-25-2026/build/source/sections/sharpness.tex"),
    ("Bunne et al. Learning single-cell perturbation responses using neural optimal transport, Nature Methods (2023)",
     "https://www.nature.com/articles/s41592-023-01969-x"),
    ("Shinar and Feinberg. Design principles for robust biochemical reaction networks, Mathematical Biosciences (2011)",
     "https://pmc.ncbi.nlm.nih.gov/articles/PMC3086454/"),
    ("Beber et al. Artefacts in statistical analyses of network motifs, Journal of the Royal Society Interface (2012)",
     "https://pmc.ncbi.nlm.nih.gov/articles/PMC3481585/"),
    ("Newman. Assortative mixing in networks, Physical Review Letters (2002)",
     "https://arxiv.org/abs/cond-mat/0205405"),
    ("Bunne et al. Conditional Monge Gap enables generalizable single-cell perturbation modelling, Nature Machine Intelligence (2026)",
     "https://www.nature.com/articles/s42256-026-01242-8")]


def sections(d):
    q=d['quantum']; qb=q['baseline']; o=d['optical']; c=d['context_rules']; net=d['networks']
    return [{
        'title':'Scientific uses of the mathematical catalogue',
        'paragraphs':[
            "The catalogue supplies tools for designing systems and deciding which scientific inference can be trusted. Its strongest immediate uses are coherent encoding of classical information, photon-efficient communication, stability assessment of rare-population assignments, constrained reaction-network repair, and degree-preserving network inference.",
            "The Claude branch is accepted as the factual handoff [1]. This continuation develops its consequences and tests the new computations. A potential wider discovery is a mass-dependent criterion for accepting rare-population transport assignments; establishing that criterion beyond the supplied construction requires the proposed data experiments.",
            "Rare-population inference is the strongest next research project because aggregate agreement can coexist with substantial changes in inferred membership. Quantum encoding is the most direct hardware experiment. Optical allocation gives the clearest ideal resource saving."
        ],
        'table':[
            ['Use','Computed result','What it makes possible'],
            ['Qubit storage',f"{100*q['local_readout_gain_fraction']:.1f}% local-readout gain",'Choose encoding from measured coherence; use ordinary classical decoding.'],
            ['Optical broadcast','12.2% to 38.9% fewer photons','Meet two user-rate demands with a smaller ideal optical budget.'],
            ['Rare-group transport','12.5% of original members replaced','Assess subgroup assignment stability alongside aggregate fit.'],
            ['Reaction repair','1 added reaction rather than 4 reverse arrows','Find a minimal permitted repair, then impose an abundance floor.'],
            ['Network inference','Assortativity estimated tail p = 0.00125','Identify a high-to-low-degree pattern missed by triangle-only analysis.']],
        'after':[
            "Original results, new computations and proposed experiments are distinguished throughout. Superposition coding, optimal transport, weak reversibility and assortativity are established methods. No world-first theorem or experimental discovery is asserted from these demonstrations."
        ]},
        {
        'title':'Classical qubit storage with measured coherence',
        'figure':'quantum_encoding.png',
        'paragraphs':[
            f"For a 5 GHz qubit stored for 100 microseconds, with T1 = 100 microseconds and effective temperature 50 mK, optimized Z-basis encoding carries {qb['z_readout']:.6f} bit per qubit. Prepare equally likely |+> and |-> and read in the X basis: with T2 = 200 microseconds the achievable rate is {qb['x_readout']:.6f}, a {100*q['local_readout_gain_fraction']:.1f}% gain.",
            "A basis rotation followed by the usual measurement implements X readout. Long classical error-correcting codes attain the resulting binary-channel rate; this demonstrated gain does not require a collective quantum measurement. It concerns classical messages, not storage of unknown quantum states.",
            "Transverse contrast is exp(-t/T2), with 1/T2 = 1/(2 T1) + 1/Tphi in the relaxation-plus-dephasing model. Thus R_X = 1 - h2((1 - exp(-t/T2))/2). Thermal effects enter through measured T1 and T2; X contrast has no additional thermal-population term.",
            f"At the stated temperature and delay, X readout beats the optimized Z code when T2 exceeds {q['x_threshold_us']:.2f} microseconds. Pure relaxation has ideal capacity {qb['gad_capacity']:.6f} bit. Added dephasing is a different channel: the plotted symmetric-pair Holevo value is an achievable collective-decoding rate, not an exact capacity theorem."
        ],
        'after':[
            "The next experiment tests whether preparation, rotation and readout errors leave a positive gain. Measure X and Z confusion matrices on the same qubits over idle time, then compare mutual information and encoded-block error. Standard coherence characterization supplies the model inputs [2]."
        ]},
        {
        'title':'Minimum optical resources for two receivers',
        'figure':'optical_budget.png',
        'paragraphs':[
            "The accepted broadcast region [1] becomes a provisioning rule. For pure-loss efficiencies eta_B >= eta_C, let g(x) = (x+1) log2(x+1) - x log2(x). Budget N and superposition fraction beta support r_B <= g(eta_B beta N), r_C <= g(eta_C N) - g(eta_C beta N). Coherent-state broadcast coding has a prior literature [3].",
            "For requested rates, reserve x = g_inverse(r_B)/eta_B photons for the near user. Then N_superposition = g_inverse(r_C + g(eta_C x))/eta_C and beta = x/N_superposition. This inverts the accepted boundary.",
            "The fair baseline allows different active powers. Minimize N_TS(f) = f g_inverse(r_B/f)/eta_B + (1-f) g_inverse(r_C/(1-f))/eta_C over the near-user fraction f. Comparing only equal active powers would overstate the saving."
        ],
        'table':[['Demand B,C','Superposition photons','Optimized TS photons','Saving']]+[
            [f"{x['near_rate']}, {x['far_rate']}",f"{x['superposition']:.3f}",f"{x['time_sharing']:.3f}",
             f"{100*x['photon_saving_fraction']:.1f}%"] for x in o['rows']],
        'after':[
            "At efficiencies 0.6/0.1 and demands 3/1 bits per mode, the budget is 12.448 versus 16.857 photons per mode. Requiring service throughout loss intervals with efficiency lower endpoints 0.5/0.08 raises the superposition budget to "
            f"{o['robust_worst_loss']['superposition']:.3f} photons per mode.",
            "These are mean-photon budgets per mode, assuming ideal joint-detection receivers, pure loss and long codes. The useful open question is how much saving survives a specific finite-block receiver. Detector hardware and added thermal noise are not simulated."
        ]},
        {
        'title':'Rare population assignments need their own error budget',
        'figure':'rare_transport.png',
        'paragraphs':[
            "Optimal transport infers cellular responses from unpaired populations [5], with conditional modelling continuing to develop [9]. The supplied construction [4] gives an exact assignment stress test. Its source is uniform on [-1,1]^2; targets are (-1,0), (1,0) and a central atom of mass m.",
            "Move the central atom upward by b without changing its mass. Its source cell changes from |x1| < m to |x1| < m + b x2. For 0 <= b <= min(m,1-m), the triangular differences give lost mass = gained mass = b/4, target W2 = b sqrt(m), and map L2 squared = b/2 + m b^2.",
            "The membership calculation is retained fraction = 1 - b/(4m), with Jaccard similarity (m - b/4)/(m + b/4). At b = m/2, 12.5% of original members leave and an equal mass enters. Jaccard similarity stays at 7/9, about 0.778, at every rarity level. The symmetric difference relative to group mass is 25%; that is distinct from 12.5% original-member replacement.",
            "For m = 0.001 and b = 0.0005, target W2 is only 0.00001581 while map L2 is 0.01581. Aggregate W2 tends to zero as rarity increases, without improving relative membership stability. Distribution agreement alone cannot certify assignments in this model."
        ],
        'after':[
            "A derived rule in this construction is W2 <= 4 delta m^(3/2) for original-member replacement below delta. For a 0.1% group and 5% replacement tolerance, the budget is 0.000006325 in model units. The mass scaling motivates adaptive validation.",
            "This is a new use of the supplied construction, whose geometry and transport distances were already in the manuscript. Test broader usefulness by reweighting held-out rare cell types, bootstrapping learned maps and scoring membership overlap. A biological guarantee and superiority of any proposed regularizer remain open."
        ]},
        {
        'title':'Repair reaction structure and set usable abundance',
        'figure':'reaction_design.png',
        'paragraphs':[
            "The accepted permanence result [1] gives a structural guarantee for weakly reversible deterministic mass-action networks. Structural design has a prior literature [6]. The continuation solves a small-instance optimization: select the lowest-cost permitted reactions that make every linkage class strongly connected.",
            "In A -> B, A -> C, B -> D, C -> D, one permitted reaction D -> A creates return paths for all four reactions. Adding every reverse arrow takes four additions. Forbid D -> A and the enumerator finds a two-reaction repair. Nodes are complexes; this example uses single-species complexes. Chemistry determines which candidate reactions are feasible.",
            "Permanence alone gives no useful rate-independent abundance floor. For A -> B -> C -> A with rates 1, 1, epsilon and total concentration 1, stationary fractions are (epsilon, epsilon, 1)/(1 + 2 epsilon). Epsilon = 0.000001 closes the cycle, yet A and B each have only about one part per million of the total concentration.",
            "Requiring all three stationary fractions >= delta gives delta/(1-2 delta) <= epsilon <= (1-delta)/(2 delta), for 0 < delta <= 1/3. A 1% floor requires 0.010204 <= epsilon <= 49.5. The lower endpoint gives fractions 0.01, 0.01, 0.98."
        ],
        'after':[
            "Scaling all rates downward leaves stationary fractions unchanged while stretching recovery time. Structural persistence, operational abundance and timely recovery are separate requirements; the exact trajectories conserve total concentration.",
            "The broader question is whether minimum chemically feasible repairs meet abundance and recovery targets when stoichiometry, thermodynamics and cost restrict candidates. Stochastic extinction at low molecule counts requires a separate model."
        ]},
        {
        'title':'A network signal beyond triangle enrichment',
        'figure':'network_motifs.png',
        'paragraphs':[
            "The null preserves every labeled vertex's degree. The accepted switch-chain result supplies the general mixing foundation [1]. Practical sampling uses four lazy chains, each with 6,240 burn-in attempts and 1,200 graphs recorded every 78 attempts. State is retained throughout. All motif counts are unweighted.",
            "Triangles and four-cycles have no strong upper-tail enrichment in this sampled null. Assortativity is much more negative than the degree-matched expectation: high-degree nodes connect to low-degree nodes more strongly than their degrees alone predict.",
            "Assortativity is established [8]; this is a worked inference on a known dataset, not a first discovery of disassortativity. Null-model choice also matters in biological motif interpretation [7]."
        ],
        'table':[['Statistic','Observed','Null mean','Estimated tail p','BY transformed']]+[
            [x['motif'].replace('_',' '),f"{x['observed']:.4g}",f"{x['null_mean']:.4g}",
             f"{x['estimated_p']:.5f}",f"{x['estimated_by_adjusted']:.5f}"] for x in net['rows']],
        'after':[
            "The assortativity tail's batch-means Monte Carlo standard error is about 0.00045. Motif effective sample sizes are about 2,070-2,212, with split R-hat 1.002-1.003. The completely enumerated 70-graph reference has exact triangle upper-tail probability 1/7.",
            "Tails and Benjamini-Yekutieli transformations are Monte Carlo estimates, not finite-run error guarantees. Diagnostics do not prove mixing. A hypothesis selected after seeing the data needs independent confirmation. Extra constraints, such as compartments or connectedness, change the state space and need their own sampling justification."
        ]},
        {
        'title':'Further uses in materials and atomic physics',
        'paragraphs':[
            "Anderson localization. The accepted two-dimensional infinite-volume result determines the limiting interpretation; finite samples can still appear metallic. Use the supplied size-dependent statistics to plan a localization-length study, not to infer the infinite phase from one sample. The next question is where sample length and coherence scale produce an observable crossover within the stated Anderson model.",
            f"Spin-chain boundaries. At L = {c['haldane']['L']}, accepted open-chain edge splitting is {100*c['haldane']['edge_to_bulk_ratio']:.2f}% of the reported bulk excitation gap. Extrapolating the supplied edge-decay length places a 1% ratio near even L = {c['haldane']['projected_even_L_for_one_percent']}. This is a design projection beyond the data, not a new gap theorem. Longer-chain calculations and symmetry-preserving perturbations test useful edge isolation.",
            f"Cold atoms. A 2% leading-order depletion signal at density 10^14 cm^-3 requires scattering length {c['bose']['a_Bohr_radii']:.1f} Bohr radii and rho a^3 = {c['bose']['rho_a_cubed']:.6f}. This is a concrete scattering-length target. Measure the momentum tail and a temperature series to distinguish quantum depletion from thermal and trap effects.",
            f"Fermion density bounds. The accepted kinetic constant {c['lieb_thirring']['kinetic_constants']['new']:.4f}, compared with {c['lieb_thirring']['kinetic_constants']['old']:.4f}, strengthens the lower kinetic-energy bound by {100*c['lieb_thirring']['kinetic_lower_bound_gain']:.2f}%. For an assumed uniform spherical density at fixed particle count and kinetic budget, the derived minimum-radius bound strengthens by {100*c['lieb_thirring']['uniform_density_radius_bound_gain']:.2f}% because the density integral scales as R^-2. Spin convention and hbar^2/(2m) normalization must match.",
            "Apply the tighter bound to exclude inadmissible trial densities or narrow variational energy intervals. The three-dimensional equality question remains open in the handoff; this calculation does not settle it."
        ]},
        {
        'title':'Further uses in crystals dynamics and algorithms',
        'paragraphs':[
            "Screened-charge crystals. Use the triangular reference to quantify competing geometries before adding substrate pinning or attraction. At kappa = 0.5, the accepted square-triangular energy difference is 0.22294%. If both absolute energy errors are normalized to the triangular energy, each must be below about 0.11147% to distinguish ordering by that gap alone. At kappa = 4 the corresponding threshold is 3.80995%. Separate errors relative to each structure's own energy require the slightly stricter gap/(2 + gap/100) bound. These are numerical planning rules, not melting predictions.",
            "Chaotic forecasts. An initial error of 10^-10 reaching tolerance 10^-3 needs log(10^7) growth. The accepted area-average entropy gives heuristic horizons of "
            +", ".join(f"{h['kicks']:.2f} kicks at K = {h['K']:.0f}" for h in c['chaos']['heuristic_horizons'])
            +". The useful question is the distribution of orbitwise horizons near stable islands. Positive metric entropy alone does not provide those quantiles, ensure rapid mixing or predict an individual orbit's error.",
            "Smooth-number algorithms. Joint and prime-predecessor laws can guide finite benchmark ensembles and parameters. Asymptotic forecasts are ranking priors, not certificates for an integer or key. Pollard stage 1 depends on prime powers dividing its exponent, a stronger operational condition than bounding only the largest prime factor. Compare random and structured ensembles and measure finite-size model error.",
            "These seven additional uses translate inherited demonstrations into operational targets. The machine-readable twelve-use agenda supplies a specific next experiment for every application."
        ]},
        {
        'title':'Candidate discoveries worth pursuing',
        'paragraphs':[
            "First priority: a mass-adaptive criterion for accepting inferred rare-cell transitions. The new calculation is membership overlap and its m^(3/2) error budget in the supplied family. The broader hypothesis is that overlap conditioned on group mass detects unstable biological predictions missed by aggregate losses.",
            "Keep aggregate fit similar while changing rare-group prevalence. Compare standard validation with stratified overlap validation on held-out populations and paired or lineage-informed references where available. Success means fewer unsupported rare-cell assignments at matched predictive performance; a possible tradeoff is more bias or less sensitivity to real transitions.",
            "Second priority: coherence-aware classical storage. The new use is an accessible encoding switch based on measured T2. Test whether preparation and readout overhead leave a positive mutual-information gain. Success could reduce physical-qubit requirements or extend the refresh interval for a classical message under observed device noise.",
            "Third priority: minimum feasible reaction repairs with operating targets. The repair is exact for its permitted candidates. Wider usefulness needs feasibility constraints, abundance floors and transient targets in one optimization. Success means fewer added reactions while preserving a specified concentration over a specified time.",
            "The optical optimizer and network inference are usable calculations under their declared models. The significance is resource allocation and improved scientific interpretation. The coding scheme, transport construction, graph concepts and statistical observables are not presented as inventions of this continuation."
        ]},
        {
        'title':'Reproducibility and source context',
        'paragraphs':[
            "Source: claude/math-repo-review at "+d['source_commit']+". Continuation: codex/scientific-use-continuation. The source manuscripts and Claude application files remain intact. Results record Python and dependency versions, numerical parameters and all four network seeds.",
            "Tests check new entropy calculations, dephasing inputs, optical inversion and rate demands, independent polygon overlaps, exact reaction repairs, conserved dynamics, labeled degrees, unweighted motifs and a completely enumerated null. Regression checks cover small optical demands and the quantum threshold's numerical endpoint.",
            "From the repository root, run python3 -m pytest review/continuation/tests -q and python3 -m review.continuation.run. Rebuild with python3 -m review.continuation.build_report using ReportLab. results/results.json contains outputs and the twelve-use experiment agenda. Figures are supplied as PNG and SVG.",
            "External sources establish application context and prior methods. They do not audit or replace the factual handoff. The computations establish consequences within stated models; laboratory outcomes and global novelty require the proposed research."
        ],
        'sources':True}]


def write_markdown(parts,path):
    blocks=[]
    for i,section in enumerate(parts):
        blocks.append(('# ' if i==0 else '## ')+section['title'])
        blocks.extend(section['paragraphs'])
        if section.get('figure'):
            blocks.append(f"![{section['title']}](figures/{section['figure']})")
        if section.get('table'):
            table=section['table']
            lines=['| '+' | '.join(table[0])+' |','| '+' | '.join(['---']*len(table[0]))+' |']
            lines.extend('| '+' | '.join(row)+' |' for row in table[1:])
            blocks.append('\n'.join(lines))
        blocks.extend(section.get('after',[]))
        if section.get('sources'):
            blocks.append('\n'.join(f"{j}. [{name}]({url})" for j,(name,url) in enumerate(SOURCES,1)))
    text='\n\n'.join(blocks)+'\n'
    for i,(_,url) in enumerate(SOURCES,1):
        text=text.replace('['+str(i)+']','['+str(i)+']('+url+')')
    path.write_text(text)


def build(results_path=HERE/'results'/'results.json',output_pdf=HERE/'output'/'pdf'/'scientific_uses.pdf'):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image
    d=json.loads(Path(results_path).read_text()); parts=sections(d)
    output_pdf=Path(output_pdf); output_pdf.parent.mkdir(parents=True,exist_ok=True)
    font='Helvetica'; bold='Helvetica-Bold'
    regular=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
    strong=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    if regular.exists() and strong.exists():
        pdfmetrics.registerFont(TTFont('ReportArial',str(regular)))
        pdfmetrics.registerFont(TTFont('ReportArialBold',str(strong)))
        font='ReportArial'; bold='ReportArialBold'
    body=ParagraphStyle('ResearchBody',fontName=font,fontSize=9.8,leading=13.7,spaceAfter=8,
                        textColor=colors.HexColor('#25323f'))
    title=ParagraphStyle('ResearchTitle',fontName=bold,fontSize=22,leading=26,spaceAfter=18,
                         textColor=colors.HexColor('#173d5a'))
    heading=ParagraphStyle('ResearchHeading',parent=title,fontSize=18,leading=22,spaceAfter=13)
    small=ParagraphStyle('ResearchSmall',parent=body,fontSize=8.2,leading=11,spaceAfter=7)
    cell_style=ParagraphStyle('ResearchCell',parent=body,fontSize=8.5,leading=11,spaceAfter=0)
    def inline(text):
        value=escape(text)
        for i,(_,url) in enumerate(SOURCES,1):
            value=value.replace('['+str(i)+']',f'<a href="{escape(url,quote=True)}" color="#235789">[{i}]</a>')
        return value
    story=[]; width=letter[0]-88
    for i,section in enumerate(parts):
        if i: story.append(PageBreak())
        story.append(Paragraph(inline(section['title']),title if i==0 else heading))
        if i==0:
            story.append(Paragraph('7 October 2026 | Five worked extensions and a twelve-use research agenda',small))
        for text in section['paragraphs']:
            story.append(Paragraph(inline(text),body))
        if section.get('figure'):
            image_path=HERE/'figures'/section['figure']
            iw,ih=ImageReader(str(image_path)).getSize()
            story.append(Image(str(image_path),width=width,height=width*ih/iw))
            story.append(Spacer(1,10))
        if section.get('table'):
            raw=section['table']; n=len(raw[0])
            widths={3:[95,130,width-225],4:[90,135,155,width-380],5:[115,75,90,115,width-395]}[n]
            rows=[[Paragraph(inline(str(x)),cell_style) for x in row] for row in raw]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff5')),
                ('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#b6c7d5')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8fa')]),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.append(table); story.append(Spacer(1,12))
        for text in section.get('after',[]):
            story.append(Paragraph(inline(text),body))
        if section.get('sources'):
            for j,(name,url) in enumerate(SOURCES,1):
                story.append(Paragraph(f'[{j}] <a href="{escape(url,quote=True)}" color="#235789">{escape(name)}</a>',small))
    def page(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#d8e1e8')); canvas.line(44,38,568,38)
        canvas.setFont(font,8); canvas.setFillColor(colors.HexColor('#627587'))
        canvas.drawString(44,26,'Scientific uses of the mathematical catalogue')
        canvas.drawRightString(568,26,str(doc.page)); canvas.restoreState()
    document=SimpleDocTemplate(str(output_pdf),pagesize=letter,rightMargin=44,leftMargin=44,
                              topMargin=42,bottomMargin=50,title=parts[0]['title'],author='Scientific application continuation')
    document.build(story,onFirstPage=page,onLaterPages=page)
    write_markdown(parts,HERE/'research_note.md')
    (HERE/'results'/'references.json').write_text(json.dumps(
        [{'id':i+1,'title':name,'url':url,'accessed':'2026-10-07'} for i,(name,url) in enumerate(SOURCES)],indent=2)+'\n')
    print(output_pdf)
    return output_pdf


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,default=HERE/'results'/'results.json')
    parser.add_argument('--pdf',type=Path,default=HERE/'output'/'pdf'/'scientific_uses.pdf')
    args=parser.parse_args()
    build(args.results,args.pdf)


if __name__=='__main__':
    main()
