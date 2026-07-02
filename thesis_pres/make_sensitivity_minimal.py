"""Minimalist post-window horizon-sensitivity figure for the presentation (dark slide).
Ensemble-median gap by horizon, both events, with the IQR band.
Reads data/validation/final_postwindow_sensitivity.csv.

Run with the project venv:
    .venv/bin/python thesis_pres/make_sensitivity_minimal.py
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
OUT = Path(__file__).resolve().parent / "images" / "postwindow_sensitivity_minimal.png"
OUT.parent.mkdir(exist_ok=True)

RUSSIA = "#ff6b6b"  # red
HORMUZ = "#ffdf5e"  # gold
TEXT = "#f0f0f5"
MUTE = "#9aa0b5"
EVSTYLE = {
    "russia": (RUSSIA, "o", "Russia 2022"),
    "hormuz": (HORMUZ, "s", "Hormuz 2026"),
}

df = pd.read_csv(VAL / "final_postwindow_sensitivity.csv")

fig, ax = plt.subplots(figsize=(10.5, 4.7))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Map each horizon label to an actual month number for the x-axis.
# 'full' differs by event: Russia ~7 months, Hormuz ~3.5.
FULL_MONTHS = {"russia": 7, "hormuz": 3.5}
HZ_MONTHS = {"1m": 1, "2m": 2, "3m": 3, "6m": 6}

for ev, (col, mark, lab) in EVSTYLE.items():
    sub = df[df["event"] == ev].copy()
    # x = actual months; 'full' becomes that event's full-window length
    xmonths = [
        FULL_MONTHS[ev] if h == "full" else HZ_MONTHS.get(h, float("nan"))
        for h in sub["horizon"]
    ]
    y = sub["ens_median_gap_pct"].values
    ax.plot(
        xmonths, y, color=col, marker=mark, lw=2.2, markersize=8, label=lab, zorder=3
    )
    if {"iqr_lo", "iqr_hi"}.issubset(sub.columns):
        ax.fill_between(
            xmonths,
            sub["iqr_lo"].values,
            sub["iqr_hi"].values,
            color=col,
            alpha=0.14,
            lw=0,
            zorder=1,
        )

# Tick at each whole month present in the data, labelled with 'mo'.
all_months = sorted({FULL_MONTHS[e] for e in EVSTYLE} | set(HZ_MONTHS.values()))
ax.set_xticks(all_months)
ax.set_xticklabels([f"{m:g} mo" for m in all_months], color=TEXT, fontsize=11)

ax.set_title(
    "Premium by post-event horizon", color=TEXT, fontsize=15, fontweight="bold", pad=10
)
ax.set_ylabel("Ensemble-median premium (%)", color=TEXT, fontsize=11)
ax.set_xlabel("Post-event horizon", color=TEXT, fontsize=11)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(TEXT)
    ax.spines[s].set_alpha(0.5)
ax.tick_params(axis="both", colors=TEXT, labelsize=10)
ax.grid(False)
ax.legend(frameon=False, fontsize=11, labelcolor=TEXT, loc="center right")

fig.text(
    0.5,
    -0.02,
    "Hormuz builds in and holds; Russia attenuates — opposite directions, so not an artefact.",
    ha="center",
    color=MUTE,
    fontsize=10.5,
    style="italic",
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT, transparent=True, bbox_inches="tight", dpi=200)
plt.close(fig)
print("wrote", OUT)
