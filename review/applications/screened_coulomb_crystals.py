#!/usr/bin/env python3
"""Ground-state crystals of 2D screened-Coulomb (Yukawa) particles (family 090).

The repository proves universal optimality of the triangular lattice in the plane:
among all configurations of density one, it minimizes the energy for every
completely monotone function of squared distance. The Yukawa / Debye-Hueckel
interaction V(r) = exp(-kappa r)/r is such a function of t = r^2
(exp(-kappa sqrt t) and t^(-1/2) are completely monotone, and so is their product),
so the result applies to complex-plasma monolayers, charged colloids at interfaces
and other screened-Coulomb layers at every screening length.

This script computes energies per particle at density one for the triangular,
square and other Bravais lattices, for the honeycomb and kagome structures, and for
randomly perturbed triangular supercells, for several screening parameters.
"""
import json
import math
import os
import sys

import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
rng = np.random.default_rng(90)


def yukawa(r, kappa):
    return np.exp(-kappa * r) / r


def periodic_energy(pts, A, kappa, rcut):
    """Energy per particle: (1/N) sum_i sum_{j, images != self} V(|x_i - x_j - image|)."""
    N = len(pts)
    A = np.asarray(A, float)
    nmax = int(math.ceil(rcut / min(np.linalg.norm(A[0]), np.linalg.norm(A[1])))) + 2
    imgs = np.array([m * A[0] + n * A[1] for m in range(-nmax, nmax + 1) for n in range(-nmax, nmax + 1)])
    total = 0.0
    for i in range(N):
        d = pts[i] - pts  # (N, 2)
        allv = (d[:, None, :] + imgs[None, :, :]).reshape(-1, 2)
        r = np.sqrt((allv ** 2).sum(1))
        r = r[(r > 1e-12) & (r < rcut)]
        total += yukawa(r, kappa).sum()
    return total / N


def bravais(z):
    """Unit-covolume lattice with shape parameter z = x + iy (basis (1,0), (x,y), scaled)."""
    x, y = z.real, z.imag
    s = 1 / math.sqrt(y)
    return np.array([[0.0, 0.0]]), [[s, 0.0], [s * x, s * y]]


def structure(name):
    if name == "triangular":
        return bravais(complex(0.5, math.sqrt(3) / 2))
    if name == "square":
        return bravais(complex(0, 1))
    if name == "honeycomb":   # two points per triangular cell, rescaled to density one
        a1, a2 = np.array([1.0, 0.0]), np.array([0.5, math.sqrt(3) / 2])
        pts = np.array([[0, 0], (a1 + a2) / 3])
        s = math.sqrt(2 / (math.sqrt(3) / 2))
        return pts * s, [a1 * s, a2 * s]
    if name == "kagome":
        a1, a2 = np.array([2.0, 0.0]), np.array([1.0, math.sqrt(3)])
        pts = np.array([[0, 0], [1, 0], [0.5, math.sqrt(3) / 2]])
        s = math.sqrt(3 / (2 * math.sqrt(3)))
        return pts * s, [a1 * s, a2 * s]
    raise KeyError(name)


def supercell(base_pts, A, n):
    pts = np.array([p + i * np.array(A[0]) + j * np.array(A[1]) for i in range(n) for j in range(n) for p in base_pts])
    return pts, [n * np.array(A[0]), n * np.array(A[1])]


def main():
    os.makedirs(OUT, exist_ok=True)
    kappas = [0.5, 1.0, 2.0, 4.0]
    print("Energy per particle at density 1, relative to the triangular lattice (percent above)")
    print("kappa   E_triangular   square   rectangle 2:1   honeycomb   kagome   perturbed tri (sigma=0.05, 0.15)")
    rows = []
    for kappa in kappas:
        rcut = 40.0 / kappa + 10
        E = {}
        for name in ("triangular", "square", "honeycomb", "kagome"):
            p, A = structure(name)
            E[name] = periodic_energy(p, A, kappa, rcut)
        p, A = bravais(complex(0, 2))
        E["rect2"] = periodic_energy(p, A, kappa, rcut)
        pert = {}
        for sig in (0.05, 0.15):
            vals = []
            for _ in range(3):
                p, A = structure("triangular")
                P, B = supercell(p, A, 8)
                P = P + rng.normal(scale=sig, size=P.shape)
                vals.append(periodic_energy(P, B, kappa, rcut))
            pert[sig] = float(np.mean(vals))
        t = E["triangular"]
        rel = lambda v: 100 * (v / t - 1)
        print(f"{kappa:5.1f}   {t:11.5f}   {rel(E['square']):+6.2f}%  {rel(E['rect2']):+8.2f}%    {rel(E['honeycomb']):+7.2f}%  "
              f"{rel(E['kagome']):+6.2f}%   {rel(pert[0.05]):+6.2f}%, {rel(pert[0.15]):+6.2f}%")
        rows.append({"kappa": kappa, "E_tri": t, "square": rel(E["square"]), "rect2": rel(E["rect2"]),
                     "honeycomb": rel(E["honeycomb"]), "kagome": rel(E["kagome"]),
                     "perturbed_005": rel(pert[0.05]), "perturbed_015": rel(pert[0.15])})
    # energy landscape along the boundary of the lattice moduli space: square -> triangular -> elongated
    path = []
    for k, th in enumerate(np.linspace(90, 60, 16)):
        path.append(("arc", complex(math.cos(math.radians(th)), math.sin(math.radians(th)))))
    for y in np.linspace(math.sqrt(3) / 2, 2.0, 16)[1:]:
        path.append(("ray", complex(0.5, y)))
    landscape = {}
    for kappa in kappas:
        rcut = 40.0 / kappa + 10
        p, A = structure("triangular")
        t = periodic_energy(p, A, kappa, rcut)
        landscape[str(kappa)] = [100 * (periodic_energy(*bravais(z), kappa, rcut) / t - 1) for _, z in path]
    json.dump({"rows": rows, "path": [[z.real, z.imag] for _, z in path], "landscape": landscape},
              open(os.path.join(OUT, "screened_coulomb_crystals.json"), "w"))
    print("\nAlong square -> triangular -> elongated lattices, the minimum is at the triangular lattice for every kappa:",
          all(min(v) >= -1e-9 for v in landscape.values()))


if __name__ == "__main__":
    main()
