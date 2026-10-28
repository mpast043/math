"""Finite matrix operational boundary; standard library, no apparatus claim."""
from __future__ import annotations
import argparse
import cmath
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from imprint import model as m
TOL=m.TOL


def block_delta(x,labels):
    if not x or len(labels)!=len(x) or any(len(row)!=len(x) for row in x):
        raise ValueError('expected nonempty square matrix and one label per coordinate')
    return [[z if labels[i]==labels[j] else 0j for j,z in enumerate(row)] for i,row in enumerate(x)]


def pinch(ps,x):
    result=m.zeros(len(x))
    for p in ps:
        result=m.add(result,m.mul(m.mul(p,x),p))
    return result


def entrywise_case(effect,rho,labels):
    delta=block_delta(rho,labels)
    difference=m.trace(m.mul(effect,m.sub(rho,delta)))
    budget=sum(abs(effect[i][j])*abs(rho[j][i]) for i in range(len(rho))
               for j in range(len(rho)) if labels[i]!=labels[j])
    return {'trace_difference':abs(difference),'entrywise_budget':budget,
            'effect_offblock_sum':sum(abs(effect[i][j]) for i in range(len(rho))
              for j in range(len(rho)) if labels[i]!=labels[j])}


def rotated_case(check=False):
    n=4
    u=[[cmath.exp(2j*math.pi*i*j/n)/math.sqrt(n) for j in range(n)] for i in range(n)]
    ps=[]
    for group in [[0,1],[2,3]]:
        p=[[complex(i==j and i in group) for j in range(n)] for i in range(n)]
        ps.append(m.mul(m.mul(u,p),m.adjoint(u)))
    # PSD trace-one rho; M has eigenvalues in [0,1] and nontrivial within-block entries.
    v=[1/math.sqrt(2),0j,1j/math.sqrt(2),0j]
    rho=m.outer(v)
    base=[[.5,.2j,0j,0j],[-.2j,.5,0j,0j],[0j,0j,.4,.1],[0j,0j,.1,.6]]
    effect=m.mul(m.mul(u,base),m.adjoint(u))
    error=abs(m.trace(m.mul(effect,rho))-m.trace(m.mul(effect,pinch(ps,rho))))
    if check:
        total=m.zeros(n)
        for i,p in enumerate(ps):
            total=m.add(total,p)
            assert m.matrix_error(m.mul(p,p),p)<TOL
            assert m.matrix_error(p,m.adjoint(p))<TOL
            assert m.matrix_error(m.mul(effect,p),m.mul(p,effect))<TOL
            for j,q in enumerate(ps):
                if i!=j:
                    assert m.matrix_error(m.mul(p,q),m.zeros(n))<TOL
        assert m.matrix_error(total,m.identity(n))<TOL
        assert error<TOL
        assert abs(m.trace(pinch(ps,rho))-m.trace(rho))<TOL
        assert m.matrix_error(pinch(ps,pinch(ps,rho)),pinch(ps,rho))<TOL
        assert min(m.hermitian_spectrum_doubled(effect))>=-TOL
        assert max(m.hermitian_spectrum_doubled(effect))<=1+TOL
    return {'dimension':n,'trace_error':error,'projection_blocks':[2,2]}


def coherent_case(check=False):
    plus=m.outer(m.source(1));mixture=[[.5,0j],[0j,.5]]
    diagonal=[[1.,0j],[0j,0j]]
    result={'global_distance_to_mixture':m.distance(plus,mixture),
            'diagonal_effect_difference':entrywise_case(diagonal,plus,[0,1])['trace_difference'],
            'coherence_effect_difference':entrywise_case(plus,plus,[0,1])['trace_difference']}
    if check:
        assert abs(result['global_distance_to_mixture']-.5)<TOL
        assert result['diagonal_effect_difference']<TOL
        assert abs(result['coherence_effect_difference']-.5)<TOL
    return result


def encoding_case(k,check=False):
    e0,e1=m.environment(k)
    w=m.isometry(k)
    x=[[0j,1.],[1.,0j]]
    local=[[x[i//2][j//2] if i%2==j%2 else 0j for j in range(4)] for i in range(4)]
    compressed=m.mul(m.mul(m.adjoint(w),local),w)
    gram=[[sum(a.conjugate()*b for a,b in zip(e,f)) for f in [e0,e1]] for e in [e0,e1]]
    expected=[[x[i][j]*gram[i][j] for j in range(2)] for i in range(2)]
    product=m.mul(m.mul(m.adjoint(w),m.mul(local,local)),w)
    if check:
        assert m.matrix_error(compressed,expected)<TOL
        assert m.matrix_error(m.mul(m.adjoint(w),w),m.identity(2))<TOL
        for rho in [m.outer(m.source(1)),m.outer(m.source(-1))]:
            full=m.mul(m.mul(w,rho),m.adjoint(w))
            assert abs(m.trace(m.mul(local,full))-m.trace(m.mul(compressed,rho)))<TOL
    return {'k':[complex(k).real,complex(k).imag],
            'offdiagonal_modulus':abs(compressed[0][1]),
            'compression_multiplication_error':m.matrix_error(product,m.mul(compressed,compressed))}


def conditional_union(weights,condition,event,a,b):
    if not all(len(x)==len(weights) for x in [condition,event,a,b]):
        raise ValueError('response lengths differ')
    if any(not math.isfinite(w) or w<0 for w in weights):
        raise ValueError('weights must be nonnegative and finite')
    if any(e and not (x or y) for e,x,y in zip(event,a,b)):
        raise ValueError('failure event is not covered by the two error events')
    mass=lambda pred:sum(w for w,c,v in zip(weights,condition,pred) if c and v)
    denominator=sum(w for w,c in zip(weights,condition) if c)
    if not math.isfinite(denominator) or denominator<=0:
        raise ValueError('condition must have positive finite accumulated weight')
    # Divide each nonnegative event mass before adding: their sum can overflow
    # even when the denominator and each normalized probability are finite.
    return {'failure':mass(event)/denominator,'bound':mass(a)/denominator+mass(b)/denominator}


def shared_records(epsilon):
    m.require_probability(epsilon)
    # Both records copy the same potentially wrong decision.
    return {'record_disagreement':0.,'source_error':epsilon}


def report(check=False):
    return {'scope':'Finite operational statistics; no global outcome selection or hardware claim',
            'tolerance':TOL,'checks_enabled':check,
            'rotated_projection':rotated_case(check),'coherent_vs_mixture':coherent_case(check),
            'encodings':[encoding_case(k,check) for k in [0j,.6,.6j,1.]],
            'shared_wrong_records':shared_records(.1)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true');p.add_argument('--output',type=Path)
    args=p.parse_args();encoded=json.dumps(report(args.check),indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(encoded);print('Checked operational-boundary reference cases.' if args.check else 'Calculated reference cases.')
    else:
        print(encoded,end='')

if __name__=='__main__':
    main()
