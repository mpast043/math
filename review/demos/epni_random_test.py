#!/usr/bin/env python3
"""Falsification test of the entropy photon-number inequality (EPnI), family 273.

Claim (proved in the repository and Lean-formalized as EntropyPhotonNumber):
for independent bosonic inputs rho_A, rho_B on n modes each, mixed on a beam
splitter of transmissivity eta,

    N(rho_C) >= eta N(rho_A) + (1 - eta) N(rho_B),   N(rho) = g^{-1}(S(rho)/n),

where g(x) = (x+1) ln(x+1) - x ln x is the thermal entropy per mode.  The EPnI
had been open since Guha-Shapiro-Erkmen (2008); Gaussian inputs were known.

Here we test it on random non-Gaussian inputs.  A beam splitter conserves total
photon number, so inputs supported on at most K photons give an output that is
supported on at most 2K photons: the computation below is exact up to floating
point (no Fock-space truncation error).  Tested: single-mode inputs (random mixed
states, Fock mixtures, cat-like superpositions) and two-mode inputs that are
entangled between their two modes.  A numerical search can only fail to find a
counterexample; it cannot prove the inequality.  Requires numpy and scipy.
"""
import sys

import numpy as np
from scipy.linalg import expm
from scipy.optimize import brentq

rng = np.random.default_rng(7)


def g(x):
    return (x + 1) * np.log1p(x) - (x * np.log(x) if x > 0 else 0.0)


def g_inv(s):
    if s <= 1e-14:
        return 0.0
    hi = 1.0
    while g(hi) < s:
        hi *= 2
    return brentq(lambda x: g(x) - s, 0.0, hi, xtol=1e-15, rtol=1e-15)


def entropy(rho):
    w = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    w = w[w > 1e-15]
    return float(-(w * np.log(w)).sum())


def photon_number(rho, nmodes):
    return g_inv(entropy(rho) / nmodes)


def ladder(d):
    return np.diag(np.sqrt(np.arange(1, d)), 1)


def beam_splitter(dA, dB, eta):
    """Two-mode beam splitter on Fock spaces of dimensions dA, dB (truncation is
    exact for states whose total photon number is below min(dA, dB))."""
    a = np.kron(ladder(dA), np.eye(dB))
    b = np.kron(np.eye(dA), ladder(dB))
    theta = np.arccos(np.sqrt(eta))
    return expm(theta * (a.conj().T @ b - b.conj().T @ a))


def random_state(d, kind):
    if kind == "mixed":
        X = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
        X = X[:, : rng.integers(1, d + 1)]
        rho = X @ X.conj().T
    elif kind == "fock-mixture":
        p = rng.dirichlet(np.ones(d) * rng.uniform(0.2, 2))
        rho = np.diag(p).astype(complex)
    elif kind == "cat-mix":
        v1 = rng.normal(size=d) + 1j * rng.normal(size=d)
        v2 = rng.normal(size=d) + 1j * rng.normal(size=d)
        p = rng.uniform()
        rho = p * np.outer(v1, v1.conj()) / np.vdot(v1, v1) + (1 - p) * np.outer(v2, v2.conj()) / np.vdot(v2, v2)
    return rho / np.trace(rho)


def single_mode_trial(K, eta, kinds):
    d = K + 1                # inputs live on 0..K photons
    D = 2 * K + 1            # outputs need 0..2K photons
    rA = np.zeros((D, D), complex); rA[:d, :d] = random_state(d, kinds[0])
    rB = np.zeros((D, D), complex); rB[:d, :d] = random_state(d, kinds[1])
    U = beam_splitter(D, D, eta)
    out = U @ np.kron(rA, rB) @ U.conj().T
    rC = np.trace(out.reshape(D, D, D, D), axis1=1, axis2=3)   # keep mode C (first output)
    lhs = photon_number(rC, 1)
    rhs = eta * photon_number(rA, 1) + (1 - eta) * photon_number(rB, 1)
    return lhs - rhs


def two_mode_trial(K, eta):
    """Each input: two modes with an entangled random state of total photon number <= K."""
    d = K + 1
    D = 2 * K + 1
    basis = [(i, j) for i in range(d) for j in range(d) if i + j <= K]

    def embed():
        # Random density matrix on two modes of dimension D each, supported on
        # `basis` (generically entangled between the two modes).
        m = len(basis)
        X = rng.normal(size=(m, m)) + 1j * rng.normal(size=(m, m))
        X = X[:, : rng.integers(1, m + 1)]
        small = X @ X.conj().T
        small /= np.trace(small)
        rho = np.zeros((D * D, D * D), complex)
        idx = [i * D + j for i, j in basis]
        rho[np.ix_(idx, idx)] = small
        return rho

    rA = embed()
    rB = embed()
    # Mode order A1 A2 B1 B2; beam splitters mix A1 with B1 and A2 with B2.
    U1 = beam_splitter(D, D, eta)
    # Build the full unitary on A1 A2 B1 B2 by reordering to (A1 B1)(A2 B2).
    full = np.kron(rA, rB).reshape([D] * 8)
    # axes: A1 A2 B1 B2 | A1' A2' B1' B2'
    full = full.transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape(D ** 4, D ** 4)   # -> A1 B1 A2 B2
    U = np.kron(U1, U1)
    out = (U @ full @ U.conj().T).reshape([D] * 8)
    # output modes C1 D1 C2 D2 ; keep C1, C2
    out = out.transpose(0, 2, 1, 3, 4, 6, 5, 7)   # -> C1 C2 D1 D2 | ...
    out = out.reshape(D * D, D * D, D * D, D * D)
    rC = np.trace(out, axis1=1, axis2=3)
    lhs = photon_number(rC, 2)
    rhs = eta * photon_number(rA, 2) + (1 - eta) * photon_number(rB, 2)
    return lhs - rhs


def main():
    worst = np.inf
    count = 0
    kinds = ["mixed", "fock-mixture", "cat-mix"]
    for K in (1, 2, 3, 4):
        for _ in range(150):
            eta = rng.uniform(0.02, 0.98)
            ks = (kinds[rng.integers(3)], kinds[rng.integers(3)])
            margin = single_mode_trial(K, eta, ks)
            worst = min(worst, margin); count += 1
    print(f"single-mode: {count} random non-Gaussian trials, minimum margin N(C) - [eta N(A) + (1-eta) N(B)] = {worst:.3e}")
    worst2 = np.inf
    count2 = 0
    for K in (1, 2):
        for _ in range(40 if K == 1 else 12):
            eta = rng.uniform(0.05, 0.95)
            margin = two_mode_trial(K, eta)
            worst2 = min(worst2, margin); count2 += 1
    print(f"two-mode (entangled within each input): {count2} trials, minimum margin = {worst2:.3e}")
    ok = worst > -1e-9 and worst2 > -1e-9
    print("RESULT:", "no violation found" if ok else "VIOLATION FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
