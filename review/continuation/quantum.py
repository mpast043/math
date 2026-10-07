"""Classical encoding decisions for Markovian relaxation plus pure dephasing."""
import math

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from review.applications.qubit_memory_capacity import bac_capacity, capacity


def h2(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -(p*math.log(p)+(1-p)*math.log1p(-p))/math.log(2)


def thermal_population(temperature_K, frequency_Hz=5e9):
    if not math.isfinite(temperature_K) or temperature_K <= 0:
        raise ValueError('Temperature must be finite and positive.')
    exponent=6.62607015e-34*frequency_Hz/(1.380649e-23*temperature_K)
    return 0.0 if exponent > 700 else 1/(1+math.exp(exponent))


def _check(t,T1,T2):
    if not all(math.isfinite(x) for x in (t,T1,T2)) or t<0 or T1<=0 or T2<=0 or T2>2*T1:
        raise ValueError('Require t >= 0, T1 > 0, and 0 < T2 <= 2 T1 for this model.')


def symmetric_holevo(p,t,T1,T2,nu):
    """Achievable Holevo rate of equal-prior sqrt(1-p)|0> +/- sqrt(p)|1>."""
    _check(t,T1,T2)
    if not (0<=p<=1 and 0<=nu<=1):
        raise ValueError('p and nu must lie in [0,1].')
    q=math.exp(-t/T1)*p+(1-math.exp(-t/T1))*nu
    transverse=math.exp(-t/T2)*math.sqrt(p*(1-p))
    radius=math.sqrt(max(0,(1-2*q)**2+4*transverse**2))
    return max(0.0,h2(q)-h2((1-min(1.0,radius))/2))


def _best_pair(t,T1,T2,nu):
    grid=np.linspace(0,1,81)
    values=[symmetric_holevo(p,t,T1,T2,nu) for p in grid]
    i=int(np.argmax(values))
    opt=minimize_scalar(lambda p:-symmetric_holevo(p,t,T1,T2,nu),
                        bounds=(grid[max(0,i-1)],grid[min(80,i+1)]),method='bounded',
                        options={'xatol':1e-12})
    return float(-opt.fun),float(opt.x)


def compare_rates(t,T1,T2,temperature_K):
    """Times share any consistent unit. Rates are classical bits per stored qubit."""
    _check(t,T1,T2)
    nu=thermal_population(temperature_K)
    gamma=-math.expm1(-t/T1)
    z=bac_capacity(gamma*nu,gamma*(1-nu))
    x=1-h2((1-math.exp(-t/T2))/2)
    pair,p=_best_pair(t,T1,T2,nu)
    ideal,_=capacity(gamma,nu)
    return {'z_readout':z,'x_readout':x,'symmetric_holevo_achievable':pair,
            'best_demonstrated_local_readout':max(x,z),'pair_population':p,
            'gad_capacity':ideal,'thermal_population':nu}


def x_readout_threshold(t,T1,temperature_K):
    """Minimum T2 for this X-readout scheme to beat optimized Z encoding.

    May exceed the physical 2*T1 limit. At t=0 both rates are 1 and no
    strictly better scheme exists, so this comparison is undefined.
    """
    if not math.isfinite(t) or not math.isfinite(T1) or t<=0 or T1<=0:
        raise ValueError('Threshold comparison requires positive finite t and T1.')
    nu=thermal_population(temperature_K)
    gamma=-math.expm1(-t/T1)
    z=bac_capacity(gamma*nu,gamma*(1-nu))
    error=brentq(lambda e:h2(e)-(1-z),0,.5,xtol=1e-14)
    contrast=1-2*error
    return -t/math.log(contrast) if contrast>0 else 0.0
