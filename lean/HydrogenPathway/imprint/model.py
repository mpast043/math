"""Finite two-mode illustration; standard library only, not a hydrogen channel.

Inner products conjugate the first argument. k = <e0|e1>, so the atom's
upper-right coherence is +/- conjugate(k)/2. Matrix trace norms below are
floating-point checks; they are not formal trace-class proofs.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

Matrix = list[list[complex]]
Vector = list[complex]
TOL = 2e-9


def require_probability(p: float) -> None:
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("probability must be finite and lie in [0,1]")


def zeros(rows: int, cols: int | None = None) -> Matrix:
    return [[0j for _ in range(rows if cols is None else cols)] for _ in range(rows)]


def identity(n: int) -> Matrix:
    return [[complex(i == j) for j in range(n)] for i in range(n)]


def adjoint(a: Matrix) -> Matrix:
    return [[a[j][i].conjugate() for j in range(len(a))] for i in range(len(a[0]))]


def add(a: Matrix, b: Matrix) -> Matrix:
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(c: complex, a: Matrix) -> Matrix:
    return [[c * x for x in row] for row in a]


def sub(a: Matrix, b: Matrix) -> Matrix:
    return add(a, scale(-1, b))


def mul(a: Matrix, b: Matrix) -> Matrix:
    assert len(a[0]) == len(b)
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def apply(a: Matrix, v: Vector) -> Vector:
    return [sum(x * y for x, y in zip(row, v)) for row in a]


def outer(v: Vector) -> Matrix:
    return [[x * y.conjugate() for y in v] for x in v]


def tensor(a: Vector, b: Vector) -> Vector:
    return [x * y for x in a for y in b]


def block_diag(a: Matrix, b: Matrix) -> Matrix:
    n, m = len(a), len(b)
    result = zeros(n + m)
    for i in range(n):
        for j in range(n):
            result[i][j] = a[i][j]
    for i in range(m):
        for j in range(m):
            result[n + i][n + j] = b[i][j]
    return result


def trace(a: Matrix) -> complex:
    return sum(a[i][i] for i in range(len(a)))


def matrix_error(a: Matrix, b: Matrix) -> float:
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def hermitian_spectrum_doubled(a: Matrix) -> list[float]:
    """Jacobi eigenvalues of the real embedding [Re A,-Im A;Im A,Re A].

    Each Hermitian eigenvalue occurs twice. Convergence is checked explicitly;
    this routine does not compute a trace norm for non-Hermitian inputs.
    """
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a nonempty square matrix")
    if any(not math.isfinite(z.real) or not math.isfinite(z.imag) for row in a for z in row):
        raise ValueError("matrix entries must be finite")
    if matrix_error(a, adjoint(a)) > 1e-10:
        raise ValueError("expected a Hermitian matrix")
    b = [[0.0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            z = a[i][j]
            b[i][j] = b[n + i][n + j] = z.real
            b[i][n + j] = -z.imag
            b[n + i][j] = z.imag
    size = len(b)
    for _ in range(80 * size * size):
        p, q = max(((i, j) for i in range(size) for j in range(i + 1, size)),
                   key=lambda ij: abs(b[ij[0]][ij[1]]))
        if abs(b[p][q]) < 1e-13:
            return [b[i][i] for i in range(size)]
        z = (b[q][q] - b[p][p]) / (2 * b[p][q])
        t = math.copysign(1 / (abs(z) + math.sqrt(1 + z * z)), z)
        c, s = 1 / math.sqrt(1 + t * t), t / math.sqrt(1 + t * t)
        app, aqq, apq = b[p][p], b[q][q], b[p][q]
        for r in range(size):
            if r != p and r != q:
                arp, arq = b[r][p], b[r][q]
                b[r][p] = b[p][r] = c * arp - s * arq
                b[r][q] = b[q][r] = s * arp + c * arq
        b[p][p], b[q][q] = app - t * apq, aqq + t * apq
        b[p][q] = b[q][p] = 0.0
    raise ArithmeticError("Jacobi eigensolver did not converge")


def trace_norm(a: Matrix) -> float:
    return sum(abs(x) for x in hermitian_spectrum_doubled(a)) / 2


def distance(a: Matrix, b: Matrix) -> float:
    return trace_norm(sub(a, b)) / 2


def guess(a: Matrix, b: Matrix, q0: float = 0.5) -> float:
    """Holevo-Helstrom optimum for normalized states and prior q0."""
    require_probability(q0)
    return (1 + trace_norm(sub(scale(q0, a), scale(1 - q0, b)))) / 2


def check_density(a: Matrix) -> None:
    assert abs(trace(a) - 1) < TOL
    assert min(hermitian_spectrum_doubled(a)) >= -TOL


def partial_trace(a: Matrix, dims: tuple[int, ...], keep: tuple[int, ...]) -> Matrix:
    assert math.prod(dims) == len(a)
    assert len(set(keep)) == len(keep) and all(0 <= k < len(dims) for k in keep)
    states = list(itertools.product(*(range(d) for d in dims)))
    traced = [k for k in range(len(dims)) if k not in keep]
    def index(s: tuple[int, ...]) -> int:
        result = 0
        for k in keep:
            result = result * dims[k] + s[k]
        return result
    result = zeros(math.prod(dims[k] for k in keep))
    for i, si in enumerate(states):
        for j, sj in enumerate(states):
            if all(si[k] == sj[k] for k in traced):
                result[index(si)][index(sj)] += a[i][j]
    return result


def environment(k: complex) -> tuple[Vector, Vector]:
    if not math.isfinite(k.real) or not math.isfinite(k.imag) or abs(k) > 1:
        raise ValueError("environment overlap must have finite modulus <= 1")
    return [1 + 0j, 0j], [k, complex(math.sqrt(max(0.0, 1 - abs(k) ** 2)))]


def isometry(k: complex) -> Matrix:
    e0, e1 = environment(k)
    return [[e0[0], 0j], [e0[1], 0j], [0j, e1[0]], [0j, e1[1]]]


def source(sign: int) -> Vector:
    assert sign in (-1, 1)
    return [complex(1 / math.sqrt(2)), complex(sign / math.sqrt(2))]


def flagged(rho: Matrix, p: float, tau: Matrix | None = None) -> Matrix:
    require_probability(p)
    return block_diag(scale(p, rho), scale(1 - p, [[1 + 0j]] if tau is None else tau))


def capture_kraus(v: Matrix, p0: float, p1: float) -> list[Matrix]:
    """One common CPTP instrument, diagonal filtering in the +/- source basis.

    For equal yields the success operator is sqrt(p)V. The failure Kraus
    labels are inaccessible and remember which source-basis component failed.
    """
    require_probability(p0)
    require_probability(p1)
    filt = add(scale(math.sqrt(p0), outer(source(1))),
               scale(math.sqrt(p1), outer(source(-1))))
    success = mul(v, filt) + [[0j, 0j]]
    failures = []
    for p, sign in ((p0, 1), (p1, -1)):
        f = zeros(len(v) + 1, 2)
        f[-1] = [math.sqrt(1 - p) * z.conjugate() for z in source(sign)]
        failures.append(f)
    return [success, *failures]


def channel(ks: list[Matrix], rho: Matrix) -> Matrix:
    result = zeros(len(ks[0]))
    for k in ks:
        result = add(result, mul(mul(k, rho), adjoint(k)))
    return result


def stinespring(ks: list[Matrix]) -> Matrix:
    return [[ks[e][o][i] for i in range(len(ks[0][0]))]
            for o in range(len(ks[0])) for e in range(len(ks))]


def choi(ks: list[Matrix]) -> Matrix:
    result = zeros(len(ks[0]) * len(ks[0][0]))
    for k in ks:
        result = add(result, outer([z for row in k for z in row]))
    return result


def flagged_identity(rho0: Matrix, rho1: Matrix, tau: Matrix,
                     p0: float, p1: float) -> tuple[float, float]:
    """Assumes normalized positive rho0/rho1/tau and orthogonal direct-sum flags."""
    observed = distance(flagged(rho0, p0, tau), flagged(rho1, p1, tau))
    formula = (trace_norm(sub(scale(p0, rho0), scale(p1, rho1))) + abs(p0 - p1)) / 2
    return observed, formula


def analyze(k: complex, p0: float, p1: float, check: bool = False) -> dict:
    require_probability(p0)
    require_probability(p1)
    v = isometry(k)
    inputs = [outer(source(s)) for s in (1, -1)]
    outputs = [outer(apply(v, source(s))) for s in (1, -1)]
    atoms = [partial_trace(rho, (2, 2), (0,)) for rho in outputs]
    photons = [partial_trace(rho, (2, 2), (1,)) for rho in outputs]
    marginals = {"atom": atoms, "photon": photons, "joint": outputs}
    ideal = {name: distance(*rhos) for name, rhos in marginals.items()}
    flagged_states = {name: [flagged(rhos[0], p0), flagged(rhos[1], p1)]
                      for name, rhos in marginals.items()}
    flag_d = {name: distance(*rhos) for name, rhos in flagged_states.items()}
    conditional = None
    if p0 + p1 > 0:
        q0 = p0 / (p0 + p1)
        conditional = {"priors": [q0, 1 - q0],
                       "guess": {name: guess(*rhos, q0) for name, rhos in marginals.items()}}
    ks = capture_kraus(v, p0, p1)
    w = stinespring(ks)
    dilated = [outer(apply(w, source(s))) for s in (1, -1)]
    global_d = distance(*dilated)
    r, dp, total = abs(k), abs(p0 - p1), p0 + p1
    predictions = {"atom": (max(dp, total * r) + dp) / 2,
                   "photon": dp, "joint": max(p0, p1)}
    failure_memory_d = None
    if p0 < 1 and p1 < 1:
        memories = []
        for rho, p in zip(dilated, (p0, p1)):
            # Project accessible output to the single failure flag, then normalize.
            memories.append([[rho[4 * 3 + a][4 * 3 + b] / (1 - p)
                              for b in range(3)] for a in range(3)])
        failure_memory_d = distance(*memories)
    e0, e1 = environment(k)
    which_mode = distance(outer(e0), outer(e1))
    if check:
        assert matrix_error(mul(adjoint(v), v), identity(2)) < TOL
        assert matrix_error(mul(adjoint(w), w), identity(2)) < TOL
        completeness = zeros(2)
        for op in ks:
            completeness = add(completeness, mul(adjoint(op), op))
        assert matrix_error(completeness, identity(2)) < TOL
        assert min(hermitian_spectrum_doubled(choi(ks))) >= -TOL
        assert abs(ideal["atom"] - r) < TOL
        assert abs(ideal["photon"]) < TOL and abs(ideal["joint"] - 1) < TOL
        assert abs(which_mode - math.sqrt(max(0, 1 - r * r))) < TOL
        for name in marginals:
            assert abs(flag_d[name] - predictions[name]) < TOL
            for rho in marginals[name] + flagged_states[name]:
                check_density(rho)
            observed, formula = flagged_identity(*marginals[name], [[1 + 0j]], p0, p1)
            assert abs(observed - formula) < TOL
        for i, rho in enumerate(inputs):
            assert matrix_error(channel(ks, rho), flagged_states["joint"][i]) < TOL
            assert matrix_error(partial_trace(dilated[i], (5, 3), (0,)),
                                flagged_states["joint"][i]) < TOL
        # Equal mode populations; these alone do not prove equal continuous momentum density.
        assert all(abs(inputs[0][i][i] - inputs[1][i][i]) < TOL for i in range(2))
        assert abs(global_d - 1) < TOL
        if failure_memory_d is not None:
            assert abs(failure_memory_d - 1) < TOL
        if r > 0:
            measurement = outer([complex(1 / math.sqrt(2)), k / r / math.sqrt(2)])
            achieved = (trace(mul(measurement, atoms[0])) +
                        trace(mul(sub(identity(2), measurement), atoms[1]))).real / 2
            assert abs(achieved - (1 + r) / 2) < TOL
    return {"k": {"real": k.real, "imag": k.imag, "modulus": r},
            "acceptance": [p0, p1], "ideal_phase_D": ideal,
            "ideal_phase_guess_equal_priors": {name: (1 + d) / 2 for name, d in ideal.items()},
            "which_mode_photon_D": which_mode, "flagged_phase_D": flag_d,
            "flagged_guess_equal_input_priors": {name: (1 + d) / 2 for name, d in flag_d.items()},
            "success_rate_equal_input_priors": total / 2,
            "conditional_success": conditional,
            "global_isometry_D": global_d, "conditional_failure_memory_D": failure_memory_d}


def collected_case(kc: complex, ku: complex, p: float, check: bool = False) -> dict:
    require_probability(p)
    c0, c1 = environment(kc)
    u0, u1 = environment(ku)
    branches = (tensor([1 + 0j, 0j], tensor(c0, u0)),
                tensor([0j, 1 + 0j], tensor(c1, u1)))
    states = [outer([(a + sign * b) / math.sqrt(2) for a, b in zip(*branches)])
              for sign in (1, -1)]
    atom = [partial_trace(rho, (2, 2, 2), (0,)) for rho in states]
    collected = [partial_trace(rho, (2, 2, 2), (1,)) for rho in states]
    ac = [partial_trace(rho, (2, 2, 2), (0, 1)) for rho in states]
    ds = {"atom": distance(*atom), "collected": distance(*collected),
          "atom_collected": distance(*ac), "full": distance(*states),
          "flagged_atom_collected": distance(flagged(ac[0], p), flagged(ac[1], p))}
    expected = {"atom": abs(kc * ku), "collected": 0.0,
                "atom_collected": abs(ku), "full": 1.0,
                "flagged_atom_collected": p * abs(ku)}
    if check:
        assert 0 <= p <= 1
        assert all(abs(ds[key] - expected[key]) < TOL for key in ds)
    return {"kC": [kc.real, kc.imag], "kU": [ku.real, ku.imag], "p": p, "D": ds}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-real", type=float)
    parser.add_argument("--k-imag", type=float, default=0.0)
    parser.add_argument("--p0", type=float, default=0.25)
    parser.add_argument("--p1", type=float)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [(0j, .4, .4), (.6 + 0j, .25, .25), (1 + 0j, 1., 1.),
             (-.6 + 0j, .25, .25), (.6j, .25, .25), (.6 + .8j, .25, .25),
             (.6 + 0j, 0., 0.), (.6 + 0j, .8, .2), (0j, 1., 0.), (1 + 0j, .8, .2)]
    if args.k_real is not None:
        cases = [(complex(args.k_real, args.k_imag), args.p0,
                  args.p0 if args.p1 is None else args.p1)]
    report = {"model": "Ideal two-mode phase-label illustration; not a hydrogen channel",
              "checks_enabled": args.check,
              "normalization": "D = half trace norm; equal input priors unless stated",
              "numerics": "Python standard library, double precision, Jacobi real embedding",
              "tolerance": TOL, "cases": [analyze(*case, check=args.check) for case in cases],
              "collected_example": collected_case(.8 + 0j, .6j, .25, args.check)}
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(encoded)
        verb = "Checked" if args.check else "Calculated"
        print(f"{verb} {len(cases)} phase/capture cases and one collected/unobserved case.")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
