"""Single-excitation collection model; finite floating-point regression."""
import numpy as np
import math,json,hashlib
from pathlib import Path
TOL=1e-12;checks=[]
def check(name,a,b):
    e=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    assert e<TOL,(name,e);checks.append({'name':name,'max_error':e})
def outer(v):return np.outer(v,v.conj())
def td(a,b):return np.linalg.svd(a-b,compute_uv=False).sum()/2
def ptr(rho,dims,keep):
    a=rho.reshape(dims+dims);ds=list(dims)
    for j in reversed(range(len(ds))):
        if j not in keep:a=np.trace(a,axis1=j,axis2=j+len(ds));ds.pop(j)
    d=math.prod(ds);return a.reshape(d,d)
v=np.array([1,0,0],complex);c0=np.array([0,1,0],complex)
c1=np.array([0,.6*np.exp(.7j),.8],complex)
u0=c0;u1=np.array([0,.4*np.exp(-.3j),math.sqrt(.84)],complex)
kc=np.vdot(c1,c0);ku=np.vdot(u1,u0)
rows=[]
for a,b in [(0,0),(1,1),(0,1),(.2,.8),(.8,.2),(.4,.4),(.01,.99)]:
    p0=math.sqrt(a)*np.kron(c0,v)+math.sqrt(1-a)*np.kron(v,u0)
    p1=math.sqrt(b)*np.kron(c1,v)+math.sqrt(1-b)*np.kron(v,u1)
    plus=np.concatenate([p0,p1])/math.sqrt(2);minus=np.concatenate([p0,-p1])/math.sqrt(2)
    acp=ptr(outer(plus),[2,3,3],[0,1]);acm=ptr(outer(minus),[2,3,3],[0,1])
    x=math.sqrt(a*b);y=math.sqrt((1-a)*(1-b))
    check(f'norm_{a}_{b}',np.vdot(plus,plus),1)
    check(f'AC_{a}_{b}',td(acp,acm),x+y*abs(ku))
    check(f'A_{a}_{b}',td(ptr(acp,[2,3],[0]),ptr(acm,[2,3],[0])),abs(x*kc+y*ku))
    check(f'C_{a}_{b}',td(ptr(acp,[2,3],[1]),ptr(acm,[2,3],[1])),0)
    pd=(a+b)/2;pm=1-pd
    det=[1,2,4,5];miss=[0,3]
    if pd>0:check(f'detected_{a}_{b}',td(acp[np.ix_(det,det)]/pd,acm[np.ix_(det,det)]/pd),x/pd)
    if pm>0:check(f'missed_{a}_{b}',td(acp[np.ix_(miss,miss)]/pm,acm[np.ix_(miss,miss)]/pm),y*abs(ku)/pm)
    rows.append({'eta0':a,'eta1':b,'D_AC':x+y*abs(ku),'D_A':abs(x*kc+y*ku),'detection_probability':pd,'conditional_detected_D':x/pd if pd else None})
r={'status':'passed','count':len(checks),'checks':checks,'scenarios':rows,'tolerance':TOL,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Single-photon loss state only. A fixed input photon pair additionally requires Gram-matrix compatibility. Coherent control and instrument not hardware-certified.'}
Path(__file__).with_name('LOSS_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'status':r['status'],'count':len(checks),'scenarios':rows},indent=2))
