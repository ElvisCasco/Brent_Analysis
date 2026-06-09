"""Does removing VIX move the estimate? Refit the preferred window for both events
with VIX IN (19-donor pool) vs VIX OUT (18-donor shared pool), identical code/grids,
and compare per-model + equal-weight ensemble post-event gap %. In-memory only —
no save_fit, nothing on disk is touched.
"""
import sys, time
sys.path.insert(0, '.')
import numpy as np, pandas as pd
import lib.config as config
from lib.data import build_panel
from lib.models import fit_model
from lib.validation import walk_forward_cv

EVENTS = ['russia', 'hormuz']

GRIDS = {
    'convex_scm':     ([{}], {'n_random_v': 120}),
    'ascm':           ([{'ridge_lambda': l} for l in [0.01, 0.1, 1.0, 10.0, 100.0]],
                       {'n_random_v': 60}),
    'elastic_net':    ([{'alpha': a, 'l1_ratio': r, 'max_iter': 10000}
                        for a in [0.001, 0.01, 0.05, 0.1, 0.5] for r in [0.2, 0.5, 0.8]], {}),
    'xgboost':        ([{'max_depth': d, 'n_estimators': 1000, 'learning_rate': lr,
                         'reg_lambda': rl, 'gamma': 0.1, 'random_state': 0, 'verbosity': 0}
                        for d in [2, 3, 4] for lr in [0.001, 0.005, 0.01, 0.03, 0.1]
                        for rl in [1.0, 10.0]],
                       {'early_stopping_rounds': 20}),   # eval_t0_end set per-cell below
    'bayesian_ridge': ([{'lambda_1': l, 'lambda_2': l, 'alpha_1': a, 'alpha_2': a}
                        for l in [1e-8, 1e-6, 1e-4, 1e-2, 1.0] for a in [1e-8, 1e-6, 1e-4]], {}),
}
_ES_KEYS = ('early_stopping_rounds', 'eval_t0_end')


def tune_and_fit(model, panel, meta, grid, fixed):
    t0 = meta['t0']
    best, best_val, best_post = None, np.inf, np.nan
    for hp in grid:
        cv = walk_forward_cv(model, panel, 'Brent', meta['donors'],
                             t0=t0, t_pre_start=meta['t_pre_start'], **fixed, **hp)
        if 'error' in cv:
            raise RuntimeError(f'{model} {hp}: {cv["error"]}')
        full_kw = {k: v for k, v in {**fixed, **hp}.items() if k not in _ES_KEYS}
        mbi = cv.get('median_best_iteration')
        if model == 'xgboost' and mbi:
            full_kw['n_estimators'] = mbi + 1
        r = fit_model(model, panel, 'Brent', meta['donors'],
                      t0=t0, t_pre_start=meta['t_pre_start'], **full_kw)
        post = r['gap'][r['gap'].index >= t0]
        post_pct = float(100 * (np.exp(post.mean()) - 1)) if len(post) else np.nan
        if cv['val_rmse'] < best_val:
            best_val, best, best_post = cv['val_rmse'], hp, post_pct
    return best_post


def run_pool(exclude, label):
    config.BREAKPOINT_EXCLUDE[:] = exclude   # mutate in place so lib.data sees it
    out = {}
    for event in EVENTS:
        panel, meta = build_panel(event=event, window='preferred', variant='shared')
        assert ('VIX' in meta['donors']) == (exclude == []), 'pool/VIX mismatch'
        res = {}
        for model, (grid, fixed) in GRIDS.items():
            f = dict(fixed)
            if model == 'xgboost':
                f['eval_t0_end'] = meta['t0']
            t = time.time()
            res[model] = tune_and_fit(model, panel, meta, grid, f)
            print(f'  [{label}] {event:7s} {model:15s} post_gap={res[model]:7.2f}%  ({time.time()-t:.0f}s)', flush=True)
        res['ENSEMBLE'] = float(np.mean(list(res.values())))
        out[event] = res
        print(f'  [{label}] {event:7s} n_donors={len(meta["donors"])} ENSEMBLE={res["ENSEMBLE"]:.2f}%\n', flush=True)
    return out


t_all = time.time()
print('=== VIX OUT (18-donor shared pool, current production) ===', flush=True)
out_excl = run_pool(['VIX'], 'OUT')
print('=== VIX IN (19-donor pool) ===', flush=True)
out_incl = run_pool([], 'IN')

print('\n' + '=' * 72)
print(f'{"":8s}{"model":16s}{"VIX-out":>10s}{"VIX-in":>10s}{"delta(pp)":>12s}')
print('=' * 72)
for event in EVENTS:
    for model in list(GRIDS) + ['ENSEMBLE']:
        a, b = out_excl[event][model], out_incl[event][model]
        print(f'{event:8s}{model:16s}{a:10.2f}{b:10.2f}{b-a:12.2f}')
    print('-' * 72)
print(f'total wall time: {time.time()-t_all:.0f}s')
