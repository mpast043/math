"""Minimum photon budgets for ideal pure-loss bosonic broadcast channels."""
import math

import numpy as np
from scipy.optimize import brentq,minimize_scalar


def g_bits(x):
    if x<0 or not math.isfinite(x):
        raise ValueError('Photon number must be nonnegative and finite.')
    if x==0:
        return 0.0
    second=math.log1p(x)-math.log(x) if x<=1 else math.log1p(1/x)
    return (math.log1p(x)+x*second)/math.log(2)


def inverse_g_bits(bits):
    if bits<0 or not math.isfinite(bits):
        raise ValueError('Entropy must be nonnegative and finite.')
    if bits==0:
        return 0.0
    if bits>1020:
        return math.inf
    if bits>60:
        return 2.0**bits/math.e
    # A tolerance in log photons preserves relative accuracy at low rates.
    low=max(-744.0,math.log(bits)-12)
    if g_bits(math.exp(low))>bits:
        raise ValueError('Entropy is below the representable photon-number resolution.')
    high=max(0.0,bits*math.log(2))
    root=brentq(lambda logx:g_bits(math.exp(logx))-bits,low,high,xtol=1e-12,rtol=1e-14)
    return math.exp(root)


def photon_budgets(near_rate,far_rate,eta_near,eta_far):
    """Minimize MEAN photons per total mode, allowing unequal TS active powers.

    The superposition solution inverts the accepted region exactly. The
    time-sharing solution optimizes its active fraction and both powers.
    """
    if (not all(math.isfinite(x) for x in (near_rate,far_rate,eta_near,eta_far))
        or min(near_rate,far_rate)<0 or max(near_rate,far_rate)>50
        or not 0<eta_far<=eta_near or eta_near+eta_far>1):
        raise ValueError('Require rates in [0,50] bits and valid degraded pure-loss efficiencies.')
    near=inverse_g_bits(near_rate)/eta_near
    total=inverse_g_bits(far_rate+g_bits(eta_far*near))/eta_far
    if near_rate==0 or far_rate==0:
        f=1.0 if near_rate else 0.0
        ts=total
        n_near=near if near_rate else 0.0
        n_far=total if far_rate else 0.0
    else:
        def budget(f):
            return (f*inverse_g_bits(near_rate/f)/eta_near
                    +(1-f)*inverse_g_bits(far_rate/(1-f))/eta_far)
        grid=np.linspace(.001,.999,199)
        vals=[budget(f) for f in grid]
        k=int(np.argmin(vals))
        lo=1e-8 if k==0 else grid[k-1]
        hi=1-1e-8 if k==198 else grid[k+1]
        opt=minimize_scalar(budget,bounds=(lo,hi),method='bounded',options={'xatol':1e-12})
        f=float(opt.x); ts=float(opt.fun)
        n_near=inverse_g_bits(near_rate/f)/eta_near
        n_far=inverse_g_bits(far_rate/(1-f))/eta_far
    return {'superposition':total,'near_photons':near,'beta':near/total if total else 0.0,
            'time_sharing':ts,'near_fraction':f,'near_active_photons':n_near,
            'far_active_photons':n_far,'photon_saving_fraction':1-total/ts if ts else 0.0}
