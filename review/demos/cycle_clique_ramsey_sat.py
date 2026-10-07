#!/usr/bin/env python3
"""Independent SAT check of small cases of R(C_m, K_n) = (m-1)(n-1)+1 (family 189).

For each (m, n) with m >= n >= 3, (m, n) != (3, 3), let N = (m-1)(n-1)+1.

* Lower bound: the 2-colouring of K_{N-1} made of n-1 disjoint red cliques of
  size m-1 (all other edges blue) is checked directly to contain no red C_m and
  no blue K_n.
* Upper bound: a SAT solver shows that no 2-colouring of K_N avoids both a red
  C_m and a blue K_n (UNSAT).

Variables x_e are true when edge e is red. Every m-cycle of K_N gives the clause
"some edge of the cycle is blue"; every n-subset gives "some edge is red".
This re-derives small values that are already known in the literature, and is
independent of the repository's own checker. It is not a proof of the general
formula, which the repository proves (and formalizes in Lean) for all m >= n >= 3.

Requires: python-sat (pysat).
"""
import itertools
import sys
import time

from pysat.solvers import Cadical153


def edge_index(N):
    idx = {}
    for i, j in itertools.combinations(range(N), 2):
        idx[(i, j)] = len(idx) + 1
    return idx


def eid(idx, a, b):
    return idx[(a, b)] if a < b else idx[(b, a)]


def cycles(N, m):
    """Each m-cycle of K_N exactly once: smallest vertex first, and the second
    vertex smaller than the last one (fixes rotation and reflection)."""
    for verts in itertools.combinations(range(N), m):
        first, rest = verts[0], verts[1:]
        for perm in itertools.permutations(rest):
            if perm[0] < perm[-1]:
                yield (first,) + perm


def has_red_cycle(red_adj, N, m):
    # Search for a simple cycle of length exactly m in the red graph.
    def dfs(start, v, depth, used):
        if depth == m:
            return start in red_adj[v]
        for w in red_adj[v]:
            if w > start and not used[w]:
                used[w] = True
                if dfs(start, w, depth + 1, used):
                    return True
                used[w] = False
        return False
    for s in range(N):
        used = [False] * N
        used[s] = True
        if dfs(s, s, 1, used):
            return True
    return False


def lower_bound_ok(m, n):
    N = (m - 1) * (n - 1)
    part = [v // (m - 1) for v in range(N)]
    red_adj = [set(w for w in range(N) if w != v and part[w] == part[v]) for v in range(N)]
    no_red_cycle = not has_red_cycle(red_adj, N, m)
    # A blue clique uses at most one vertex per red block, so its size is at most n-1.
    no_blue_clique = len(set(part)) == n - 1
    return no_red_cycle and no_blue_clique


def upper_bound_unsat(m, n, time_limit=None):
    N = (m - 1) * (n - 1) + 1
    idx = edge_index(N)
    s = Cadical153()
    nclauses = 0
    for cyc in cycles(N, m):
        s.add_clause([-eid(idx, cyc[k], cyc[(k + 1) % m]) for k in range(m)])
        nclauses += 1
    for sub in itertools.combinations(range(N), n):
        s.add_clause([eid(idx, a, b) for a, b in itertools.combinations(sub, 2)])
        nclauses += 1
    # Symmetry breaking: vertex 0's red degree is maximal is not needed; keep it plain.
    t0 = time.time()
    sat = s.solve()
    dt = time.time() - t0
    s.delete()
    return (not sat), N, len(idx), nclauses, dt


def main():
    cases = [(4, 3), (5, 3), (6, 3), (7, 3), (4, 4), (5, 4), (6, 4), (5, 5)]
    if len(sys.argv) > 1:
        cases = [tuple(map(int, a.split(','))) for a in sys.argv[1:]]
    all_ok = True
    print(f"{'(m,n)':8} {'formula':>7} {'lower':>6} {'upper(UNSAT)':>12} {'vars':>5} {'clauses':>8} {'secs':>7}")
    for m, n in cases:
        lo = lower_bound_ok(m, n)
        unsat, N, nv, nc, dt = upper_bound_unsat(m, n)
        ok = lo and unsat
        all_ok &= ok
        print(f"({m},{n})    {N:7d} {str(lo):>6} {str(unsat):>12} {nv:5d} {nc:8d} {dt:7.2f}")
    print("ALL CASES CONSISTENT WITH R(C_m,K_n)=(m-1)(n-1)+1" if all_ok else "MISMATCH FOUND")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
