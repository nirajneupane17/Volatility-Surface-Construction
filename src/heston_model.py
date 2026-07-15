"""
heston_model.py
===============
Heston stochastic volatility model — analytical approximation,
calibration, and local volatility extraction via Dupire's formula.

Author : Niraj Neupane | github.com/nirajneupane17
Series : Quant Trading Projects — Volatility Series
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Tuple


def heston_iv_approx(K: float, T: float, S: float,
                      v0: float = 0.04, kappa: float = 2.5,
                      theta: float = 0.04, xi: float = 0.5,
                      rho: float = -0.70, r: float = 0.053) -> float:
    """
    Heston (1993) approximate implied volatility.
    Uses small-time expansion — accurate for T < 2 years.

    Parameters
    ----------
    v0    : initial variance (v0 = sigma0^2)
    kappa : mean-reversion speed
    theta : long-run variance
    xi    : vol-of-vol (volatility of variance)
    rho   : correlation between spot and variance (typically negative)
    """
    x = np.log(K/S)
    atm_var = v0 + (theta - v0) * (1 - np.exp(-kappa*T)) / (kappa*T + 1e-8)
    atm_vol = np.sqrt(max(atm_var, 0.001))
    # Linear skew term from rho
    skew = rho * xi / (2*kappa) * (1 - np.exp(-kappa*T)) / (T + 1e-8)
    # Curvature from xi
    curv = xi**2 / (8*kappa**3*T + 1e-8) * \
           (1 - np.exp(-kappa*T))**2 * (1 + np.exp(-kappa*T))
    iv = atm_vol + skew*x + curv*x**2
    return max(iv, 0.03)


def calibrate_heston(market_surface: pd.DataFrame,
                      S: float, r: float,
                      x0: Dict = None) -> Dict:
    """
    Calibrate Heston model to market implied vol surface.
    Minimises sum of squared IV errors across strikes and maturities.

    Parameters
    ----------
    market_surface : DataFrame with columns: strike, maturity_T, implied_vol
    S, r           : spot and risk-free rate
    x0             : initial parameter guess

    Returns
    -------
    dict: calibrated v0, kappa, theta, xi, rho + calibration error
    """
    if x0 is None:
        x0 = {'v0':0.04,'kappa':2.5,'theta':0.04,'xi':0.5,'rho':-0.70}
    params0 = [x0['v0'], x0['kappa'], x0['theta'], x0['xi'], x0['rho']]
    bounds  = [(0.001, 1.0), (0.1, 15.0), (0.001, 1.0), (0.01, 2.0), (-0.99, -0.01)]

    def objective(params):
        v0, kappa, theta, xi, rho = params
        errors = []
        for _, row in market_surface.iterrows():
            model_iv = heston_iv_approx(row['strike'], row['maturity_T'], S,
                                         v0, kappa, theta, xi, rho, r)
            errors.append((model_iv*100 - row['implied_vol_pct'])**2)
        return np.mean(errors)

    res = minimize(objective, params0, method='L-BFGS-B', bounds=bounds,
                   options={'maxiter': 500, 'ftol': 1e-10})
    v0, kappa, theta, xi, rho = res.x
    return {'v0': round(v0,6), 'kappa': round(kappa,4), 'theta': round(theta,6),
            'xi': round(xi,4), 'rho': round(rho,4),
            'rmse_vol_pts': round(np.sqrt(res.fun), 4), 'converged': res.success}


def dupire_local_vol(surface_df: pd.DataFrame, S: float, r: float) -> pd.DataFrame:
    """
    Dupire (1994) local volatility from implied vol surface.
    σ_loc²(K,T) = (∂C/∂T) / (0.5*K²*∂²C/∂K²)
    Approximated numerically from the IV surface.
    """
    result = []
    mats = sorted(surface_df['maturity_T'].unique())
    for i, T in enumerate(mats[1:-1]):
        d  = surface_df[surface_df['maturity_T'] == T].sort_values('strike')
        T_prev = mats[i]; T_next = mats[i+2]
        d_prev = surface_df[surface_df['maturity_T'] == T_prev].sort_values('strike')
        d_next = surface_df[surface_df['maturity_T'] == T_next].sort_values('strike')
        for _, row in d.iterrows():
            K = row['strike']
            iv = row['implied_vol'] / 100
            iv_prev_T = d_prev.iloc[(d_prev['strike']-K).abs().argsort()[:1]]['implied_vol'].values[0]/100
            iv_next_T = d_next.iloc[(d_next['strike']-K).abs().argsort()[:1]]['implied_vol'].values[0]/100
            dT = (T_next - T_prev) / 2
            div_dT = (iv_next_T**2 - iv_prev_T**2) / (2*dT)
            local_var = max(iv**2 + 2*iv*T*div_dT, 0.0001)
            result.append({'strike': K, 'maturity_T': T, 'local_vol': round(np.sqrt(local_var)*100, 4)})
    return pd.DataFrame(result)


if __name__ == '__main__':
    surf = pd.read_csv('/home/claude/VOLSURF/data/vol_surface.csv')
    sample = surf[surf['maturity_days'].isin([30, 90, 180])].copy()
    result = calibrate_heston(sample, S=185, r=0.053)
    print("Heston calibration:")
    for k, v in result.items(): print(f"  {k}: {v}")
    print("heston_model.py OK")
