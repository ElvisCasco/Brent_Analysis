"""Milestone-3 donor-importance heatmap: grayscale, white = not used (weight 0),
rows grouped by economic category (not sorted by importance). 19-donor shared pool.
Saves plots/milestone3/donor_importance_heatmap.png. Run: uv run python this.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from lib.config import DONOR_POOL_VARIANT
from lib.data import load_fit

WINDOW, VARIANT = 'preferred', DONOR_POOL_VARIANT
MODELS = ['convex_scm', 'ascm', 'elastic_net', 'xgboost', 'bayesian_ridge']
MODEL_DISPLAY = {'convex_scm': 'Convex SCM', 'ascm': 'ASCM', 'elastic_net': 'Elastic-net',
                 'xgboost': 'XGBoost', 'bayesian_ridge': 'Bayesian\nRidge'}
EVENTS = [{'name': 'Strait of Hormuz crisis', 'slug': 'hormuz'},
          {'name': 'Russia invades Ukraine', 'slug': 'russia'}]

# Rows grouped by economic category (VIX added for the 19-donor pool).
CATS = {
    'Metals':        ['Silver', 'Platinum', 'Gold'],
    'Agriculturals': ['Coffee', 'Sugar', 'LiveCattle'],
    'Equities':      ['SP500', 'Nikkei'],
    'FX':            ['AUD', 'JPY', 'CHF', 'CNY', 'INR', 'KRW', 'ZAR', 'MXN'],
    'Rates/credit':  ['TLT', 'HYG'],
    'Volatility':    ['VIX'],
}

ordered, bounds, blocks = [], [], []
for cat, mem in CATS.items():
    if ordered:
        bounds.append(len(ordered))
    start = len(ordered)
    ordered.extend(mem)
    blocks.append((cat, start, len(ordered)))


def importance(fit):
    w = fit['weights'].reindex(ordered).fillna(0).abs()
    t = w.sum()
    return (w / t if t > 0 else w).values


mats = {}
for ev in EVENTS:
    M = np.zeros((len(ordered), len(MODELS)))
    for j, m in enumerate(MODELS):
        f = load_fit(ev['slug'], WINDOW, m, variant=VARIANT)
        if f is not None:
            M[:, j] = importance(f)
    mats[ev['slug']] = M
vmax = max(M.max() for M in mats.values())

# Sequential blue for used donors (truncated so the smallest used value is clearly
# blue, not near-white); zeros masked -> flat light gray = "not used".
cmap = LinearSegmentedColormap.from_list('b', plt.cm.Blues(np.linspace(0.22, 1.0, 256)))
cmap.set_bad('#e0e0e0')

fig, axes = plt.subplots(1, 2, figsize=(14, 9))
# Colorbar lives along the BOTTOM, so the panels can use the full width.
fig.subplots_adjust(left=0.075, right=0.985, top=0.95, bottom=0.13, wspace=0.05)
im = None
for ax, ev in zip(axes, EVENTS):
    M = mats[ev['slug']]
    Mm = np.ma.masked_where(M == 0, M)
    im = ax.imshow(Mm, cmap=cmap, aspect='auto', vmin=0, vmax=vmax)

    # light grid so cells (incl. gray 'not used') read as discrete boxes
    ax.set_xticks(np.arange(-.5, len(MODELS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(ordered), 1), minor=True)
    ax.grid(which='minor', color='#c8c8c8', linewidth=0.6)
    ax.tick_params(which='minor', length=0)

    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([MODEL_DISPLAY[m] for m in MODELS], fontsize=10.5)
    ax.set_yticks(range(len(ordered)))
    ax.set_yticklabels(ordered if ax is axes[0] else [], fontsize=10)

    for b in bounds:                                  # category separators
        ax.axhline(b - 0.5, color='black', linewidth=1.1)
    for i in range(len(ordered)):                     # value labels for used cells
        for j in range(len(MODELS)):
            v = M[i, j]
            if v > 0.04:
                ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=8.5,
                        color='white' if v > 0.55 * vmax else 'black')
    ax.set_title(ev['name'], fontsize=14, pad=8)
    for sp in ax.spines.values():
        sp.set_visible(False)

# category labels down the far left (abbreviated so they fit short blocks without overlap)
CAT_ABBR = {'Metals': 'Metals', 'Agriculturals': 'Agric.', 'Equities': 'Equity',
            'FX': 'FX', 'Rates/credit': 'Rates', 'Volatility': 'Vol.'}
for cat, s, e in blocks:
    axes[0].text(-1.15, (s + e - 1) / 2, CAT_ABBR[cat], rotation=90, va='center', ha='center',
                 fontsize=9, fontweight='bold', color='#555', clip_on=False)

# Horizontal colorbar along the bottom (frees the full width for the panels).
cax = fig.add_axes([0.30, 0.06, 0.34, 0.018])
cbar = fig.colorbar(im, cax=cax, orientation='horizontal')
cbar.set_label('within-model importance share', fontsize=10.5)
cbar.ax.tick_params(labelsize=9)
# 'not used' key on the bottom row, to the right of the colorbar.
fig.legend(handles=[Patch(facecolor='#e0e0e0', edgecolor='#c8c8c8', label='not used (weight 0)')],
           loc='center left', bbox_to_anchor=(0.70, 0.075), fontsize=10.5, frameon=False)
out = ROOT / 'plots' / 'milestone3' / 'donor_importance_heatmap.png'
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=200, bbox_inches='tight')
print('saved', out)
