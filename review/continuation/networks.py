"""Stateful degree-preserving sampling and descriptive motif inference."""
import math

import networkx as nx
import numpy as np

from review.applications.switch_chain_null_models import all_graphs


class SwitchChain:
    """Lazy symmetric edge-switch chain, retaining state across advances."""
    def __init__(self,G,seed):
        if G.is_directed() or G.is_multigraph() or nx.number_of_selfloops(G):
            raise ValueError('Require an undirected simple loop-free graph.')
        self.nodes=list(G.nodes())
        self.rank={v:i for i,v in enumerate(self.nodes)}
        self.edges=[self._edge(a,b) for a,b in G.edges()]
        self.adj={v:set(G[v]) for v in G}
        self.rng=np.random.default_rng(seed)
        self.accepted=0; self.attempts=0

    def _edge(self,a,b):
        return (a,b) if self.rank[a]<self.rank[b] else (b,a)

    def advance(self,steps):
        if not isinstance(steps,(int,np.integer)) or steps<0:
            raise ValueError('Steps must be a nonnegative integer.')
        m=len(self.edges)
        for _ in range(steps):
            self.attempts+=1
            if m<2 or self.rng.random()<.5:
                continue
            i=int(self.rng.integers(m)); j=int(self.rng.integers(m-1)); j+=j>=i
            a,b=self.edges[i]; c,d=self.edges[j]
            if len({a,b,c,d})<4:
                continue
            if self.rng.random()<.5:
                c,d=d,c
            if c in self.adj[a] or d in self.adj[b]:
                continue
            self.adj[a].remove(b); self.adj[b].remove(a)
            self.adj[c].remove(d); self.adj[d].remove(c)
            self.adj[a].add(c); self.adj[c].add(a)
            self.adj[b].add(d); self.adj[d].add(b)
            self.edges[i]=self._edge(a,c); self.edges[j]=self._edge(b,d)
            self.accepted+=1

    def graph(self):
        G=nx.Graph(); G.add_nodes_from(self.nodes); G.add_edges_from(self.edges)
        return G


def motifs(G):
    A=nx.to_numpy_array(G,dtype=np.int64,weight=None)
    common=A@A
    upper=common[np.triu_indices(len(G),1)]
    four=int(np.sum(upper*(upper-1)//2)//2)
    triangle=int(np.trace(common@A)//6)
    degrees=dict(G.degree()); m=G.number_of_edges()
    if not m:
        assort=0.0
    else:
        mean=sum(d*d for d in degrees.values())/(2*m)
        second=sum(d**3 for d in degrees.values())/(2*m)
        product=sum(degrees[a]*degrees[b] for a,b in G.edges())/m
        assort=(product-mean*mean)/(second-mean*mean) if second>mean*mean else 0.0
    return {'triangles':triangle,'four_cycles':four,'assortativity':float(assort)}


def integrated_time(x):
    x=np.asarray(x,float); x=x-x.mean(); n=len(x)
    if n<4 or not np.any(x):
        return 1.0
    fft=np.fft.rfft(x,2*n)
    ac=np.fft.irfft(fft*np.conjugate(fft))[:n]
    ac/=ac[0]
    total=1.0
    for k in range(1,n-1,2):
        pair=ac[k]+ac[k+1]
        if pair<=0:
            break
        total+=2*pair
    return max(1.0,float(total))


def split_rhat(chains):
    chains=np.asarray(chains,float)
    half=chains.shape[1]//2
    x=np.concatenate([chains[:,:half],chains[:,-half:]],axis=0)
    within=np.var(x,axis=1,ddof=1).mean()
    between=half*np.var(x.mean(axis=1),ddof=1)
    if within==0:
        return 1.0 if between==0 else None
    return float(math.sqrt(((half-1)/half*within+between/half)/within))


def tail_mcse(indicators):
    """Batch-means MCSE; a constant observed tail is not zero uncertainty."""
    indicators=np.asarray(indicators,float)
    if not np.any(indicators!=indicators.flat[0]):
        return None
    batches=min(20,indicators.shape[1]//10)
    if batches<2:
        return None
    width=indicators.shape[1]//batches
    means=indicators[:,:width*batches].reshape(-1,batches,width).mean(axis=2).ravel()
    return float(np.std(means,ddof=1)/math.sqrt(len(means)))


def by_adjust(pvalues):
    """Benjamini-Yekutieli transformation of estimated tails, not an MCMC guarantee."""
    pvalues=np.asarray(pvalues,float); n=len(pvalues); order=np.argsort(pvalues)
    harmonic=sum(1/k for k in range(1,n+1))
    adjusted=np.minimum.accumulate((pvalues[order]*n*harmonic/np.arange(1,n+1))[::-1])[::-1]
    result=np.empty(n); result[order]=np.minimum(1,adjusted)
    return result.tolist()


def exact_reference():
    graphs=all_graphs([2]*6)
    counts=[]
    for edges in graphs:
        G=nx.Graph(); G.add_nodes_from(range(6)); G.add_edges_from(edges)
        counts.append(motifs(G)['triangles'])
    return {'degree_sequence':[2]*6,'states':len(graphs),'observed_triangles':2,
            'triangle_tail':float(np.mean(np.array(counts)>=2))}


def sample_motifs(draws=1200,burn=6240,thin=78,seeds=(131,276,374,149)):
    if draws<20 or thin<1 or burn<0 or len(seeds)<2:
        raise ValueError('Require >=20 draws, positive thinning, nonnegative burn and >=2 chains.')
    G=nx.karate_club_graph(); degrees=dict(G.degree()); names=list(motifs(G))
    observed=motifs(G); arrays=[]; acceptance=[]
    for i,seed in enumerate(seeds):
        start=G if i%2==0 else nx.havel_hakimi_graph([degrees[v] for v in G])
        chain=SwitchChain(start,seed); chain.advance(burn)
        series=[]
        for _ in range(draws):
            chain.advance(thin)
            H=chain.graph()
            if dict(H.degree())!=degrees:
                raise RuntimeError('Labeled degree sequence changed.')
            measured=motifs(H)
            series.append([measured[name] for name in names])
        arrays.append(series); acceptance.append(chain.accepted/chain.attempts)
    arrays=np.array(arrays,float); rows=[]
    for i,name in enumerate(names):
        x=arrays[:,:,i]
        upper=name!='assortativity'
        indicators=(x>=observed[name]) if upper else (x<=observed[name])
        total=x.size
        p=(1+np.sum(indicators))/(1+total)
        ess=sum(draws/integrated_time(chain) for chain in x)
        rows.append({'motif':name,'tail':'upper' if upper else 'lower','observed':observed[name],
                     'null_mean':float(x.mean()),'null_sd':float(x.std(ddof=1)),
                     'estimated_p':float(p),'tail_mcse':tail_mcse(indicators),
                     'ess':float(ess),'split_rhat':split_rhat(x),
                     'chain_means':x.mean(axis=1).tolist()})
    for row,adjusted in zip(rows,by_adjust([r['estimated_p'] for r in rows])):
        row['estimated_by_adjusted']=adjusted
    return {'dataset':'Zachary karate club, NetworkX built-in, unweighted',
            'nodes':len(G),'edges':G.number_of_edges(),'draws_per_chain':draws,
            'burn_attempts':burn,'thin_attempts':thin,'seeds':list(seeds),
            'acceptance':acceptance,'degrees_preserved':True,'rows':rows,
            'samples':arrays.tolist(),'exact_reference':exact_reference()}
