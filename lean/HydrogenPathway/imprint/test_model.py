"""Numerical regressions, not a formal proof of spectral or channel identities."""
import cmath
import math
import random
import unittest

import model as m


class ImprintTests(unittest.TestCase):
    def assertClose(self, x, y):
        self.assertLess(abs(x - y), m.TOL)

    def test_spectrum_and_trace_norm(self):
        self.assertClose(m.trace_norm([[0j, -1j], [1j, 0j]]), 2)
        self.assertClose(m.trace_norm([[-.7 + 0j, 0j], [0j, .3 + 0j]]), 1)
        v = [complex(.6), .8j]
        self.assertClose(m.trace_norm(m.outer(v)), 1)
        u = [[v[0], -v[1].conjugate()], [v[1], v[0].conjugate()]]
        rotated = m.mul(m.mul(u, [[-.7 + 0j, 0j], [0j, .3 + 0j]]), m.adjoint(u))
        self.assertClose(m.trace_norm(rotated), 1)

    def test_mode_populations_are_not_pointwise_momentum(self):
        plus, minus = m.source(1), m.source(-1)
        self.assertEqual([abs(z) ** 2 for z in plus], [abs(z) ** 2 for z in minus])
        self.assertClose(sum(x.conjugate() * y for x, y in zip(plus, minus)), 0)
        # Explicit disjoint finite momentum-bin support does give equal distributions.
        phi0 = [1 / math.sqrt(2), 1 / math.sqrt(2), 0j, 0j]
        phi1 = [0j, 0j, 1 / math.sqrt(2), 1j / math.sqrt(2)]
        momenta = [[abs((a + sign * b) / math.sqrt(2)) ** 2
                    for a, b in zip(phi0, phi1)] for sign in (1, -1)]
        for x, y in zip(*momenta):
            self.assertClose(x, y)
        # Orthogonal but overlapping mode functions are a counterexample.
        overlapping0, overlapping1 = plus, minus
        distributions = [[abs((a + sign * b) / math.sqrt(2)) ** 2
                          for a, b in zip(overlapping0, overlapping1)] for sign in (1, -1)]
        self.assertGreater(abs(distributions[0][0] - distributions[1][0]), .9)

    def test_phase_and_capture_grid(self):
        for k in (0j, .6 + 0j, -.6 + 0j, .6j, .6 + .8j, cmath.exp(.7j)):
            for p0, p1 in ((0., 0.), (.25, .25), (1., 1.), (.8, .2), (1., 0.)):
                with self.subTest(k=k, p0=p0, p1=p1):
                    m.analyze(k, p0, p1, check=True)

    def test_complex_coherence_convention(self):
        k = .3 + .4j
        v = m.isometry(k)
        atom = m.partial_trace(m.outer(m.apply(v, m.source(1))), (2, 2), (0,))
        self.assertClose(atom[0][1], k.conjugate() / 2)
        self.assertClose(atom[1][0], k / 2)

    def test_equal_yield_flag_scaling(self):
        for k in (0j, .3 + .4j, 1j):
            for p in (0., .01, .4, 1.):
                result = m.analyze(k, p, p)
                for name in ("atom", "photon", "joint"):
                    self.assertClose(result["flagged_phase_D"][name], p * result["ideal_phase_D"][name])
                if p == 0:
                    self.assertIsNone(result["conditional_success"])

    def test_failure_information_is_in_inaccessible_memory(self):
        result = m.analyze(.6j, .25, .25, check=True)
        self.assertClose(result["flagged_phase_D"]["joint"], .25)
        self.assertClose(result["conditional_failure_memory_D"], 1)
        self.assertClose(result["global_isometry_D"], 1)
        # No sum of marginal distinguishabilities is asserted to be conserved.
        self.assertClose(sum(result["ideal_phase_D"].values()), 1.6)

    def test_kraus_map_on_a_coherent_mixed_input(self):
        v = m.isometry(.3 + .4j)
        ks = m.capture_kraus(v, .8, .2)
        r0, r1 = m.outer([1 + 0j, 0j]), m.outer([.6 + 0j, .8j])
        mixed = m.add(m.scale(.37, r0), m.scale(.63, r1))
        out = m.channel(ks, mixed)
        linear = m.add(m.scale(.37, m.channel(ks, r0)), m.scale(.63, m.channel(ks, r1)))
        self.assertLess(m.matrix_error(out, linear), m.TOL)
        w = m.stinespring(ks)
        dilated = m.mul(m.mul(w, mixed), m.adjoint(w))
        reduced = m.partial_trace(dilated, (5, 3), (0,))
        self.assertLess(m.matrix_error(out, reduced), m.TOL)
        m.check_density(out)
        self.assertGreaterEqual(min(m.hermitian_spectrum_doubled(m.choi(ks))), -m.TOL)

    def test_general_unequal_flagged_identity(self):
        rng = random.Random(1729)
        def density():
            a = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(2)]
            n = math.sqrt(sum(abs(x) ** 2 for x in a))
            pure = m.outer([x / n for x in a])
            w = rng.random()
            return m.add(m.scale(w, pure), m.scale((1 - w) / 2, m.identity(2)))
        for _ in range(30):
            rho0, rho1, tau = density(), density(), density()
            p0, p1 = rng.random(), rng.random()
            observed, formula = m.flagged_identity(rho0, rho1, tau, p0, p1)
            self.assertClose(observed, formula)
            self.assertGreaterEqual(observed + m.TOL, abs(p0 - p1))
            self.assertLessEqual(observed, max(p0, p1) + m.TOL)

    def test_common_failure_state_is_a_real_assumption(self):
        rho = m.identity(2)
        rho = m.scale(.5, rho)
        tau0, tau1 = m.outer([1 + 0j, 0j]), m.outer([0j, 1 + 0j])
        # All failures: distinguishable failure states invalidate the common-tau formula.
        self.assertClose(m.distance(m.flagged(rho, 0, tau0), m.flagged(rho, 0, tau1)), 1)
        self.assertClose(m.flagged_identity(rho, rho, tau0, 0, 0)[1], 0)

    def test_unequal_acceptance_changes_the_priors(self):
        result = m.analyze(0j, 1., 0., check=True)
        self.assertEqual(result["conditional_success"]["priors"], [1., 0.])
        self.assertClose(result["conditional_success"]["guess"]["photon"], 1)
        self.assertClose(result["ideal_phase_guess_equal_priors"]["photon"], .5)
        self.assertClose(result["flagged_phase_D"]["photon"], 1)
        result = m.analyze(0j, .8, .2)
        self.assertClose(result["flagged_phase_D"]["photon"], .6)

    def test_collected_and_unobserved_factorization(self):
        for kc, ku, p in ((.8 + 0j, .6j, .25), (1j, 0j, 1.), (0j, 1j, .1),
                          (.3 + .4j, -.6 + 0j, .7)):
            m.collected_case(kc, ku, p, check=True)

    def test_full_flagged_error_budget(self):
        v = m.isometry(.3 + .4j)
        models = [m.flagged(m.outer(m.apply(v, m.source(s))), .4) for s in (1, -1)]
        noise = m.scale(.2, m.identity(5))
        actual = [m.add(m.scale(1 - eps, rho), m.scale(eps, noise))
                  for rho, eps in zip(models, (.1, .2))]
        dmodel, dactual = m.distance(*models), m.distance(*actual)
        errors = [m.distance(a, b) for a, b in zip(actual, models)]
        floor = max(0, dmodel - sum(errors))
        self.assertGreaterEqual(dactual + m.TOL, floor)
        self.assertGreaterEqual(m.guess(*actual) + m.TOL, (1 + floor) / 2)

    def test_invalid_parameters_and_nonhermitian_input(self):
        for k in (2 + 0j, complex(float("nan"), 0)):
            with self.assertRaises(ValueError):
                m.analyze(k, .5, .5)
        for p in (-.1, 1.1, float("nan")):
            with self.assertRaises(ValueError):
                m.analyze(.6 + 0j, p, .5)
        with self.assertRaises(ValueError):
            m.trace_norm([[0j, 1 + 0j], [0j, 0j]])
        with self.assertRaises(ValueError):
            m.trace_norm([])
        with self.assertRaises(ValueError):
            m.trace_norm([[complex(float("nan"), 0)]])


if __name__ == "__main__":
    unittest.main()
