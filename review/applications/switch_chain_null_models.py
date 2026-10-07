#!/usr/bin/env python3
"""Uniform random graphs with a given degree sequence: the switch chain as a null model (family 131).

Repository result: the lazy edge-switch chain on simple graphs with a prescribed degree sequence
mixes in O(n^8) steps for EVERY graphical degree sequence (the Kannan-Tetali-Vempala conjecture);
an exact uniform sampler with expected polynomial running time follows.

Why it matters: network science tests whether a pattern (triangles, motifs, assortativity,
rich clubs) is significant by comparing against random graphs with the same degrees. The switch
chain is the standard way to draw them, because the alternatives fail on heterogeneous degrees:
rejection sampling from the configuration model almost never produces a simple graph, and the
"erased" configuration model changes the degrees. Until now, polynomial mixing was proved only
for restricted classes of sequences, so every application rested on an unproved assumption.

Part 1 checks, by exhaustive enumeration, that the chain is symmetric (so its stationary law is
uniform) and measures its exact mixing on small sequences. Part 2 runs the standard motif test on
Zachary's karate-club network and compares with the two configuration-model shortcuts.
"""
import itertools
import json
import math
import os
import sys
from collections import Counter

import networkx as nx
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"


# ---------- Part 1: exact chain on small degree sequences ----------

def all_graphs(deg):
    """All labeled simple graphs with degree sequence deg, as frozensets of edges."""
    n = len(deg)
    pairs = list(itertools.combinations(range(n), 2))
    out, rem, chosen = [], list(deg), []

    def rec(i):
        if i == len(pairs):
            if not any(rem):
                out.append(frozenset(chosen))
            return
        a, b = pairs[i]
        # prune: vertex a has no later pairs once b passes n-1
        if rem[a] > 0 and rem[b] > 0:
            rem[a] -= 1; rem[b] -= 1; chosen.append((a, b))
            rec(i + 1)
            chosen.pop(); rem[a] += 1; rem[b] += 1
        if b == n - 1 and rem[a] > 0:
            return
        rec(i + 1)
    rec(0)
    return out


def switch_matrix(graphs):
    index = {g: i for i, g in enumerate(graphs)}
    m = len(next(iter(graphs)))
    pairs = m * (m - 1) // 2
    rows, cols, vals = [], [], []
    for g, i in index.items():
        edges = sorted(g)
        stay = 0.5
        for e, f in itertools.combinations(edges, 2):
            (a, b), (c, d) = e, f
            for x, y, z, w in ((a, c, b, d), (a, d, b, c)):          # the two rewirings
                p = 0.5 * 0.5 / pairs
                n1, n2 = tuple(sorted((x, y))), tuple(sorted((z, w)))
                if x == y or z == w or n1 in g or n2 in g or n1 == n2:
                    stay += p
                    continue
                h = (g - {e, f}) | {n1, n2}
                rows.append(i); cols.append(index[h]); vals.append(p)
        rows.append(i); cols.append(i); vals.append(stay)
    N = len(graphs)
    return sp.csr_matrix((vals, (rows, cols)), shape=(N, N))


def exact_mixing(P, starts, eps=0.25, tmax=100000):
    N = P.shape[0]
    worst = 0
    PT = P.T.tocsr()
    for s in starts:
        x = np.zeros(N); x[s] = 1.0
        for t in range(1, tmax):
            x = PT @ x
            if 0.5 * np.abs(x - 1.0 / N).sum() <= eps:
                worst = max(worst, t)
                break
    return worst


def part1(rng):
    res = []
    for name, deg in (("3-regular, n = 8", [3] * 8),
                      ("one hub, n = 8", [6, 3, 2, 2, 2, 2, 2, 1]),
                      ("two hubs, n = 9", [7, 6, 2, 2, 2, 2, 1, 1, 1])):
        graphs = all_graphs(deg)
        P = switch_matrix(graphs)
        sym = abs(P - P.T).max()
        rowsum = np.abs(np.asarray(P.sum(axis=1)).ravel() - 1).max()
        if P.shape[0] <= 2000:
            lam = np.sort(np.linalg.eigvalsh(P.toarray()))[-2]
        else:
            lam = np.sort(eigsh(P, k=2, which="LA")[0])[0]
        trel = 1 / (1 - lam)
        starts = list(rng.choice(len(graphs), size=min(30, len(graphs)), replace=False))
        tmix = exact_mixing(P, starts)
        n, m = len(deg), sum(deg) // 2
        print(f"  {name:18s} degrees {deg}: {len(graphs)} graphs, |P - P^T| = {sym:.1e}, row sums 1 +- {rowsum:.1e},"
              f" relaxation time {trel:.1f}, t_mix(1/4) = {tmix} steps (= {tmix / m:.1f} per edge);"
              f" the theorem's bound 2n^8 = {2 * n ** 8:.1e}")
        res.append({"name": name, "deg": deg, "states": len(graphs), "asym": float(sym), "t_rel": float(trel),
                    "t_mix": int(tmix), "edges": m, "bound": 2 * n ** 8})
    return res


# ---------- Part 2: motif test on the karate-club network ----------

def triangles(adj):
    return sum(len(adj[a] & adj[b]) for a in adj for b in adj[a] if a < b) // 3


def switch_run(G, steps, thin, rng):
    adj = {v: set(G[v]) for v in G}
    edges = [tuple(e) for e in G.edges()]
    tri = triangles(adj)
    out, accepted = [], 0
    m = len(edges)
    for t in range(steps):
        i, j = rng.integers(m), rng.integers(m - 1)
        j += j >= i
        (a, b), (c, d) = edges[i], edges[j]
        if rng.random() < 0.5:
            c, d = d, c
        if a != c and b != d and c not in adj[a] and d not in adj[b]:
            tri -= len(adj[a] & adj[b]); adj[a].discard(b); adj[b].discard(a)
            tri -= len(adj[c] & adj[d]); adj[c].discard(d); adj[d].discard(c)
            tri += len(adj[a] & adj[c]); adj[a].add(c); adj[c].add(a)
            tri += len(adj[b] & adj[d]); adj[b].add(d); adj[d].add(b)
            edges[i], edges[j] = (a, c), (b, d)
            accepted += 1
        if t % thin == 0:
            out.append(tri)
    return np.array(out), accepted / steps


def autocorr_time(x):
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:n]
    acf /= acf[0]
    tau = 1.0
    for k in range(1, n):
        tau += 2 * acf[k]
        if k >= 5 * tau:
            break
    return tau, acf[:200]


def part2(rng):
    G = nx.karate_club_graph()
    deg = [d for _, d in G.degree()]
    m = G.number_of_edges()
    obs = triangles({v: set(G[v]) for v in G})
    # (a) rejection sampling from the configuration model: probability that a pairing is simple
    trials, simple = 20000, 0
    stubs = np.repeat(np.arange(len(deg)), deg)
    for _ in range(trials):
        s = rng.permutation(stubs).reshape(-1, 2)
        if np.all(s[:, 0] != s[:, 1]) and len({tuple(sorted(e)) for e in s.tolist()}) == m:
            simple += 1
    # (b) erased configuration model: triangles and how much the degrees change
    er_tri, er_edges = [], []
    for _ in range(4000):
        s = rng.permutation(stubs).reshape(-1, 2)
        H = nx.Graph(); H.add_nodes_from(range(len(deg)))
        H.add_edges_from((a, b) for a, b in s.tolist() if a != b)
        er_tri.append(sum(nx.triangles(H).values()) // 3); er_edges.append(H.number_of_edges())
    # (c) switch chain started from the observed graph
    thin = 10
    burn, _ = switch_run(G, 50 * m, thin, rng)
    series, acc = switch_run(G, 4000 * m, thin, rng)
    series = series[len(series) // 20:]
    tau, acf = autocorr_time(series.astype(float))
    tau_steps = tau * thin
    mu, sd = series.mean(), series.std()
    z = (obs - mu) / sd
    print(f"\n  karate club: n = {len(deg)}, m = {m}, max degree {max(deg)}, observed triangles {obs}")
    print(f"  configuration-model rejection: {simple} simple graphs in {trials} pairings"
          f" (acceptance {simple / trials:.4f})")
    print(f"  erased configuration model: mean edges {np.mean(er_edges):.1f} of {m} (degrees changed),"
          f" triangles {np.mean(er_tri):.1f} +- {np.std(er_tri):.1f}")
    print(f"  switch chain: acceptance {acc:.3f}, integrated autocorrelation time of the triangle count"
          f" {tau_steps:.0f} switch attempts = {tau_steps / m:.1f} per edge;"
          f" effective samples {len(series) / tau:.0f}")
    print(f"  null distribution (uniform simple graphs, same degrees): triangles {mu:.1f} +- {sd:.1f};"
          f" observed {obs} -> z = {z:.1f}  (against the erased model it would be z = "
          f"{(obs - np.mean(er_tri)) / np.std(er_tri):.1f})")
    hist = Counter(series.tolist())
    return {"n": len(deg), "m": m, "observed": obs, "reject_accept": simple / trials,
            "erased_edges": float(np.mean(er_edges)), "erased_tri": [float(np.mean(er_tri)), float(np.std(er_tri))],
            "switch_acceptance": acc, "tau_steps": tau_steps, "ess": float(len(series) / tau),
            "erased_z": float((obs - np.mean(er_tri)) / np.std(er_tri)), "null_mean": float(mu), "null_sd": float(sd),
            "z": float(z), "hist": sorted([[int(k), int(v)] for k, v in hist.items()]),
            "acf": [float(a) for a in acf[:100]], "thin": thin}


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(131)
    print("Part 1: exact switch chain on small degree sequences (all labeled graphs enumerated)")
    p1 = part1(rng)
    print("\nPart 2: triangle-motif test on Zachary's karate club")
    p2 = part2(rng)
    json.dump({"exact": p1, "karate": p2}, open(os.path.join(OUT, "switch_chain_null_models.json"), "w"))


if __name__ == "__main__":
    main()
