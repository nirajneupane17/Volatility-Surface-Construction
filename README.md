<div align="center">

# Volatility Surface Construction & Smile Dynamics

### Quant Trading Projects — Volatility Series

*A complete institutional-grade volatility modeling framework:
Black-Scholes implied vol extraction, smile and skew construction,
3D vol surface interpolation, Heston model calibration,
Dupire local volatility, and realized vs implied vol risk premium.*

[![Python](https://img.shields.io/badge/Python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## What Is This Project?

The volatility surface is the most important data structure in options markets.
It maps implied volatility as a function of strike and maturity for a given
underlying asset. Every options desk, every derivatives pricing team, and every
vol-aware risk management function relies on a well-constructed vol surface.

Black-Scholes assumes constant volatility. The market does not agree.
OTM puts trade at higher implied vol than ATM options (the smile).
Short-dated options often trade at higher vol than long-dated ones
(term structure inversion). The vol surface captures all of this
and provides a consistent framework for pricing, hedging, and trading.

This project builds the complete volatility modeling stack:
from raw option prices to a full 3D surface, with Heston calibration,
skew analytics, and a 5-year realized vs implied vol comparison.

---

## Who This Is For

| Audience | What They Get |
|:---|:---|
| **Quant Finance Students** | Implied vol extraction, smile, skew, Heston — all tested in derivatives interviews |
| **Options Traders** | Risk reversal, butterfly, term structure — the daily language of vol desks |
| **Quant Researchers** | Heston calibration, Dupire local vol, vol surface interpolation — live research tools |
| **Risk Analysts** | Vol surface for VaR, stress testing, and sensitivities reporting |

---

## Key Results

| Metric | Value | Context |
|:---|:---:|:---|
| **ATM IV (30d)** | ~19.8% | Near-dated at-the-money vol |
| **ATM IV (360d)** | ~20.5% | Long-dated higher — term structure upward sloping |
| **25δ Risk Reversal (30d)** | ~−1.8 vol pts | Negative = left skew = puts more expensive than calls |
| **25δ Butterfly (30d)** | ~+0.4 vol pts | Positive = fat tails = smile curvature above ATM |
| **IV Surface Range** | 15.5% – 26.2% | Deep OTM puts most expensive, OTM calls cheapest |
| **Vol Risk Premium** | ~+2.95% | Implied vol persistently above realised vol |
| **IV > RV** | ~72% of days | Vol sellers earn the premium most of the time |
| **Heston ρ** | −0.70 | Strong negative correlation — equity-style left skew |
| **Heston RMSE** | ~0.3 vol pts | Excellent calibration fit |

---

## What Is in the Data

### `data/vol_surface.csv`
Full implied volatility surface — 21 strikes × 12 maturities = 252 option quotes.

| Column | Description |
|:---|:---|
| `strike` | Absolute strike price |
| `strike_pct` | Strike as fraction of spot (1.0 = ATM) |
| `maturity_days` | Days to expiry: 7, 14, 21, 30, 45, 60, 90, 120, 150, 180, 240, 360 |
| `implied_vol_pct` | Implied volatility in percent |
| `option_price` | Black-Scholes option price |
| `option_type` | 'call' or 'put' |
| `delta` | Black-Scholes delta |
| `log_moneyness` | ln(K/S) — standard x-axis for vol smile |

### `data/term_structure.csv`
ATM implied vol + 25-delta risk reversal and butterfly across all maturities.

### `data/vol_timeseries.csv`
Daily time series 2020–2025: realized vol (21-day), implied vol (30-day),
VIX proxy, vol risk premium, and RV/IV ratio.

---

## How It Works

```
Step 1  Generate option price grid
        21 strikes (70%–130% of spot) × 12 maturities (7–360 days)
        Heston model to produce realistic smile and skew

Step 2  Extract implied volatility
        Invert Black-Scholes price formula → implied vol
        Newton-Raphson solver with Brent fallback

Step 3  Construct vol smile and term structure
        IV vs strike at fixed maturity = smile
        ATM IV vs maturity = term structure

Step 4  Compute skew metrics
        25-delta risk reversal = Put25d − Call25d
        25-delta butterfly = (Put25d + Call25d)/2 − ATM
        Higher RR = more downside fear / left skew

Step 5  Calibrate Heston model
        Fit v0, κ, θ, ξ, ρ to market smile
        Minimise RMSE across all strikes and maturities

Step 6  Realised vs implied vol analysis
        VRP = Implied vol − Realized vol
        Positive VRP = vol sellers earn risk premium
```

---

## Key Findings

**1. The smile exists because the market is smarter than Black-Scholes.**
OTM puts trade at 5–8% higher IV than ATM options at 30-day expiry.
This is not mispricing — it is the market's compensation for crash risk,
adverse selection, and the non-normal distribution of returns.

**2. The risk reversal tells you where fear lives.**
A negative 25-delta risk reversal means puts are more expensive than
equivalent calls. The magnitude tells you how strongly the market
is pricing asymmetric downside risk.

**3. Heston fits the smile — Black-Scholes does not.**
The Heston model with ρ=−0.70 captures the entire surface with
RMSE of ~0.3 vol points. Black-Scholes with any single volatility
cannot fit the smile at all — a different vol is needed for every strike.

**4. The vol risk premium is real and persistent.**
Implied vol exceeded realized vol on ~72% of all days 2020–2025.
This is why short-vega (selling options) strategies are profitable
over long horizons — but they crash catastrophically when they fail.

**5. The term structure inversion matters for trading.**
When short-dated IV > long-dated IV (backwardation), the market
expects near-term volatility to mean-revert — often signals a crisis.
When long-dated > short-dated (contango), the structure is normal.

---

## Project Structure

```
Volatility-Surface-Construction/
│
├── 📁 data/
│   ├── vol_surface.csv        252 option quotes · 21 strikes × 12 maturities
│   ├── term_structure.csv     ATM IV · 25δ RR · butterfly across maturities
│   └── vol_timeseries.csv     Realized vs implied vol · VRP · 2020–2025
│
├── 📓 notebooks/
│   ├── 01_bs_pricing_iv.ipynb         BS pricing · IV extraction · Greeks
│   ├── 02_vol_smile_surface.ipynb     Smile construction · 3D surface
│   ├── 03_skew_term_structure.ipynb   RR · butterfly · term structure
│   ├── 04_heston_calibration.ipynb    Heston fit · residuals · rho sensitivity
│   └── 05_realized_vs_implied.ipynb   VRP · RV/IV comparison · 2020–2025
│
├── 🐍 src/
│   ├── bs_pricing.py      BS price · Greeks · IV solver · Newton-Raphson
│   ├── vol_surface.py     Smile · term structure · RR · butterfly · interpolation
│   └── heston_model.py    Heston IV approx · calibration · Dupire local vol
│
├── 📊 results/
│   ├── 01_vol_smile.png           Smile across maturities · log-moneyness
│   ├── 02_term_structure.png      ATM · 25δ · RR · butterfly vs maturity
│   ├── 03_vol_surface_3d.png      3D wireframe + heatmap
│   ├── 04_skew_analysis.png       Smile shape · delta space · curvature
│   ├── 05_heston_calibration.png  Market vs model · residuals · rho sensitivity
│   ├── 06_realized_vs_implied.png VRP time series · distribution · scatter
│   └── 07_summary_dashboard.png   Full vol analytics overview
│
└── README.md
```

---

## Source Module Reference

### `bs_pricing.py`
| Function | What It Does |
|:---|:---|
| `bs_price(S,K,T,r,sigma,q,type)` | Black-Scholes call/put price |
| `bs_greeks(S,K,T,r,sigma,q,type)` | Delta · Gamma · Vega · Theta · Rho |
| `implied_vol(price,S,K,T,r,q,type)` | Newton-Raphson IV solver with Brent fallback |
| `surface_from_prices(df,S,r,q)` | Batch IV extraction from price DataFrame |

### `vol_surface.py`
| Function | What It Does |
|:---|:---|
| `vol_smile(surface_df, maturity_days)` | IV vs strike at given expiry |
| `atm_term_structure(surface_df)` | ATM IV across all maturities |
| `risk_reversal(surface_df, Td, delta)` | 25δ Put IV − Call IV |
| `butterfly(surface_df, Td, delta)` | 25δ (Put+Call)/2 − ATM |
| `interpolate_surface(surface_df, strikes, mats)` | Bivariate spline interpolation |
| `vol_cone(rv_series, windows)` | Historical RV cone vs current IV |

### `heston_model.py`
| Function | What It Does |
|:---|:---|
| `heston_iv_approx(K,T,S,v0,kappa,theta,xi,rho,r)` | Analytical Heston IV approximation |
| `calibrate_heston(market_surface,S,r,x0)` | L-BFGS calibration to market surface |
| `dupire_local_vol(surface_df,S,r)` | Local volatility via Dupire formula |

---

## References

- Black, F. & Scholes, M. — *The Pricing of Options and Corporate Liabilities* (1973)
- Heston, S. — *A Closed-Form Solution for Options with Stochastic Volatility* (1993)
- Dupire, B. — *Pricing with a Smile* (1994)
- Derman, E. & Kani, I. — *Riding on a Smile* (1994)
- Gatheral, J. — *The Volatility Surface: A Practitioner's Guide* (2006)
- Carr, P. & Wu, L. — *The Variance Risk Premium* (2009)

---

<div align="center">

**Niraj Neupane**
Quantitative Researcher · Financial Economist
Chartered Accountant (ICAI) · FRM Candidate

[github.com/nirajneupane17](https://github.com/nirajneupane17)

*Built with Python · NumPy · SciPy · Pandas · Matplotlib*

</div>
