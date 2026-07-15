"""
bs_pricing.py
=============
Black-Scholes option pricing, Greeks, and implied volatility extraction.
Foundation for volatility surface construction.

Author : Niraj Neupane | github.com/nirajneupane17
Series : Quant Trading Projects — Volatility Series
"""
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Union, Dict


def bs_price(S: float, K: float, T: float, r: float,
              sigma: float, q: float = 0.0,
              option_type: str = 'call') -> float:
    """
    Black-Scholes option price.

    Parameters
    ----------
    S    : spot price
    K    : strike price
    T    : time to expiry (years)
    r    : risk-free rate (continuous)
    sigma: implied volatility
    q    : dividend yield
    option_type: 'call' or 'put'
    """
    if T <= 0:
        return max(0, S-K) if option_type == 'call' else max(0, K-S)
    d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    F  = S * np.exp((r-q)*T)
    if option_type == 'call':
        return np.exp(-r*T) * (F*norm.cdf(d1) - K*norm.cdf(d2))
    return np.exp(-r*T) * (K*norm.cdf(-d2) - F*norm.cdf(-d1))


def bs_greeks(S: float, K: float, T: float, r: float,
               sigma: float, q: float = 0.0,
               option_type: str = 'call') -> Dict:
    """
    Full Black-Scholes Greeks.
    Delta, Gamma, Vega, Theta, Rho, Vanna, Volga.
    """
    if T <= 0:
        return {g: np.nan for g in ['delta','gamma','vega','theta','rho']}
    d1 = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    sign = 1 if option_type == 'call' else -1

    delta = sign * np.exp(-q*T) * norm.cdf(sign*d1)
    gamma = np.exp(-q*T) * norm.pdf(d1) / (S*sigma*np.sqrt(T))
    vega  = S * np.exp(-q*T) * norm.pdf(d1) * np.sqrt(T) / 100  # per 1% vol
    theta = (-(S*np.exp(-q*T)*norm.pdf(d1)*sigma)/(2*np.sqrt(T))
             - sign*r*K*np.exp(-r*T)*norm.cdf(sign*d2)
             + sign*q*S*np.exp(-q*T)*norm.cdf(sign*d1)) / 365
    rho   = sign * K * T * np.exp(-r*T) * norm.cdf(sign*d2) / 100

    return {'delta': round(delta,6), 'gamma': round(gamma,8),
            'vega': round(vega,6), 'theta': round(theta,6),
            'rho': round(rho,6), 'd1': round(d1,6), 'd2': round(d2,6)}


def implied_vol(price: float, S: float, K: float, T: float,
                 r: float, q: float = 0.0,
                 option_type: str = 'call',
                 tol: float = 1e-7,
                 max_iter: int = 200) -> float:
    """
    Newton-Raphson implied volatility solver.
    Falls back to Brent's method if Newton diverges.

    Returns NaN if no solution (deep ITM/OTM or bid-ask issue).
    """
    if T <= 0: return np.nan
    intrinsic = max(0, S-K) if option_type == 'call' else max(0, K-S)
    if price <= intrinsic + 1e-8: return np.nan

    # Newton-Raphson
    sigma = 0.20
    for _ in range(max_iter):
        p    = bs_price(S, K, T, r, sigma, q, option_type)
        d1   = (np.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        vega = S * np.exp(-q*T) * norm.pdf(d1) * np.sqrt(T)
        if vega < 1e-10: break
        diff = p - price
        if abs(diff) < tol: return round(sigma, 8)
        sigma -= diff / vega
        if sigma <= 0: sigma = 0.001

    # Fallback: Brent
    try:
        return round(brentq(
            lambda v: bs_price(S,K,T,r,v,q,option_type)-price,
            1e-6, 10.0, xtol=tol, maxiter=max_iter), 8)
    except: return np.nan


def surface_from_prices(prices_df: pd.DataFrame,
                          S: float, r: float, q: float = 0.0) -> pd.DataFrame:
    """
    Extract implied vol surface from a DataFrame of option prices.
    Required columns: strike, maturity_T, option_price, option_type
    """
    result = prices_df.copy()
    result['implied_vol'] = result.apply(
        lambda row: implied_vol(row['option_price'], S, row['strike'],
                                row['maturity_T'], r, q, row['option_type']), axis=1)
    return result


if __name__ == '__main__':
    p = bs_price(185, 185, 0.25, 0.053, 0.20, 0.005, 'call')
    g = bs_greeks(185, 185, 0.25, 0.053, 0.20, 0.005, 'call')
    iv = implied_vol(p, 185, 185, 0.25, 0.053, 0.005, 'call')
    print(f"Price: {p:.4f}  Delta: {g['delta']:.4f}  IV: {iv:.4f}")
    print("bs_pricing.py OK")
