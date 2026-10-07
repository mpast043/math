#!/usr/bin/env python3
"""Chaos in the Chirikov standard map: Lyapunov exponent, chaotic area, entropy (family 146).

Repository result: the standard map (x, p) -> (x + p + K sin x, p + K sin x) on the 2-torus has
positive metric entropy with respect to area for every sufficiently large K (Sinai's conjecture).
By Pesin's formula the entropy equals the area integral of the positive Lyapunov exponent, so the
theorem says the chaos seen in simulations occupies positive area and is not a numerical artefact,
for every large K, including the windows K ~ 2 pi n where stable accelerator-mode islands exist.

The standard map is the kicked rotor: it models particle motion in circular accelerators,
electron heating in tokamaks and cyclotron-resonance heating, comet orbits perturbed by Jupiter,
and the atom-optics kicked-rotor experiments. This script measures, for a grid of K:
  * the area-averaged finite-time Lyapunov exponent (estimate of the metric entropy),
  * the fraction of area whose orbits are chaotic,
and compares them with Chirikov's large-K prediction ln(K/2).
"""
import json
import math
import os
import sys

import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
M = 160            # M x M grid of initial conditions
STEPS = 2000
CHAOTIC = 0.05     # finite-time exponent above this counts as chaotic (regular orbits: ~ log(STEPS)/STEPS)

KS = [0.5, 0.8, 0.971635, 1.2, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 2 * math.pi, 6.5, 7.0, 8.0, 10.0,
      4 * math.pi, 15.0, 20.0, 30.0, 50.0, 100.0]


def lyapunov(K, m=M, steps=STEPS, seed=0):
    rng = np.random.default_rng(seed)
    g = (np.arange(m) + 0.5) / m * 2 * np.pi
    x, p = np.meshgrid(g, g)
    x = (x.ravel() + rng.uniform(-1e-3, 1e-3, m * m)) % (2 * np.pi)
    p = p.ravel().copy()
    # tangent vector (dx, dp), renormalised every step
    dx = np.ones_like(x) / math.sqrt(2)
    dp = np.ones_like(x) / math.sqrt(2)
    acc = np.zeros_like(x)
    for _ in range(steps):
        kc = K * np.cos(x)
        dp_new = dp + kc * dx
        dx_new = dx + dp_new
        p = (p + K * np.sin(x)) % (2 * np.pi)
        x = (x + p) % (2 * np.pi)
        norm = np.hypot(dx_new, dp_new)
        acc += np.log(norm)
        dx = dx_new / norm
        dp = dp_new / norm
    return acc / steps


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    print(f"{M}x{M} initial conditions, {STEPS} iterations each")
    print("      K     mean lambda   ln(K/2)   chaotic area   mean lambda on chaotic set")
    for K in KS:
        lam = lyapunov(K)
        chaotic = lam > CHAOTIC
        frac = float(np.mean(chaotic))
        mean = float(np.mean(np.maximum(lam, 0)))
        on_chaos = float(np.mean(lam[chaotic])) if chaotic.any() else 0.0
        ref = math.log(K / 2) if K > 2 else float("nan")
        print(f"  {K:8.4f}   {mean:8.4f}    {ref:8.4f}     {frac:7.4f}        {on_chaos:8.4f}")
        rows.append({"K": K, "entropy": mean, "ln_K_over_2": ref if K > 2 else None,
                     "chaotic_fraction": frac, "lambda_chaotic": on_chaos})
    big = [r for r in rows if r["K"] >= 10]
    worst = max(abs(r["entropy"] - r["ln_K_over_2"]) for r in big)
    print(f"\nfor K >= 10, |entropy estimate - ln(K/2)| <= {worst:.3f}")
    json.dump({"steps": STEPS, "grid": M, "rows": rows}, open(os.path.join(OUT, "standard_map_entropy.json"), "w"))


if __name__ == "__main__":
    main()
