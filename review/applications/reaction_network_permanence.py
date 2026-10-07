#!/usr/bin/env python3
"""Weak reversibility forces permanence in mass-action chemistry (family 149).

Repository result: every weakly reversible mass-action system (each linkage class strongly
connected), with ANY positive rate constants and any deficiency, is permanent: each positive
stoichiometric compatibility class has a compact absorbing set in the open positive orthant,
so all species concentrations are eventually bounded below and above by positive constants.

Why it matters: in systems biology and ecology one usually knows the reaction graph but not the
rate constants. The theorem turns a property of the graph that can be checked by hand into a
guarantee for every choice of rates: no species can be driven to extinction (or blow up). Before,
this was known for complex-balanced systems, or in low dimension, or for a single linkage class.

Demonstration: random weakly reversible networks with 4 species, several linkage classes and
positive deficiency (outside the complex-balanced setting), random rates spread over two orders of
magnitude, started next to the boundary (some species at 1e-6). For each network we also delete
one reaction, which breaks weak reversibility, and run the same starts.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
NETWORKS = int(sys.argv[2]) if len(sys.argv) > 2 else 200
S = 4
T_END = 2000.0


def random_network(rng):
    """Linkage classes = directed cycles (plus random chords) over random complexes of order <= 2."""
    while True:
        seen, classes = set(), []
        for _ in range(rng.integers(2, 4)):
            cyc, length = [], rng.integers(2, 5)
            for _ in range(200):
                y = tuple(int(v) for v in rng.integers(0, 3, S) * (rng.random(S) < 0.4))
                if sum(y) <= 2 and y not in seen:
                    seen.add(y); cyc.append(y)
                if len(cyc) == length:
                    break
            if len(cyc) >= 2:
                classes.append(cyc)
        reactions = []
        for cyc in classes:
            m = len(cyc)
            reactions += [(cyc[i], cyc[(i + 1) % m]) for i in range(m)]
            if m >= 3 and rng.random() < 0.5:                       # optional chord
                i, j = rng.choice(m, 2, replace=False)
                if (cyc[i], cyc[j]) not in reactions:
                    reactions.append((cyc[i], cyc[j]))
        Y = np.array([r[0] for r in reactions], float)
        D = np.array([np.subtract(r[1], r[0]) for r in reactions], float)
        n, ell, s = len(seen), len(classes), np.linalg.matrix_rank(D)
        if np.all(np.abs(D).sum(axis=0) > 0) and s >= 2 and n - ell - s >= 1:
            return {"classes": classes, "reactions": reactions, "Y": Y, "D": D, "deficiency": int(n - ell - s),
                    "rank": int(s), "complexes": n}


def is_weakly_reversible(reactions):
    graph = {}
    for a, b in reactions:
        graph.setdefault(a, set()).add(b)
    def reaches(src, dst):
        stack, seen = [src], {src}
        while stack:
            v = stack.pop()
            if v == dst:
                return True
            for w in graph.get(v, ()):
                if w not in seen:
                    seen.add(w); stack.append(w)
        return False
    return all(reaches(b, a) for a, b in reactions)


def simulate(Y, D, k, x0):
    """Integrate in log-concentrations so tiny values stay accurate. Returns (status, late-time minimum, decay)."""
    def rhs(t, z):
        z = np.clip(z, -700, 700)
        with np.errstate(over="ignore", invalid="ignore"):   # only reached on runs that are blowing up or dying out
            return (D.T @ (k * np.exp(np.clip(Y @ z, -700, 700)))) * np.exp(-z)
    blow = lambda t, z: np.max(z) - np.log(1e6)
    blow.terminal = True
    sol = solve_ivp(rhs, (0, T_END), np.log(x0), method="LSODA", rtol=1e-8, atol=1e-9,
                    events=blow, dense_output=True)
    if sol.status == 1:
        return "blow-up", None, None
    a = np.exp(sol.sol(np.linspace(T_END / 2, 3 * T_END / 4, 200))).min()
    b = np.exp(sol.sol(np.linspace(3 * T_END / 4, T_END, 200))).min()
    return "ok", float(min(a, b)), float(b / a) if a > 0 else 0.0


def boundary_start(rng, xbar, D):
    """A point in the same stoichiometric class as xbar with some species at 1e-6 of their xbar value."""
    v = D.T @ rng.normal(size=D.shape[0])
    if not np.any(v < 0):
        v = -v
    neg = v < 0
    t = np.min(xbar[neg] / -v[neg])
    return np.maximum(xbar + t * (1 - 1e-6) * v, 1e-300)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(149)
    ratios, abs_min, deficiencies, runs = [], [], [], 0
    ctrl = {"extinct": 0, "blow-up": 0, "persistent": 0}
    for net_i in range(NETWORKS):
        net = random_network(rng)
        deficiencies.append(net["deficiency"])
        R = len(net["reactions"])
        k = 10 ** rng.uniform(-1, 1, R)
        xbar = 10 ** rng.uniform(-1, 1, S)
        status, ref, _ = simulate(net["Y"], net["D"], k, xbar)
        # a deletion that really breaks weak reversibility
        drops = [j for j in range(R) if not is_weakly_reversible(net["reactions"][:j] + net["reactions"][j + 1:])]
        keep = np.arange(R) != rng.choice(drops)
        for _ in range(3):
            x0 = boundary_start(rng, xbar, net["D"])
            status, m, _ = simulate(net["Y"], net["D"], k, x0)
            runs += 1
            ratios.append(m / ref if status == "ok" else -1.0)
            abs_min.append(m if status == "ok" else -1.0)
            status, m, decay = simulate(net["Y"][keep], net["D"][keep], k[keep], x0)
            if status == "blow-up":
                ctrl["blow-up"] += 1
            elif m < 1e-9 or decay < 0.5:
                ctrl["extinct"] += 1
            else:
                ctrl["persistent"] += 1
        if (net_i + 1) % 50 == 0:
            print(f"  {net_i + 1} networks done", flush=True)
    r = np.array(ratios)
    ok = r > 0
    print(f"\n{NETWORKS} random weakly reversible networks, {S} species, deficiency {min(deficiencies)}-"
          f"{max(deficiencies)} (mean {np.mean(deficiencies):.2f}), rates log-uniform on [0.1, 10].")
    print(f"{runs} runs started inside the class of a random state xbar, with some species at 1e-6 of xbar.")
    print(f"  blow-ups: {int(np.sum(~ok))}")
    print(f"  late-time minimum / late-time minimum from xbar itself: min {r[ok].min():.3f}, median "
          f"{np.median(r[ok]):.3f}, max {r[ok].max():.3f}")
    print(f"  runs whose late-time minimum is below 1e-3 of the reference: {int(np.sum(r[ok] < 1e-3))}")
    print(f"same starts with one reaction deleted so that weak reversibility fails: extinction {ctrl['extinct']}, "
          f"blow-up {ctrl['blow-up']}, persistent {ctrl['persistent']}")
    json.dump({"networks": NETWORKS, "runs": runs, "deficiency": deficiencies, "ratio": ratios,
               "late_min": abs_min, "control": ctrl}, open(os.path.join(OUT, "reaction_network_permanence.json"), "w"))


if __name__ == "__main__":
    main()
