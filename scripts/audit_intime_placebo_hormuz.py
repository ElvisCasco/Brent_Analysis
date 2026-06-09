"""Audit the Hormuz in-time placebo for regional-event contamination.

Background
----------
[docs/results.md](../docs/results.md) flags a -10/-12% mean gap in the Hormuz
in-time placebo's fake-post period (2025-08-28 -> 2026-02-27) and notes it is
"consistent with (but does not require) a runup-to-Hormuz premium starting in
late 2025."

This script tests two alternative explanations:
  (a) RUSSIA contamination: Russia-Ukraine intensification inside the same
      window, contaminating the donor->Brent relationship the SCM learned.
  (b) IRAN/ISRAEL/LEVANT co-treatment: the Hormuz event itself sits inside an
      active US-Iran war, so Iran-axis events in the placebo window are best
      read as anticipatory drift from the same shock complex (NOT independent
      noise; see iran_israel_levant_events.csv header).

Method
------
1. Re-fit all 5 models with T_0_fake = 2025-08-28 (same as
   [docs/validation.md](../docs/validation.md) §5e (ii)).
2. For each fitted model, extract the *per-day* gap path inside the fake-post
   window (currently only the mean is saved in
   data/validation/inference_intime.csv).
3. Load each event source from data/external/ and tag each trading day as
   "<source>_proximate" if it falls within +/- PROXIMITY_DAYS of an event
   in that source. An additional "any_proximate" flag is the OR across
   sources.
4. Compare ensemble-median gap on proximate vs quiet days per source; overlay
   GPRD.

Interpretation rule (per source)
--------------------------------
- |mean_gap_proximate| >> |mean_gap_quiet|  -> placebo signal IS contaminated
  by that source's events; the "runup-to-Hormuz premium" interpretation
  weakens (for Russia) or strengthens (for Iran, since Iran events are
  co-treatment with the eventual Hormuz event).
- mean_gap_proximate ~= mean_gap_quiet      -> placebo signal NOT driven by
  that source.

Outputs (purely additive; no existing result is modified)
---------------------------------------------------------
- data/validation/intime_placebo_audit_hormuz.csv   per-day gap matrix + tags
  (one set of nearest-event/proximate columns per source).
- data/validation/intime_placebo_audit_summary.csv  proximate vs quiet split,
  with a `source` column repeated per (series, source) pair plus an
  aggregate `any` row.
- plots/hormuz/intime_placebo_audit.html            annotated time-series
  plot with one vline color per source.

Usage
-----
    python scripts/audit_intime_placebo_hormuz.py [--proximity-days 3]

Re-run after editing any event CSV. Rows whose `source` column contains
USER_VERIFY are treated as placeholders and dropped (with a warning).
Rows with un-parseable dates (e.g. "2025-09-XX") are also dropped.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Make `lib` importable when run as `python scripts/audit_intime_placebo_hormuz.py`
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.config import T0, T0_FAKE, MODELS, MODEL_HPARAMS, DATA, VALIDATION  # noqa: E402
from lib.data import build_panel, load_gpr  # noqa: E402
from lib.validation import in_time_placebo, get_tuned_hparams  # noqa: E402


# ---- Audit configuration (kept fixed so this audit is a deterministic re-read
# of the existing in-time placebo, not a new specification) ----
EVENT = 'hormuz'
WINDOW = 'preferred'
VARIANT = 'shared'

# Each entry: source_key -> CSV path. Source key is used as a column-name
# prefix (e.g. "russia_proximate", "iran_proximate") and as the `source`
# value in the summary table.
EVENT_SOURCES = {
    'russia': DATA / 'external' / 'russia_ukraine_events.csv',
    'iran':   DATA / 'external' / 'iran_israel_levant_events.csv',
}
# Backward-compat alias retained in case anything imports this name.
EVENTS_CSV = EVENT_SOURCES['russia']

AUDIT_CSV = VALIDATION / 'intime_placebo_audit_hormuz.csv'
SUMMARY_CSV = VALIDATION / 'intime_placebo_audit_summary.csv'
PLOT_HTML = ROOT / 'plots' / 'hormuz' / 'intime_placebo_audit.html'

# Plot vline color per source.
SOURCE_COLORS = {'russia': 'orange', 'iran': 'mediumvioletred'}


# ---------------------------------------------------------------------------
# Step 0 -- Load and clean each event list
# ---------------------------------------------------------------------------
def load_events(path, label: str) -> pd.DataFrame:
    """Load one verified event CSV; drop placeholder rows + un-parseable dates."""
    if not path.exists():
        print(f"[WARN] {label}: events file not found at {path}; treating as empty.")
        return pd.DataFrame(columns=['date', 'label', 'category', 'source', 'notes'])
    df = pd.read_csv(path, comment='#')
    # un-parseable dates (e.g. "2025-09-XX") -> NaT -> dropped
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    n_bad_dates = int(df['date'].isna().sum())
    if n_bad_dates:
        print(f"[WARN] {label}: dropping {n_bad_dates} row(s) with un-parseable date.")
        df = df.dropna(subset=['date'])
    placeholder = df['source'].astype(str).str.contains('USER_VERIFY', na=False)
    n_placeholder = int(placeholder.sum())
    if n_placeholder:
        print(f"[WARN] {label}: dropping {n_placeholder} placeholder event(s) "
              f"(source contains USER_VERIFY).")
        df = df.loc[~placeholder].copy()
    return df.sort_values('date').reset_index(drop=True)


# Backward-compat shim so any external caller still works.
def load_russia_events() -> pd.DataFrame:
    return load_events(EVENT_SOURCES['russia'], 'russia')


# ---------------------------------------------------------------------------
# Step 1 -- Re-run the in-time placebo and keep per-day gap paths
# ---------------------------------------------------------------------------
def fit_all_models(panel: pd.DataFrame, donors: list[str],
                   t0_fake: pd.Timestamp, t_pre_start: pd.Timestamp
                   ) -> dict[str, pd.Series | None]:
    """Re-run in_time_placebo for each model; return {model: gap_pct series}.

    Mirrors the loop in [notebooks/04_Inference.ipynb](../notebooks/04_Inference.ipynb)
    but keeps the full per-day gap series instead of collapsing to a mean.
    """
    out: dict[str, pd.Series | None] = {}
    for model in MODELS:
        kwargs = {**MODEL_HPARAMS.get(model, {}),
                  **get_tuned_hparams(model, EVENT, WINDOW, VARIANT)}
        try:
            r = in_time_placebo(model, panel, 'Brent', donors,
                                t0_fake=t0_fake, t_pre_start=t_pre_start, **kwargs)
            # r['gap'] is in log units (log y - log y_hat). Per-day -> percent.
            gap_pct = 100.0 * (np.exp(r['gap']) - 1.0)
            out[model] = gap_pct
            pr = r.get('pre_rmspe_log', float('nan'))
            print(f"  fitted {model:>15s}  pre-RMSPE(log)={pr:.4f}")
        except Exception as e:  # broad on purpose -- log per-model failures
            print(f"  FAILED {model:>15s}  {type(e).__name__}: {str(e)[:80]}")
            out[model] = None
    return out


# ---------------------------------------------------------------------------
# Step 2 -- Per-day audit table: stitch models + GPRD + per-source event tags
# ---------------------------------------------------------------------------
def assemble_audit_table(model_gaps: dict[str, pd.Series | None],
                         t0_fake: pd.Timestamp, t0_real: pd.Timestamp,
                         event_sources: dict[str, pd.DataFrame],
                         proximity_days: int) -> pd.DataFrame:
    """Build the per-day audit table restricted to the fake-post window.

    Columns: <one per fitted model>, ens_median, GPRD, GPRD_30d,
             nearest_<src>_event_days, nearest_<src>_event_label,
             <src>_proximate    (one set per source in event_sources),
             any_proximate      (OR across all sources).
    """
    gaps = pd.DataFrame({m: g for m, g in model_gaps.items() if g is not None})
    mask = (gaps.index >= t0_fake) & (gaps.index < t0_real)
    gaps = gaps.loc[mask].copy()
    gaps['ens_median'] = gaps.median(axis=1)

    # Descriptive GPR overlay (no causal claim, just to eyeball drivers)
    try:
        gpr = load_gpr()
        gaps = gaps.join(gpr[['GPRD', 'GPRD_30d']], how='left')
    except Exception as e:
        print(f"  [GPR overlay skipped] {e}")

    idx_dates = gaps.index.values.astype('datetime64[D]')
    prox_cols = []
    for src_key, ev_df in event_sources.items():
        days_col = f'nearest_{src_key}_event_days'
        label_col = f'nearest_{src_key}_event_label'
        flag_col = f'{src_key}_proximate'
        if len(ev_df) == 0:
            gaps[days_col] = np.nan
            gaps[label_col] = ''
            gaps[flag_col] = False
        else:
            ev_dates = ev_df['date'].values.astype('datetime64[D]')
            diff = (idx_dates[:, None] - ev_dates[None, :]).astype('timedelta64[D]').astype(int)
            nearest_idx = np.argmin(np.abs(diff), axis=1)
            nearest_days = diff[np.arange(len(idx_dates)), nearest_idx]
            gaps[days_col] = nearest_days
            gaps[label_col] = ev_df['label'].iloc[nearest_idx].values
            gaps[flag_col] = np.abs(nearest_days) <= proximity_days
        prox_cols.append(flag_col)

    # OR across all sources -- catches the "is the placebo contaminated by
    # ANY known shock?" question.
    gaps['any_proximate'] = gaps[prox_cols].any(axis=1) if prox_cols else False
    return gaps


# ---------------------------------------------------------------------------
# Step 3 -- Summary: proximate vs quiet means per (source x series)
# ---------------------------------------------------------------------------
def summarize(audit_df: pd.DataFrame,
              event_sources: dict[str, pd.DataFrame]) -> pd.DataFrame:
    series_cols = [c for c in (*MODELS, 'ens_median') if c in audit_df.columns]
    rows = []
    # One block per source (russia, iran, ...) plus an aggregate "any" block.
    src_keys = [*event_sources.keys(), 'any']
    for src_key in src_keys:
        flag_col = f'{src_key}_proximate' if src_key != 'any' else 'any_proximate'
        if flag_col not in audit_df.columns:
            continue
        for c in series_cols:
            prox = audit_df.loc[audit_df[flag_col], c]
            quiet = audit_df.loc[~audit_df[flag_col], c]
            rows.append({
                'source': src_key,
                'series': c,
                'n_total': int(audit_df[c].notna().sum()),
                'n_proximate': int(prox.notna().sum()),
                'n_quiet': int(quiet.notna().sum()),
                'mean_gap_pct_proximate': float(prox.mean()) if len(prox) else float('nan'),
                'mean_gap_pct_quiet': float(quiet.mean()) if len(quiet) else float('nan'),
                'mean_gap_pct_full': float(audit_df[c].mean()),
                'diff_proximate_minus_quiet': (
                    float(prox.mean() - quiet.mean()) if len(prox) and len(quiet) else float('nan')
                ),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Step 4 -- Annotated Plotly time-series
# ---------------------------------------------------------------------------
def make_plot(audit_df: pd.DataFrame,
              event_sources: dict[str, pd.DataFrame],
              t0_fake: pd.Timestamp, t0_real: pd.Timestamp):
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [plot skipped] plotly not installed")
        return None

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    # Faint per-model lines
    for m in [c for c in MODELS if c in audit_df.columns]:
        fig.add_trace(go.Scatter(
            x=audit_df.index, y=audit_df[m], name=m, mode='lines',
            line=dict(width=1), opacity=0.35,
            hovertemplate='%{x|%Y-%m-%d}: %{y:.2f}%<extra>' + m + '</extra>',
        ), secondary_y=False)

    # Bold ensemble median
    fig.add_trace(go.Scatter(
        x=audit_df.index, y=audit_df['ens_median'], name='ensemble median',
        mode='lines', line=dict(width=3, color='black'),
        hovertemplate='%{x|%Y-%m-%d}: %{y:.2f}%<extra>ens_median</extra>',
    ), secondary_y=False)

    fig.add_hline(y=0, line=dict(color='grey', dash='dot'))

    if 'GPRD_30d' in audit_df.columns:
        fig.add_trace(go.Scatter(
            x=audit_df.index, y=audit_df['GPRD_30d'], name='GPRD (30d MA)',
            mode='lines', line=dict(color='firebrick', dash='dash', width=1.5),
            hovertemplate='%{x|%Y-%m-%d}: GPRD30d=%{y:.1f}<extra></extra>',
        ), secondary_y=True)

    # Per-source event vertical lines (only those inside the fake-post window).
    # Annotation y-offset alternates per source so labels don't overlap.
    y_offsets = {'russia': 1.02, 'iran': 1.10}
    for src_key, ev_df in event_sources.items():
        color = SOURCE_COLORS.get(src_key, 'steelblue')
        y_off = y_offsets.get(src_key, 1.18)
        in_win = ev_df[(ev_df['date'] >= t0_fake) & (ev_df['date'] < t0_real)]
        prefix = src_key[:2].upper()
        for _, ev in in_win.iterrows():
            fig.add_vline(x=ev['date'], line=dict(color=color, dash='dash', width=1))
            fig.add_annotation(
                x=ev['date'], y=y_off, yref='paper',
                text=f"[{prefix}] {str(ev['label'])[:25]}",
                showarrow=False, textangle=-30,
                font=dict(size=8, color=color),
            )

    fake_post_end = t0_real - pd.Timedelta(days=1)
    fig.update_layout(
        title=(f"Hormuz in-time placebo audit  |  fake T0 = {t0_fake.date()}  |  "
               f"fake-post window {t0_fake.date()} -> {fake_post_end.date()}  |  "
               f"sources: {', '.join(event_sources.keys())}"),
        xaxis_title='date',
        template='plotly_white',
        legend=dict(orientation='h', y=-0.18),
        height=680,
        margin=dict(t=110),
    )
    fig.update_yaxes(title_text='gap_pct = 100 x (Brent / synthetic - 1)', secondary_y=False)
    fig.update_yaxes(title_text='GPRD (Caldara-Iacoviello daily)', secondary_y=True)
    return fig


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--proximity-days', type=int, default=3,
                    help='|days| from any event in any source to flag a '
                         'trading day as "<source>_proximate" (default 3)')
    args = ap.parse_args()

    print("== Hormuz in-time placebo audit ==")
    print(f"  fake T_0       : {T0_FAKE[EVENT].date()}")
    print(f"  real T_0       : {T0[EVENT].date()}")
    print(f"  pool / window  : {VARIANT} / {WINDOW}")
    print(f"  proximity_days : +/-{args.proximity_days}")

    event_sources = {key: load_events(path, key)
                     for key, path in EVENT_SOURCES.items()}
    for key, df in event_sources.items():
        rel = EVENT_SOURCES[key].relative_to(ROOT)
        print(f"  events ({key:<6s}) : {len(df):>3d} verified rows from {rel}")

    panel, meta = build_panel(event=EVENT, window=WINDOW, variant=VARIANT)
    print(f"  donors         : {len(meta['donors'])}  panel obs={len(panel)}")

    print("\n[1/3] re-fitting in-time placebo for each model...")
    model_gaps = fit_all_models(
        panel, meta['donors'],
        t0_fake=T0_FAKE[EVENT], t_pre_start=meta['t_pre_start'],
    )

    print("\n[2/3] assembling per-day audit table...")
    audit_df = assemble_audit_table(
        model_gaps,
        t0_fake=T0_FAKE[EVENT], t0_real=T0[EVENT],
        event_sources=event_sources,
        proximity_days=args.proximity_days,
    )
    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit_df.to_csv(AUDIT_CSV)
    print(f"  wrote {AUDIT_CSV.relative_to(ROOT)}  ({len(audit_df)} rows)")

    summary = summarize(audit_df, event_sources)
    summary.to_csv(SUMMARY_CSV, index=False)
    print(f"  wrote {SUMMARY_CSV.relative_to(ROOT)}")
    print("\n--- proximate vs quiet summary (per source) ---")
    print(summary.round(3).to_string(index=False))

    print("\n[3/3] writing annotated plot...")
    fig = make_plot(
        audit_df, event_sources,
        t0_fake=T0_FAKE[EVENT], t0_real=T0[EVENT],
    )
    if fig is not None:
        PLOT_HTML.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(PLOT_HTML)
        print(f"  wrote {PLOT_HTML.relative_to(ROOT)}")

    print("\nDone. Per-source interpretation:")
    print("  RUSSIA  |mean_prox| >> |mean_quiet| -> placebo signal IS Russia-contaminated")
    print("          (weakens the runup-to-Hormuz premium reading).")
    print("  IRAN    |mean_prox| >> |mean_quiet| -> placebo signal IS driven by Iran-axis")
    print("          events; this is co-treatment with the eventual Hormuz event, so it")
    print("          STRENGTHENS the runup-to-Hormuz reading rather than weakening it.")


if __name__ == '__main__':
    main()
