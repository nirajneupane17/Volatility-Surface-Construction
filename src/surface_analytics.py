"""
surface_analytics.py — Vol surface analytics: term structure, skew, local vol.
Author: Niraj Neupane | github.com/nirajneupane17
Project: Volatility Surface Construction
"""
import numpy as np
import pandas as pd
from scipy.interpolate import RectBivariateSpline
from typing import List, Dict, Optional

def atm_term_structure(options_df,expiry_col='expiry',T_col='T',iv_col='implied_vol',m_col='moneyness'):
    """Extract ATM implied vol by expiry."""
    atm=options_df[options_df[m_col]==1.0].copy()
    atm=atm.sort_values(T_col)[['expiry',T_col,iv_col]].reset_index(drop=True)
    return atm

def forward_vol(atm_df,T_col='T',iv_col='implied_vol'):
    """Compute forward (instantaneous) volatility from term structure."""
    atm=atm_df.copy(); atm['forward_vol']=np.nan
    for i in range(1,len(atm)):
        T1=atm.loc[i-1,T_col]; T2=atm.loc[i,T_col]
        s1=atm.loc[i-1,iv_col]; s2=atm.loc[i,iv_col]
        var_fwd=(s2**2*T2-s1**2*T1)/(T2-T1)
        atm.loc[i,'forward_vol']=np.sqrt(max(0,var_fwd))
    return atm

def vol_skew(options_df,expiry,delta_otm=0.90,m_col='moneyness',iv_col='implied_vol'):
    """Compute put skew = IV(delta_otm) - IV(ATM) for a given expiry."""
    d=options_df[options_df['expiry']==expiry]
    atm_iv=d[d[m_col]==1.0][iv_col].values
    otm_iv=d[d[m_col]==round(delta_otm,2)][iv_col].values
    if len(atm_iv)==0 or len(otm_iv)==0: return np.nan
    return float(otm_iv[0]-atm_iv[0])

def vol_risk_reversal(options_df,expiry,m_otm=0.90,m_otc=1.10):
    """Risk reversal = IV(OTM call) - IV(OTM put)."""
    d=options_df[options_df['expiry']==expiry]
    put_iv=d[d['moneyness']==round(m_otm,2)]['implied_vol'].values
    call_iv=d[d['moneyness']==round(m_otc,2)]['implied_vol'].values
    if len(put_iv)==0 or len(call_iv)==0: return np.nan
    return float(call_iv[0]-put_iv[0])

def vol_butterfly(options_df,expiry,m_wing=0.90):
    """Butterfly spread = (IV(OTM put)+IV(OTM call))/2 - IV(ATM)."""
    d=options_df[options_df['expiry']==expiry]
    atm=d[d['moneyness']==1.0]['implied_vol'].values
    put_w=d[d['moneyness']==round(m_wing,2)]['implied_vol'].values
    call_w=d[d['moneyness']==round(2-m_wing,2)]['implied_vol'].values
    if len(atm)==0 or len(put_w)==0 or len(call_w)==0: return np.nan
    return float((put_w[0]+call_w[0])/2-atm[0])

def surface_summary(options_df,expiry_list):
    """Full surface summary: ATM IV, skew, RR, butterfly per expiry."""
    rows=[]
    for exp in expiry_list:
        d=options_df[options_df['expiry']==exp]
        if len(d)==0: continue
        T=d['T'].values[0]; atm_iv=d[d['moneyness']==1.0]['implied_vol'].values
        rows.append({'expiry':exp,'T_days':round(T*252),'atm_iv':round(atm_iv[0]*100,2) if len(atm_iv)>0 else np.nan,
            'skew_90':round(vol_skew(options_df,exp)*100,3),
            'rr_90_110':round(vol_risk_reversal(options_df,exp)*100,3) if vol_risk_reversal(options_df,exp) else np.nan,
            'butterfly_90':round(vol_butterfly(options_df,exp)*100,3) if vol_butterfly(options_df,exp) else np.nan,})
    return pd.DataFrame(rows)

if __name__=='__main__':
    import pandas as pd
    opts=pd.read_csv('/home/claude/VOL/data/options_chain.csv')
    term=atm_term_structure(opts)
    fwd=forward_vol(term)
    print(fwd.to_string())
    print("surface_analytics.py OK")
