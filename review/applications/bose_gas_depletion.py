#!/usr/bin/env python3
"""Quantum depletion of dilute Bose gases (family 267), applied to cold-atom parameters.

The repository proves, for the hard-sphere gas (and for bounded repulsive potentials
with scattering length a), with the thermodynamic limit taken first, that the
occupations of nonzero momenta follow the Bogoliubov profile:
    n(k) ~ g(k / k_xi),  g(t) = (t^2+1)/(2 sqrt(t^4+2t^2)) - 1/2,  k_xi = sqrt(8 pi rho a),
so the depleted fraction is (8 / (3 sqrt(pi))) sqrt(rho a^3) to leading order, and the large-momentum
tail is n(k) ~ (4 pi rho a)^2 / k^4 (Tan's contact at Bogoliubov order). A companion
paper proves Bose-Einstein condensation at a fixed positive temperature for the
dilute hard-sphere gas, which had been open for interacting gases.

This script evaluates the depletion law and the momentum profile for representative
experimental parameters (computed predictions, not measurements). Values for liquid
helium are outside the dilute regime and are shown only for contrast.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import quad

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
a0 = 5.29177210903e-11


def g(t):
    """(t^2+1)/(2 sqrt(t^4+2t^2)) - 1/2, written without cancellation at large t."""
    r = math.sqrt(t ** 4 + 2 * t * t)
    return 1 / (2 * r * (t * t + 1 + r))


def main():
    os.makedirs(OUT, exist_ok=True)
    # check the total mass of the Bogoliubov measure: (8pi)^{3/2}/(2pi)^3 * int g(|t|) d^3t = 8/(3 sqrt(pi))
    f = lambda t: 4 * math.pi * t * t * g(t)
    mass = (8 * math.pi) ** 1.5 / (2 * math.pi) ** 3 * (quad(f, 0, 1, limit=200)[0] + quad(f, 1, np.inf, limit=200)[0])
    print(f"Total mass of the Bogoliubov measure: {mass:.6f} (8/(3 sqrt pi) = {8 / (3 * math.sqrt(math.pi)):.6f})")
    systems = [
        ("23Na BEC, a = 52 a0, n = 1e14 cm^-3", 52 * a0, 1e20),
        ("87Rb BEC, a = 100 a0, n = 1e14 cm^-3", 100 * a0, 1e20),
        ("87Rb BEC, a = 100 a0, n = 1e15 cm^-3", 100 * a0, 1e21),
        ("39K box, Feshbach a = 1000 a0, n = 5e11 cm^-3", 1000 * a0, 5e17),
        ("39K box, Feshbach a = 3000 a0, n = 5e11 cm^-3", 3000 * a0, 5e17),
    ]
    rows = []
    print("\nsystem                                         n a^3        depleted fraction   healing length xi")
    for name, a, n in systems:
        eta = n * a ** 3
        dep = 8 / (3 * math.sqrt(math.pi)) * math.sqrt(eta)
        xi = 1 / math.sqrt(8 * math.pi * n * a)
        print(f"{name:46s} {eta:9.2e}     {dep * 100:7.3f} %          {xi * 1e6:6.3f} um")
        rows.append({"name": name, "eta": eta, "sqrt_eta": math.sqrt(eta), "depletion": dep, "xi_um": xi * 1e6})
    eta_he = 2.2e28 * (2.2e-10) ** 3
    print(f"(liquid 4He: n a^3 ~ {eta_he:.2f}, far outside the dilute regime; the formula does not apply)")
    ts = np.logspace(-2, 1.5, 60)
    prof = [g(t) for t in ts]
    print("\nMomentum profile g(t): small t ~ 1/(2 sqrt 2 t), g(0.01) = %.2f; large t ~ 1/(4 t^4), 4 t^4 g(t) = %.3f at t = 10."
          % (g(0.01), g(10) * 4e4))
    print("The 1/k^4 tail n(k) -> (4 pi rho a)^2 / k^4 is the Bogoliubov value of Tan's contact, measured in experiments"
          " from the momentum tail.")
    json.dump({"rows": rows, "profile": {"t": ts.tolist(), "g": prof}}, open(os.path.join(OUT, "bose_gas_depletion.json"), "w"))


if __name__ == "__main__":
    main()
