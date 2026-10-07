/*
 * Independent illustration of Seymour's second-neighbourhood conjecture (family 173).
 *
 * Exhaustively enumerates every oriented graph on n labelled vertices
 * (each unordered pair is absent, i->j, or j->i: 3^(n choose 2) graphs) and
 * checks that some vertex v has |N++(v)| >= |N+(v)|, where N++(v) is the set
 * of vertices at directed distance exactly two.  Then tests random oriented
 * graphs on larger vertex sets.  This is a finite sanity check, not a proof;
 * the repository's Lean proof covers all finite oriented graphs.
 *
 * Build: cc -O2 -fopenmp seymour_exhaustive.c -o seymour_exhaustive
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

static int has_good_vertex(int n, const uint64_t *out) {
    for (int v = 0; v < n; v++) {
        uint64_t first = out[v], second = 0, m = first;
        while (m) {
            int u = __builtin_ctzll(m);
            m &= m - 1;
            second |= out[u];
        }
        second &= ~(first | (1ULL << v));
        if (__builtin_popcountll(first) <= __builtin_popcountll(second)) return 1;
    }
    return 0;
}

static long long exhaustive(int n) {
    int pairs = n * (n - 1) / 2;
    int pi[64], pj[64], k = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) { pi[k] = i; pj[k] = j; k++; }
    long long total = 1;
    for (int t = 0; t < pairs; t++) total *= 3;
    long long bad = 0;
    #pragma omp parallel for reduction(+:bad) schedule(dynamic, 4096)
    for (long long code = 0; code < total; code++) {
        uint64_t out[64] = {0};
        long long c = code;
        for (int t = 0; t < pairs; t++) {
            int s = (int)(c % 3); c /= 3;
            if (s == 1) out[pi[t]] |= 1ULL << pj[t];
            else if (s == 2) out[pj[t]] |= 1ULL << pi[t];
        }
        if (!has_good_vertex(n, out)) bad++;
    }
    printf("n=%d: %lld oriented graphs checked, counterexamples=%lld\n", n, total, bad);
    return bad;
}

static uint64_t rng_state = 0x9E3779B97F4A7C15ULL;
static uint64_t rng(void) {  /* xorshift64* */
    rng_state ^= rng_state >> 12; rng_state ^= rng_state << 25; rng_state ^= rng_state >> 27;
    return rng_state * 2685821657736338717ULL;
}

static long long random_tests(int n, long long samples, double density) {
    long long bad = 0;
    uint64_t out[64];
    for (long long s = 0; s < samples; s++) {
        for (int i = 0; i < n; i++) out[i] = 0;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++) {
                double r = (rng() >> 11) * (1.0 / 9007199254740992.0);
                if (r < density / 2) out[i] |= 1ULL << j;
                else if (r < density) out[j] |= 1ULL << i;
            }
        if (!has_good_vertex(n, out)) bad++;
    }
    printf("n=%d density=%.2f: %lld random oriented graphs, counterexamples=%lld\n", n, density, samples, bad);
    return bad;
}

int main(int argc, char **argv) {
    int nmax = argc > 1 ? atoi(argv[1]) : 6;
    long long bad = 0;
    clock_t t0 = clock();
    for (int n = 1; n <= nmax; n++) bad += exhaustive(n);
    double dens[] = {0.3, 0.6, 0.9, 1.0};
    for (int n = 8; n <= 40; n += 8)
        for (int d = 0; d < 4; d++) bad += random_tests(n, 200000, dens[d]);
    printf("total counterexamples found: %lld (cpu %.1fs)\n", bad, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return bad != 0;
}
