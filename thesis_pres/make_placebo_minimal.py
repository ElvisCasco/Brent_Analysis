"""Minimalist in-space placebo figure for the presentation (dark slide).
Hormuz, convex SCM: each donor's post/pre RMSPE ratio, Brent highlighted.
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

# Label Brent's bar.
if is_brent.any():
    bi = int(np.where(is_brent)[0][0])
    ax.text(
        bi,
        ratios[bi] + 0.15,
        "Brent",
        ha="center",
        va="bottom",
        color=BRENT,
        fontsize=13,
        fontweight="bold",
    )

ax.set_title(
    "In-space placebo — Hormuz", color=TEXT, fontsize=15, fontweight="bold", pad=10
)
ax.set_ylabel("Post / pre RMSPE ratio", color=TEXT, fontsize=11)
ax.set_xticks([])
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
