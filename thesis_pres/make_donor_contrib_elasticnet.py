"""Elastic-net donor-contribution decomposition for both events.

The elastic net fits log-Brent as  intercept + sum_j beta_j * log(donor_j).
Relative to each series' pre-event mean the intercept cancels, so each donor's
contribution to the counterfactual over the post window is

    C_j = beta_j * ( mean_post(log P_j) - mean_pre(log P_j) )   [log points ~ %]
          ^weight   ^average post-window divergence

i.e. NOT the weight alone -- it is the weight times how far the donor moved
after the event. Its contribution to the PREMIUM (= observed - counterfactual)
is -C_j: a donor with a negative weight that rises post-event pushes the
counterfactual down and thereby widens the premium.

Run with the project venv:
    .venv/Scripts/python.exe thesis_pres/make_donor_contrib_elasticnet.py
"""
import sys
import pickle
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.data import build_panel  # noqa: E402

EVENTS = [('russia', 'Russia 2022'), ('hormuz', 'Hormuz 2026')]
OUT = Path(__file__).resolve().parent / 'images' / 'donor_contrib_elasticnet.png'
OUT.parent.mkdir(exist_ok=True)

WIDEN = '#ffd166'   # yellow — widens the premium
NARROW = '#ff6b6b'  # red    — narrows the premium
BRENT = '#f0f0f5'   # white  — Brent's own move (the thing being explained)
TOTAL = '#ffb703'   # solid gold — the resulting premium
TEXT = '#f0f0f5'
SMALL_CUT = 1.0     # bucket donors smaller than this (pp) into "Other donors"


def premium_contributions(event):
    """Return a signed Series (pct points) of each active donor's contribution
    to the premium, plus Brent's own post-window move and the reported premium."""
    log_panel, meta = build_panel(event, 'preferred', 'shared')
    fit_path = ROOT / 'data' / 'results' / event / 'preferred' / 'shared' / 'elastic_net' / 'fit.pkl'
    with open(fit_path, 'rb') as f:
        fit = pickle.load(f)
    w = fit['weights']                    # pd.Series indexed by donor name
    t0 = meta['t0']
    pre, post = log_panel.index < t0, log_panel.index >= t0

    dlog = log_panel[list(w.index)].loc[post].mean() - log_panel[list(w.index)].loc[pre].mean()
    C = w * dlog                          # contribution to counterfactual (log pts)
    contrib = (-C) * 100.0                # contribution to premium (pct points)
    contrib = contrib[w.abs() > 1e-3].sort_values()

    brent_move = (log_panel['Brent'].loc[post].mean()
                  - log_panel['Brent'].loc[pre].mean()) * 100.0
    return contrib, brent_move


def waterfall_rows(contrib, brent_move):
    """Build waterfall steps: Brent's own move, then donor steps (small ones
    bucketed), ending in the resulting premium. Returns rows + the premium."""
    big = contrib[contrib.abs() >= SMALL_CUT].sort_values(ascending=False)
    small = contrib[contrib.abs() < SMALL_CUT]

    steps = [('Brent (own move)', brent_move, BRENT)]
    for name, v in big.items():
        steps.append((name, v, WIDEN if v >= 0 else NARROW))
    if len(small):
        s = small.sum()
        steps.append(('Other donors', s, WIDEN if s >= 0 else NARROW))

    rows, cum = [], 0.0
    for name, delta, color in steps:
        rows.append((name, cum, cum + delta, color))
        cum += delta
    premium_log = cum
    rows.append(('Premium', 0.0, premium_log, TOTAL))
    return rows, premium_log


fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
fig.patch.set_alpha(0)

for ax, (event, title) in zip(axes, EVENTS):
    contrib, brent_move = premium_contributions(event)
    rows, premium_log = waterfall_rows(contrib, brent_move)
    premium_pct = (np.exp(premium_log / 100.0) - 1.0) * 100.0
    print(f'{title}: premium ~ {premium_pct:.1f}%  (Brent move {brent_move:+.1f}, '
          f'donors {contrib.sum():+.1f})')

    ax.patch.set_alpha(0)
    n = len(rows)
    ypos = np.arange(n)[::-1]                 # first row at top
    span = max(abs(v) for _, s, e, _ in rows for v in (s, e))

    for y, (name, start, end, color) in zip(ypos, rows):
        left, width = min(start, end), abs(end - start)
        ax.barh(y, width, left=left, color=color, height=0.6, zorder=3)
        # connector to the next step's baseline
        if name != 'Premium':
            ax.plot([end, end], [y - 0.5, y - 1 + 0.2], color=TEXT, lw=0.6,
                    alpha=0.35, zorder=1)
        # Every label is in log points so the bars literally add up to the
        # Premium bar; the Premium also shows its price-% conversion in ().
        if name == 'Premium':
            lab = f'{premium_log:+.1f} lp  (≈ {premium_pct:.0f}%)'
        else:
            lab = f'{end - start:+.1f}'
        xr = max(start, end)
        ax.text(xr + 0.015 * span, y, lab, va='center', ha='left',
                color=TEXT, fontsize=11,
                fontweight='bold' if name in ('Brent (own move)', 'Premium') else 'normal')

    ax.axvline(0, color=TEXT, lw=1.0, alpha=0.5, zorder=2)
    ax.set_yticks(ypos)
    ax.set_yticklabels([r[0] for r in rows], color=TEXT, fontsize=12)
    # emphasise the two anchor rows
    for tick, (name, *_ ) in zip(ax.get_yticklabels(), rows):
        if name in ('Brent (own move)', 'Premium'):
            tick.set_fontweight('bold')
    ax.set_title(title, color=TEXT, fontsize=15, fontweight='bold', pad=8)

    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(TEXT)
    ax.spines['bottom'].set_alpha(0.4)
    ax.tick_params(axis='x', colors=TEXT, labelsize=10)
    ax.tick_params(axis='y', length=0)
    ax.grid(False)
    ax.set_xlim(min(0, min(min(s, e) for _, s, e, _ in rows)) - 0.10 * span,
                span * 1.14)
    ax.margins(y=0.06)

fig.text(0.5, -0.01,
         "Premium  =  Brent's own post-event move  +  donor contributions "
         "(weight × avg post-window divergence)",
         ha='center', color=TEXT, fontsize=12)
fig.text(0.5, -0.06,
         "All bars in log points and add up exactly to the Premium bar "
         "(shown with its price-% conversion in brackets).",
         ha='center', color='#9aa0b5', fontsize=10, style='italic')
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT, transparent=True, bbox_inches='tight', dpi=200)
plt.close(fig)
print('wrote', OUT)
