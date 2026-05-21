"""Validation tests for SCM fits.

Each test takes a model-fit result (and sometimes the raw panel) and returns a
dict / DataFrame of test statistics + pass/fail flag.
"""
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

from .config import WALK_FORWARD_SPLIT, EVENT_WINDOW_PRE_DAYS, EVENT_WINDOW_POST_DAYS, LOO_MIN_WEIGHT
from .models import fit_model
from .data import load_fit


def get_tuned_hparams(model, event, window='preferred', variant='shared'):
    """Load the val-tuned hyperparameters that 02_Fit_Models saved with each fit.

    Returns empty dict if no fit on disk or no tuned_hparams stored (e.g. convex_scm).
    """
    fit = load_fit(event, window, model, variant=variant)
    if fit is None:
        return {}
    return dict(fit.get('_extra', {}).get('tuned_hparams', {}) or {})


# ===== §5a (i) Walk-forward hold-out cross-validation =====

def walk_forward_cv(model_name, panel, treated, donors, t0, t_pre_start,
                    split=WALK_FORWARD_SPLIT, **kwargs):
    """Fit on first `split` of pre-period, evaluate on last (1-split).

    Returns dict with train_rmse, val_rmse, ratio, n_train, n_val.
    """
    pre = panel.loc[(panel.index >= t_pre_start) & (panel.index < t0)]
    n = len(pre)
    n_train = int(n * split)
    if n_train < 30 or (n - n_train) < 10:
        return {'error': 'pre-period too short for walk-forward CV',
                'n': n, 'n_train': n_train}

    t_train_end = pre.index[n_train]

    # Fit using only the training portion of the pre-period
    result = fit_model(model_name, panel, treated, donors,
                       t0=t_train_end, t_pre_start=t_pre_start, **kwargs)

    train_resid = result['gap'].loc[result['gap'].index < t_train_end]
    val_resid = result['gap'].loc[(result['gap'].index >= t_train_end) &
                                  (result['gap'].index < t0)]

    train_rmse = float(np.sqrt(np.mean(train_resid.values ** 2)))
    val_rmse = float(np.sqrt(np.mean(val_resid.values ** 2))) if len(val_resid) > 0 else np.nan
    ratio = val_rmse / train_rmse if train_rmse > 0 else np.nan

    return {
        'model': model_name,
        'train_rmse': train_rmse,
        'val_rmse': val_rmse,
        'val_train_ratio': ratio,
        'n_train': len(train_resid),
        'n_val': len(val_resid),
        'passes': bool(ratio is not np.nan and ratio < 2.0),  # heuristic
    }


# ===== §5a (ii) Moment matching =====

def moment_matching(result, panel, treated):
    """Pre-period moment comparison: log-Brent vs log-synthetic."""
    t0, t_pre_start = result['t0'], result['t_pre_start']
    pre_mask = (panel.index >= t_pre_start) & (panel.index < t0)

    y = panel.loc[pre_mask, treated]
    s = result['synth'][pre_mask]

    def stats_vec(x):
        return [float(x.mean()), float(x.std()), float(x.min()),
                float(x.max()), float(x.autocorr(1)) if len(x) > 1 else np.nan]

    treated_stats = stats_vec(y)
    synth_stats = stats_vec(s)

    df = pd.DataFrame({
        'treated': treated_stats,
        'synth': synth_stats,
    }, index=['mean', 'sd', 'min', 'max', 'ar1'])
    df['delta'] = df['synth'] - df['treated']
    df['delta_pct'] = 100.0 * df['delta'] / df['treated'].abs().replace(0, np.nan)
    return df


# ===== §5b Pre-period parallel-fit defence =====

def parallel_fit_test(result):
    """SCM analog of DiD parallel-trends.

    Tests the pre-period gap series: should hover around zero with no significant trend.
    Returns dict with mean, t-stat, SD, AR(1), trend slope, R², and a pass flag.
    """
    gap_pct = 100.0 * (np.exp(result['gap']) - 1.0)
    pre = gap_pct[gap_pct.index < result['t0']].dropna()
    n = len(pre)

    if n < 10:
        return {'n': n, 'error': 'pre-period too short'}

    mean = float(pre.mean())
    sd = float(pre.std())
    se = sd / np.sqrt(n) if n > 1 else np.nan
    t_stat = mean / se if (not np.isnan(se) and se > 0) else np.nan
    p_t = float(2 * (1 - stats.t.cdf(abs(t_stat), df=n - 1))) if not np.isnan(t_stat) else np.nan
    ar1 = float(pre.autocorr(lag=1)) if n > 1 else np.nan

    # Linear trend in % per year
    days = np.asarray((pre.index - pre.index.min()).days, dtype=float)
    X = sm.add_constant(days)
    ols = sm.OLS(pre.values, X).fit()
    slope_per_year = float(ols.params[1]) * 365.0
    slope_p = float(ols.pvalues[1])
    rsq = float(ols.rsquared)

    passes = bool(
        abs(mean) < 0.5 and
        (np.isnan(p_t) or p_t > 0.05) and
        (np.isnan(ar1) or abs(ar1) < 0.9) and
        abs(slope_per_year) < 5.0 and
        slope_p > 0.10 and
        rsq < 0.10
    )

    return {
        'n': n,
        'mean_pct': mean,
        'sd_pct': sd,
        't_stat': t_stat,
        'p_mean_zero': p_t,
        'ar1': ar1,
        'slope_pct_per_year': slope_per_year,
        'p_slope_zero': slope_p,
        'r_squared': rsq,
        'passes': passes,
    }


# ===== §5c Pre-period regime stability via distance correlation =====

def _distance_correlation(x, y):
    """Distance correlation (Székely & Rizzo 2007). Captures arbitrary statistical dependence."""
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    n = len(x)
    if n != len(y) or n < 4:
        return np.nan

    a = np.abs(x[:, None] - x[None, :])
    b = np.abs(y[:, None] - y[None, :])
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = (A * B).mean()
    dvar_x = (A * A).mean()
    dvar_y = (B * B).mean()
    if dvar_x <= 0 or dvar_y <= 0:
        return 0.0
    return float(np.sqrt(max(dcov2, 0)) / (dvar_x * dvar_y) ** 0.25)


def regime_stability_test(panel, treated, donors, t_pre_start, t_pre_end, n_thirds=3):
    """Test regime stability: distance correlation Brent-donor across pre-period thirds.

    Returns DataFrame: donors × thirds, plus a 'max_shift' column.
    """
    pre = panel.loc[(panel.index >= t_pre_start) & (panel.index < t_pre_end)]
    n = len(pre)
    bounds = [pre.index[int(i * n / n_thirds)] for i in range(n_thirds)]
    bounds.append(pre.index[-1] + pd.Timedelta(days=1))

    rows = {}
    for d in donors:
        thirds = []
        for i in range(n_thirds):
            sub = pre.loc[(pre.index >= bounds[i]) & (pre.index < bounds[i + 1])]
            if len(sub) >= 4:
                thirds.append(_distance_correlation(sub[treated], sub[d]))
            else:
                thirds.append(np.nan)
        rows[d] = thirds

    df = pd.DataFrame(rows, index=[f'third_{i+1}' for i in range(n_thirds)]).T
    df['max_shift'] = df.max(axis=1) - df.min(axis=1)
    df['stable'] = df['max_shift'] < 0.20
    return df


# ===== §5d Donor SUTVA / cleanliness battery =====

def event_window_return_test(series, event_date, pre_days=EVENT_WINDOW_PRE_DAYS,
                              post_days=EVENT_WINDOW_POST_DAYS, control_days=60):
    """Wilcoxon two-sample test: returns in [-pre_days, +post_days] window vs control window.

    Returns dict with W-statistic, p-value, mean return in window and in control.
    """
    s = series.dropna()
    if len(s) == 0:
        return {'p': np.nan, 'error': 'empty series'}

    ret = np.log(s).diff()
    pre_d = event_date - pd.tseries.offsets.BDay(pre_days)
    post_d = event_date + pd.tseries.offsets.BDay(post_days)
    in_window = ret.loc[(ret.index >= pre_d) & (ret.index <= post_d)]

    control_end = pre_d - pd.tseries.offsets.BDay(5)
    control_start = control_end - pd.tseries.offsets.BDay(control_days)
    control = ret.loc[(ret.index >= control_start) & (ret.index <= control_end)]

    if len(in_window) < 3 or len(control) < 10:
        return {'p': np.nan, 'error': 'insufficient data'}

    stat, p = stats.mannwhitneyu(in_window.dropna(), control.dropna(),
                                  alternative='two-sided')
    return {
        'mean_window': float(in_window.mean()),
        'mean_control': float(control.mean()),
        'W': float(stat),
        'p': float(p),
        'n_window': len(in_window),
        'n_control': len(control),
    }


def chow_break_test_bootstrap(series, break_date, n_boot=500, seed=0):
    """Bootstrap structural break test on log-returns.

    Null: returns have no structural break at break_date.
    Test statistic: |mean(post) - mean(pre)| / pooled SD.
    Bootstrap p-value from random permutation of pre/post labels.
    """
    s = np.log(series.dropna()).diff().dropna()
    pre = s[s.index < break_date]
    post = s[s.index >= break_date]
    if len(pre) < 30 or len(post) < 10:
        return {'p': np.nan, 'error': 'insufficient data'}

    def stat(pre_vals, post_vals):
        pooled_sd = np.sqrt((pre_vals.var() + post_vals.var()) / 2)
        return abs(post_vals.mean() - pre_vals.mean()) / (pooled_sd + 1e-12)

    observed = stat(pre.values, post.values)

    rng = np.random.default_rng(seed)
    combined = np.concatenate([pre.values, post.values])
    n_pre = len(pre)
    boot_stats = np.empty(n_boot)
    for i in range(n_boot):
        rng.shuffle(combined)
        boot_stats[i] = stat(combined[:n_pre], combined[n_pre:])

    p = float((boot_stats >= observed).mean())
    return {
        'observed_stat': float(observed),
        'p': p,
        'n_pre': len(pre),
        'n_post': len(post),
    }


# ===== §5e (i) and (also used in 5d) In-space placebo =====

def in_space_placebo(model_name, panel, treated, donors, t0, t_pre_start, **kwargs):
    """In-space placebo: refit treating each donor as treated.

    Returns DataFrame indexed by unit name with columns:
        rmspe_pre, rmspe_post, ratio, rank, p_value, gap_post_mean
    """
    units = [treated] + list(donors)
    rows = {}

    for unit in units:
        # Use the other donors as the pool for this unit
        unit_donors = [d for d in donors if d != unit]
        if unit == treated:
            unit_donors = list(donors)

        if len(unit_donors) < 3:
            rows[unit] = {'error': 'too few donors after exclusion'}
            continue

        try:
            r = fit_model(model_name, panel, unit, unit_donors,
                          t0=t0, t_pre_start=t_pre_start, **kwargs)
            pre = r['gap'][r['gap'].index < t0]
            post = r['gap'][r['gap'].index >= t0]
            rmspe_pre = float(np.sqrt(np.mean(pre.values ** 2))) if len(pre) > 0 else np.nan
            rmspe_post = float(np.sqrt(np.mean(post.values ** 2))) if len(post) > 0 else np.nan
            ratio = rmspe_post / rmspe_pre if rmspe_pre > 0 else np.nan
            gap_post_mean = float(100 * (np.exp(post.mean()) - 1)) if len(post) > 0 else np.nan
            rows[unit] = {
                'rmspe_pre': rmspe_pre,
                'rmspe_post': rmspe_post,
                'ratio': ratio,
                'gap_post_mean_pct': gap_post_mean,
            }
        except Exception as e:
            rows[unit] = {'error': str(e)[:60]}

    df = pd.DataFrame(rows).T
    if 'ratio' in df.columns:
        df['rank'] = df['ratio'].rank(ascending=False, method='min')
        df['p_value'] = df['rank'] / df['ratio'].notna().sum()
    return df


# ===== §5e (ii) In-time placebo =====

def in_time_placebo(model_name, panel, treated, donors, t0_fake, t_pre_start, **kwargs):
    """In-time placebo: refit with fake T_0 in the pre-period.

    Returns the model fit result (with t0 = t0_fake) plus a summary of the gap
    in the 'fake post-period' (between t0_fake and the real t0).
    """
    return fit_model(model_name, panel, treated, donors,
                     t0=t0_fake, t_pre_start=t_pre_start, **kwargs)


# ===== §5e (iii) Leave-one-donor-out =====

def leave_one_out(model_name, panel, treated, donors, t0, t_pre_start,
                  min_weight=LOO_MIN_WEIGHT, **kwargs):
    """For each high-weight donor, drop and refit.

    Returns dict: {donor_dropped: fit_result_dict}. Includes '_baseline' (all donors).
    """
    baseline = fit_model(model_name, panel, treated, donors,
                         t0=t0, t_pre_start=t_pre_start, **kwargs)
    high_weight = baseline['weights'][baseline['weights'].abs() > min_weight].index.tolist()

    results = {'_baseline': baseline}
    for d in high_weight:
        sub = [x for x in donors if x != d]
        if len(sub) < 3:
            continue
        try:
            r = fit_model(model_name, panel, treated, sub,
                          t0=t0, t_pre_start=t_pre_start, **kwargs)
            results[d] = r
        except Exception as e:
            results[d] = {'error': str(e)[:60]}
    return results


# ===== Helper: summarize multiple fit results into a gap distribution =====

def gap_distribution(results_dict, t0):
    """Given dict of fit results, return DataFrame of post-period mean gap (%) per fit."""
    rows = []
    for name, r in results_dict.items():
        if 'gap' not in r:
            continue
        post = r['gap'][r['gap'].index >= t0]
        if len(post) == 0:
            continue
        rows.append({
            'name': name,
            'mean_gap_pct': float(100 * (np.exp(post.mean()) - 1)),
            'median_gap_pct': float(100 * (np.exp(post.median()) - 1)),
            'max_gap_pct': float(100 * (np.exp(post.max()) - 1)),
            'min_gap_pct': float(100 * (np.exp(post.min()) - 1)),
        })
    return pd.DataFrame(rows).set_index('name')


# ===== B-H FDR correction =====

def benjamini_hochberg(p_values, alpha=0.10):
    """Benjamini-Hochberg FDR correction. Returns boolean array (True = reject null)."""
    p = np.asarray(p_values, dtype=float)
    n = (~np.isnan(p)).sum()
    if n == 0:
        return np.zeros_like(p, dtype=bool)

    valid = ~np.isnan(p)
    p_valid = p[valid]
    order = np.argsort(p_valid)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(p_valid) + 1)

    threshold = (ranks / n) * alpha
    reject_valid = p_valid <= threshold
    # Apply step-up rule: all p ≤ p[k*] where k* is the largest rank passing
    if reject_valid.any():
        k_star = ranks[reject_valid].max()
        reject_valid = ranks <= k_star
    else:
        reject_valid[:] = False

    result = np.zeros_like(p, dtype=bool)
    result[valid] = reject_valid
    return result
