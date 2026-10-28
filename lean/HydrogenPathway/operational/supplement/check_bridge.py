"""Finite-dimensional regression checks, not interval certificates or Lean proofs."""
import json, math, hashlib
from pathlib import Path
import numpy as np
TOL=1e-12
checks=[]
def check(name, actual, expected):
    error=float(np.max(np.abs(np.asarray(actual)-np.asarray(expected))))
    assert error<TOL,(name,error)
    checks.append({'name':name,'max_error':error,'passed':True})
def ket0(n):
    v=np.zeros(2**n);v[0]=1;return v
def ket1(n):
    v=np.zeros(2**n);v[-1]=1;return v
def outer(v):return np.outer(v,v.conj())
def td(a,b):return np.linalg.svd(a-b,compute_uv=False).sum()/2
def partial(rho,dims,keep):
    a=rho.reshape(dims+dims);ds=list(dims)
    for j in reversed(range(len(ds))):
        if j not in keep:
            a=np.trace(a,axis1=j,axis2=j+len(ds));ds.pop(j)
    d=math.prod(ds);return a.reshape(d,d)
def product(vs):
    a=np.array([1.]);
    for v in vs:a=np.kron(a,v)
    return a
r=.6;c0=np.array([1.,0]);c1=np.array([r,math.sqrt(1-r*r)])
plus=(np.kron(c0,c0)+np.kron(np.array([0.,1]),c1))/math.sqrt(2)
minus=(np.kron(c0,c0)-np.kron(np.array([0.,1]),c1))/math.sqrt(2)
check('phase_global_distance',td(outer(plus),outer(minus)),1)
check('phase_photon_distance',td(partial(outer(plus),[2,2],[1]),partial(outer(minus),[2,2],[1])),0)
check('phase_atom_distance',td(partial(outer(plus),[2,2],[0]),partial(outer(minus),[2,2],[0])),r)
check('branch_photon_distance',td(outer(c0),outer(c1)),.8)
check('branch_photon_min_error',(1-td(outer(c0),outer(c1)))/2,.1)
eps=.1;gamma=2*math.sqrt(eps*(1-eps));scenarios=[]
for n in [2,3,5]:
    e0=math.sqrt(1-eps)*ket0(n)+math.sqrt(eps)*ket1(n)
    e1=math.sqrt(eps)*ket0(n)+math.sqrt(1-eps)*ket1(n)
    check(f'correlated_overlap_N{n}',np.vdot(e1,e0),gamma)
    for i in range(n):
        check(f'correlated_local_error_N{n}_{i}',(1-td(partial(outer(e0),[2]*n,[i]),partial(outer(e1),[2]*n,[i])))/2,eps)
    f0=np.array([math.sqrt(1-eps),math.sqrt(eps)])
    f1=np.array([math.sqrt(eps),math.sqrt(1-eps)])
    check(f'product_overlap_N{n}',np.vdot(product([f1]*n),product([f0]*n)),gamma**n)
    independent_majority=sum(math.comb(n,k)*eps**k*(1-eps)**(n-k) for k in range(n//2+1,n+1))
    if n%2==0:independent_majority+=.5*math.comb(n,n//2)*eps**(n//2)*(1-eps)**(n//2)
    scenarios.append({'N':n,'single_record_error':eps,'shared_error_majority_error':eps,'independent_error_majority_error':independent_majority,'product_coherence':gamma**n,'correlated_coherence':gamma})
check('independent_three_majority_error',scenarios[1]['independent_error_majority_error'],.028)
# A classical measure-and-copy detector: two pure inputs of overlap .6 can
# yield commuting distributions (.9,.1) and (.1,.9), and any copy count
# leaves discrimination unchanged. These are ideal Helstrom outcomes.
for n in [1,3,8]:
    p0=np.zeros(2**n);p1=np.zeros(2**n);p0[0]=p1[-1]=.9;p0[-1]=p1[0]=.1
    check(f'classical_copy_distance_N{n}',np.abs(p0-p1).sum()/2,.8)
# Pairwise independence need not imply full independence: even parity.
p=np.zeros((2,2,2))
for a in range(2):
    for b in range(2):p[a,b,a^b]=.25
for axis in range(3):check(f'parity_pairwise_independence_axis{axis}',p.sum(axis=axis),np.ones((2,2))*.25)
check('parity_joint_total_variation_from_product',np.abs(p-.125).sum()/2,.5)
report={'status':'passed','checks':checks,'count':len(checks),'tolerance':TOL,'numpy_version':np.__version__,'scope':'Analytic toy-model regression only; no hardware parameters, interval certificate, Lean proof, or resolution of unique outcomes.','scenarios':scenarios,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
Path(__file__).with_name('RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'count':len(checks),'scenarios':scenarios},indent=2))
