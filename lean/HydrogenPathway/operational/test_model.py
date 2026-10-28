"""Finite operational-boundary regressions. No hardware or interval claim."""
import math
import random
import unittest
import model as o

class BoundaryTests(unittest.TestCase):
    def test_complete_rotated_projection_boundary(self):
        self.assertLess(o.rotated_case(check=True)['trace_error'], 2e-9)

    def test_entrywise_bound_complex_and_block_labels(self):
        rng=random.Random(20261028)
        for n in [1,2,4,5]:
            for _ in range(10):
                labels=[i%2 for i in range(n)]
                a=[[complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(n)] for _ in range(n)]
                b=[[complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(n)] for _ in range(n)]
                d=o.entrywise_case(a,b,labels)
                self.assertLessEqual(d['trace_difference'], d['entrywise_budget']+2e-9)

    def test_full_coherence_and_block_statistics_differ(self):
        d=o.coherent_case(check=True)
        self.assertAlmostEqual(d['global_distance_to_mixture'], .5)
        self.assertAlmostEqual(d['diagonal_effect_difference'], 0.)
        self.assertAlmostEqual(d['coherence_effect_difference'], .5)

    def test_commutation_sufficient_not_necessary(self):
        m=[[.5,.2],[.2,.5]]
        rho=[[.4,0],[0,.6]]
        self.assertGreater(o.entrywise_case(m,rho,[0,1])['effect_offblock_sum'], 0.)
        self.assertAlmostEqual(o.entrywise_case(m,rho,[0,1])['trace_difference'], 0.)

    def test_compressed_local_x_remains_allowed(self):
        for k in [0j,.6,.6j,1.]:
            d=o.encoding_case(k,check=True)
            self.assertAlmostEqual(d['offdiagonal_modulus'],abs(k))
        # It is compression, rather than banning local X, that suppresses coherence.
        self.assertAlmostEqual(o.encoding_case(0j)['compression_multiplication_error'],1.)

    def test_conditional_record_bound_needs_no_independence(self):
        weights=[.45,.05,.05,.45]
        c=[True,True,False,False]
        initial=[False,True,True,False]
        changed=[True,True,False,False]
        later=[True,False,True,False]
        d=o.conditional_union(weights,c,later,initial,changed)
        self.assertAlmostEqual(d['failure'], .9)
        self.assertGreaterEqual(d['bound'],d['failure'])

    def test_shared_wrong_records_still_agree(self):
        d=o.shared_records(.1)
        self.assertEqual(d['record_disagreement'],0.)
        self.assertAlmostEqual(d['source_error'],.1)

    def test_constant_and_coarse_labels_preserve_within_block_coherence(self):
        rho=[[1/3]*3 for _ in range(3)]
        self.assertEqual(o.block_delta(rho,[0,0,0]),rho)
        coarse=o.block_delta(rho,[0,0,1])
        self.assertAlmostEqual(coarse[0][1],1/3)
        self.assertEqual(coarse[0][2],0j)
        self.assertEqual(o.block_delta(coarse,[0,0,1]),coarse)
        self.assertAlmostEqual(o.m.trace(coarse),o.m.trace(rho))

    def test_complex_effect_tight_entrywise_bound(self):
        rho=[[.5,-.5j],[.5j,.5]]
        d=o.entrywise_case(rho,rho,[0,1])
        self.assertAlmostEqual(d['trace_difference'],.5)
        self.assertAlmostEqual(d['entrywise_budget'],.5)

    def test_non_density_trace_identity(self):
        rho=[[1,2],[3,4]];effect=[[5,0],[0,6]]
        self.assertEqual(o.m.trace(o.m.mul(effect,rho)),29)
        self.assertEqual(o.m.trace(o.m.mul(effect,o.block_delta(rho,[0,1]))),29)

    def test_later_coherent_control_changes_measurement_boundary(self):
        rho=o.m.outer(o.m.source(1));mixture=o.block_delta(rho,[0,1])
        h=[[1/math.sqrt(2),1/math.sqrt(2)],[1/math.sqrt(2),-1/math.sqrt(2)]]
        z=[[1,0],[0,0]]
        transformed=o.m.mul(o.m.mul(o.m.adjoint(h),z),h)
        self.assertAlmostEqual(o.entrywise_case(transformed,rho,[0,1])['trace_difference'],.5)
        self.assertGreater(o.entrywise_case(transformed,rho,[0,1])['effect_offblock_sum'],0.)

    def test_invalid_condition_and_cover(self):
        with self.assertRaises(ValueError):
            o.conditional_union([1e308,1e308],[True,True],[True,True],[True,True],[False,False])
        d=o.conditional_union([1e308],[True],[True],[True],[True])
        self.assertEqual(d['bound'],2.)
        with self.assertRaises(ValueError):
            o.conditional_union([1.],[False],[False],[False],[False])
        with self.assertRaises(ValueError):
            o.conditional_union([1.],[True],[True],[False],[False])
        with self.assertRaises(ValueError):
            o.conditional_union([-1.],[True],[False],[False],[False])

if __name__=='__main__':
    unittest.main()
