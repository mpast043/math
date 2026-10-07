"""Permitted graph repairs and a quantitative closed-cycle design example."""
import itertools
import math

import networkx as nx
import numpy as np
from scipy.linalg import expm


def weakly_reversible(nodes,edges):
    G=nx.DiGraph(); G.add_nodes_from(nodes); G.add_edges_from(edges)
    return all(nx.is_strongly_connected(G.subgraph(c)) for c in nx.weakly_connected_components(G))


def minimum_repair(nodes,edges,candidates):
    """Exact minimum positive cost over <=20 permitted candidate reactions.

    Nodes identify chemical complexes, not a species-interaction graph.
    Candidates stay inside original linkage classes, preserving their
    stoichiometric span. Chemistry determines the permitted candidate list.
    """
    G=nx.DiGraph(); G.add_nodes_from(nodes); G.add_edges_from(edges)
    if len(candidates)>20:
        raise ValueError('Exact demonstration is limited to 20 candidate reactions.')
    component={v:i for i,c in enumerate(nx.weakly_connected_components(G)) for v in c}
    seen=set()
    for a,b,cost in candidates:
        if (a not in component or b not in component or a==b or (a,b) in seen
            or G.has_edge(a,b) or component[a]!=component[b] or not math.isfinite(cost) or cost<=0):
            raise ValueError('Candidates must be distinct positive-cost missing edges within a linkage class.')
        seen.add((a,b))
    if weakly_reversible(nodes,edges):
        return {'added':[],'cost':0.0}
    best=None
    for k in range(1,len(candidates)+1):
        for choice in itertools.combinations(candidates,k):
            cost=sum(c[2] for c in choice)
            if best is not None and (cost,k)>=(best['cost'],len(best['added'])):
                continue
            added=[(a,b) for a,b,_ in choice]
            if weakly_reversible(nodes,edges+added):
                best={'added':added,'cost':float(cost)}
    return best


def cycle_stationary(epsilon):
    if not math.isfinite(epsilon) or epsilon<=0:
        raise ValueError('Closing rate must be finite and positive.')
    return np.array([epsilon,epsilon,1.])/(1+2*epsilon)


def cycle_floor_interval(delta):
    """Closing rates with all three stationary fractions >= delta."""
    if not math.isfinite(delta) or not 0<delta<=1/3:
        raise ValueError('A positive equal floor cannot exceed one third.')
    return delta/(1-2*delta),(1-delta)/(2*delta)


def cycle_trajectory(epsilon,initial,times):
    cycle_stationary(epsilon)
    initial=np.asarray(initial,float); times=np.asarray(times,float)
    if (initial.shape!=(3,) or np.any(initial<0) or not np.isfinite(initial).all()
        or np.any(times<0) or not np.isfinite(times).all()):
        raise ValueError('Initial concentrations and times must be finite and nonnegative.')
    generator=np.array([[-1.,0.,epsilon],[1.,-1.,0.],[0.,1.,-epsilon]])
    return np.array([expm(generator*t)@initial for t in times])
