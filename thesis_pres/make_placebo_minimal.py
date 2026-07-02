"""Minimalist in-space placebo figure for the presentation (dark slide).
Hormuz, convex SCM: each donor's post/pre RMSPE ratio, Brent highlighted,
with the top few placebo units labelled horizontally below their bars.
Reads data/validation/inference_inspace_hormuz_convex_scm.csv.

Run with the project venv:
    .venv/bin/python thesis_pres/make_placebo_minimal.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
VAL = ROOT / "data" / "validation"
OUT = Path(__file__).resolve().parent / "images" / "placebo_hormuz_minimal.png"
OUT.parent.mkdir(exist_ok=True)

BRENT = "#ffdf5e"  # Brent — bright gold (the winner)
DONOR = "#5a6b8c"  # placebo donors — muted slate
TEXT = "#f0f0f5"
MUTE = "#9aa0b5"
N_LABEL = 4  # how many of the highest-ratio units to name

# Unit name is the (unnamed) index; the post/pre ratio is the 'ratio' column.
df = pd.read_csv(VAL / "inference_inspace_hormuz_convex_scm.csv", index_col=0)

# Drop unfittable placebos: a huge pre-period RMSPE means the synthetic never
# tracked that unit, so its ratio is meaningless (e.g. Nikkei). Brent is always kept.
if "rmspe_pre" in df.columns:
    keep = (df["rmspe_pre"] < 1.0) | (df.index.str.lower() == "brent")
    df = df[keep]

# Sort ascending so the rank-1 unit (largest ratio) sits at the far right.
df = df[["ratio"]].dropna().sort_values("ratio")
names = df.index.astype(str).values
ratios = df["ratio"].astype(float).values
is_brent = np.array(["brent" in n.lower() for n in names])
colors = np.where(is_brent, BRENT, DONOR)

fig, ax = plt.subplots(figsize=(11.0, 4.6))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

xpos = np.arange(len(ratios))
ax.bar(xpos, ratios, color=colors, width=0.72, zorder=3)
ax.set_ylim(0, ratios.max() * 1.10)

# Horizontal labels BELOW the top-ranked bars, as x-axis ticks.
top_positions = sorted(np.argsort(ratios)[-N_LABEL:])
ax.set_xticks(top_positions)
ax.set_xticklabels([names[i] for i in top_positions])
for tick, i in zip(ax.get_xticklabels(), top_positions):
    is_b = is_brent[i]
    tick.set_color(BRENT if is_b else MUTE)
    tick.set_fontsize(12 if is_b else 10)
    tick.set_fontweight("bold" if is_b else "normal")

ax.set_title(
    "In-space placebo — Hormuz", color=TEXT, fontsize=15, fontweight="bold", pad=10
)
ax.set_ylabel("Post / pre RMSPE ratio", color=TEXT, fontsize=11)
ax.set_xlabel(
    "Placebo units (each donor refit as treated), sorted by ratio",
    color=MUTE,
    fontsize=10,
)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(TEXT)
    ax.spines[s].set_alpha(0.5)
ax.tick_params(axis="y", colors=TEXT, labelsize=10)
ax.tick_params(axis="x", length=0)
ax.grid(False)
ax.margins(x=0.01)

fig.text(
    0.5,
    -0.02,
    "Brent's premium stands alone against all placebos, p at the 0.050 floor.",
    ha="center",
    color=MUTE,
    fontsize=10.5,
    style="italic",
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT, transparent=True, bbox_inches="tight", dpi=200)
plt.close(fig)
print("wrote", OUT)
