"""
vol_surface.py
==============
Volatility surface construction, interpolation, and analytics.
Smile, skew, term structure, risk reversal, and butterfly.

Author : Niraj Neupane | github.com/nirajneupane17
Series : Quant Trading Projects — Volatility Series
"""
import numpy as np
import pandas as pd
from scipy.interpolate import RectBivariateSpline, griddata
from typing import Dict, Tuple, Optional


def vol_smile(surface_df: pd.DataFrame,
               maturity_days: int) -> pd.DataFrame:
    """Extract smile (IV vs strike) for a given expiry."""
    return surface_df[surface_df['maturity_days'] == maturity_days]\
        .sort_values('strike_pct')[['strike', 'strike_pct', 'log_moneyness',
                                     'implied_vol_pct', 'delta', 'option_type']].copy()


def atm_term_structure(surface_df: pd.DataFrame) -> pd.DataFrame:
    """ATM IV across all maturities — the vol term structure."""
    result = []
    for Td in surface_df['maturity_days'].unique():
        d = surface_df[surface_df['maturity_days'] == Td]
        # Find closest to ATM (strike_pct = 1.0)
        atm = d.iloc[(d['strike_pct'] - 1.0).abs().argsort()[:1]]
        result.append({'maturity_days': Td, 'atm_iv_pct': atm['implied_vol_pct'].values[0]})
    return pd.DataFrame(result).sort_values('maturity_days')


def risk_reversal(surface_df: pd.DataFrame,
                   maturity_days: int,
                   delta_target: float = 0.25) -> float:
    """
    25-delta risk reversal = Put IV − Call IV.
    Negative = left skew (more demand for downside protection).
    Standard FX and equity vol market convention.
    """
    d = surface_df[surface_df['maturity_days'] == maturity_days].copy()
    put_25d  = d[d['delta'].between(-delta_target-0.05, -delta_target+0.05)]['implied_vol_pct'].mean()
    call_25d = d[d['delta'].between(delta_target-0.05, delta_target+0.05)]['implied_vol_pct'].mean()
    return float(put_25d - call_25d)


def butterfly(surface_df: pd.DataFrame,
               maturity_days: int,
               delta_target: float = 0.25) -> float:
    """
    25-delta butterfly = (Put25d + Call25d)/2 − ATM
    Measures smile curvature — higher = fatter tails.
    """
    d = surface_df[surface_df['maturity_days'] == maturity_days].copy()
    put_25d  = d[d['delta'].between(-delta_target-0.05, -delta_target+0.05)]['implied_vol_pct'].mean()
    call_25d = d[d['delta'].between(delta_target-0.05, delta_target+0.05)]['implied_vol_pct'].mean()
    atm      = d.iloc[(d['strike_pct'] - 1.0).abs().argsort()[:1]]['implied_vol_pct'].values[0]
    return float((put_25d + call_25d)/2 - atm)


def interpolate_surface(surface_df: pd.DataFrame,
                          strikes_pct: np.ndarray,
                          maturities_T: np.ndarray) -> np.ndarray:
    """
    Bivariate spline interpolation of the vol surface.
    Returns 2D array of IVs on new (strikes × maturities) grid.
    No-arbitrage not enforced — for visualisation only.
    """
    piv = surface_df.pivot_table(index='maturity_T', columns='strike_pct',
                                   values='implied_vol_pct')
    x_orig = piv.columns.values
    y_orig = piv.index.values
    spline = RectBivariateSpline(y_orig, x_orig, piv.values, kx=3, ky=3)
    return spline(maturities_T, strikes_pct)


def vol_cone(realized_vol_series: pd.Series,
              windows: list = [21, 63, 126, 252]) -> pd.DataFrame:
    """
    Realized vol cone — historical range of realised vol at each window.
    Used to contextualise current IV levels vs historical RV.
    """
    result = []
    for w in windows:
        rv = realized_vol_series.rolling(w).std() * np.sqrt(252) * 100
        result.append({'window_days': w,
            'p10': round(rv.quantile(0.10), 2), 'p25': round(rv.quantile(0.25), 2),
            'median': round(rv.quantile(0.50), 2), 'p75': round(rv.quantile(0.75), 2),
            'p90': round(rv.quantile(0.90), 2), 'current': round(rv.iloc[-1], 2)})
    return pd.DataFrame(result)


if __name__ == '__main__':
    surf = pd.read_csv('/home/claude/VOLSURF/data/vol_surface.csv')
    smile_30 = vol_smile(surf, 30)
    ts = atm_term_structure(surf)
    rr = risk_reversal(surf, 30)
    bf = butterfly(surf, 30)
    print(f"30d ATM IV: {ts[ts['maturity_days']==30]['atm_iv_pct'].values[0]:.2f}%")
    print(f"30d Risk Reversal: {rr:.2f} vol pts")
    print(f"30d Butterfly: {bf:.2f} vol pts")
    print("vol_surface.py OK")
