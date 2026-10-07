#!/usr/bin/env python3
"""Generalized amplitude-damping (GAD) channel: closed-form classical capacity and
independent numerical cross-checks (family 276).

The repository proves (Theorem 1.1 of "Classical capacity and entropy inequalities
for generalized amplitude damping", Lean-formalized as AmplitudeDamping):

    C(A_{g,nu}) = chi(A_{g,nu}) = (1/ln 2) max_{0<=p<=1} [ h((1-g)p + g nu) - G(v(p)) ],
    v(p) = g nu (1-nu) + g (1-g) (p - nu)^2,   G(u) = h((1 + sqrt(1-4u))/2),

i.e. one-shot Holevo information is additive, so entangled inputs across channel
uses never help.  This script

  1. evaluates the formula on a grid (a ready-to-use capacity table);
  2. checks it against King's theorem at nu = 1/2 (unital case), an independent
     classical result: C = 1 - h2((1 + sqrt(1-g))/2);
  3. checks it against direct numerical maximisation of the one-use Holevo
     quantity over ensembles of up to 4 arbitrary pure qubit states;
  4. runs a falsification test of the new additivity claim for two uses: it
     numerically maximises the Holevo information of A (x) A over ensembles of
     entangled two-qubit pure states and the minimum output entropy over entangled
     inputs, and compares with 2*chi(A) and 2*S_min(A).

Numerical optimisation can only fail to find a violation; it cannot prove
additivity.  Requires numpy and scipy.
"""
import sys

import numpy as np
from scipy.optimize import minimize, minimize_scalar

LN2 = np.log(2.0)
rng = np.random.default_rng(20261007)


def h(q):
    q = np.clip(q, 0.0, 1.0)
    out = 0.0
    for x in (q, 1.0 - q):
        if x > 0:
            out -= x * np.log(x)
    return out


def G(u):
    u = min(max(u, 0.0), 0.25)
    return h((1.0 + np.sqrt(1.0 - 4.0 * u)) / 2.0)


def capacity_formula(g, nu):
    """Closed form (bits) from the paper's main theorem."""
    def neg(p):
        v = g * nu * (1 - nu) + g * (1 - g) * (p - nu) ** 2
        return -(h((1 - g) * p + g * nu) - G(v))
    grid = np.linspace(0, 1, 2001)
    p0 = grid[np.argmin([neg(p) for p in grid])]
    res = minimize_scalar(neg, bounds=(max(0, p0 - 1e-3), min(1, p0 + 1e-3)), method="bounded",
                          options={"xatol": 1e-12})
    return -res.fun / LN2, res.x


# ---------- channel as Kraus operators -------------------------------------------------
def kraus(g, nu):
    """Kraus form matching the paper's convention A(rho) with t = (1-g) q + g nu."""
    s = np.sqrt
    K0 = s(1 - nu) * np.array([[1, 0], [0, s(1 - g)]], dtype=complex)
    K1 = s(1 - nu) * np.array([[0, s(g)], [0, 0]], dtype=complex)
    K2 = s(nu) * np.array([[s(1 - g), 0], [0, 1]], dtype=complex)
    K3 = s(nu) * np.array([[0, 0], [s(g), 0]], dtype=complex)
    return [K0, K1, K2, K3]


def apply(Ks, rho):
    return sum(K @ rho @ K.conj().T for K in Ks)


def check_kraus_matches_paper(g, nu):
    """Compare with the paper's explicit matrix formula on random inputs."""
    Ks = kraus(g, nu)
    assert np.allclose(sum(K.conj().T @ K for K in Ks), np.eye(2))
    for _ in range(20):
        q = rng.uniform()
        z = np.sqrt(q * (1 - q)) * rng.uniform() * np.exp(1j * rng.uniform(0, 2 * np.pi))
        rho = np.array([[1 - q, z], [np.conj(z), q]])
        t = (1 - g) * q + g * nu
        want = np.array([[1 - t, np.sqrt(1 - g) * z], [np.sqrt(1 - g) * np.conj(z), t]])
        assert np.allclose(apply(Ks, rho), want)


def S(rho):
    w = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    w = w[w > 1e-15]
    return float(-(w * np.log(w)).sum())


def kron_kraus(Ks):
    return [np.kron(A, B) for A in Ks for B in Ks]


def holevo(Ks, states, weights):
    outs = [apply(Ks, np.outer(s, s.conj())) for s in states]
    avg = sum(w * o for w, o in zip(weights, outs))
    return (S(avg) - sum(w * S(o) for w, o in zip(weights, outs))) / LN2


def unpack(x, k, d):
    raw = x[: 2 * k * d].reshape(k, d, 2)
    states = raw[..., 0] + 1j * raw[..., 1]
    states = states / np.linalg.norm(states, axis=1, keepdims=True)
    logits = x[2 * k * d:]
    w = np.exp(logits - logits.max())
    return states, w / w.sum()


def max_holevo(Ks, d, k, restarts, iters=400):
    best = 0.0
    for _ in range(restarts):
        x0 = rng.normal(size=2 * k * d + k)
        f = lambda x: -holevo(Ks, *unpack(x, k, d))
        res = minimize(f, x0, method="L-BFGS-B", options={"maxiter": iters})
        best = max(best, -res.fun)
    return best


def min_output_entropy(Ks, d, restarts):
    best = np.inf
    for _ in range(restarts):
        x0 = rng.normal(size=2 * d)
        def f(x):
            psi = x[:d] + 1j * x[d:]
            psi = psi / np.linalg.norm(psi)
            return S(apply(Ks, np.outer(psi, psi.conj())))
        res = minimize(f, x0, method="L-BFGS-B")
        best = min(best, res.fun)
    return best


def main():
    print("1) Capacity table C(gamma, nu) in bits per channel use (closed form)")
    gammas = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
    nus = [0.0, 0.05, 0.1, 0.25, 0.5]
    print("gamma\\nu " + " ".join(f"{nu:>8.2f}" for nu in nus))
    for g in gammas:
        print(f"{g:8.2f} " + " ".join(f"{capacity_formula(g, nu)[0]:8.5f}" for nu in nus))

    print("\n2) Unital case nu=1/2 vs King's theorem  C = 1 - h2((1+sqrt(1-g))/2)")
    worst = 0.0
    for g in np.linspace(0.02, 0.98, 25):
        c_formula = capacity_formula(g, 0.5)[0]
        c_king = 1 - h((1 + np.sqrt(1 - g)) / 2) / LN2
        worst = max(worst, abs(c_formula - c_king))
    print(f"   max |formula - King| over 25 values of gamma: {worst:.2e}")
    ok_king = worst < 1e-8

    print("\n3) One-use Holevo optimum by direct numerical search (ensembles of 2-4 pure states)")
    ok_one = True
    for g, nu in [(0.3, 0.1), (0.6, 0.2), (0.8, 0.05), (0.5, 0.35)]:
        check_kraus_matches_paper(g, nu)
        Ks = kraus(g, nu)
        c_formula = capacity_formula(g, nu)[0]
        c_num = max(max_holevo(Ks, 2, k, restarts=6) for k in (2, 3, 4))
        ok_one &= (c_num <= c_formula + 1e-7) and (c_num >= c_formula - 1e-5)
        print(f"   g={g:.2f} nu={nu:.2f}: formula {c_formula:.8f}  numerical {c_num:.8f}  diff {c_num - c_formula:+.1e}")

    print("\n4) Two-use additivity falsification test (entangled 2-qubit ensembles)")
    ok_two = True
    for g, nu in [(0.3, 0.1), (0.6, 0.2), (0.8, 0.05)]:
        Ks = kraus(g, nu)
        K2 = kron_kraus(Ks)
        c1 = capacity_formula(g, nu)[0]
        chi2 = max(max_holevo(K2, 4, k, restarts=4, iters=300) for k in (4, 6))
        smin1 = min_output_entropy(Ks, 2, restarts=8)
        smin2 = min_output_entropy(K2, 4, restarts=12)
        ok_two &= (chi2 <= 2 * c1 + 1e-6) and (smin2 >= 2 * smin1 - 1e-7)
        print(f"   g={g:.2f} nu={nu:.2f}: best chi(A(x)A) found {chi2:.8f} vs 2C {2 * c1:.8f}; "
              f"S_min(A(x)A) {smin2:.8f} vs 2 S_min(A) {2 * smin1:.8f}")

    ok = ok_king and ok_one and ok_two
    print("\nRESULT:", "all checks consistent with the theorem" if ok else "DISCREPANCY FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
