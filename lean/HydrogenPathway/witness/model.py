"""Control-conditional phase witness. All numbers are illustrative, not hydrogen data.

Standard-library finite matrices reuse PR2 helpers without changing them. A fixed
parity decoder is kept even for an incorrect phase; no adaptive oracle is used.
"""
from __future__ import annotations
import argparse
import cmath
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from imprint import model as m


def kron(a, b):
    return [[a[i][j] * b[k][l] for j in range(len(a[0])) for l in range(len(b[0]))]
            for i in range(len(a)) for k in range(len(b))]


def finite(x):
    if not math.isfinite(x):
        raise ValueError('expected finite parameter')


def reflection(kc):
    """Hermitian unitary, swapping c0 and exp(-i theta)c1 on their span."""
    c0, c1 = m.environment(kc)
    r = abs(kc)
    theta = cmath.phase(kc) if r else 0.
    if r == 1:
        return m.identity(2), theta
    d1 = [cmath.exp(-1j*theta)*z for z in c1]
    difference = [a-b for a, b in zip(c0, d1)]
    norm = math.sqrt(sum(abs(z)**2 for z in difference))
    hminus = [z/norm for z in difference]
    return m.sub(m.identity(2), m.scale(2, m.outer(hminus))), theta


def measurement_case(kc, ku, delta=0., check=False):
    """Four-outcome product PVM; delta is actual minus calibrated atomic phase."""
    finite(delta)
    c0, c1 = m.environment(kc)
    u0, u1 = m.environment(ku)
    rc, theta = reflection(kc)
    phi = cmath.phase(ku) if abs(ku) else 0.
    alpha = theta + phi + delta
    xa = [[0j, cmath.exp(-1j*alpha)], [cmath.exp(1j*alpha), 0j]]
    branches = (m.tensor([1, 0], m.tensor(c0, u0)),
                m.tensor([0, 1], m.tensor(c1, u1)))
    states = [m.outer([(a+s*b)/math.sqrt(2) for a, b in zip(*branches)]) for s in (1,-1)]
    ac = [m.partial_trace(rho, (2,2,2), (0,1)) for rho in states]
    atoms = [m.partial_trace(rho, (2,2,2), (0,)) for rho in states]
    outcomes = []
    effects = {}
    for a in (1,-1):
        for b in (1,-1):
            pa = m.scale(.5, m.add(m.identity(2), m.scale(a, xa)))
            pb = m.scale(.5, m.add(m.identity(2), m.scale(b, rc)))
            effects[a,b] = kron(pa, pb)
    for rho in ac:
        outcomes.append({f'{a},{b}': m.trace(m.mul(e, rho)).real for (a,b), e in effects.items()})
    means = [sum(a*b*row[f'{a},{b}'] for a,b in effects) for row in outcomes]
    atom_means = [m.trace(m.mul(xa, rho)).real for rho in atoms]
    t = (cmath.exp(1j*(theta-alpha))*ku).real
    contrast = (means[0]-means[1])/2
    atom_contrast = (atom_means[0]-atom_means[1])/2
    if check:
        assert m.matrix_error(rc, m.adjoint(rc)) < m.TOL
        assert m.matrix_error(m.mul(rc,rc), m.identity(2)) < m.TOL
        assert max(abs(a-b) for a,b in zip(m.apply(rc,c0),
                   [cmath.exp(-1j*theta)*z for z in c1])) < m.TOL
        assert max(abs(a-b) for a,b in zip(m.apply(rc,c1),
                   [cmath.exp(1j*theta)*z for z in c0])) < m.TOL
        total = m.zeros(4)
        for e in effects.values():
            total = m.add(total,e)
            assert m.matrix_error(m.mul(e,e), e) < m.TOL
            assert min(m.hermitian_spectrum_doubled(e)) >= -m.TOL
        assert m.matrix_error(total,m.identity(4)) < m.TOL
        observable = kron(xa,rc)
        assert m.matrix_error(m.mul(observable,observable),m.identity(4)) < m.TOL
        for s,row,rho in zip((1,-1),outcomes,ac):
            assert abs(sum(row.values())-1) < m.TOL
            assert min(row.values()) >= -m.TOL
            for a,b in effects:
                assert abs(row[f'{a},{b}']-(1+b*abs(kc))*(1+s*a*b*t)/4) < m.TOL
            assert abs(sum(a*b*row[f'{a},{b}'] for a,b in effects)-
                       m.trace(m.mul(observable,rho)).real) < m.TOL
        assert abs(contrast-abs(ku)*math.cos(delta)) < m.TOL
        assert abs(atom_contrast-abs(kc)*t) < m.TOL
    return {'kC':[complex(kc).real,complex(kc).imag],
            'kU':[complex(ku).real,complex(ku).imag], 'phase_error_radians':delta,
            'calibrated_atomic_phase_radians':theta+phi, 'outcomes':outcomes,
            'joint_contrast':contrast, 'atom_contrast':atom_contrast,
            'joint_guess_fixed_parity':(1+contrast)/2,
            'joint_guess_best_relabel':(1+abs(contrast))/2}


def guess_from_response(rows):
    """Equal input priors, guesses +/- on clicks, random fair guess on every erasure."""
    erasure = lambda row: sum(v for key,v in row.items() if key not in ('plus','minus'))
    return (rows[0]['plus']+rows[1]['minus'])/2+(erasure(rows[0])+erasure(rows[1]))/4


def response(q, b, contrast, false_contrast, failure_rates):
    """Label-blind branch rates; adversarial source-correlated false guesses allowed.

    False accepts replace a fraction b/(1-q) of failed attempts. Other failure
    flags stay distinct and are retained. This is an explicit classical channel.
    """
    if q+b > 1:
        raise ValueError('true plus false probability exceeds one')
    survival = 1-b/(1-q) if q < 1 else 0.
    rows = []
    for sign in (1,-1):
        rows.append({'plus':q*(1+sign*contrast)/2+b*(1+sign*false_contrast)/2,
                     'minus':q*(1-sign*contrast)/2+b*(1-sign*false_contrast)/2,
                     **{key:value*survival for key,value in failure_rates.items()}})
    return rows


def budget(p, ea, ec, r, u, vj, phase_cost, epsj, epsa, bj, ba):
    """Sufficient worst-case budget; eps are expectation-contrast errors, not trace distance."""
    lower = vj*u*(1-phase_cost)-epsj
    upper = r*u+epsa  # Safe even for an ideal, optimally phased atom readout.
    margin = p*ea*(ec*lower-upper)-bj-ba
    required_ec = ((upper+(bj+ba)/(p*ea))/lower if p*ea > 0 and lower > 0 else None)
    return {'joint_contrast_lower':lower, 'atom_contrast_upper':upper,
            'signed_score_margin_lower':margin,
            'guaranteed_guess_advantage':margin/2,
            'strict_advantage_certified':margin > 0,
            'required_photon_efficiency_strictly_above':required_ec}


def attempt_case(kc, ku, p, eta_a, eta_c, *, delta=0., visibility_joint=1.,
                 visibility_atom=1., b_joint=0., b_atom=0., b_hybrid=0., false_joint=0.,
                 false_atom=0., false_hybrid=0., eps_joint=0., eps_atom=0., check=False):
    for value in [p,eta_a,eta_c,visibility_joint,visibility_atom,b_joint,b_atom,b_hybrid]:
        m.require_probability(value)
    for value in [eps_joint,eps_atom]:
        finite(value)
        if value < 0:
            raise ValueError('expectation errors must be nonnegative')
    if visibility_joint > visibility_atom:
        raise ValueError('joint visibility must not exceed shared atomic visibility')
    for value in [false_joint,false_atom,false_hybrid]:
        finite(value)
        if abs(value) > 1:
            raise ValueError('false contrast must lie in [-1,1]')
    measurement = measurement_case(kc,ku,delta,check)
    qj,qa = p*eta_a*eta_c,p*eta_a
    cj = visibility_joint*measurement['joint_contrast']
    ca = visibility_atom*measurement['atom_contrast']
    jr = response(qj,b_joint,cj,false_joint,{'capture_failure':1-p,
                  'atom_no_click':p*(1-eta_a),'photon_no_click':p*eta_a*(1-eta_c)})
    ar = response(qa,b_atom,ca,false_atom,{'capture_failure':1-p,'atom_no_click':p*(1-eta_a)})
    fallback = qa-qj
    hybrid_mean = (qj*cj+fallback*ca)/qa if qa else 0.
    hr = response(qa,b_hybrid,hybrid_mean,false_hybrid,
                  {'capture_failure':1-p,'atom_no_click':p*(1-eta_a)})
    gj,ga,gh = guess_from_response(jr),guess_from_response(ar),guess_from_response(hr)
    # cos(delta) >= 1-delta^2/2 globally; use cap 2 for a nonnegative valid cost.
    phase_cost = min(2.,delta*delta/2)
    bound = budget(p,eta_a,eta_c,abs(kc),abs(ku),visibility_joint,phase_cost,
                   eps_joint,eps_atom,b_joint,b_atom)
    hybrid_margin = qj*(bound['joint_contrast_lower']-bound['atom_contrast_upper'])-b_hybrid-b_atom
    hybrid_bound = {'signed_score_margin_lower':hybrid_margin,
                    'guaranteed_guess_advantage':hybrid_margin/2,
                    'strict_advantage_certified':hybrid_margin > 0}
    if check:
        for rows in [jr,ar,hr]:
            for row in rows:
                assert abs(sum(row.values())-1) < m.TOL
                assert min(row.values()) >= -m.TOL
        assert abs(gj-(1+qj*cj+b_joint*false_joint)/2) < m.TOL
        assert abs(ga-(1+qa*ca+b_atom*false_atom)/2) < m.TOL
        assert gj-ga+ m.TOL >= bound['guaranteed_guess_advantage']
        assert abs(gh-ga-(qj*(cj-ca)+b_hybrid*false_hybrid-b_atom*false_atom)/2) < m.TOL
        assert gh-ga+m.TOL >= hybrid_bound['guaranteed_guess_advantage']
    return {'parameters':{'p':p,'eta_atom':eta_a,'eta_photon':eta_c,
            'visibility_joint':visibility_joint,'visibility_atom':visibility_atom,
            'false_accept_joint_per_attempt':b_joint,'false_accept_atom_per_attempt':b_atom,'false_accept_hybrid_per_attempt':b_hybrid,
            'false_joint_contrast':false_joint,'false_atom_contrast':false_atom,'false_hybrid_contrast':false_hybrid,
            'eps_joint_contrast':eps_joint,'eps_atom_contrast':eps_atom},
            'measurement':measurement,
            'joint':{'true_readout_rate':qj,'contrast':cj,'response':jr,'guess':gj},
            'atom':{'true_readout_rate':qa,'contrast':ca,'response':ar,'guess':ga},
            'hybrid':{'coincidence_rate':qj,'fallback_rate':fallback,'fallback_contrast':ca,
                      'response':hr,'guess':gh},
            'guess_difference':gj-ga,'budget':bound,
            'hybrid_guess_difference':gh-ga,'hybrid_budget':hybrid_bound}


def loss_povm(kc,ku,p,eta_a,eta_c,va=1.,vj=1.,delta=0.,hybrid=False):
    """Complete true-readout POVM on the toy AC space, including erasure flags.

    Atomic visibility va is shared. Independent photon label flips supply
    vC=vj/va. No false-event instrument is asserted by this construction.
    """
    for value in [p,eta_a,eta_c,va,vj]:
        m.require_probability(value)
    if vj > va:
        raise ValueError('joint visibility must not exceed atomic visibility')
    data=measurement_case(kc,ku,delta)
    alpha=data['calibrated_atomic_phase_radians']+delta
    xa=[[0j,cmath.exp(-1j*alpha)],[cmath.exp(1j*alpha),0j]]
    rc,_=reflection(kc)
    vc=vj/va if va else 0.
    qa,qj=p*eta_a,p*eta_a*eta_c
    effects={'capture_failure':m.scale(1-p,m.identity(4)),
             'atom_no_click':m.scale(p*(1-eta_a),m.identity(4))}
    for a in (1,-1):
        pa=m.scale(.5,m.add(m.identity(2),m.scale(a*va,xa)))
        for b in (1,-1):
            pb=m.scale(.5,m.add(m.identity(2),m.scale(b*vc,rc)))
            effects[f'a={a},b={b}']=m.scale(qj,kron(pa,pb))
        if hybrid:
            effects[f'fallback_a={a}']=m.scale(qa-qj,kron(pa,m.identity(2)))
    if not hybrid:
        effects['photon_no_click']=m.scale(qa-qj,m.identity(4))
    return effects


def port_efficiency_case(kc,ku,eta_plus,eta_minus,delta=0.,check=False):
    """Atomic readout always retained. Photon outcome efficiencies differ.

    The compatible instrument has K_b=sqrt(eta_b) Pi_b and
    K_empty=sum_b sqrt(1-eta_b) Pi_b. No-click is scalar only if efficiencies
    coincide (on the occupied support). Multiplying all rates by qA restores
    capture and atomic losses; this case sets qA=1 for clarity.
    """
    m.require_probability(eta_plus)
    m.require_probability(eta_minus)
    data = measurement_case(kc,ku,delta,check)
    raw,rows = [],[]
    for source_row in data['outcomes']:
        record = {}
        result = {'plus':0.,'minus':0.,'erase':0.}
        for a in (1,-1):
            for b in (1,-1):
                prob = source_row[f'{a},{b}']
                eta = eta_plus if b == 1 else eta_minus
                record[f'a={a},b={b},detected'] = prob*eta
                record[f'a={a},b={b},missed'] = prob*(1-eta)
                result['plus' if a*b == 1 else 'minus'] += prob*eta
                result['plus' if a == 1 else 'minus'] += prob*(1-eta)
        raw.append(record)
        rows.append(result)
    rate=(eta_plus*(1+abs(kc))+eta_minus*(1-abs(kc)))/2
    g=guess_from_response(rows)
    baseline=(1+data['atom_contrast'])/2
    expected=eta_minus*(1-abs(kc))*data['joint_contrast']/2
    if check:
        for row in raw:
            assert abs(sum(row.values())-1) < m.TOL and min(row.values()) >= -m.TOL
        assert abs(g-baseline-expected) < m.TOL
    return {'recorded_photon_rate':rate,'hybrid_gain':g-baseline,
            'naive_gain_from_average_efficiency':rate*(1-abs(kc))*data['joint_contrast']/2,
            'port_efficiencies':[eta_plus,eta_minus],'full_records':raw,'response':rows}


def report(check=False):
    cases = [
        ('illustrative_control_budget', dict(kc=.4j,ku=.8,p=.2,eta_a=.9,eta_c=.85,
              delta=.1,visibility_joint=.95,b_joint=.002,b_atom=.001,b_hybrid=.002,
              false_joint=-1.,false_atom=1.,false_hybrid=-1.,eps_joint=.02,eps_atom=.01)),
        ('ideal_threshold_equal',dict(kc=.6,ku=.8,p=.25,eta_a=.7,eta_c=.6)),
        ('inefficient_joint_worse',dict(kc=.6,ku=.8,p=.25,eta_a=.7,eta_c=.3)),
        ('phase_unknown_wrong_pi',dict(kc=.2j,ku=-.8j,p=.3,eta_a=1.,eta_c=1.,delta=math.pi)),
        ('no_unobserved_coherence',dict(kc=.4,ku=0j,p=.2,eta_a=.9,eta_c=.85)),
        ('rare_success',dict(kc=0j,ku=1.,p=.001,eta_a=1.,eta_c=1.)),
        ('identical_collected_modes',dict(kc=1j,ku=.8j,p=1.,eta_a=1.,eta_c=1.)),
        ('zero_capture',dict(kc=0j,ku=1.,p=0.,eta_a=1.,eta_c=1.))]
    return {'description':'Illustrative control-conditional product measurement; no hydrogen realization claim',
            'checks_enabled':check,'tolerance':m.TOL,
            'cases':{name:attempt_case(**params,check=check) for name,params in cases},
            'outcome_dependent_detection_counterexample':port_efficiency_case(.6,.8,1.,0.,check=check)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    encoded=json.dumps(report(args.check),indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(encoded)
        print('Calculated eight witness/loss cases'+(' with checks.' if args.check else '.'))
    else:
        print(encoded,end='')


if __name__ == '__main__':
    main()
