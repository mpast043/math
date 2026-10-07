#!/usr/bin/env python3
"""How many classical bits can a decaying qubit hold? (family 276)

The repository proves the classical capacity of the generalized amplitude-damping
channel A_{gamma,nu}, including over entangled multi-use codes:

    C = (1/ln2) max_p [ h((1-gamma)p + gamma nu) - G(gamma nu(1-nu) + gamma(1-gamma)(p-nu)^2) ],
    G(u) = h((1+sqrt(1-4u))/2),

attained by the two states sqrt(1-p)|0> +/- sqrt(p)|1> with collective decoding.

Application: a superconducting qubit (f = 5 GHz, T1 = 100 us) idling for time t is
A_{gamma,nu} with gamma = 1 - exp(-t/T1) and nu the thermal excited population at the
effective temperature, nu = 1/(1 + exp(hf/kT)). We compute the capacity versus
storage time, the optimal signal states, and the gain over the naive scheme (store a
bit as |0> or |1>, read out in that basis), which is a binary asymmetric channel.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize_scalar

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
LN2 = math.log(2)
h_planck, k_B = 6.62607015e-34, 1.380649e-23


def h(q):
    if q <= 0 or q >= 1:
        return 0.0
    return -q * math.log(q) - (1 - q) * math.log(1 - q)


def G(u):
    u = min(max(u, 0.0), 0.25)
    return h((1 + math.sqrt(1 - 4 * u)) / 2)


def capacity(g, nu):
    f = lambda p: -(h((1 - g) * p + g * nu) - G(g * nu * (1 - nu) + g * (1 - g) * (p - nu) ** 2))
    grid = np.linspace(0, 1, 401)
    p0 = grid[int(np.argmin([f(p) for p in grid]))]
    r = minimize_scalar(f, bounds=(max(0, p0 - 0.005), min(1, p0 + 0.005)), method="bounded", options={"xatol": 1e-10})
    return -r.fun / LN2, r.x


def bac_capacity(e01, e10):
    """Binary asymmetric channel: P(read 1 | stored 0) = e01, P(read 0 | stored 1) = e10."""
    def I(q):  # q = P(store 1)
        p1 = q * (1 - e10) + (1 - q) * e01
        return h(p1) - (q * h(e10) + (1 - q) * h(e01))
    r = minimize_scalar(lambda q: -I(q), bounds=(0, 1), method="bounded", options={"xatol": 1e-10})
    return -r.fun / LN2


def nu_of_T(T, f=5e9):
    return 1.0 / (1.0 + math.exp(h_planck * f / (k_B * T)))


def main():
    os.makedirs(OUT, exist_ok=True)
    T1 = 100e-6
    temps = [0.030, 0.050, 0.070, 0.100]
    ts = np.linspace(0, 3 * T1, 61)
    curves = {}
    print("Effective temperature -> thermal population nu (5 GHz qubit)")
    for T in temps:
        print(f"  {T*1e3:5.0f} mK -> nu = {nu_of_T(T):.4f}")
    print("\nStorage time  " + "  ".join(f"C({T*1e3:.0f} mK)" for T in temps) + "   naive(50 mK)  optimal p (50 mK)")
    for T in temps:
        nu = nu_of_T(T)
        curves[f"{T*1e3:.0f} mK"] = [capacity(1 - math.exp(-t / T1), nu)[0] for t in ts]
    naive = []
    for i, t in enumerate(ts):
        g = 1 - math.exp(-t / T1)
        nu = nu_of_T(0.050)
        naive.append(bac_capacity(g * nu, g * (1 - nu)))
        if i % 10 == 0:
            cap, p = capacity(g, nu)
            row = "  ".join(f"{curves[k][i]:9.4f}" for k in curves)
            print(f"  {t*1e6:6.0f} us   {row}     {naive[-1]:8.4f}       {p:.3f}")
    # storage time at which capacity drops to 1/2 bit
    for T in temps:
        c = np.array(curves[f"{T*1e3:.0f} mK"])
        t_half = float(np.interp(0.5, c[::-1], ts[::-1]))
        print(f"  capacity falls to 0.5 bit after {t_half*1e6:.1f} us at {T*1e3:.0f} mK")
    i_mid = 20  # t = T1
    gain = curves["50 mK"][i_mid] / naive[i_mid] - 1
    print(f"\nAt t = T1 and 50 mK: optimal {curves['50 mK'][i_mid]:.4f} bit vs naive {naive[i_mid]:.4f} bit (+{gain*100:.1f}%)")
    json.dump({"t_us": (ts * 1e6).tolist(), "curves": curves, "naive_50mK": naive},
              open(os.path.join(OUT, "qubit_memory_capacity.json"), "w"))


if __name__ == "__main__":
    main()
