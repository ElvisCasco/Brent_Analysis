"""Naive-vs-SCM counterfactual PATHS (line chart) for the presentation (dark slide).
Observed Brent, SCM synthetic, random-walk-flat, and linear-trend counterfactuals,
both events. Reads the fits via synth_levels + rebuilds the two naive lines on log-Brent.

Run with the project venv:
    .venv/bin/python thesis_pres/make_naive_paths_minimal.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "thesis"))
from lib.config import T0  # noqa: E402
from make_figures import synth_levels, EVTITLE  # noqa: E402

OUT = Path(__file__).resolve().parent / "images" / "naive_paths_minimal.png"
OUT.parent.mkdir(exist_ok=True)

ACTUAL = "#f0f0f5"  # observed Brent — white
SCM = "#ff6b6b"  # SCM synthetic — red
RW = "#7ab8ff"  # random walk — blue
TREND = "#a0e0a0"  # linear trend — green
TEXT = "#f0f0f5"
MUTE = "#9aa0b5"


def naive_lines(actual_log, t0):
    """Random-walk-flat and linear-trend counterfactuals on log-Brent, post-window."""
    pre = actual_log[actual_log.index < t0]
    post_idx = actual_log.index[actual_log.index >= t0]
    n_pre, n_post = len(pre), len(post_idx)
    rw = pd.Series(pre.iloc[-1], index=post_idx)
    slope, intercept = np.polyfit(np.arange(n_pre), pre.values, 1)
    trend = pd.Series(
        intercept + slope * np.arange(n_pre, n_pre + n_post), index=post_idx
    )
    return np.exp(rw), np.exp(trend)


fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
fig.patch.set_alpha(0)

for ax, ev in zip(axes, ["russia", "hormuz"]):
    actual, synth_df, ens = synth_levels(ev)  # levels (USD)
    t0 = T0[ev]
    actual_log = np.log(actual)
    rw, trend = naive_lines(actual_log, t0)
    post = actual.index >= t0

    ax.patch.set_alpha(0)
    ax.plot(
        actual.index,
        actual.values,
        color=ACTUAL,
        lw=1.9,
        zorder=5,
        label="Observed Brent",
    )
    ax.plot(
        ens.index[post],
        ens[post].values,
        color=SCM,
        lw=1.9,
        zorder=4,
        label="SCM synthetic",
    )
    ax.plot(
        rw.index,
        rw.values,
        color=RW,
        lw=1.5,
        ls=(0, (5, 3)),
        zorder=3,
        label="Random walk",
    )
    ax.plot(
        trend.index,
        trend.values,
        color=TREND,
        lw=1.5,
        ls=(0, (2, 2)),
        zorder=3,
        label="Linear trend",
    )
    ax.axvline(t0, color=MUTE, ls=(0, (4, 4)), lw=1.0, alpha=0.55, zorder=0)
    ax.set_title(EVTITLE[ev], color=TEXT, fontsize=14, fontweight="bold", pad=8)

    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(TEXT)
        ax.spines[s].set_alpha(0.5)
    ax.tick_params(axis="both", colors=TEXT, labelsize=9)
    ax.grid(False)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(ax.xaxis.get_major_locator())
    )

axes[0].set_ylabel("Brent (USD / bbl)", color=TEXT, fontsize=10)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="lower center",
    ncol=4,
    frameon=False,
    fontsize=9.5,
    labelcolor=TEXT,
    bbox_to_anchor=(0.5, -0.04),
)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT, transparent=True, bbox_inches="tight", dpi=200)
plt.close(fig)
print("wrote", OUT)
