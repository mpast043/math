"""Rare-group membership implications of the accepted three-atom construction."""
import math

import numpy as np

from review.applications.ot_stability import area,cell,clip,map_distance,solve_weights,w2_distance


def _check(m,b):
    if not (math.isfinite(m) and math.isfinite(b) and 0<m<1 and 0<=b<=min(m,1-m)):
        raise ValueError('Require 0 < m < 1 and 0 <= b <= min(m,1-m), without strip clipping.')


def assignment_metrics(m,b):
    """Exact metrics on the uniform square; membership is a proposed use."""
    _check(m,b)
    lost=b/4
    intersection=m-lost
    return {'w2':b*math.sqrt(m),'map_l2':math.sqrt(b/2+m*b*b),
            'lost_mass':lost,'gained_mass':lost,'reassigned_mass':b/2,
            'retained_fraction':intersection/m,'replacement_fraction':lost/m,
            'jaccard':intersection/(m+lost)}


def polygon_metrics(m,b):
    """Compute overlaps independently using the accepted numerical solver."""
    _check(m,b)
    Y=np.array([[-1.,0.],[1.,0.],[0.,0.]])
    Z=Y.copy(); Z[2,1]=b
    masses=np.array([(1-m)/2,(1-m)/2,m])
    w=solve_weights(Y,masses); v=solve_weights(Z,masses)
    polygon=cell(Y,w,2)
    for j in (0,1):
        polygon=clip(polygon,Z[2]-Z[j],v[2]-v[j])
    intersection=area(polygon)/4
    return {'w2':float(w2_distance(Y,masses,Z,masses)),
            'map_l2':float(map_distance(Y,w,Z,v)),
            'lost_mass':float(m-intersection),
            'jaccard':float(intersection/(2*m-intersection))}
