#!/usr/bin/env python3
"""How stable are optimal transport maps? Exponent 1/2 for generic targets, 1/3 in the worst case (family 374).

Repository result: for the uniform source on a convex body in dimension >= 2 and targets in a fixed
compact set, Brenier maps satisfy ||T_mu - T_nu||_{L^2} <= C W_2(mu, nu)^{1/3}, and the exponent 1/3
is sharp even for three-atom targets. This disproves the conjectured square-root bound.

Why it matters: OT maps are estimated from data in domain adaptation, generative modelling,
single-cell trajectory inference and colour transfer. A stability inequality converts an error in the
estimated target distribution into an error in the map. The theorem gives the uniform worst-case
conversion and shows where it bites: targets with small-mass components. A tiny cluster can be moved
at almost no W_2 cost, yet its transport cell tilts and reassigns a much larger region of the source.

This script solves the semi-discrete OT problem itself (uniform source on [-1, 1]^2, power diagrams
by exact polygon clipping, Newton's method on the dual weights), so it does not reuse the paper's
explicit potentials. It measures the map change against W_2 (exact 3x3 transport LP) for
  (A) the paper's family: masses ((1-a)/2, (1-a)/2, a), central atom 0 -> (a/2) e_2, a -> 0,
  (B) a generic family: masses 1/3 each, central atom 0 -> eps e_2, eps -> 0,
  (C) a fixed small mass a = 0.01 with the central atom moved by b -> 0.
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import linprog

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
SQUARE = [np.array(p, float) for p in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def clip(poly, n, c):
    """Part of a convex polygon where n.x + c >= 0."""
    out = []
    for k in range(len(poly)):
        P, Q = poly[k], poly[(k + 1) % len(poly)]
        fp, fq = n @ P + c, n @ Q + c
        if fp >= 0:
            out.append(P)
        if fp * fq < 0:
            out.append(P + fp / (fp - fq) * (Q - P))
    return out


def area(poly):
    if len(poly) < 3:
        return 0.0
    x = np.array([p[0] for p in poly]); y = np.array([p[1] for p in poly])
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def chord(poly, n, c):
    """Length of the intersection of a convex polygon with the line n.x + c = 0."""
    pts = []
    for k in range(len(poly)):
        P, Q = poly[k], poly[(k + 1) % len(poly)]
        fp, fq = n @ P + c, n @ Q + c
        if fp == 0:
            pts.append(P)
        elif fp * fq < 0:
            pts.append(P + fp / (fp - fq) * (Q - P))
    return max((np.linalg.norm(p - q) for p in pts for q in pts), default=0.0)


def cell(Y, w, i, skip=None):
    poly = SQUARE
    for j in range(len(Y)):
        if j != i and j != skip:
            poly = clip(poly, Y[i] - Y[j], w[i] - w[j])
    return poly


def solve_weights(Y, m, tol=1e-14):
    """Weights w with |{x: argmax_j x.y_j + w_j = i}| / 4 = m_i (damped Newton, w_0 = 0)."""
    N = len(Y)
    w = -0.5 * np.sum(Y ** 2, axis=1)                    # Voronoi start: all cells non-empty
    for _ in range(200):
        areas = np.array([area(cell(Y, w, i)) / 4 for i in range(N)])
        g = areas - m
        if np.max(np.abs(g)) < tol:
            return w
        J = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    l = chord(cell(Y, w, i, skip=j), Y[i] - Y[j], w[i] - w[j]) / np.linalg.norm(Y[i] - Y[j]) / 4
                    J[i, j] -= l; J[i, i] += l
        step = np.zeros(N)
        step[1:] = np.linalg.solve(J[1:, 1:], -g[1:])
        t = 1.0
        while t > 1e-12:                                   # keep every cell non-empty (Kitagawa-Merigot-Thibert)
            w_new = w + t * step
            a_new = np.array([area(cell(Y, w_new, i)) / 4 for i in range(N)])
            if np.all(a_new > 0.5 * np.minimum(m, areas)) and np.max(np.abs(a_new - m)) <= (1 - t / 2) * np.max(np.abs(g)):
                break
            t /= 2
        w = w_new
    raise RuntimeError("Newton did not converge")


def map_distance(Y1, w1, Y2, w2):
    tot = 0.0
    for i in range(len(Y1)):
        c1 = cell(Y1, w1, i)
        for j in range(len(Y2)):
            poly = c1
            for k in range(len(Y2)):
                if k != j:
                    poly = clip(poly, Y2[j] - Y2[k], w2[j] - w2[k])
            tot += area(poly) / 4 * np.sum((Y1[i] - Y2[j]) ** 2)
    return np.sqrt(tot)


def w2_distance(Y1, m1, Y2, m2):
    n1, n2 = len(Y1), len(Y2)
    C = np.array([[np.sum((p - q) ** 2) for q in Y2] for p in Y1]).ravel()
    A = []
    for i in range(n1):
        row = np.zeros(n1 * n2); row[i * n2:(i + 1) * n2] = 1; A.append(row)
    for j in range(n2):
        row = np.zeros(n1 * n2); row[j::n2] = 1; A.append(row)
    res = linprog(C, A_eq=np.array(A), b_eq=np.concatenate([m1, m2]), bounds=(0, None), method="highs")
    return np.sqrt(res.fun)


def family_point(masses, shift):
    Y1 = np.array([[-1.0, 0.0], [1.0, 0.0], [0.0, 0.0]])
    Y2 = Y1.copy(); Y2[2] = [0.0, shift]
    m = np.array(masses)
    w1, w2 = solve_weights(Y1, m), solve_weights(Y2, m)
    return float(w2_distance(Y1, m, Y2, m)), float(map_distance(Y1, w1, Y2, w2))


def main():
    os.makedirs(OUT, exist_ok=True)
    out = {}
    grid = np.logspace(-4, -0.7, 12)
    specs = {
        "A: paper's family, mass a, shift a/2": [(((1 - a) / 2, (1 - a) / 2, a), a / 2, a) for a in grid],
        "B: masses 1/3, shift eps": [((1 / 3, 1 / 3, 1 / 3), e, e) for e in grid],
        "C: mass 0.01, shift b": [((0.495, 0.495, 0.01), b, b) for b in grid[grid < 0.01]],
    }
    for name, pts in specs.items():
        rows = []
        print(f"\n{name}")
        print("    parameter      W2(mu,nu)       ||T_mu - T_nu||    closed form (family A)")
        for masses, shift, par in pts:
            w2, dT = family_point(masses, shift)
            cf = np.sqrt(par) / 2 * np.sqrt(1 + par ** 2) if name.startswith("A") else float("nan")
            print(f"   {par:10.3e}    {w2:12.5e}     {dT:12.5e}      {cf:12.5e}")
            rows.append({"param": par, "w2": w2, "dT": dT})
        x = np.log([r["w2"] for r in rows]); y = np.log([r["dT"] for r in rows])
        slope = np.polyfit(x[:6], y[:6], 1)[0]
        print(f"   log-log slope of ||dT|| against W2 for the smallest perturbations: {slope:.4f}")
        mass = pts[0][0][2]
        if not name.startswith("A"):
            const = rows[0]["dT"] / (mass ** -0.25 * np.sqrt(rows[0]["w2"]))
            print(f"   ||dT|| / (m^(-1/4) W2^(1/2)) = {const:.4f} with central mass m = {mass:.4g}")
        out[name] = {"rows": rows, "slope": slope, "mass": mass}
    json.dump(out, open(os.path.join(OUT, "ot_stability.json"), "w"))


if __name__ == "__main__":
    main()
