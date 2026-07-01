"""Minimalist Brent timeline for the presentation.
Transparent background, no grid, no clutter — only the two focal events
(Russia 2022, Hormuz 2026) are called out. Colours are light so it reads on
the dark #1a1a2e slide.

Run with the project venv:
    .venv/Scripts/python.exe thesis_pres/make_timeline_minimal.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.data import load_brent          # noqa: E402
from lib.config import T0                # noqa: E402

OUT = Path(__file__).resolve().parent / 'images' / 'brent_timeline_minimal.png'
OUT.parent.mkdir(exist_ok=True)

# Palette tuned for a dark slide.
LINE   = '#c9ccd6'   # muted light grey for the Brent path
RUSSIA = '#ff6b6b'   # soft red
HORMUZ = '#ffd166'   # amber / gold
TEXT   = '#f0f0f5'

brent = load_brent()['Brent'].loc['2020-01-01':]

fig, ax = plt.subplots(figsize=(10.5, 4.6))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Brent path, understated.
ax.plot(brent.index, brent.values, color=LINE, lw=1.4, alpha=0.55, zorder=1)

# Call out the two events with a dot only (no vertical rule).
EVLABEL = {'russia': 'Russian Invasion\nof Ukraine',
           'hormuz': 'Strait of Hormuz\nDisruption'}
# Anchor labels so neither runs off the frame (Russia centred, Hormuz to the left).
EVALIGN = {'russia': ('right', (-18, 14)),
           'hormuz': ('right', (-14, 26))}
for ev, colour in [('russia', RUSSIA), ('hormuz', HORMUZ)]:
    d = T0[ev]
    # nearest available price to the event date
    y = brent.iloc[brent.index.get_indexer([d], method='nearest')[0]]
    ax.scatter([d], [y], s=110, color=colour, zorder=4,
               edgecolors='#1a1a2e', linewidths=1.2)
    ha, off = EVALIGN[ev]
    ax.annotate(EVLABEL[ev], xy=(d, y), xytext=off,
                textcoords='offset points', ha=ha, va='bottom',
                color=colour, fontsize=14, fontweight='bold', linespacing=1.05)

# Keep the left and bottom axes; drop the top/right frame.
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for s in ('left', 'bottom'):
    ax.spines[s].set_color(TEXT)
    ax.spines[s].set_alpha(0.5)
ax.grid(False)
ax.set_xlabel('Year', color=TEXT, fontsize=12)
ax.set_ylabel('Brent spot price (USD / barrel)', color=TEXT, fontsize=12)
ax.tick_params(axis='both', colors=TEXT, labelsize=11)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_ylim(0, brent.max() * 1.18)
ax.margins(x=0.02)

fig.savefig(OUT, transparent=True, bbox_inches='tight', dpi=200)
plt.close(fig)
print('wrote', OUT)
