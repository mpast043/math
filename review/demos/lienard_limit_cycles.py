#!/usr/bin/env python3
"""Quintic Lienard systems x' = y - F(x), y' = -x: at most two limit cycles (family 143).

The repository proves (Lean: QuinticLienard) that deg F <= 5 gives at most two limit
cycles and that two occur.  Its sharpness example (Section 1 of
"Two limit cycles for quintic Lienard systems") is  x'' + mu f(x) x' + x = 0  with
mu = 1/10, f(x) = x^4 - 10 x^2 + 5, i.e.  F(x) = mu (x^5/5 - 10 x^3/3 + 5 x);
first-order averaging predicts amplitudes 2X with X^2 = (5 -/+ sqrt 15)/2.

This script (independent numerics, not a proof)
  1. locates the two limit cycles of that example with a Poincare return map on
     the positive y-axis, and compares their x-amplitudes with the averaging
     prediction;
  2. scans random quintic F and counts sign changes of the displacement function
     (each hyperbolic limit cycle crosses the positive y-axis exactly once), to look
     for a system with three or more cycles.  None should be found if the theorem
     holds; semistable cycles are invisible to sign counting, so this test is a
     sanity check rather than a falsification of the full statement.
Requires numpy and scipy.
"""
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

rng = np.random.default_rng(16)


def make_F(coeffs):
    # coeffs: f1..f5 with F(x) = sum f_j x^j  (F(0) = 0 without loss of generality)
    c = np.asarray(coeffs, float)
    def F(x):
        return sum(c[j] * x ** (j + 1) for j in range(len(c)))
    return F


def return_map(F, y0, rtol=1e-11, atol=1e-12):
    """Start at (0, y0) with y0 > 0, flow until the next crossing of {x = 0, y > 0}."""
    def rhs(t, z):
        x, y = z
        return [y - F(x), -x]

    def hit(t, z):
        return z[0]
    hit.direction = 1   # x goes from negative to positive on the positive y-axis side
    # first leave the axis (x becomes positive), then wait for the upward crossing
    sol = solve_ivp(rhs, (0, 400), [0.0, y0], events=hit, rtol=rtol, atol=atol,
                    max_step=0.05, dense_output=False)
    for t, z in zip(sol.t_events[0], sol.y_events[0]):
        if t > 1e-6 and z[1] > 0:
            return z[1], sol
    return np.nan, sol


def displacement(F, y0):
    y1, _ = return_map(F, y0)
    return y1 - y0


def amplitude(F, y0):
    _, sol = return_map(F, y0)
    return np.max(np.abs(sol.y[0]))


def example():
    mu = 0.1
    F = make_F([5 * mu, 0, -10 * mu / 3, 0, mu / 5])
    ys = np.linspace(0.2, 6.0, 59)
    d = np.array([displacement(F, y) for y in ys])
    roots = []
    for a, b, da, db in zip(ys[:-1], ys[1:], d[:-1], d[1:]):
        if np.isfinite(da) and np.isfinite(db) and da * db < 0:
            roots.append(brentq(lambda y: displacement(F, y), a, b, xtol=1e-10))
    pred = [2 * np.sqrt((5 - np.sqrt(15)) / 2), 2 * np.sqrt((5 + np.sqrt(15)) / 2)]
    print("Example x'' + (1/10)(x^4 - 10x^2 + 5) x' + x = 0")
    print(f"  sign changes of the displacement on y in [0.2, 6]: {len(roots)}")
    for k, y in enumerate(roots):
        note = f" (averaging prediction {pred[k]:.4f})" if k < len(pred) else ""
        print(f"  limit cycle {k + 1}: crosses x=0 at y={y:.6f}, max|x| = {amplitude(F, y):.4f}{note}")
    return len(roots)


def count_cycles(F, ymax=5.0, n=36):
    ys = np.linspace(0.05, ymax, n)
    d = np.array([displacement(F, y) for y in ys])
    ok = np.isfinite(d)
    s = np.sign(d[ok])
    return int(np.sum(s[:-1] * s[1:] < 0))


def random_scan(trials):
    hist = {}
    worst = None
    for _ in range(trials):
        # random weak-damping quintic (non-stiff regime), scanned for y in [0.05, 5]
        c = rng.normal(size=5)
        c[4] = abs(c[4]) + 0.05          # positive leading term: orbits are bounded
        scale = 10 ** rng.uniform(-2.5, -1.0)
        c = c * scale * np.array([1, 1, 1 / 4, 1 / 16, 1 / 64])
        k = count_cycles(make_F(c))
        hist[k] = hist.get(k, 0) + 1
        if worst is None or k > worst[0]:
            worst = (k, c)
    return hist, worst


def main():
    n_example = example()
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    hist, worst = random_scan(trials)
    print(f"\nRandom quintic Lienard systems: {trials} trials; histogram of detected cycles: {dict(sorted(hist.items()))}")
    print(f"  maximum detected: {worst[0]}")
    ok = n_example == 2 and worst[0] <= 2
    print("RESULT:", "consistent with 'at most two, and two occur'" if ok else "DISCREPANCY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
