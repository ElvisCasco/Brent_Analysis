"""Regenerate all fit artifacts for the 19-donor shared pool (VIX kept), all 3
windows x 2 events x 5 models, using the SAME grids/CV/save path as notebook 02.
Writes data/results/{event}/{window}/shared/{model}/{fit.pkl,gap_pct.csv,summary.csv}
via save_fit -- exactly what notebooks 03-06 read. Run with: uv run python this.py
"""
import sys, time
sys.path.insert(0, '.')
import numpy as np, pandas as pd
from lib.config import DONOR_POOL_VARIANT
from lib.data import build_panel, save_fit
from lib.models import fit_model
from lib.validation import walk_forward_cv

assert DONOR_POOL_VARIANT == 'shared'
EVENTS = ['russia', 'hormuz']
WINDOWS = ['preferred', 'extended', 'narrow']

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
                       {'early_stopping_rounds': 20}),
    'bayesian_ridge': ([{'lambda_1': l, 'lambda_2': l, 'alpha_1': a, 'alpha_2': a}
                        for l in [1e-8, 1e-6, 1e-4, 1e-2, 1.0] for a in [1e-8, 1e-6, 1e-4]], {}),
}
_ES_KEYS = ('early_stopping_rounds', 'eval_t0_end')


def tune_and_fit(model, panel, meta, grid, fixed):
    t0 = meta['t0']
    best_val, best_hp, best_res = np.inf, None, None
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
        if cv['val_rmse'] < best_val:
            best_val, best_hp, best_res = cv['val_rmse'], hp, r
    best_res.setdefault('_extra', {})['tuned_hparams'] = best_hp
    return best_res


t_all = time.time()
for event in EVENTS:
    for window in WINDOWS:
        panel, meta = build_panel(event=event, window=window, variant='shared')
        assert 'VIX' in meta['donors'], 'VIX missing -- config not updated?'
        for model, (grid, fixed) in GRIDS.items():
            f = dict(fixed)
            if model == 'xgboost':
                f['eval_t0_end'] = meta['t0']
            t = time.time()
            res = tune_and_fit(model, panel, meta, grid, f)
            save_fit(res, event, window, model, variant='shared')
            post = res['gap'][res['gap'].index >= meta['t0']]
            pct = 100 * (np.exp(post.mean()) - 1) if len(post) else float('nan')
            print(f'{event:7s} {window:9s} {model:15s} n={len(meta["donors"])} '
                  f'post={pct:6.2f}%  ({time.time()-t:.0f}s)', flush=True)
print(f'\nDONE regenerating all fits in {time.time()-t_all:.0f}s')
