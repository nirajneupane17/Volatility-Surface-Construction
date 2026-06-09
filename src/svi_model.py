"""
svi_model.py — SVI parametrisation and calibration (Gatheral 2004).
Author: Niraj Neupane | github.com/nirajneupane17
Project: Volatility Surface Construction
"""
import numpy as np
from scipy.optimize import minimize
from typing import Optional, Tuple, Dict

def svi_total_var(k,a,b,rho,m,sigma):
    """Raw SVI total variance: w(k) = a + b*(rho*(k-m) + sqrt((k-m)^2 + sigma^2))"""
    return a+b*(rho*(k-m)+np.sqrt((k-m)**2+sigma**2))

def svi_implied_vol(k,T,a,b,rho,m,sigma):
    """SVI implied vol from log-moneyness k=ln(K/F) and time T."""
    w=svi_total_var(k,a,b,rho,m,sigma)
    return np.sqrt(np.maximum(w,0)/T)

def svi_constraints_satisfied(a,b,rho,m,sigma):
    """Check SVI no-arbitrage conditions (Fukasawa 2012)."""
    if b<=0 or sigma<=0: return False
    if abs(rho)>=1: return False
    if a+b*sigma*np.sqrt(1-rho**2)<0: return False
    return True

def calibrate_svi(log_moneyness,market_iv,T,n_restarts=50):
    """Calibrate SVI to market implied vols via least squares."""
    total_var_mkt=market_iv**2*T
    def obj(params):
        a,b,rho,m,sigma=params
        if not svi_constraints_satisfied(a,b,rho,m,sigma): return 1e10
        w=svi_total_var(log_moneyness,a,b,rho,m,sigma)
        if np.any(w<0): return 1e10
        return np.sum((w-total_var_mkt)**2)

    best_params=None; best_val=1e10
    np.random.seed(42)
    for _ in range(n_restarts):
        p0=[np.random.uniform(0.005,0.08),np.random.uniform(0.01,0.30),
            np.random.uniform(-0.8,0.0),np.random.uniform(-0.2,0.2),
            np.random.uniform(0.05,0.60)]
        res=minimize(obj,p0,method='Nelder-Mead',
            options={'maxiter':10000,'xatol':1e-10,'fatol':1e-12})
        if res.success and res.fun<best_val:
            a,b,rho,m,sigma=res.x
            if svi_constraints_satisfied(a,b,rho,m,sigma):
                best_params=res.x; best_val=res.fun
    return best_params

def svi_rmse(log_moneyness,market_iv,T,params):
    a,b,rho,m,sigma=params
    w=svi_total_var(log_moneyness,a,b,rho,m,sigma)
    fitted_iv=np.sqrt(np.maximum(w,0)/T)
    return np.sqrt(np.mean((fitted_iv-market_iv)**2))

def butterfly_arbitrage_check(k_grid,params,T):
    """Check butterfly arbitrage: d^2w/dk^2 >= 0 (simplified)."""
    a,b,rho,m,sigma=params
    dk=k_grid[1]-k_grid[0]
    w=svi_total_var(k_grid,a,b,rho,m,sigma)
    d2w=np.diff(w,2)/(dk**2)
    return bool(np.all(d2w>=-1e-6))

def calendar_spread_check(params_T1,params_T2,T1,T2,k_grid):
    """Calendar spread check: w(k,T2) >= w(k,T1) for all k."""
    w1=svi_total_var(k_grid,*params_T1)
    w2=svi_total_var(k_grid,*params_T2)
    return bool(np.all(w2>=w1-1e-8))

if __name__=='__main__':
    np.random.seed(42)
    k=np.linspace(-0.3,0.3,20)
    iv=0.20+0.05*k**2-0.03*k+np.random.normal(0,0.002,20)
    params=calibrate_svi(k,iv,0.25,n_restarts=20)
    if params: print(f"SVI params: a={params[0]:.4f} b={params[1]:.4f} rho={params[2]:.4f}")
    print("svi_model.py OK")
