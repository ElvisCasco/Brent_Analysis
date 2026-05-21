"""Data loading + per-event panel building + fit save/load."""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA, RESULTS, VALIDATION, T0, PRE_WINDOWS, POST_END


# ===== Raw data loaders =====

def load_brent():
    df = pd.read_csv(DATA / 'brent_spot.csv', parse_dates=['Date'])
    df = df.rename(columns={'Date': 'date', 'Price': 'Brent'})
    return df.set_index('date').sort_index().dropna()


def load_donors():
    return pd.read_parquet(DATA / 'donors.parquet')


def load_audit():
    return pd.read_csv(DATA / 'donor_audit.csv')


def load_gpr():
    gpr = pd.read_parquet(DATA / 'gpr_daily.parquet')
    gpr['GPRD_30d'] = gpr['GPRD'].rolling(30, min_periods=10).mean()
    return gpr


def load_events():
    return pd.read_csv(DATA / 'historical_events.csv', parse_dates=['date'])


# ===== Per-event donor pools =====

def get_donor_pool(event='russia', variant='strict_clean'):
    """Return list of donor names per the audit table.

    variant: 'strict_clean' (C only) | 'permissive' (C+M) | 'full' (all)
    """
    audit = load_audit()
    col = {'russia': 'Russia_2022', 'hormuz': 'Hormuz_2026'}[event]
    if variant == 'strict_clean':
        return audit.loc[audit[col] == 'C', 'donor'].tolist()
    elif variant == 'permissive':
        return audit.loc[audit[col].isin(['C', 'M']), 'donor'].tolist()
    elif variant == 'full':
        return audit['donor'].tolist()
    else:
        raise ValueError(f'unknown variant: {variant!r}')


def shared_pool():
    """The 21-donor intersection (Russia strict-clean = subset of Hormuz strict-clean).

    PREFERRED specification per methodology §3. Required by the cross-event
    weight-transfer validation (§5f) which needs both events to share the input vector.
    """
    return get_donor_pool('russia', 'strict_clean')


# ===== Panel builders =====

def build_panel(event='russia', window='preferred', variant='shared'):
    """Build the log-panel for one (event, window, variant) cell.

    Returns
    -------
    panel : DataFrame
        log-Brent + log-donor levels, indexed by date, covering t_pre_start..t_post_end
    meta : dict
        t0, t_pre_start, t_pre_end, t_post_end, donors list, event, window, variant
    """
    brent = load_brent()
    donors_all = load_donors()

    if variant == 'shared':
        donor_list = shared_pool()
    else:
        donor_list = get_donor_pool(event, variant)

    t_pre_start, t_pre_end = PRE_WINDOWS[event][window]
    t0 = T0[event]
    t_post_end = POST_END[event]

    panel = brent[['Brent']].join(donors_all[donor_list], how='inner')
    panel = panel.ffill(limit=5).dropna()
    panel = panel.loc[t_pre_start:t_post_end]
    log_panel = np.log(panel.where(panel > 0).dropna())

    meta = {
        'event': event,
        'window': window,
        'variant': variant,
        't0': t0,
        't_pre_start': t_pre_start,
        't_pre_end': t_pre_end,
        't_post_end': t_post_end,
        'donors': donor_list,
        'n_pre': int((log_panel.index < t0).sum()),
        'n_post': int((log_panel.index >= t0).sum()),
    }
    return log_panel, meta


# ===== Fit save/load =====

def save_fit(result, event, window, model, variant='shared', base_dir=None):
    """Save a model fit result to data/results/{event}/{window}/{variant}/{model}/."""
    base_dir = base_dir or RESULTS
    out_dir = Path(base_dir) / event / window / variant / model
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / 'fit.pkl', 'wb') as f:
        pickle.dump(result, f)

    # Also save a human-readable summary CSV
    summary = pd.Series({
        'event': event,
        'window': window,
        'variant': variant,
        'model': model,
        'rmspe_pre_log': result['rmspe_pre'],
        'rmspe_pre_pct': (np.exp(result['rmspe_pre']) - 1.0) * 100,
        't0': str(result['t0']),
        't_pre_start': str(result['t_pre_start']),
        'n_pre': int((result['actual'].index < result['t0']).sum()),
        'n_post': int((result['actual'].index >= result['t0']).sum()),
        'n_donors_active': int((result['weights'].abs() > 0.005).sum()),
    })
    summary.to_csv(out_dir / 'summary.csv', header=False)

    # And the gap series as CSV for easy inspection
    gap_pct = 100.0 * (np.exp(result['gap']) - 1.0)
    gap_pct.to_csv(out_dir / 'gap_pct.csv', header=['gap_pct'])

    return out_dir


def load_fit(event, window, model, variant='shared', base_dir=None):
    """Load a model fit result, or None if not found."""
    base_dir = base_dir or RESULTS
    path = Path(base_dir) / event / window / variant / model / 'fit.pkl'
    if not path.exists():
        return None
    with open(path, 'rb') as f:
        return pickle.load(f)


def list_fits(base_dir=None):
    """List all available fits. Returns list of (event, window, variant, model) tuples."""
    base_dir = Path(base_dir or RESULTS)
    if not base_dir.exists():
        return []
    fits = []
    for event_dir in base_dir.iterdir():
        if not event_dir.is_dir():
            continue
        for window_dir in event_dir.iterdir():
            if not window_dir.is_dir():
                continue
            for variant_dir in window_dir.iterdir():
                if not variant_dir.is_dir():
                    continue
                for model_dir in variant_dir.iterdir():
                    if not model_dir.is_dir():
                        continue
                    if (model_dir / 'fit.pkl').exists():
                        fits.append((event_dir.name, window_dir.name,
                                     variant_dir.name, model_dir.name))
    return fits


# ===== Validation table save/load =====

def save_validation_table(df, name, base_dir=None):
    """Save a validation table to data/validation/{name}.csv."""
    base_dir = base_dir or VALIDATION
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    out = base_dir / f'{name}.csv'
    df.to_csv(out)
    return out


def load_validation_table(name, base_dir=None):
    """Load a validation table; returns None if not found."""
    base_dir = base_dir or VALIDATION
    path = Path(base_dir) / f'{name}.csv'
    if not path.exists():
        return None
    return pd.read_csv(path, index_col=0)
