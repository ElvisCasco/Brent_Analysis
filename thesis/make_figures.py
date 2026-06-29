"""Generate thesis figures from the regenerated pipeline outputs.
All figures get labelled axes, titles, and legends. Output -> thesis/figures/*.png
Run with the project venv:  .venv/Scripts/python.exe thesis/make_figures.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.data import load_brent  # noqa: E402
from lib.config import T0, PRE_WINDOWS, POST_END  # noqa: E402

FIG = Path(__file__).resolve().parent / 'figures'
FIG.mkdir(exist_ok=True)
RES = ROOT / 'data' / 'results'
VAL = ROOT / 'data' / 'validation'
MODELS = ['convex_scm', 'ascm', 'elastic_net', 'xgboost', 'bayesian_ridge']
EVTITLE = {'russia': 'Russia 2022', 'hormuz': 'Hormuz 2026'}
plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': 0.3,
                     'figure.dpi': 140, 'savefig.bbox': 'tight'})


def synth_levels(event):
    """Reconstruct each model's synthetic Brent level and the ensemble-median synthetic.
    gap_pct = 100*(actual/synth - 1)  =>  synth = actual / (1 + gap/100)."""
    brent = load_brent()['Brent']
    s, _ = PRE_WINDOWS[event]['preferred']
    e = POST_END[event]
    actual = brent.loc[s:e]
    synths = {}
    for m in MODELS:
        g = pd.read_csv(RES / event / 'preferred' / 'shared' / m / 'gap_pct.csv',
                        index_col=0, parse_dates=True)['gap_pct']
        g = g.reindex(actual.index)
        synths[m] = actual / (1 + g / 100.0)
    synth_df = pd.DataFrame(synths)
    ens = synth_df.median(axis=1)
    return actual, synth_df, ens


# ---------- Figure 1: Brent timeline with both events ----------
def fig_timeline():
    from matplotlib.patches import Patch
    brent = load_brent()['Brent'].loc['2020-01-01':]
    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    ax.plot(brent.index, brent.values, color='black', lw=1.0, label='Brent spot (EIA RBRTEd)')
    trans = ax.get_xaxis_transform()  # x in data coords, y in axes fraction

    # Shade each event's pre-window and post-window (preferred specification).
    for k, ev in enumerate([('russia'), ('hormuz')]):
        s, t0 = PRE_WINDOWS[ev]['preferred'][0], pd.Timestamp(T0[ev])
        ax.axvspan(pd.Timestamp(s), t0, color='steelblue', alpha=0.10,
                   label='Pre-window' if k == 0 else None)
        ax.axvspan(t0, pd.Timestamp(POST_END[ev]), color='firebrick', alpha=0.10,
                   label='Post-window' if k == 0 else None)

    # All curated events in the plotted window get a letter marker (a, b, ...); the
    # letter -> event key lives in the figure notes, not on the plot.
    ev_csv = ROOT / 'data' / 'historical_events.csv'
    focal_dates = {pd.Timestamp(T0['russia']), pd.Timestamp(T0['hormuz'])}
    events = pd.read_csv(ev_csv, parse_dates=['date'])
    events = events[(events['date'] >= brent.index.min()) &
                    (events['date'] <= brent.index.max())].sort_values('date')
    letters = 'abcdefghijklmnopqrstuvwxyz'
    yrow = [0.93, 0.84]  # stagger letters so the spring-2020 cluster stays legible
    for i, (_, r) in enumerate(events.iterrows()):
        focal = r['date'] in focal_dates
        col = 'firebrick' if r['date'] == pd.Timestamp(T0['russia']) else \
              'navy' if r['date'] == pd.Timestamp(T0['hormuz']) else 'grey'
        ax.axvline(r['date'], color=col, ls='--' if focal else ':',
                   lw=1.4 if focal else 0.8, alpha=1.0 if focal else 0.7)
        ax.text(r['date'], yrow[i % len(yrow)], letters[i], transform=trans,
                ha='center', va='center', fontsize=8,
                fontweight='bold' if focal else 'normal', color=col,
                bbox=dict(boxstyle='circle,pad=0.15', fc='white', ec=col, lw=0.7))
    ax.set_xlabel('Date')
    ax.set_ylabel('Brent spot price (USD / barrel)')
    ax.set_ylim(0, brent.max() * 1.08)
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0, 1, 0.12), mode='expand',
              ncol=3, frameon=False, fontsize=8)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.savefig(FIG / 'brent_timeline.png')
    plt.close(fig)


# ---------- Figure 2: counterfactual paths (both events, side by side) ----------
def fig_paths():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))
    for ax, ev in zip(axes, ['russia', 'hormuz']):
        actual, synth_df, ens = synth_levels(ev)
        t0 = T0[ev]
        # individual model synthetics (thin grey)
        for m in MODELS:
            ax.plot(synth_df.index, synth_df[m].values, color='grey', lw=0.6, alpha=0.5)
        ax.plot(actual.index, actual.values, color='black', lw=1.6, label='Actual Brent')
        ax.plot(ens.index, ens.values, color='C0', lw=1.6, label='Synthetic (ensemble median)')
        # shade post-event gap
        post = actual.index >= t0
        ax.fill_between(actual.index[post], ens[post].values, actual[post].values,
                        color='C0', alpha=0.18, label='Estimated premium')
        ax.axvline(t0, color='firebrick', ls='--', lw=1.0)
        ax.set_title(f'{EVTITLE[ev]}  ($T_0$={t0.date()})')
        ax.set_xlabel('Date')
        ax.set_ylabel('Brent price (USD / barrel)')
        ax.legend(loc='upper left', frameon=False, fontsize=8)
        for lab in ax.get_xticklabels():
            lab.set_rotation(30); lab.set_ha('right')
    fig.savefig(FIG / 'counterfactual_paths.png')
    plt.close(fig)


# ---------- Figure 3: post-window horizon sensitivity ----------
def fig_sensitivity():
    df = pd.read_csv(VAL / 'final_postwindow_sensitivity.csv')
    order = ['1m', '2m', '3m', '6m', 'full']
    pos = {h: i for i, h in enumerate(order)}   # fixed x-position per horizon, shared by both events
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for ev, col, mark in [('russia', 'firebrick', 'o'), ('hormuz', 'navy', 's')]:
        sub = df[df['event'] == ev].set_index('horizon').reindex(order).dropna(subset=['ens_median_gap_pct'])
        x = [pos[h] for h in sub.index]
        ax.plot(x, sub['ens_median_gap_pct'].values, color=col, marker=mark, label=EVTITLE[ev])
        ax.fill_between(x, sub['iqr_lo'].values, sub['iqr_hi'].values, color=col, alpha=0.15)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order)
    ax.axhline(0, color='grey', lw=0.8, ls=':')
    ax.set_xlabel('Post-event horizon')
    ax.set_ylabel('Ensemble-median gap (%)')
    ax.legend(frameon=False)
    fig.savefig(FIG / 'postwindow_sensitivity.png')
    plt.close(fig)


# ---------- Figure 4: in-space placebo (Hormuz, convex) gap distribution ----------
def fig_placebo():
    f = VAL / 'inference_inspace_hormuz_convex_scm.csv'
    if not f.exists():
        return
    df = pd.read_csv(f, index_col=0)
    df = df.sort_values('ratio')
    is_brent = df.index.astype(str).str.contains('Brent', case=False)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    colors = ['firebrick' if b else 'grey' for b in is_brent]
    ax.bar(range(len(df)), df['ratio'].values, color=colors)
    ax.set_xlabel('Placebo units (donors) and Brent, sorted by post/pre RMSPE ratio')
    ax.set_ylabel('Post/pre RMSPE ratio')
    ax.set_xticks([])
    fig.savefig(FIG / 'placebo_hormuz.png')
    plt.close(fig)


if __name__ == '__main__':
    fig_timeline()
    fig_paths()
    fig_sensitivity()
    fig_placebo()
    print('figures written to', FIG)
    for p in sorted(FIG.glob('*.png')):
        print('  ', p.name)
