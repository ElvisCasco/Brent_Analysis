"""Minimalist naive-baseline figure for the presentation (dark slide).
SCM ensemble median vs donor-free univariate counterfactuals, full-window gap.
Reads data/validation/naive_baseline_comparison.csv.

Run with the project venv:
    .venv/bin/python thesis_pres/make_naive_minimal.py
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
OUT = Path(__file__).resolve().parent / "images" / "naive_baselines_minimal.png"
OUT.parent.mkdir(exist_ok=True)

SCM = "#ffdf5e"  # SCM — bright gold (the hero)
NAIVE = "#ff6b6b"  # naive baselines — red
TEXT = "#f0f0f5"
MUTE = "#9aa0b5"
EVTITLE = {"russia": "Russia 2022", "hormuz": "Hormuz 2026"}

df = pd.read_csv(VAL / "naive_baseline_comparison.csv")
full = df[df["horizon"] == "full"].set_index("event")

# Bars: SCM first (gold), then the donor-free naive counterfactuals (red).
BARS = [
    ("scm_median", "SCM\n(ours)", SCM),
    ("rw_flat", "Random\nwalk", NAIVE),
    ("rw_drift", "RW +\ndrift", NAIVE),
    ("lin_trend", "Linear\ntrend", NAIVE),
]

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.7))
fig.patch.set_alpha(0)

for ax, ev in zip(axes, ["russia", "hormuz"]):
    ax.patch.set_alpha(0)
    row = full.loc[ev]
    vals = [row[c] for c, _, _ in BARS]
    labels = [lab for _, lab, _ in BARS]
    colors = [col for _, _, col in BARS]
    xpos = np.arange(len(vals))

    ax.bar(xpos, vals, color=colors, width=0.68, zorder=3)
    ax.axhline(0, color=TEXT, lw=1.0, alpha=0.5, zorder=2)

    for x, v in zip(xpos, vals):
        ax.text(
            x,
            v + (2.5 if v >= 0 else -2.5),
            f"{v:.0f}%",
            ha="center",
            va="bottom" if v >= 0 else "top",
            color=TEXT,
            fontsize=11,
            fontweight="bold",
        )

    ax.set_title(EVTITLE[ev], color=TEXT, fontsize=15, fontweight="bold", pad=10)
    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, color=TEXT, fontsize=10.5)
    ax.set_ylim(min(0, min(vals)) - 12, max(vals) + 12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(TEXT)
        ax.spines[s].set_alpha(0.5)
    ax.tick_params(axis="y", colors=TEXT, labelsize=9)
    ax.tick_params(axis="x", length=0)
    ax.grid(False)

axes[0].set_ylabel("Full-window premium (%)", color=TEXT, fontsize=11)
fig.text(
    0.5,
    -0.02,
    "The naive trend flips sign across events; the SCM does not.",
    ha="center",
    color=MUTE,
    fontsize=10.5,
    style="italic",
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT, transparent=True, bbox_inches="tight", dpi=200)
plt.close(fig)
print("wrote", OUT)
