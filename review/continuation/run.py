"""Run the five continuations and derive decision rules for all twelve uses.

From the repository root: python3 -m review.continuation.run
"""
import argparse
import importlib.metadata
import json
import math
from pathlib import Path
import platform

import numpy as np

from . import networks,optical,quantum,reactions,transport

SOURCE='80b50443f73da7934815df0973231b13666890f6'
HERE=Path(__file__).resolve().parent
HANDOFF=HERE.parent/'applications'/'results'


def context_rules():
    """Use accepted existing outputs; do not rerun their proof-checking experiments."""
    def read(name):
        return json.loads((HANDOFF/(name+'.json')).read_text())
    haldane=read('haldane_gap'); last=haldane['open'][-1]
    edge_ratio=last['edge_split']/last['bulk_gap']
    projected=last['L']+haldane['edge_decay_length']*math.log(edge_ratio/.01)
    depletion=.02; density=1e20; factor=8/(3*math.sqrt(math.pi))
    gas_parameter=(depletion/factor)**2
    scattering_length=(gas_parameter/density)**(1/3)
    kinetic=read('lieb_thirring')['K']
    crystal=read('screened_coulomb_crystals')['rows']
    chaos=read('standard_map_entropy')['rows']
    anderson=read('anderson_level_statistics')['rows']
    smooth=read('smooth_numbers_crypto')['applications']
    return {
        'anderson':{'2d_weak_disorder':[r for r in anderson if r['d']==2 and r['W']==4],
                    'use':'Distinguish finite-sample metallic appearance from the accepted infinite-volume limit.'},
        'haldane':{'L':last['L'],'edge_to_bulk_ratio':edge_ratio,
                   'projected_even_L_for_one_percent':int(2*math.ceil(projected/2)),
                   'projection_status':'Exponential extrapolation of accepted L<=16 data; new larger-chain calculation required.'},
        'bose':{'depletion_target':depletion,'density_m^-3':density,'rho_a_cubed':gas_parameter,
                'a_m':scattering_length,'a_Bohr_radii':scattering_length/5.29177210903e-11,
                'status':'Leading-order homogeneous dilute-gas prediction.'},
        'lieb_thirring':{'kinetic_constants':kinetic,'kinetic_lower_bound_gain':kinetic['new']/kinetic['old']-1,
                        'uniform_density_radius_bound_gain':math.sqrt(kinetic['new']/kinetic['old'])-1,
                        'status':'Bounds for one spin state, hbar^2/(2m)=1; not measured material properties.'},
        'crystals':{'rows':[{'kappa':r['kappa'],'square_gap_percent':r['square'],
                            'per_energy_estimate_error_percent_must_be_below':r['square']/2} for r in crystal],
                    'status':'Numerical resolution for comparing the two accepted lattice energies, not a melting prediction.'},
        'chaos':{'initial_error':1e-10,'tolerance':1e-3,
                 'heuristic_horizons':[{'K':r['K'],'entropy':r['entropy'],
                                        'kicks':math.log(1e7)/r['entropy']} for r in chaos if r['K'] in (10,20,100)],
                 'status':'Area-average entropy gives a heuristic; orbitwise finite-time quantiles still need measurement.'},
        'smooth_numbers':{'accepted_model_predictions':smooth,
                          'status':'Asymptotic smoothness priors; finite-key error bounds and stage-1 prime-power conditions remain to be studied.'}}


def agenda():
    return [
        {'family':'276','use':'Classical qubit storage','delivered':'Dephasing-aware X/Z encoding rule and achievable rates.',
         'question':'Can encoding selected from measured T1,T2 and readout error improve stored classical information?',
         'next_experiment':'Randomize X and Z encodings on the same qubits, measure confusion matrices versus idle time, and estimate mutual information with confidence intervals.'},
        {'family':'273','use':'Optical broadcast','delivered':'Minimum photon budget against fraction-and-power-optimized time sharing.',
         'question':'How much of the ideal photon saving survives finite-block joint detection and uncertain optical loss?',
         'next_experiment':'Apply identical two-user rate demands and photon counting to both schemes; fit receiver penalties separately from transmission loss.'},
        {'family':'261','use':'Disordered materials','delivered':'Accepted finite-size data translated into an experimental scale question.',
         'question':'At what length, phase-coherence time and disorder does a 2D sample cross from apparent metal to insulating response?',
         'next_experiment':'Measure quasi-1D transfer-matrix localization lengths, then vary sample length and dephasing; keep symmetry class and Hamiltonian within the stated model.'},
        {'family':'268','use':'Spin-chain boundary states','delivered':'Edge/bulk separation and a labeled chain-length projection.',
         'question':'Which symmetry-preserving disorder or anisotropy retains a usable edge state while leaving the bulk gapped?',
         'next_experiment':'Use DMRG on L=20,30,40 with controlled perturbations; resolve edge splitting and bulk excitation separately.'},
        {'family':'267','use':'Cold-atom experimental design','delivered':'Inverted depletion law for a 2% signal at a specified density.',
         'question':'Can quantum depletion be separated from thermal and trap-induced depletion at accessible signal strength?',
         'next_experiment':'Sweep scattering length across the calculated target and measure condensate fraction and high-k contact jointly, including a temperature series.'},
        {'family':'262','use':'Density-functional and fermion simulation','delivered':'Improved kinetic and density-compression lower bounds.',
         'question':'Can the tighter bound prune inadmissible trial densities or certify useful energy intervals?',
         'next_experiment':'For fixed spin convention, compute kinetic energy and integral rho^(5/3) in benchmark trial states; compare interval widths under both constants.'},
        {'family':'090','use':'Screened-charge crystals','delivered':'Energy precision required to distinguish square and triangular lattices.',
         'question':'How do substrate pinning, defects or a weak attractive interaction compete with the triangular reference?',
         'next_experiment':'Compute defect formation energies at fixed density and screening, then introduce perturbations explicitly outside universal-optimality assumptions.'},
        {'family':'146','use':'Chaotic forecast limits','delivered':'An entropy-to-precision planning rule from accepted numerical outputs.',
         'question':'Can orbitwise error-growth quantiles predict reliable forecast horizons near stable islands?',
         'next_experiment':'Use paired perturbed trajectories at K=10,20,100 and accelerator-mode windows; compare first-passage times with finite-time Lyapunov quantiles.'},
        {'family':'149','use':'Reaction-network design','delivered':'Exact permitted-edge repair and a quantitative stationary abundance floor.',
         'question':'Can a chemically feasible minimum repair maintain desired species abundance over an operational timescale?',
         'next_experiment':'Constrain candidate reactions by stoichiometry and thermodynamics, then test rates and abundance floors; add stochastic extinction analysis for small copy numbers.'},
        {'family':'131','use':'Network motif inference','delivered':'Three degree-preserving motif tails with multi-chain diagnostics.',
         'question':'Which purported biological motifs remain unusual after the relevant structural constraints are preserved?',
         'next_experiment':'Start with an undirected interaction dataset and prespecified motifs; compare degree-only and compartment-aware nulls, establishing mixing separately for additional constraints.'},
        {'family':'011,012','use':'Smooth-number algorithm selection','delivered':'Accepted model outputs retained as finite-benchmark priors.',
         'question':'How accurately do asymptotic smoothness laws rank algorithms at finite problem sizes?',
         'next_experiment':'Benchmark random and structured integer ensembles with explicit prime-power conditions for Pollard stage 1; quantify finite-size model error.'},
        {'family':'374','use':'Rare-population transport inference','delivered':'Exact membership turnover, Jaccard similarity and a mass-dependent error budget.',
         'question':'Can rare-population membership checks prevent stable-looking aggregate transport predictions from masking unstable assignments?',
         'next_experiment':'Reweight held-out rare groups over several orders of magnitude; bootstrap maps and score group-membership overlap alongside aggregate distribution fit.'}]


def make_plots(data,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import networkx as nx
    folder.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'figure.facecolor':'white','axes.facecolor':'white','savefig.dpi':220})
    blue,orange,green='#235789','#CC6B32','#35745B'
    def save(fig,name):
        fig.tight_layout()
        fig.savefig(folder/(name+'.png'))
        fig.savefig(folder/(name+'.svg'))
        plt.close(fig)
    q=data['quantum']; rows=q['coherence_sweep']
    fig,ax=plt.subplots(figsize=(8.4,3.6))
    x=[r['T2_us'] for r in rows]
    ax.plot(x,[r['symmetric_holevo_achievable'] for r in rows],label='Symmetric pair, collective decoding',color=green)
    ax.plot(x,[r['x_readout'] for r in rows],label='X-basis readout, classical decoding',color=blue)
    ax.axhline(q['baseline']['z_readout'],label='Optimized Z-basis code',color=orange)
    ax.axhline(q['baseline']['gad_capacity'],label='Ideal GAD capacity (no extra dephasing)',color='#78818a',ls=':')
    ax.axvline(q['x_threshold_us'],color=blue,ls='--',lw=1)
    ax.set(xlabel='Measured T2 (microseconds)',ylabel='Classical bits per stored qubit',
           title='One T1 of storage: T1 = 100 us, effective temperature 50 mK')
    ax.legend(fontsize=8,loc='upper left'); save(fig,'quantum_encoding')
    fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    o=data['optical']['rows']; positions=np.arange(len(o)); width=.36
    axes[0].bar(positions-width/2,[r['superposition'] for r in o],width,label='Superposition',color=blue)
    axes[0].bar(positions+width/2,[r['time_sharing'] for r in o],width,label='Power-optimized time sharing',color=orange)
    axes[0].set(xticks=positions,xticklabels=[f"{r['near_rate']}, {r['far_rate']}" for r in o],
                xlabel='Demand pair: near, far (bits per mode)',ylabel='Mean photons per mode',yscale='log')
    axes[0].legend(fontsize=8)
    axes[1].bar(positions,[100*r['photon_saving_fraction'] for r in o],color=green)
    axes[1].set(xticks=positions,xticklabels=[f"{r['near_rate']}, {r['far_rate']}" for r in o],
                xlabel='Same demand pair',ylabel='Photon saving (%)')
    fig.suptitle('Identical rates and photon accounting: eta near = 0.6, eta far = 0.1')
    save(fig,'optical_budget')
    fig,axes=plt.subplots(1,2,figsize=(9,3.7))
    m,b=.2,.1; y=np.linspace(-1,1,401)
    for sign in (-1,1):
        old=np.full_like(y,sign*m); new=sign*(m+b*y)
        axes[0].plot(old,y,'--',color='#78818a'); axes[0].plot(new,y,color=blue)
        axes[0].fill_betweenx(y,old,new,where=y>0,color=blue,alpha=.25)
        axes[0].fill_betweenx(y,old,new,where=y<0,color=orange,alpha=.35)
    axes[0].set(xlim=(-.6,.6),ylim=(-1,1),xlabel='Source coordinate x1',ylabel='Source coordinate x2',
                title='Rare transport cell: same mass, new members')
    masses=np.array([r['mass'] for r in data['transport']['rows']])
    values=np.array([r['w2'] for r in data['transport']['rows']])
    axes[1].loglog(masses,values,'o-',color=blue,label='Shift b = m/2: 12.5% replaced')
    axes[1].loglog(masses,4*.05*masses**1.5,'s--',color=green,label='Budget for at most 5% replaced')
    axes[1].set(xlabel='Rare-group mass m',ylabel='Target W2 distance (model units)',
                title='Small aggregate error is compatible with turnover')
    axes[1].legend(fontsize=8); save(fig,'rare_transport')
    fig,axes=plt.subplots(1,2,figsize=(9,3.7))
    G=nx.DiGraph(data['reactions']['diamond_edges'])
    pos={'A':(0,0),'B':(1,1),'C':(1,-1),'D':(2,0)}
    nx.draw_networkx(G,pos,ax=axes[0],node_color='#e7eef4',node_size=1000,arrowsize=20)
    nx.draw_networkx_edges(G,pos,edgelist=[('D','A')],ax=axes[0],edge_color=green,
                           style='dashed',connectionstyle='arc3,rad=.5',arrowsize=20,width=2)
    axes[0].set_title('One permitted reaction closes four existing paths'); axes[0].axis('off')
    eps=np.logspace(-6,2,150)
    axes[1].loglog(eps,[min(reactions.cycle_stationary(e)) for e in eps],color=blue)
    lo,hi=data['reactions']['floor_interval']
    axes[1].axhline(.01,color=orange,label='1% stationary floor')
    axes[1].axvspan(lo,hi,alpha=.13,color=green,label='Rates meeting the floor')
    axes[1].set(xlabel='Closing rate epsilon (forward rates = 1)',ylabel='Smallest stationary species fraction',
                title='Permanence alone does not set useful abundance')
    axes[1].legend(fontsize=8); save(fig,'reaction_design')
    fig,axes=plt.subplots(1,3,figsize=(10,3.3))
    net=data['networks']; samples=np.asarray(net['samples'])
    for i,(ax,row) in enumerate(zip(axes,net['rows'])):
        ax.hist(samples[:,:,i].ravel(),bins=24,color=blue,alpha=.8,density=True)
        ax.axvline(row['observed'],color=orange,lw=2,label='Observed')
        ax.set(xlabel=row['motif'].replace('_',' '),ylabel='Null density',
               title=f"Estimated tail p = {row['estimated_p']:.3f}")
        ax.legend(fontsize=8)
    fig.suptitle('Karate club: the same labeled degrees in every null graph')
    save(fig,'network_motifs')


def build_results(output_dir=HERE/'results',network_draws=1200,make_figures=True):
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    q={'parameters':{'idle_us':100,'T1_us':100,'baseline_T2_us':200,'temperature_K':.05,'frequency_Hz':5e9},
       'baseline':quantum.compare_rates(100,100,200,.05),
       'x_threshold_us':quantum.x_readout_threshold(100,100,.05),
       'coherence_sweep':[{'T2_us':float(t2),**quantum.compare_rates(100,100,float(t2),.05)} for t2 in np.linspace(30,200,35)],
       'temperature_thresholds':[{'temperature_mK':t*1000,'x_threshold_us':quantum.x_readout_threshold(100,100,t)} for t in (.03,.05,.07,.1)]}
    q['local_readout_gain_fraction']=q['baseline']['x_readout']/q['baseline']['z_readout']-1
    o={'efficiencies':{'near':.6,'far':.1},
       'rows':[{'near_rate':rb,'far_rate':rc,**optical.photon_budgets(rb,rc,.6,.1)} for rb,rc in ((1,.5),(2,1),(3,1),(4,2))],
       'robust_worst_loss':{'near_efficiency_lower_bound':.5,'far_efficiency_lower_bound':.08,
                           'near_rate':3,'far_rate':1,**optical.photon_budgets(3,1,.5,.08)}}
    tr={'source':'Uniform probability on [-1,1]^2; three-atom targets',
        'rows':[{'mass':m,'shift':m/2,**transport.assignment_metrics(m,m/2),
                 'independent_polygon_computation':transport.polygon_metrics(m,m/2),
                 'w2_budget_for_five_percent_replacement':4*.05*m**1.5} for m in (.1,.01,.001,.0001)]}
    edges=[('A','B'),('A','C'),('B','D'),('C','D')]
    candidates=[('D','A',1),('D','B',1),('B','A',1),('D','C',1),('C','A',1)]
    interval=reactions.cycle_floor_interval(.01)
    times=np.linspace(0,50,101); initial=[1e-8,1e-8,1-2e-8]
    cr={'diamond_edges':edges,'candidates':candidates,
        'minimum_repair':reactions.minimum_repair(list('ABCD'),edges,candidates),
        'repair_when_direct_return_forbidden':reactions.minimum_repair(list('ABCD'),edges,candidates[1:]),
        'floor_target':.01,'floor_interval':list(interval),
        'weak_closing_rate':1e-6,'weak_stationary':reactions.cycle_stationary(1e-6).tolist(),
        'designed_stationary':reactions.cycle_stationary(interval[0]).tolist(),
        'times':times.tolist(),'trajectory':reactions.cycle_trajectory(interval[0],initial,times).tolist(),
        'all_rates_scaled_by_point_zero_one':reactions.cycle_trajectory(interval[0],initial,times*.01).tolist()}
    data={'source_branch':'claude/math-repo-review','source_commit':SOURCE,
          'continuation_branch':'codex/scientific-use-continuation','source_treatment':'Accepted factual handoff; source proofs not audited.',
          'python':platform.python_version(),'dependencies':{name:importlib.metadata.version(name) for name in ('numpy','scipy','networkx','matplotlib')},
          'quantum':q,'optical':o,'transport':tr,'reactions':cr,
          'networks':networks.sample_motifs(draws=network_draws),'context_rules':context_rules(),'agenda':agenda()}
    (output_dir/'results.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    if make_figures:
        make_plots(data,output_dir.parent/'figures')
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'results')
    parser.add_argument('--network-draws',type=int,default=1200)
    args=parser.parse_args()
    data=build_results(args.output,args.network_draws)
    summary={'local_X_readout_gain_percent':100*data['quantum']['local_readout_gain_fraction'],
             'X_readout_T2_threshold_us':data['quantum']['x_threshold_us'],
             'optical_photon_saving_percent':[100*r['photon_saving_fraction'] for r in data['optical']['rows']],
             'rare_group_original_members_replaced_percent':100*data['transport']['rows'][0]['replacement_fraction'],
             'minimum_reaction_additions':len(data['reactions']['minimum_repair']['added']),
             'motif_estimated_tail_p':[r['estimated_p'] for r in data['networks']['rows']]}
    print(json.dumps(summary,indent=2,allow_nan=False))


if __name__=='__main__':
    main()
