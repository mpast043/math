#!/usr/bin/env python3
"""Smoothness laws for p-1 and for consecutive integers, applied to cryptography (families 011, 012).

Repository results:
  * Ford-Konyagin-Luca conjecture: the prime factors of p-1, for p a uniformly random
    prime up to x, follow the Poisson-Dirichlet(1) law, exactly like a random integer.
    In particular P(p-1 is p^(1/u)-smooth) -> rho(u) (Dickman's function).
  * Erdos-Pomerance joint Dickman law: the largest prime factors of n and n+1 are
    asymptotically independent, so P(n and n+1 both n^(1/u)-smooth) -> rho(u)^2.

Uses: Pollard's p-1 method finds a prime factor p of a modulus when p-1 is smooth;
Pohlig-Hellman breaks discrete logs modulo p when p-1 is smooth. Isogeny-based
signatures (SQIsign family) need primes p with p^2 - 1 having a large smooth part,
found by searching for twin smooth integers (n, n+1 both smooth).
This script computes rho, measures both laws on all integers and primes up to N,
and turns the laws into attack-success and search-yield estimates.
"""
import json
import math
import os
import sys
import time

import numpy as np
from decimal import Decimal, getcontext

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
N = int(float(sys.argv[2])) if len(sys.argv) > 2 else 100_000_000


def dickman_coefficients(kmax=24, terms=220, prec=60):
    """Power series of rho on each [k-1, k]: rho(u) = sum_i a_i (k - u)^i.

    From u rho'(u) = -rho(u-1): a_{i+1} = (b_i + i a_i) / (k (i+1)), b = series on [k-2, k-1],
    and a_0 = rho(k-1) - sum_{i>=1} a_i by continuity. Computed in 60-digit decimal arithmetic:
    absolute rounding errors are not damped as rho decays, so double precision is not enough
    beyond u ~ 9. Agrees with 40- and 90-digit runs to 10 significant figures up to u = 20.
    """
    getcontext().prec = prec
    coeffs = {1: [Decimal(1)] + [Decimal(0)] * (terms - 1)}
    for k in range(2, kmax + 1):
        b = coeffs[k - 1]
        a = [Decimal(0)] * terms
        for i in range(terms - 1):
            a[i + 1] = (b[i] + i * a[i]) / (k * (i + 1))
        a[0] = b[0] - sum(a[1:])
        coeffs[k] = a
    return coeffs


DICKMAN = dickman_coefficients()


def rho(u):
    if u <= 1:
        return 1.0
    k = math.ceil(u)
    w = Decimal(k) - Decimal(repr(float(u)))
    s = Decimal(0)
    for c in reversed(DICKMAN[k]):
        s = s * w + c
    return float(s)


# Excess log-mass of small primes in p-1 relative to a random integer:
# E[v_q(p-1)] - E[v_q(n)] = q/(q-1)^2 - 1/(q-1) = 1/(q-1)^2, so p-1 looks like a random integer
# about e^KAPPA times smaller. This gives the first-order finite-size correction to the limit law.
def small_prime_excess(limit=10**6):
    sieve = np.ones(limit + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    q = np.nonzero(sieve)[0].astype(np.float64)
    return float(np.sum(np.log(q) / (q - 1) ** 2))


KAPPA = small_prime_excess()


def largest_prime_factor_sieve(n):
    lpf = np.ones(n + 1, dtype=np.uint32)
    is_comp = np.zeros(n + 1, dtype=bool)
    t0 = time.time()
    for p in range(2, n + 1):
        if not is_comp[p]:
            lpf[p::p] = p           # later (larger) primes overwrite earlier ones
            if p * p <= n:
                is_comp[p * p::p] = True
    print(f"sieved largest prime factors up to {n:.0e} in {time.time() - t0:.0f} s", flush=True)
    return lpf, ~is_comp


def mean_log(lo, hi):
    """Average of log n over n uniform in [lo, hi]."""
    return (hi * math.log(hi) - lo * math.log(lo)) / (hi - lo) - 1


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Dickman rho:", ", ".join(f"rho({u})={rho(u):.6g}" for u in (2, 3, 4, 5, 8, 10, 12, 16, 20)))
    print(f"small-prime excess of p-1: kappa = sum_q log q/(q-1)^2 = {KAPPA:.6f}")
    lpf, isprime = largest_prime_factor_sieve(N)
    us = [1.5, 2.0, 2.5, 3.0, 4.0]
    rows = []
    decades = [(N // 1000, N // 100), (N // 100, N // 10), (N // 10, N)]
    print("\nFixed u, three size ranges. Limit theorems: P(p-1 smooth)/P(n smooth) -> 1 and P(both)/(P(n) P(n+1)) -> 1.")
    print("'model' is the first-order finite-size prediction rho(u - kappa u / log x) / rho(u).")
    print("  range          u    rho(u)    P(n smooth)  P(p-1 smooth)  ratio p-1/n  model   independence ratio")
    for lo, hi in decades:
        idx = np.arange(lo, hi - 1)
        logn = np.log(idx.astype(np.float64))
        u_n = logn / np.log(np.maximum(lpf[idx], 2).astype(np.float64))
        u_n1 = logn / np.log(np.maximum(lpf[idx + 1], 2).astype(np.float64))
        primes = idx[isprime[idx]]
        u_p = np.log(primes.astype(np.float64)) / np.log(np.maximum(lpf[primes - 1], 2).astype(np.float64))
        L = mean_log(lo, hi)
        for u in us:
            pn = float(np.mean(u_n >= u)); pn1 = float(np.mean(u_n1 >= u)); pp = float(np.mean(u_p >= u))
            both = float(np.mean((u_n >= u) & (u_n1 >= u)))
            ind = both / (pn * pn1)
            model = rho(u - KAPPA * u / L) / rho(u)
            print(f"  [{lo:.0e},{hi:.0e}] {u:4.1f}  {rho(u):.5f}   {pn:.5f}      {pp:.5f}        {pp / pn:6.3f}     {model:6.3f}      {ind:6.3f}")
            rows.append({"lo": lo, "hi": hi, "log_x": L, "u": u, "rho": rho(u), "p_n": pn, "p_pm1": pp,
                         "ratio": pp / pn, "model_ratio": model, "p_both": both, "indep_ratio": ind})
    apps = {"pollard": [], "twin": []}
    print("\nPollard p-1 stage 1 with bound B on a prime factor p of an RSA modulus.")
    print("Limit law: P(success) -> rho(u), u = log p / log B; with the small-prime correction rho(u - kappa/log B):")
    for bits_p, bits_B in ((256, 32), (512, 40), (512, 64), (1024, 64), (1024, 80)):
        u = bits_p / bits_B
        corr = rho(u - KAPPA / (bits_B * math.log(2)))
        print(f"  p ~ 2^{bits_p}, B = 2^{bits_B}:  u = {u:5.2f},  rho(u) = {rho(u):.3e},  corrected = {corr:.3e},"
              f"  expected primes tried per success ~ 2^{-math.log2(corr):.1f}")
        apps["pollard"].append({"bits_p": bits_p, "bits_B": bits_B, "u": u, "rho": rho(u), "corrected": corr})
    print("\nTwin smooth pairs (n, n+1 both B-smooth) near X. Joint Dickman law: density -> rho(u)^2, u = log X / log B.")
    print("(Leading order only; for B far below exp((log log X)^{5/3}) the true density is larger than rho(u)^2.)")
    for bits_X, bits_B in ((64, 16), (128, 16), (256, 32), (256, 20)):
        u = bits_X / bits_B
        dens = rho(u) ** 2
        print(f"  X = 2^{bits_X}, B = 2^{bits_B}:  u = {u:5.2f},  density = 2^{math.log2(dens):.1f},"
              f"  pairs in [X, 2X] ~ 2^{bits_X + math.log2(dens):.1f},  random trials per pair ~ 2^{-math.log2(dens):.1f}")
        apps["twin"].append({"bits_X": bits_X, "bits_B": bits_B, "u": u, "log2_density": math.log2(dens)})
    grid = [round(x, 2) for x in np.linspace(1, 12, 111)]
    json.dump({"kappa": KAPPA, "rows": rows, "applications": apps,
               "rho_curve": {"u": grid, "rho": [rho(x) for x in grid]}},
              open(os.path.join(OUT, "smooth_numbers_crypto.json"), "w"))


if __name__ == "__main__":
    main()
