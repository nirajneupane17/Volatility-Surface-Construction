"""
bs_engine.py — Black-Scholes pricing and implied vol solver.
Author: Niraj Neupane | github.com/nirajneupane17
Project: Volatility Surface Construction
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from typing import Optional

def d1d2(S,K,T,r,q,sigma):
    d1=(np.log(S/K)+(r-q+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    return d1, d1-sigma*np.sqrt(T)

def bs_price(S,K,T,r,q,sigma,option='call'):
    if T<=0 or sigma<=0:
        return max(0,S*np.exp(-q*T)-K*np.exp(-r*T)) if option=='call' else max(0,K*np.exp(-r*T)-S*np.exp(-q*T))
    d1,d2=d1d2(S,K,T,r,q,sigma)
    if option=='call':
        return S*np.exp(-q*T)*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
    return K*np.exp(-r*T)*norm.cdf(-d2)-S*np.exp(-q*T)*norm.cdf(-d1)

def bs_vega(S,K,T,r,q,sigma):
    if T<=0 or sigma<=0: return 0
    d1,_=d1d2(S,K,T,r,q,sigma)
    return S*np.exp(-q*T)*norm.pdf(d1)*np.sqrt(T)

def bs_delta(S,K,T,r,q,sigma,option='call'):
    if T<=0: return (1.0 if S>K else 0.0) if option=='call' else (-1.0 if S<K else 0.0)
    d1,_=d1d2(S,K,T,r,q,sigma)
    return np.exp(-q*T)*norm.cdf(d1) if option=='call' else -np.exp(-q*T)*norm.cdf(-d1)

def bs_gamma(S,K,T,r,q,sigma):
    if T<=0 or sigma<=0: return 0
    d1,_=d1d2(S,K,T,r,q,sigma)
    return np.exp(-q*T)*norm.pdf(d1)/(S*sigma*np.sqrt(T))

def bs_theta(S,K,T,r,q,sigma,option='call'):
    if T<=0: return 0
    d1,d2=d1d2(S,K,T,r,q,sigma)
    term1=-S*np.exp(-q*T)*norm.pdf(d1)*sigma/(2*np.sqrt(T))
    if option=='call':
        return (term1+q*S*np.exp(-q*T)*norm.cdf(d1)-r*K*np.exp(-r*T)*norm.cdf(d2))/365
    return (term1-q*S*np.exp(-q*T)*norm.cdf(-d1)+r*K*np.exp(-r*T)*norm.cdf(-d2))/365

def implied_vol_newton(price,S,K,T,r,q,option='call',tol=1e-8,max_iter=100):
    """Newton-Raphson implied vol solver."""
    if T<=0: return np.nan
    intrinsic=bs_price(S,K,T,r,q,1e-9,option)
    if price<=intrinsic+1e-10: return np.nan
    sigma=0.25  # initial guess
    for _ in range(max_iter):
        px=bs_price(S,K,T,r,q,sigma,option)
        v=bs_vega(S,K,T,r,q,sigma)
        if abs(v)<1e-12: break
        sigma-=(px-price)/v
        sigma=max(1e-6,min(10.0,sigma))
        if abs(px-price)<tol: return sigma
    # fallback to Brent
    try: return brentq(lambda s:bs_price(S,K,T,r,q,s,option)-price,1e-6,10.0,xtol=tol)
    except: return np.nan

def implied_vol_surface(options_df,S,r,q,col_price='call_mid',col_option='call'):
    """Compute IV for an entire options chain DataFrame."""
    ivs=[]
    for _,row in options_df.iterrows():
        iv=implied_vol_newton(row[col_price],S,row['strike'],row['T'],r,q,col_option)
        ivs.append(iv)
    return ivs

if __name__=='__main__':
    S,K,T,r,q,sigma=450,450,0.25,0.053,0.013,0.20
    px=bs_price(S,K,T,r,q,sigma)
    iv=implied_vol_newton(px,S,K,T,r,q)
    print(f"Price={px:.4f}  IV={iv:.4f}  Match={abs(iv-sigma)<1e-6}")
    print("bs_engine.py OK")
