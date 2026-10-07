#!/usr/bin/env python3
"""Lieb-Thirring constants from family 262, and what they imply.

Repository result (Sharp one-dimensional Lieb-Thirring inequalities for matrix
potentials, Theorem 1.1): for 1/2 < gamma < 3/2 and every matrix size m,

    Tr(-d^2/dx^2 - W)_-^gamma <= C_gamma * int tr W(x)^(gamma+1/2) dx,
    C_gamma = ((gamma-1/2)/(gamma+1/2))^(gamma-1/2) Gamma(gamma+1) / (sqrt(pi) Gamma(gamma+3/2)),

with equality for W = diag((r+1) sech^2(r x), 0, ...), r = 1/(gamma-1/2).

Consequence derived here (standard Laptev-Weidl dimension lifting, which needs the
1D bound for operator-valued potentials; the finite-m bound with an m-independent
constant extends to those by finite-rank approximation):
    L_{gamma,d} <= R_gamma * L^cl_{gamma,d}        for 1 <= gamma < 3/2, every d,
    L_{gamma,d} <= R_gamma R_{gamma+1/2} L^cl_{gamma,d} for 1/2 < gamma < 1, d >= 2,
    R_gamma = C_gamma / L^cl_{gamma,1} = 2 ((2gamma-1)/(2gamma+1))^(gamma-1/2).
At gamma = 1 (the case behind the stability of matter) R_1 = 2/sqrt(3) = 1.1547; the
best published bound before 2026 was 1.456 (Frank-Hundertmark-Jex-Nam, 2021). The
repository credits the gamma = 1 operator-valued case to Read-Schulz (2026).

This script (1) tabulates the constants, (2) converts them into the fermionic kinetic
energy inequality T >= K int rho^(5/3), and (3) tests the 1D matrix inequality
numerically on random non-commuting potentials and on the extremal soliton.
"""
import json
import math
import sys

import numpy as np
from scipy.linalg import eigh
from scipy.special import gamma as G

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
rng = np.random.default_rng(262)


def C(g):
    return ((g - 0.5) / (g + 0.5)) ** (g - 0.5) * G(g + 1) / (math.sqrt(math.pi) * G(g + 1.5))


def Lcl(g, d):
    return G(g + 1) / ((4 * math.pi) ** (d / 2) * G(g + 1 + d / 2))


def R(g):
    return 2 * ((2 * g - 1) / (2 * g + 1)) ** (g - 0.5) if g < 1.5 else 1.0


def lifted_ratio(g, d):
    """Upper bound for L_{g,d}/L^cl_{g,d} from the 1D matrix constants (d >= 2)."""
    if g >= 1.5:
        return 1.0
    if g >= 1.0:
        return R(g)
    return R(g) * R(g + 0.5)


def spectrum_moment(Wfun, m, gam, L=30.0, N=1400):
    """Sum |E_j|^gam over negative eigenvalues of -d^2/dx^2 - W on [-L, L] (Dirichlet)."""
    x = np.linspace(-L, L, N + 2)[1:-1]
    h = x[1] - x[0]
    Wx = np.array([Wfun(t) for t in x])            # (N, m, m)
    H = np.zeros((N * m, N * m))
    lap = 2.0 / h ** 2
    for i in range(N):
        sl = slice(i * m, (i + 1) * m)
        H[sl, sl] = lap * np.eye(m) - Wx[i]
        if i + 1 < N:
            nx = slice((i + 1) * m, (i + 2) * m)
            H[sl, nx] = -np.eye(m) / h ** 2
            H[nx, sl] = -np.eye(m) / h ** 2
    ev = eigh(H, eigvals_only=True, subset_by_value=(-np.inf, 0.0))
    lhs = float(np.sum(np.abs(ev) ** gam))
    # integral of tr W^(gam+1/2) by the trapezoid rule on a finer grid
    xf = np.linspace(-L, L, 8001)
    vals = []
    for t in xf:
        w = np.linalg.eigvalsh(Wfun(t))
        vals.append(np.sum(np.clip(w, 0, None) ** (gam + 0.5)))
    rhs = float(np.trapezoid(vals, xf))
    return lhs, rhs, len(ev)


def random_matrix_potential(m):
    k = rng.integers(1, 4)
    centers = rng.uniform(-6, 6, size=k)
    widths = rng.uniform(0.4, 2.0, size=k)
    amps = 10 ** rng.uniform(-0.7, 1.0, size=k)
    projs = []
    for _ in range(k):
        A = rng.normal(size=(m, m)) + 1j * rng.normal(size=(m, m))
        A = A[:, : rng.integers(1, m + 1)]
        P = A @ A.conj().T
        projs.append(P / np.linalg.eigvalsh(P).max())
    # realify the complex Hermitian potential as a 2m x 2m real symmetric one
    def W(t):
        M = sum(a * np.exp(-((t - c) / w) ** 2) * P for a, c, w, P in zip(amps, centers, widths, projs))
        return np.block([[M.real, -M.imag], [M.imag, M.real]]) / 1.0
    return W


def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    gs = [round(0.5 + 0.02 * i, 2) for i in range(1, 51)]
    table = [{"gamma": g, "R_gamma": R(g), "lifted_d3": lifted_ratio(g, 3)} for g in gs]
    print("gamma   C_gamma     L^cl_1     R_gamma   bound on L_{gamma,3}/L^cl_{gamma,3}")
    for g in (0.75, 1.0, 1.25, 1.5):
        print(f"{g:5.2f}  {C(g):.6f}  {Lcl(g, 1):.6f}  {R(g):.4f}   {lifted_ratio(g, 3):.4f}")
    r1 = R(1.0)
    # Kinetic energy inequality T >= K int rho^(5/3) (one spin state): K = (3/5)(2/(5 L_{1,3}))^(2/3)
    K_tf = 0.6 * (6 * math.pi ** 2) ** (2 / 3)
    K_new = K_tf / r1 ** (2 / 3)
    K_old = K_tf / 1.456 ** (2 / 3)
    print(f"\nLieb-Thirring kinetic constant (3D, one spin state): K_TF = {K_tf:.4f}")
    print(f"  from R_1 = 2/sqrt3 = {r1:.4f}:  K >= {K_new:.4f}  ({K_new / K_tf:.1%} of Thomas-Fermi)")
    print(f"  from 1.456 (2021):        K >= {K_old:.4f}  ({K_old / K_tf:.1%} of Thomas-Fermi)")

    # Numerical test of the 1D matrix inequality
    tests = []
    for gam in (0.75, 1.0, 1.25):
        r = 1 / (gam - 0.5)
        sech = lambda t, r=r: np.diag([(r + 1) / np.cosh(r * t) ** 2, 0.0])
        lhs, rhs, n = spectrum_moment(sech, 2, gam, L=12.0, N=1400)
        tests.append({"gamma": gam, "kind": "extremal sech^2", "ratio": lhs / (C(gam) * rhs), "bound_states": n})
        for trial in range(6):
            m = int(rng.integers(2, 4))
            W = random_matrix_potential(m)
            lhs, rhs, n = spectrum_moment(W, 2 * m, gam, L=14.0, N=700)
            tests.append({"gamma": gam, "kind": f"random {m}x{m} complex", "ratio": lhs / (C(gam) * rhs), "bound_states": n})
    print("\nratio  Tr(H)_-^gamma / (C_gamma int tr W^(gamma+1/2))   (theorem: <= 1, = 1 for the soliton)")
    for t in tests:
        print(f"  gamma={t['gamma']:.2f}  {t['kind']:22s} bound states={t['bound_states']:3d}  ratio={t['ratio']:.4f}")
    worst = max(t["ratio"] for t in tests if t["kind"] != "extremal sech^2")
    print(f"largest ratio over random matrix potentials: {worst:.4f}")
    json.dump({"curve": table, "tests": tests, "K": {"TF": K_tf, "new": K_new, "old": K_old}},
              open(os.path.join(OUT, "lieb_thirring.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
