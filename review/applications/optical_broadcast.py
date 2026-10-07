#!/usr/bin/env python3
"""Exact capacity region of the pure-loss optical broadcast channel (family 273).

The entropy photon-number inequality (EPnI) was the missing step in the converse of
Guha-Shapiro-Erkmen (2007). With it (Corollary in the EPnI paper), the classical
capacity region of the degraded pure-loss broadcast channel with transmissivities
eta_B > eta_C (eta_B + eta_C <= 1) and mean photon number N per use is the convex
hull of the pairs (nats per use)

    R_B <= g(eta_B beta N),   R_C <= g(eta_C N) - g(eta_C beta N),   0 <= beta <= 1,

g(x) = (x+1) ln(x+1) - x ln x. It is achieved by coherent-state superposition coding.
This script computes the region for representative fibre/free-space splits and
compares it with time-sharing (the best a naive scheme achieves), reporting the
gain in the weak receiver's rate when the strong receiver gets half its maximum.
It also reports the companion corollary: the minimum output entropy of a thermal
attenuator at fixed input entropy.
"""
import json
import math
import os
import sys

import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
LN2 = math.log(2)


def g(x):
    return 0.0 if x <= 0 else (x + 1) * math.log1p(x) - x * math.log(x)


def ginv(s):
    lo, hi = 0.0, 1.0
    while g(hi) < s:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if g(mid) < s else (lo, mid)
    return (lo + hi) / 2


def region(etaB, etaC, N, n=201):
    betas = np.linspace(0, 1, n)
    RB = np.array([g(etaB * b * N) for b in betas]) / LN2
    RC = np.array([g(etaC * N) - g(etaC * b * N) for b in betas]) / LN2
    return RB, RC


def weak_rate_at(RB, RC, target):
    # boundary is decreasing in RC as RB increases; interpolate RC at RB = target
    return float(np.interp(target, RB, RC))


def main():
    os.makedirs(OUT, exist_ok=True)
    cases = [
        ("Fibre splitter 50/25 (25% lost), N = 1", 0.5, 0.25, 1.0),
        ("Fibre splitter 50/25, N = 10", 0.5, 0.25, 10.0),
        ("Free-space, near 60% / far 10%, N = 10", 0.6, 0.1, 10.0),
        ("Free-space, near 60% / far 10%, N = 100", 0.6, 0.1, 100.0),
    ]
    data = []
    print("case                                         C_B(bits) C_C(bits)  weak rate at R_B=C_B/2: superposition vs time-sharing (gain)")
    for name, eB, eC, N in cases:
        RB, RC = region(eB, eC, N)
        CB, CC = RB[-1], RC[0]
        half = CB / 2
        sup = weak_rate_at(RB, RC, half)
        ts = CC * (1 - half / CB)
        print(f"{name:44s} {CB:8.3f} {CC:8.3f}   {sup:6.3f} vs {ts:6.3f}  (+{(sup / ts - 1) * 100:.0f}%)")
        data.append({"name": name, "etaB": eB, "etaC": eC, "N": N, "RB": RB.tolist(), "RC": RC.tolist(),
                     "CB": CB, "CC": CC, "weak_superposition": sup, "weak_timesharing": ts})
    print("\nThermal attenuator, minimum output entropy per mode at input entropy s (nats):")
    print("  S_min = g(eta g^{-1}(s) + (1-eta) N_B), attained by thermal inputs")
    for eta, NB in ((0.5, 0.0), (0.5, 1.0), (0.9, 0.1)):
        row = [g(eta * ginv(s) + (1 - eta) * NB) / LN2 for s in (0.5, 1.0, 2.0)]
        print(f"  eta={eta}, N_B={NB}: s=0.5,1,2 nats -> S_min = " + ", ".join(f"{v:.3f}" for v in row) + " bits")
    json.dump(data, open(os.path.join(OUT, "optical_broadcast.json"), "w"))


if __name__ == "__main__":
    main()
