#!/usr/bin/env python3
"""Anderson localization in two and three dimensions: what finite-size numerics see (family 261).

Repository result, for H = discrete Laplacian (hopping 1) + i.i.d. uniform potential on [-W/2, W/2]:
  * d = 2: for EVERY W > 0 the spectrum is almost surely pure point (all states localized).
  * d >= 3: for small W > 0 there is purely absolutely continuous spectrum (extended states)
    on a fixed energy interval.
These are the two predictions of the scaling theory of localization (Abrahams, Anderson,
Licciardello, Ramakrishnan 1979): no metal in 2D, a metal-insulator transition in 3D.

Why it matters: in 2D the localization length grows like exp(c / W^2), so at weak disorder it
exceeds any sample a computer (or most experiments) can reach, and numerics alone cannot decide
whether weakly disordered 2D systems (thin films, graphene-like lattices, photonic lattices) are
metals. The theorem settles it. This script shows what simulations see. The level-spacing ratio
r = min(s_n, s_{n+1}) / max(s_n, s_{n+1}) averages 0.5307 for extended states (GOE statistics)
and 2 ln 2 - 1 = 0.3863 for localized states (Poisson statistics). Its trend with system size L
tells which phase a sample flows to.
"""
import json
import os
import sys
import time

import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
GOE, POISSON = 0.5307, 2 * np.log(2) - 1
WINDOW = 0.2   # use the middle 20% of the spectrum (energies near the band centre)


def hamiltonian(L, d, W, rng):
    n = L ** d
    idx = np.arange(n).reshape((L,) * d)
    H = np.zeros((n, n))
    for axis in range(d):
        nb = np.roll(idx, -1, axis=axis).ravel()
        H[idx.ravel(), nb] = -1.0
        H[nb, idx.ravel()] = -1.0
    H[np.arange(n), np.arange(n)] = rng.uniform(-W / 2, W / 2, n)
    return H


def mean_ratio(L, d, W, samples, rng):
    rs = []
    for _ in range(samples):
        e = np.linalg.eigvalsh(hamiltonian(L, d, W, rng))
        n = len(e)
        mid = e[int(n * (0.5 - WINDOW / 2)): int(n * (0.5 + WINDOW / 2))]
        s = np.diff(mid)
        r = np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])
        rs.append(r)
    r = np.concatenate(rs)
    per_sample = [x.mean() for x in rs]
    err = np.std(per_sample, ddof=1) / np.sqrt(len(per_sample)) if len(per_sample) > 1 else float("nan")
    return float(r.mean()), float(err)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(2026)
    plan = {
        2: {"L": [(16, 160), (32, 40), (64, 16)], "W": [1, 2, 4, 6, 8, 12, 16]},
        3: {"L": [(8, 160), (12, 40), (16, 16)], "W": [4, 8, 12, 14, 16.5, 19, 22, 26]},
    }
    rows = []
    print(f"<r> for extended states (GOE) = {GOE}, localized (Poisson) = {POISSON:.4f}")
    for d, cfg in plan.items():
        print(f"\nd = {d}")
        print("   W  " + "".join(f"    L={L:<3d}         " for L, _ in cfg["L"]) + "  trend with L")
        for W in cfg["W"]:
            vals = []
            t0 = time.time()
            for L, samples in cfg["L"]:
                m, e = mean_ratio(L, d, W, samples, rng)
                vals.append((L, m, e))
                rows.append({"d": d, "W": W, "L": L, "samples": samples, "r": m, "err": e})
            trend = vals[-1][1] - vals[0][1]
            sigma = np.hypot(vals[-1][2], vals[0][2])
            word = ("rises toward GOE" if trend > 2 * sigma else
                    "falls toward Poisson" if trend < -2 * sigma else "no significant change")
            print(f"  {W:4.1f} " + "".join(f"  {m:.4f} +- {e:.4f}  " for _, m, e in vals) + f"  {trend:+.4f} +- {sigma:.4f} {word}"
                  f"   ({time.time() - t0:.0f} s)", flush=True)
    json.dump({"goe": GOE, "poisson": POISSON, "window": WINDOW, "rows": rows},
              open(os.path.join(OUT, "anderson_level_statistics.json"), "w"))


if __name__ == "__main__":
    main()
