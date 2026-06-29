"""Donor contribution analysis for the SCM ensemble (Chapter 6 support).

Produces, for the 19-donor shared pool and both focal events:
  1. docs/figures/donor_importance_heatmap.png  -- normalized |weight| per model,
     category-grouped, two panels (Russia, Hormuz). Same construction as the
     milestone heatmap (lib fit pickles -> abs -> per-model normalize).
  2. docs/data/donor_contribution_metrics.csv   -- per donor, per event:
       w_mean   consensus importance (mean normalized |weight| across the 4 linear
                + tree models; Bayesian ridge excluded -- its "weights" are
                standardized coefficients, not comparable; see thesis App. B)
       w_disp   across-model dispersion of normalized |weight| (model disagreement)
       rho_lvl  pre-window corr(log Brent, log donor)      -> TREND co-movement
       rho_ret  pre-window corr(dlog Brent, dlog donor)    -> VARIANCE co-movement
       post_div standardized idiosyncratic post-window move of the donor relative
                to a leave-one-out common factor (Brent-free) -> post-treatment
                divergence / possible contamination by another event

All three diagnostics are descriptive, not causal. Run from repo root with the venv.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.data import load_brent, load_donors, load_fit          # noqa: E402
from lib.config import PRE_WINDOWS, POST_END, T0, DONOR_POOL_VARIANT  # noqa: E402

FIGDIR = ROOT / 'docs' / 'figures'; FIGDIR.mkdir(parents=True, exist_ok=True)
OUTDIR = ROOT / 'docs' / 'data'; OUTDIR.mkdir(parents=True, exist_ok=True)

MODELS = ['convex_scm', 'ascm', 'elastic_net', 'xgboost', 'bayesian_ridge']
MODEL_DISP = {'convex_scm': 'Convex SCM', 'ascm': 'ASCM', 'elastic_net': 'Elastic-net',
              'xgboost': 'XGBoost', 'bayesian_ridge': 'Bayesian\nRidge'}
# consensus excludes bayesian_ridge (incomparable importances)
CONSENSUS_MODELS = ['convex_scm', 'ascm', 'elastic_net', 'xgboost']
CATS = {'Metals': ['Silver', 'Platinum', 'Gold'],
        'Agriculturals': ['Coffee', 'Sugar', 'LiveCattle'],
        'Equities': ['SP500', 'Nikkei'],
        'FX': ['AUD', 'JPY', 'CHF', 'CNY', 'INR', 'KRW', 'ZAR', 'MXN'],
        'Rates/credit': ['TLT', 'HYG'],
        'Volatility': ['VIX']}
POOL = [d for mem in CATS.values() for d in mem]            # 19 donors, grouped
EVENTS = [('russia', 'Russia 2022'), ('hormuz', 'Hormuz 2026')]


def norm_imp(fit):
    w = fit['weights'].reindex(POOL).fillna(0).abs()
    t = w.sum()
    return (w / t) if t > 0 else w


# ---------------- importance matrices + heatmap ----------------
imp = {}  # event -> DataFrame (donor x model) normalized |weight|
for ev, _ in EVENTS:
    M = pd.DataFrame(index=POOL, columns=MODELS, dtype=float)
    for m in MODELS:
        f = load_fit(ev, 'preferred', m, variant=DONOR_POOL_VARIANT)
        M[m] = norm_imp(f) if f is not None else 0.0
    imp[ev] = M.fillna(0.0)

vmax = max(imp[ev].values.max() for ev, _ in EVENTS)
bounds = np.cumsum([len(m) for m in CATS.values()])[:-1]
cmap = LinearSegmentedColormap.from_list('b', plt.cm.Blues(np.linspace(0.22, 1.0, 256)))
cmap.set_bad('#e0e0e0')

fig, axes = plt.subplots(1, 2, figsize=(12, 8))
fig.subplots_adjust(left=0.12, right=0.99, top=0.92, bottom=0.10, wspace=0.06)
im = None
for ax, (ev, title) in zip(axes, EVENTS):
    M = imp[ev].values.astype(float)
    Mm = np.ma.masked_where(M == 0, M)
    im = ax.imshow(Mm, cmap=cmap, aspect='auto', vmin=0, vmax=vmax)
    ax.set_xticks(np.arange(-.5, len(MODELS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(POOL), 1), minor=True)
    ax.grid(which='minor', color='#c8c8c8', linewidth=0.6); ax.tick_params(which='minor', length=0)
    ax.set_xticks(range(len(MODELS))); ax.set_xticklabels([MODEL_DISP[m] for m in MODELS], fontsize=10)
    ax.set_yticks(range(len(POOL)))
    ax.set_yticklabels(POOL if ax is axes[0] else [], fontsize=9.5)
    for b in bounds:
        ax.axhline(b - .5, color='black', lw=1.1)
    ax.set_title(title, fontsize=12)
cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02)
cb.set_label('normalized |weight| (per model)', fontsize=9)
fig.savefig(FIGDIR / 'donor_importance_heatmap.png', dpi=140, bbox_inches='tight')
plt.close(fig)
print('wrote', FIGDIR / 'donor_importance_heatmap.png')

# ---------------- per-donor diagnostics ----------------
brent = load_brent()['Brent'].astype(float)
donors = load_donors()
rows = []
for ev, _ in EVENTS:
    s, e_pre = PRE_WINDOWS[ev]['preferred']
    e_post = POST_END[ev]
    t0 = T0[ev]
    # align on common dates within full sample
    sub = pd.concat([brent.rename('Brent'), donors[POOL]], axis=1).loc[s:e_post].dropna()
    pre = sub.loc[s:t0]
    post = sub.loc[t0:e_post]
    lb = np.log(pre['Brent'])
    rb = np.log(pre['Brent']).diff().dropna()
    # leave-one-out common factor on pre-window log-returns (standardized)
    pool_ret = np.log(pre[POOL]).diff().dropna()
    z = (pool_ret - pool_ret.mean()) / pool_ret.std(ddof=0)
    post_ret = np.log(post[POOL]).diff().dropna()
    zp = (post_ret - pool_ret.mean()) / pool_ret.std(ddof=0)   # standardize by PRE stats
    for d in POOL:
        ld = np.log(pre[d]); rd = np.log(pre[d]).diff().dropna()
        rho_lvl = np.corrcoef(lb, ld)[0, 1]
        idx = rb.index.intersection(rd.index)
        rho_ret = np.corrcoef(rb.loc[idx], rd.loc[idx])[0, 1]
        # leave-one-out factor = mean of other donors' standardized returns
        others = [c for c in POOL if c != d]
        f_pre = z[others].mean(axis=1)
        f_post = zp[others].mean(axis=1)
        # beta of donor (standardized) on factor, pre-window
        zd_pre = z[d].loc[f_pre.index]
        beta = np.cov(zd_pre, f_pre)[0, 1] / np.var(f_pre)
        # post-window idiosyncratic residual (own move not explained by common factor)
        zd_post = zp[d].loc[f_post.index]
        resid = zd_post - beta * f_post
        post_div = resid.sum() / np.sqrt(len(resid))   # standardized cumulative idiosyncratic move
        w = imp[ev].loc[d, CONSENSUS_MODELS].astype(float)
        rows.append(dict(event=ev, donor=d, w_mean=w.mean(), w_disp=w.std(ddof=0),
                         rho_lvl=rho_lvl, rho_ret=rho_ret, post_div=post_div))

met = pd.DataFrame(rows)
met.to_csv(OUTDIR / 'donor_contribution_metrics.csv', index=False)
print('wrote', OUTDIR / 'donor_contribution_metrics.csv')

# ---------------- printed summary for the writeup ----------------
pd.set_option('display.width', 200, 'display.max_rows', 100,
              'display.float_format', lambda x: f'{x:.3f}')
for ev, title in EVENTS:
    m = met[met.event == ev].set_index('donor').drop(columns='event')
    m = m.reindex(POOL)
    print(f'\n===== {title} =====')
    print(m.to_string())
