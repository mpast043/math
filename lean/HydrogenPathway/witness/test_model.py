"""Physical-model regressions, not certified numerical interval calculations."""
import math
import unittest
import model as w


class WitnessTests(unittest.TestCase):
    def test_complex_reflection_and_product_outcomes(self):
        # Removing the complex phase from the reflection or atomic basis breaks this.
        for kc in [0j, .6, -.6, .6j, .3 + .4j, 1j, -1., .999999999]:
            for ku in [0j, .6, -.8j, .3 + .4j, 1.]:
                for delta in [0., .3, math.pi / 2, math.pi]:
                    data = w.measurement_case(kc, ku, delta, check=True)
                    t = abs(ku) * math.cos(delta)
                    self.assertAlmostEqual(data['joint_contrast'], t)
                    self.assertAlmostEqual(data['atom_contrast'], abs(kc) * t)
                    self.assertAlmostEqual(data['joint_guess_fixed_parity'], (1+t)/2)

    def test_bad_phase_cannot_be_silently_optimized(self):
        data = w.measurement_case(.2j, -.8j, math.pi, check=True)
        self.assertAlmostEqual(data['joint_guess_fixed_parity'], .1)
        self.assertAlmostEqual(data['joint_guess_best_relabel'], .9)

    def test_all_photon_outcomes_retained(self):
        d = w.measurement_case(.6, .8, 0., check=True)
        for source in d['outcomes']:
            self.assertEqual(len(source), 4)
            self.assertAlmostEqual(sum(source.values()), 1.)
        # Favorable b=+ branch is only .8 probable, never the whole attempt.
        self.assertAlmostEqual(d['outcomes'][0]['1,1'] + d['outcomes'][0]['-1,1'], .8)

    def test_no_click_complete_tables(self):
        for p, ea, ec in [(0.,1.,1.), (1.,0.,1.), (1.,1.,0.), (1.,1.,1.), (.2,.7,.8)]:
            q = p*ea*ec
            for b in [0., (1-q)/2]:
                data = w.attempt_case(.4j, .8, p, ea, ec, b_joint=b,
                                      b_atom=(1-p*ea)/3, check=True)
                for mode in ['joint', 'atom']:
                    table = data[mode]['response']
                    for row in table:
                        self.assertAlmostEqual(sum(row.values()), 1.)
                        self.assertTrue(all(x >= -1e-12 for x in row.values()))

    def test_fair_efficiency_threshold(self):
        for ec in [.3, .6, .9]:
            d = w.attempt_case(.6, .8, .25, .7, ec, check=True)
            expected = .25*.7*.8*(ec-.6)/2
            self.assertAlmostEqual(d['guess_difference'], expected)
            self.assertEqual(d['guess_difference'] > 1e-12, ec > .6)

    def test_adversarial_false_accept_bounds_and_budget(self):
        d = w.attempt_case(.4j, .8, .2, .9, .85, visibility_joint=.95,
                           delta=.1, b_joint=.002, b_atom=.001,
                           false_joint=-1., false_atom=1., check=True)
        self.assertGreater(d['budget']['guaranteed_guess_advantage'], .02)
        self.assertGreaterEqual(d['guess_difference'] + 1e-12,
                                d['budget']['guaranteed_guess_advantage'])
        # At large false rates the sufficient certificate must refuse success.
        bad = w.attempt_case(.4, .8, .2, .9, .85, b_joint=.2,
                             b_atom=.2, false_joint=-1., false_atom=1., check=True)
        self.assertFalse(bad['budget']['strict_advantage_certified'])

    def test_expectation_error_budget_not_trace_distance(self):
        d = w.attempt_case(.4, .8, .2, .9, .85, visibility_joint=.95,
                           delta=.1, eps_joint=.02, eps_atom=.01, check=True)
        self.assertLess(d['budget']['joint_contrast_lower'], d['joint']['contrast'])
        self.assertGreater(d['budget']['atom_contrast_upper'], d['atom']['contrast'])

    def test_unknown_phase_and_unobserved_loss(self):
        self.assertAlmostEqual(w.measurement_case(.4, .8, math.pi/2)['joint_contrast'], 0.)
        self.assertAlmostEqual(w.measurement_case(.4, 0j)['joint_contrast'], 0.)

    def test_selection_and_state_dependent_loss_counterexamples(self):
        # Fair guess after erasure is .5, even if the only accepted label is +.
        rows = [{'plus':1., 'minus':0., 'erase':0.}, {'plus':0., 'minus':0., 'erase':1.}]
        self.assertAlmostEqual(w.guess_from_response(rows), .75)
        # Conditional-perfect .999? no: full success-only perfect at rate .001 is .5005.
        rare = w.attempt_case(0j, 1., .001, 1., 1., check=True)
        self.assertAlmostEqual(rare['joint']['guess'], .5005)

    def test_hybrid_retains_atomic_records_when_photon_missing(self):
        for ec in [0., .01, .3, .6, 1.]:
            d = w.attempt_case(.6, .8, .25, .7, ec, check=True)
            self.assertAlmostEqual(d['hybrid_guess_difference'], .25*.7*ec*.8*.4/2)
            self.assertGreaterEqual(d['hybrid']['guess'] + 1e-12, d['atom']['guess'])
            self.assertAlmostEqual(d['hybrid']['fallback_rate'], .25*.7*(1-ec))
        # An adversarial false channel can erase the hybrid gain.
        d = w.attempt_case(.6,.8,.25,.7,.01,b_hybrid=.01,false_hybrid=-1.,check=True)
        self.assertFalse(d['hybrid_budget']['strict_advantage_certified'])

    def test_outcome_dependent_efficiency_invalidates_average_rate(self):
        d = w.port_efficiency_case(.6,.8,1.,0.,check=True)
        self.assertAlmostEqual(d['recorded_photon_rate'], .8)
        self.assertAlmostEqual(d['hybrid_gain'], 0.)
        self.assertGreater(d['naive_gain_from_average_efficiency'], .1)
        for ep,em in [(0.,1.),(.4,.4),(.1,.9),(0.,0.),(1.,1.)]:
            d = w.port_efficiency_case(.6j,.8j,ep,em,check=True)
            self.assertAlmostEqual(d['hybrid_gain'], em*.4*.8/2)

    def test_loss_povm_is_complete_and_supports_same_atomic_readout(self):
        for p,ea,ec,va,vj in [(0.,1.,1.,1.,1.),(1.,1.,1.,1.,1.),(.2,.9,.3,.95,.8)]:
            for hybrid in [False,True]:
                effects = w.loss_povm(.3+.4j,.8j,p,ea,ec,va,vj,hybrid=hybrid)
                total = w.m.zeros(4)
                for e in effects.values():
                    total = w.m.add(total,e)
                    self.assertGreaterEqual(min(w.m.hermitian_spectrum_doubled(e)), -1e-10)
                self.assertLess(w.m.matrix_error(total,w.m.identity(4)), 1e-10)
                # Contract the lossy POVM with both AC density matrices independently.
                c0,c1=w.m.environment(.3+.4j)
                u0,u1=w.m.environment(.8j)
                branches=[w.m.tensor([1,0],w.m.tensor(c0,u0)),
                          w.m.tensor([0,1],w.m.tensor(c1,u1))]
                rows=[]
                for sign in [1,-1]:
                    rho=w.m.outer([(a+sign*b)/math.sqrt(2) for a,b in zip(*branches)])
                    ac=w.m.partial_trace(rho,(2,2,2),(0,1))
                    row={'plus':0.,'minus':0.,'erase':0.}
                    for key,e in effects.items():
                        prob=w.m.trace(w.m.mul(e,ac)).real
                        if key.startswith('a='):
                            a,b=map(int,[part.split('=')[1] for part in key.split(',')])
                            row['plus' if a*b==1 else 'minus']+=prob
                        elif key.startswith('fallback_a='):
                            a=int(key.split('=')[1])
                            row['plus' if a==1 else 'minus']+=prob
                        else:
                            row['erase']+=prob
                    rows.append(row)
                expected=w.attempt_case(.3+.4j,.8j,p,ea,ec,visibility_atom=va,visibility_joint=vj)
                self.assertAlmostEqual(w.guess_from_response(rows), expected['hybrid' if hybrid else 'joint']['guess'])

    def test_invalid_nonfinite_and_budget_parameters(self):
        for call in [lambda: w.measurement_case(1.1, .5),
                     lambda: w.measurement_case(.5, .5, float('nan')),
                     lambda: w.attempt_case(.4,.8,1.,1.,1.,b_joint=.1),
                     lambda: w.attempt_case(.4,.8,.2,.9,.8,eps_joint=-.1),
                     lambda: w.attempt_case(.4,.8,.2,.9,.8,false_atom=2.),
                     lambda: w.attempt_case(.4,.8,.2,.9,.8,visibility_joint=1.1)]:
            with self.assertRaises(ValueError):
                call()


if __name__ == '__main__':
    unittest.main()
