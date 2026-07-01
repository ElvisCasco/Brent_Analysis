"""Minimalist counterfactual-paths figure for the presentation.
Transparent background, no per-model grey lines. Shows observed Brent, the
ensemble-median synthetic counterfactual, and a shaded cross-model IQR band
(Q25-Q75) over the post-event window. Styled for the dark #1a1a2e slide.

Run with the project venv:
    .venv/Scripts/python.exe thesis_pres/make_paths_minimal.py
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
from lib.config import T0, PRE_WINDOWS, POST_END  # noqa: E402

# Reuse the reconstruction helper from the thesis figure script.
sys.path.insert(0, str(ROOT / 'thesis'))
from make_figures import synth_levels, EVTITLE     # noqa: E402

OUT = Path(__file__).resolve().parent / 'images' / 'counterfactual_paths_minimal.png'
OUT.parent.mkdir(exist_ok=True)

# Palette tuned for a dark slide — the slide's highlight colours.
ACTUAL  = '#f0f0f5'   # observed Brent — bright white
SYNTH   = '#ff6b6b'   # ensemble-median counterfactual — red
BAND    = '#ff6b6b'   # IQR band — same red, translucent
PREMIUM = '#ffdf5e'   # premium (gap) — bright yellow (stays yellow on navy)
TEXT    = '#f0f0f5'
MUTE    = '#9aa0b5'

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.7))
fig.patch.set_alpha(0)

for ax, ev in zip(axes, ['russia', 'hormuz']):
    actual, synth_df, ens = synth_levels(ev)
    t0 = T0[ev]
    post = actual.index >= t0
    lo = synth_df.quantile(0.25, axis=1)   # cross-model IQR
    hi = synth_df.quantile(0.75, axis=1)

    ax.patch.set_alpha(0)

    # Cross-model IQR band around the synthetic, post-event only. Kept faint and
    # drawn first, with thin edge lines so it still reads as a band under the fill.
    ax.fill_between(actual.index[post], lo[post].values, hi[post].values,
                    color=BAND, alpha=0.16, lw=0, zorder=1,
                    label='Counterfactual IQR (across models)')
    ax.plot(actual.index[post], lo[post].values, color=BAND, lw=0.7, alpha=0.5, zorder=1)
    ax.plot(actual.index[post], hi[post].values, color=BAND, lw=0.7, alpha=0.5, zorder=1)
    # Premium: the gap between observed and the counterfactual, post-event only.
    # High opacity + bright yellow so it stays yellow on the navy slide (a faint
    # yellow over dark navy alpha-blends to olive/brown).
    ax.fill_between(actual.index[post], ens[post].values, actual[post].values,
                    color=PREMIUM, alpha=0.72, lw=0, zorder=2)
    # The two headline lines.
    ax.plot(actual.index, actual.values, color=ACTUAL, lw=1.9,
            zorder=4, label='Observed Brent')
    ax.plot(ens.index, ens.values, color=SYNTH, lw=1.9, zorder=3,
            label='Synthetic counterfactual (median)')

    # Event onset: a soft vertical guide, no hard rule.
    ax.axvline(t0, color=MUTE, ls=(0, (4, 4)), lw=1.0, alpha=0.55, zorder=0)
    ax.set_title(EVTITLE[ev], color=TEXT, fontsize=15, fontweight='bold', pad=10)

    # Minimal frame: keep left + bottom only.
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(TEXT)
        ax.spines[s].set_alpha(0.5)
    ax.grid(False)
    ax.set_xlabel('Date', color=TEXT, fontsize=11)
    ax.tick_params(axis='both', colors=TEXT, labelsize=10)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

axes[0].set_ylabel('Brent price (USD / barrel)', color=TEXT, fontsize=11)

# One shared legend, light text, above the panels.
handles, labels = axes[1].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False,
           fontsize=10.5, labelcolor=TEXT, bbox_to_anchor=(0.5, -0.02))

fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT, transparent=True, bbox_inches='tight', dpi=200)
plt.close(fig)
print('wrote', OUT)
