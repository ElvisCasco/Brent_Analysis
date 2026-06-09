"""Battery C robustness: re-run the Bai-Perron relationship break test (and HLT)
on the ANALYSIS PERIOD only (each event's pre-window), instead of the 2010->2026
full history used in 01.5. Answers: do the in-pre-window break flags (VIX for
Russia; Silver/Platinum/EM_Eq for Hormuz) survive when the long pre-2020 history
is dropped, or were they leveraging contrast with old regimes?

Run on preferred / extended / narrow window variants because a single short
window has low break-detection power; agreement across variants = robust flag.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from lib.config import T0, PRE_WINDOWS
from lib.data import load_brent, load_donors, load_audit
from lib.validation import bai_perron_breaks, hlt_trend_break

BP_MIN_FRAC = 0.10
BP_MAX_BREAKS = 5
EVENTS = ['russia', 'hormuz']
VARIANTS = ['preferred', 'extended', 'narrow']

# Donors the FULL-HISTORY run flagged as breaking inside the pre-window (01.5 / docs).
FULL_HISTORY_FLAGS = {
    'russia': {'Wheat': '2022-..', 'VIX': '2022-01-07'},
    'hormuz': {'Silver': '2024-09-13', 'Platinum': '2024-09-13', 'EM_Eq': '2024-09-13'},
}

brent_full = load_brent()['Brent']
donors = load_donors()
audit = load_audit().set_index('donor')


def weekly_logret(s):
    return np.log(s.resample('W-FRI').last().dropna()).diff().dropna()


def weekly_loglevel(s):
    return np.log(s.resample('W-FRI').last().dropna())


brent_w = weekly_logret(brent_full)
audit_col = {'russia': 'Russia_2022', 'hormuz': 'Hormuz_2026'}

print('=' * 78)
print('BATTERY C (ii) Bai-Perron — ANALYSIS-PERIOD-ONLY robustness')
print('Sample per run = [window_start, T0)  (strictly pre-T0; Brent untreated)')
print('=' * 78)

for event in EVENTS:
    t0 = T0[event]
    print(f'\n##### {event.upper()}  (T0 = {t0.date()}) #####')
    print(f'Full-history in-prewindow flags: {FULL_HISTORY_FLAGS[event]}')

    for variant in VARIANTS:
        w_start, _ = PRE_WINDOWS[event][variant]
        # strictly pre-T0 window
        bw = brent_w.loc[w_start:t0]
        bw = bw[bw.index < t0]
        n_weeks = len(bw)
        min_seg = max(2, int(np.ceil(BP_MIN_FRAC * n_weeks)))
        print(f'\n  --- variant={variant}  window=[{w_start.date()} -> {t0.date()})  '
              f'n={n_weeks} wk  min_seg={min_seg} wk (~{min_seg/4.33:.1f} mo) ---')

        rows = {}
        for d in donors.columns:
            dw = weekly_logret(donors[d].dropna())
            common = bw.index.intersection(dw.index)
            if len(common) < 30:
                continue
            r = bai_perron_breaks(dw.loc[common], bw.loc[common],
                                  min_size_frac=BP_MIN_FRAC, max_breaks=BP_MAX_BREAKS)
            if r['n_breaks'] > 0:
                rows[d] = '; '.join(str(bd.date()) for bd in r['break_dates'])

        if rows:
            for d, dates in sorted(rows.items()):
                tag = '  <-- FULL-HISTORY FLAGGED' if d in FULL_HISTORY_FLAGS[event] else ''
                aud = audit.loc[d, audit_col[event]] if d in audit.index else '?'
                print(f'      {d:12s} [{aud}]  breaks: {dates}{tag}')
        else:
            print('      no donor shows ANY within-window break (BIC selects 0 for all)')

        # explicit check on the focal donors
        for d in FULL_HISTORY_FLAGS[event]:
            present = d in rows
            print(f'      focal: {d:10s} within-window break detected? {present}')

print('\n' + '=' * 78)
print('BATTERY C (iii) HLT trend-break — analysis-period only (focal donors)')
print('=' * 78)
for event in EVENTS:
    t0 = T0[event]
    print(f'\n##### {event.upper()} #####')
    for variant in ['extended']:  # longest window = most HLT power
        w_start, _ = PRE_WINDOWS[event][variant]
        for d in list(FULL_HISTORY_FLAGS[event]) + (['VIX'] if event == 'hormuz' else []):
            if d not in donors.columns:
                continue
            lvl = weekly_loglevel(donors[d].dropna())
            lvl = lvl.loc[w_start:t0]
            lvl = lvl[lvl.index < t0]
            if len(lvl) < 30:
                print(f'  {d}: too short ({len(lvl)})'); continue
            r = hlt_trend_break(lvl, trim=0.10, sig='5%')
            if 'error' in r:
                print(f'  {d}: HLT error {r.get("error")}'); continue
            print(f'  [{variant}] {d:10s} t_lambda={r["t_lambda"]:.3f} '
                  f'crit5%={r["crit_value"]} reject={r["reject_5"]} '
                  f'lambda={r["lam"]:.2f} break={r["break_date"].date()}')
