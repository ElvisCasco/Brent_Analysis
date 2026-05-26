"""Validation tests for SCM fits.

Each test takes a model-fit result (and sometimes the raw panel) and returns a
dict / DataFrame of test statistics + pass/fail flag.
"""
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

from .config import (WALK_FORWARD_N_FOLDS, WALK_FORWARD_HORIZON, WALK_FORWARD_MIN_TRAIN_FRAC,
                     EVENT_WINDOW_PRE_DAYS, EVENT_WINDOW_POST_DAYS, LOO_MIN_WEIGHT)
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


# ===== §5a (i) Walk-forward cross-validation (expanding window) =====

def walk_forward_cv(model_name, panel, treated, donors, t0, t_pre_start,
                    n_folds=WALK_FORWARD_N_FOLDS,
                    horizon=WALK_FORWARD_HORIZON,
                    min_train_frac=WALK_FORWARD_MIN_TRAIN_FRAC,
                    **kwargs):
    """Expanding-window walk-forward CV.

    Splits the pre-event window into n_folds expanding-window forecast periods.
    Fold i fits on [t_pre_start, tau_i) and projects on [tau_i, tau_i + horizon).
    The training set grows with i; the val window has fixed length `horizon`.

    Headline val_rmse is the Hyndman pooled RMSE over the concatenated fold val
    residuals (val windows are non-overlapping, so this is unbiased). Headline
    train_rmse is the cross-fold mean of per-fold train_rmse — training sets
    overlap across folds (fold k's train is a superset of fold k-1's), so
    pooling train residuals would over-weight early observations. Per-fold RMSE
    and cross-fold std are also returned so fold-to-fold variability is visible.

    For XGBoost / models that consume `eval_t0_end`, the eval window for early
    stopping is set per-fold to the fold's val span. Median best_iteration
    across folds is returned for use in the final train+val refit.

    Args:
        n_folds: number of expanding-window folds (default from config, 5).
        horizon: business-day length of each fold's val window (default from config, 20).
        min_train_frac: smallest fold's training set size, as fraction of pre-period.

    Returns:
        dict with headline keys `train_rmse` (cross-fold mean), `val_rmse`
        (pooled non-overlapping), `val_train_ratio`, plus `folds` (per-fold
        DataFrame), `val_rmse_mean_of_folds`, `val_rmse_std_of_folds`,
        `median_best_iteration`.
    """
    pre = panel.loc[(panel.index >= t_pre_start) & (panel.index < t0)]
    n = len(pre)
    min_train = int(n * min_train_frac)
    if min_train < 30 or n_folds < 1 or horizon < 1:
        return {'error': 'invalid CV configuration', 'n': n,
                'min_train': min_train, 'n_folds': n_folds, 'horizon': horizon}

    available = n - min_train - horizon
    if available < 0:
        return {'error': 'pre-period too short for walk-forward CV at this horizon',
                'n': n, 'min_train': min_train, 'horizon': horizon}

    step = available // (n_folds - 1) if n_folds > 1 else 0

    fold_results = []
    all_val_resid = []

    for i in range(n_folds):
        cut_idx = min(min_train + i * step, n - horizon)
        tau_i = pre.index[cut_idx]
        end_idx = min(cut_idx + horizon - 1, n - 1)
        tau_end = pre.index[end_idx]

        # Per-fold kwargs: replace `eval_t0_end` (XGB early stopping anchor) with this fold's val end
        fold_kwargs = dict(kwargs)
        if 'eval_t0_end' in fold_kwargs:
            fold_kwargs['eval_t0_end'] = tau_end + pd.Timedelta(days=1)

        # Fit on [t_pre_start, tau_i) — model treats tau_i as if it were T_0
        result_i = fit_model(model_name, panel, treated, donors,
                             t0=tau_i, t_pre_start=t_pre_start, **fold_kwargs)
        gap = result_i['gap']

        train_resid_i = gap.loc[gap.index < tau_i].values
        val_resid_i = gap.loc[(gap.index >= tau_i) & (gap.index <= tau_end)].values

        train_rmse_i = float(np.sqrt(np.mean(train_resid_i ** 2))) if len(train_resid_i) > 0 else np.nan
        val_rmse_i = float(np.sqrt(np.mean(val_resid_i ** 2))) if len(val_resid_i) > 0 else np.nan
        ratio_i = val_rmse_i / train_rmse_i if train_rmse_i and train_rmse_i > 0 else np.nan

        fold_results.append({
            'fold': i,
            'tau': tau_i, 'tau_end': tau_end,
            'n_train': len(train_resid_i), 'n_val': len(val_resid_i),
            'train_rmse': train_rmse_i, 'val_rmse': val_rmse_i,
            'val_train_ratio': ratio_i,
            'best_iteration': result_i.get('_extra', {}).get('best_iteration'),
        })
        all_val_resid.append(val_resid_i)

    folds = pd.DataFrame(fold_results)
    # Pooled val_rmse: concat fold val residuals (Hyndman convention). Val windows are
    # non-overlapping by construction, so this is unbiased.
    pooled_val_rmse = float(np.sqrt(np.mean(np.concatenate(all_val_resid) ** 2)))
    # Train RMSE: mean of per-fold train_rmse. Training sets overlap across folds
    # (fold k's train is a superset of fold k-1's), so pooling train residuals would
    # over-weight early observations. The cross-fold mean is the unbiased summary.
    mean_train_rmse = float(folds['train_rmse'].mean())
    headline_ratio = pooled_val_rmse / mean_train_rmse if mean_train_rmse > 0 else np.nan

    best_iters = folds['best_iteration'].dropna()
    median_best_iter = int(best_iters.median()) if len(best_iters) > 0 else None

    return {
        'model': model_name,
        'folds': folds,
        # Headline numbers: pooled val_rmse (non-overlapping) over mean train_rmse (per-fold avg)
        'train_rmse': mean_train_rmse,
        'val_rmse': pooled_val_rmse,
        'val_train_ratio': headline_ratio,
        # Variance across folds (multi-fold-only signal)
        'val_rmse_mean_of_folds': float(folds['val_rmse'].mean()),
        'val_rmse_std_of_folds': float(folds['val_rmse'].std()) if len(folds) > 1 else 0.0,
        # Totals + meta
        'n_train': int(folds['n_train'].sum()),
        'n_val': int(folds['n_val'].sum()),
        'n_folds': n_folds,
        'horizon': horizon,
        'min_train_frac': min_train_frac,
        # XGB-specific (None otherwise)
        'median_best_iteration': median_best_iter,
        # Heuristic one-sided overfit flag
        'passes': bool(not np.isnan(headline_ratio) and headline_ratio < 2.0),
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


def ks_distribution_shift(series, break_date):
    """Two-sample Kolmogorov-Smirnov on log-returns pre vs post break_date.

    Null: the pre-event and post-event return distributions are equal.
    A rejection signals a *distribution-level* shift in the donor — broader than
    a mean shift (which the structural-break test detects) or a window anomaly
    (which the event-window test detects).

    Returns dict with ks_stat, p, n_pre, n_post.
    """
    from scipy.stats import ks_2samp
    s = series.dropna()
    if len(s) < 30:
        return {'p': np.nan, 'error': 'insufficient data'}
    ret = np.log(s).diff().dropna()
    pre = ret[ret.index < break_date]
    post = ret[ret.index >= break_date]
    if len(pre) < 10 or len(post) < 10:
        return {'p': np.nan, 'error': 'too few obs in one side'}
    stat, p = ks_2samp(pre.values, post.values)
    return {'ks_stat': float(stat), 'p': float(p),
            'n_pre': int(len(pre)), 'n_post': int(len(post))}


def permutation_mean_shift_test(series, break_date, n_boot=500, seed=0):
    """Permutation test for a mean shift in log-returns at a known break date.

    Tests the Chow-style hypothesis (Chow 1960 *Econometrica*) of equal pre/post
    means at a *pre-specified* break date, but uses a permutation reference
    distribution (Lehmann & Romano 2005 *Testing Statistical Hypotheses* ch. 15)
    rather than the parametric F-statistic. This is not the Andrews (1993)
    sup-Wald test, which is for an *unknown* break point.

    Implementation: random permutation of the pre/post labels (sampling without
    replacement via np.shuffle), not a true bootstrap (sampling with replacement).
    The function argument `n_boot` is retained for backward compatibility but
    refers to the number of permutation draws.

    Null: log-returns have no mean shift at break_date (i.e., the pre/post
    labels are exchangeable).
    Test statistic: |mean(post) - mean(pre)| / pooled SD.

    P-value uses the Phipson & Smyth (2010, Statistical Applications in
    Genetics and Molecular Biology 9(1):39) correction p = (1 + B*) / (1 + B)
    where B* is the count of permutation statistics at least as extreme as
    observed. This guarantees p in [1/(B+1), 1] -- a literal p=0 is not a
    valid Monte Carlo permutation p-value because the observed statistic
    itself is one realization from the permutation distribution.
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

    # Phipson & Smyth (2010) correction: +1 to numerator and denominator.
    p = float((1 + (boot_stats >= observed).sum()) / (1 + n_boot))
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
