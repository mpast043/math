"""Tests for the continuation calculations, not for the accepted source proofs."""
import importlib
import math

import networkx as nx
import numpy as np
import pytest


def module(name):
    try:
        return importlib.import_module('review.continuation.' + name)
    except ModuleNotFoundError as exc:
        pytest.fail(f'Continuation implementation is missing: {exc.name}')


def test_qubit_holevo_matches_density_matrix_entropy():
    q = module('quantum')
    p, t, t1, t2, nu = .37, 81., 100., 130., .12
    z = math.exp(-t/t1) * p + (1-math.exp(-t/t1))*nu
    off = math.exp(-t/t2)*math.sqrt(p*(1-p))
    signal = np.array([[1-z, off], [off, z]])
    eig = np.linalg.eigvalsh(signal)
    entropy = -np.sum(eig*np.log2(eig))
    expected = q.h2(z)-entropy
    assert q.symmetric_holevo(p,t,t1,t2,nu) == pytest.approx(expected,abs=1e-12)


def test_qubit_readout_uses_measured_coherence_and_zero_time():
    q = module('quantum')
    r = q.compare_rates(100,100,200,.05)
    assert r['x_readout'] == pytest.approx(1-q.h2((1-math.exp(-.5))/2))
    assert r['gad_capacity'] > r['x_readout'] > r['z_readout']
    assert q.compare_rates(0,100,200,.05)['x_readout'] == pytest.approx(1)
    assert q.compare_rates(100,100,50,.05)['x_readout'] < r['z_readout']
    with pytest.raises(ValueError): q.compare_rates(100,100,201,.05)


def test_qubit_coherence_threshold_changes_the_encoding_decision():
    q = module('quantum')
    threshold=q.x_readout_threshold(100,100,.05)
    assert 100 < threshold < 200
    a=q.compare_rates(100,100,threshold-.01,.05)
    b=q.compare_rates(100,100,threshold+.01,.05)
    assert a['x_readout'] < a['z_readout']
    assert b['x_readout'] > b['z_readout']


@pytest.mark.parametrize('bits',[0,.1,1,8])
def test_optical_entropy_inversion(bits):
    o=module('optical')
    assert o.g_bits(o.inverse_g_bits(bits)) == pytest.approx(bits,abs=1e-10)


def test_optical_budgets_meet_demands_with_fair_time_sharing():
    o=module('optical')
    for rb,rc in ((1,.5),(3,1),(0,1),(1,0)):
        d=o.photon_budgets(rb,rc,.6,.1)
        assert o.g_bits(.6*d['near_photons']) == pytest.approx(rb,abs=1e-9)
        far=o.g_bits(.1*d['superposition'])-o.g_bits(.1*d['near_photons'])
        assert far == pytest.approx(rc,abs=1e-9)
        assert d['superposition'] <= d['time_sharing']*(1+1e-8)+1e-9
        f=d['near_fraction']
        if rb and rc:
            assert f*o.g_bits(.6*d['near_active_photons']) == pytest.approx(rb,abs=1e-8)
            assert (1-f)*o.g_bits(.1*d['far_active_photons']) == pytest.approx(rc,abs=1e-8)
    with pytest.raises(ValueError): o.photon_budgets(1,1,.1,.6)


def test_transport_membership_matches_independent_polygon_solver():
    tr=module('transport')
    for m,b in ((.01,.005),(.1,.025),(.3,0)):
        exact=tr.assignment_metrics(m,b)
        numeric=tr.polygon_metrics(m,b)
        assert numeric['w2'] == pytest.approx(exact['w2'],abs=1e-11)
        assert numeric['map_l2'] == pytest.approx(exact['map_l2'],abs=1e-9)
        assert numeric['lost_mass'] == pytest.approx(exact['lost_mass'],abs=1e-10)
        assert numeric['jaccard'] == pytest.approx(exact['jaccard'],abs=1e-10)
    assert tr.assignment_metrics(.001,.0005)['retained_fraction'] == pytest.approx(.875)
    assert tr.assignment_metrics(.001,.0005)['jaccard'] == pytest.approx(7/9)
    with pytest.raises(ValueError): tr.assignment_metrics(.01,.02)


def test_reaction_repair_minimizes_allowed_cost_and_reports_infeasible():
    r=module('reactions')
    edges=[('A','B'),('A','C'),('B','D'),('C','D')]
    candidates=[('D','A',1),('D','B',1),('B','A',1),('D','C',1),('C','A',1)]
    repair=r.minimum_repair(['A','B','C','D'],edges,candidates)
    assert repair['added'] == [('D','A')]
    assert repair['cost'] == 1
    restricted=r.minimum_repair(['A','B','C','D'],edges,candidates[1:])
    assert len(restricted['added']) == 2
    assert r.weakly_reversible(['A','B','C','D'],edges+restricted['added'])
    assert r.minimum_repair(['A','B'],[('A','B')],[]) is None


def test_reaction_abundance_floor_and_dynamic_conservation():
    r=module('reactions')
    lo,hi=r.cycle_floor_interval(.01)
    assert lo == pytest.approx(1/98)
    assert min(r.cycle_stationary(lo)) == pytest.approx(.01)
    assert min(r.cycle_stationary(hi)) == pytest.approx(.01)
    trajectory=r.cycle_trajectory(lo,[1e-8,1e-8,1-2e-8],np.linspace(0,50,101))
    assert np.all(trajectory>=-1e-12)
    assert np.max(np.abs(trajectory.sum(axis=1)-1)) < 1e-12
    assert trajectory[-1] == pytest.approx(r.cycle_stationary(lo),abs=1e-8)
    with pytest.raises(ValueError): r.cycle_floor_interval(.34)


def test_network_chain_preserves_labeled_degrees_and_carries_state():
    n=module('networks')
    G=nx.karate_club_graph()
    chain=n.SwitchChain(G,seed=7)
    chain.advance(2000)
    after_burn=set(chain.edges)
    assert after_burn != {tuple(sorted(e)) for e in G.edges()}
    chain.advance(100)
    assert set(chain.edges) != after_burn
    H=chain.graph()
    assert dict(H.degree()) == dict(G.degree())
    assert nx.number_of_selfloops(H)==0
    assert H.number_of_edges()==G.number_of_edges()
    assert n.motifs(H)['triangles']==sum(nx.triangles(H).values())//3


def test_network_exact_tail_on_all_two_regular_six_vertex_graphs():
    n=module('networks')
    d=n.exact_reference()
    assert d['states']==70
    assert d['triangle_tail']==pytest.approx(1/7)
    assert n.tail_mcse(np.zeros((4,100))) is None


def test_weighted_dataset_is_counted_as_unweighted_like_its_null_graphs():
    n=module('networks')
    G=nx.karate_club_graph()
    assert n.motifs(G)['triangles']==45
    assert n.motifs(G)==n.motifs(nx.Graph(G.edges()))
    K=nx.complete_graph(4)
    nx.set_edge_attributes(K,7,'weight')
    assert n.motifs(K)['triangles']==4
    assert n.motifs(K)['four_cycles']==3


def test_runner_records_provenance_and_all_twelve_uses(tmp_path):
    run=module('run')
    import json
    result=run.build_results(tmp_path,network_draws=40,make_figures=False)
    assert result['source_commit']=='80b50443f73da7934815df0973231b13666890f6'
    assert result['networks']['degrees_preserved']
    assert len(result['agenda'])==12
    assert result['optical']['rows'][0]['superposition']>0
    written=json.loads((tmp_path/'results.json').read_text())
    assert written['quantum']['baseline']['x_readout']==result['quantum']['baseline']['x_readout']
    assert 'NaN' not in (tmp_path/'results.json').read_text()
