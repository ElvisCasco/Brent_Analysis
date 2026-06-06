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


# ===== §5c (ii) Bai-Perron multiple structural-break dating =====

def _prefix_ssr(y, x):
    """Closed-form SSR matrix for OLS of y on [1, x] over every segment i..j inclusive.

    Returns an (n, n) upper-triangular matrix where ``SSR[i, j]`` is the residual
    sum of squares of regressing ``y[i:j+1]`` on a constant and ``x[i:j+1]``.
    Computed from prefix sums in O(n^2) with O(1) arithmetic per entry — only the
    simple-regression case (intercept + one regressor) is supported, which is all
    the trend and Brent-relationship specs in §5c (ii) need. Segments shorter than
    two observations are set to ``np.inf``.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    n = len(y)
    z = np.zeros(1)
    Sx = np.concatenate([z, np.cumsum(x)])
    Sy = np.concatenate([z, np.cumsum(y)])
    Sxx = np.concatenate([z, np.cumsum(x * x)])
    Sxy = np.concatenate([z, np.cumsum(x * y)])
    Syy = np.concatenate([z, np.cumsum(y * y)])

    SSR = np.full((n, n), np.inf)
    for i in range(n):
        j = np.arange(i, n)
        m = (j - i + 1).astype(float)
        sx = Sx[j + 1] - Sx[i]
        sy = Sy[j + 1] - Sy[i]
        sxx = Sxx[j + 1] - Sxx[i]
        sxy = Sxy[j + 1] - Sxy[i]
        syy = Syy[j + 1] - Syy[i]
        sxx_c = sxx - sx * sx / m
        sxy_c = sxy - sx * sy / m
        syy_c = syy - sy * sy / m
        beta = np.where(sxx_c > 1e-12, sxy_c / np.where(sxx_c > 1e-12, sxx_c, 1.0), 0.0)
        ssr = syy_c - beta * sxy_c
        SSR[i, j] = np.where(m >= 2, np.maximum(ssr, 0.0), np.inf)
    return SSR


def bai_perron_breaks(y, x, min_size_frac=0.10, max_breaks=5):
    """Bai & Perron (1998, 2003) multiple structural-break dating for a simple
    regression ``y_t = a_s + b_s * x_t + e_t`` allowing up to ``max_breaks`` breaks.

    Globally minimises total SSR over all admissible partitions (minimum segment
    length ``h = ceil(min_size_frac * n)``) by dynamic programming, then selects
    the number of breaks by BIC. Restricted to one regressor plus an intercept —
    the two specifications used in §5c (ii):

    - **trend spec**: ``x`` = a linear time index, ``y`` = donor log-level →
      breaks in level / trend slope (a "change in trend" test on the donor's own path).
    - **relationship spec**: ``x`` = Brent log-returns, ``y`` = donor log-returns →
      breaks in the donor-Brent co-movement (the formal upgrade to the §5c
      distance-correlation regime-stability test).

    This is the *known-form, unknown-date* counterpart to §5d's
    ``permutation_mean_shift_test`` (known date, mean only): Bai-Perron searches
    for the break dates rather than assuming them, so it can place a break at an
    arbitrary point and report *when* a donor's behaviour shifted.

    Args:
        y, x: aligned pandas Series (same DatetimeIndex, NaNs already dropped).
        min_size_frac: minimum segment length as a fraction of the sample.
        max_breaks: maximum number of breaks to search for.

    Returns dict with keys:
        n_breaks: BIC-selected number of breaks
        break_dates: Timestamps that *start* each post-break segment
        break_idx: integer positions of those break dates
        bic, ssr: BIC and global-min SSR for m = 0..max_breaks
        segments: per-segment (start, end, intercept, slope, n) for selected m
        n: sample size
    """
    if len(y) != len(x):
        raise ValueError('y and x must be aligned (equal length)')
    idx = y.index
    yv = np.asarray(y, dtype=float)
    xv = np.asarray(x, dtype=float)
    n = len(yv)
    h = max(2, int(np.ceil(min_size_frac * n)))
    max_m = min(max_breaks, n // h - 1)
    if max_m < 1:
        # Sample too short for even one break at this min segment size.
        X = np.column_stack([np.ones(n), xv])
        coef, *_ = np.linalg.lstsq(X, yv, rcond=None)
        ssr0 = float(np.sum((yv - X @ coef) ** 2))
        return {
            'n_breaks': 0, 'break_idx': [], 'break_dates': [],
            'bic': [np.nan], 'ssr': [ssr0],
            'segments': [{'start': idx[0], 'end': idx[-1],
                          'intercept': float(coef[0]), 'slope': float(coef[1]), 'n': n}],
            'n': n,
        }

    SSR = _prefix_ssr(yv, xv)

    # DP: cost[m, j] = min SSR partitioning obs 0..j into (m+1) segments, each >= h.
    cost = np.full((max_m + 1, n), np.inf)
    bptr = np.full((max_m + 1, n), -1, dtype=int)
    for j in range(n):
        if j + 1 >= h:
            cost[0, j] = SSR[0, j]
    for m in range(1, max_m + 1):
        for j in range((m + 1) * h - 1, n):
            lo = m * h - 1          # earliest admissible end of the previous block
            hi = j - h              # latest end leaving the final segment >= h
            if hi < lo:
                continue
            tot = cost[m - 1, lo:hi + 1] + SSR[lo + 1:hi + 2, j]
            k = int(np.argmin(tot))
            cost[m, j] = tot[k]
            bptr[m, j] = lo + k

    # BIC over m = 0..max_m. p = 2*(m+1) regression coefficients + m break fractions.
    bic, ssr_path = [], []
    for m in range(max_m + 1):
        s = cost[m, n - 1]
        ssr_path.append(float(s))
        if not np.isfinite(s) or s <= 0:
            bic.append(np.inf)
        else:
            p = 2 * (m + 1) + m
            bic.append(float(n * np.log(s / n) + np.log(n) * p))
    m_star = int(np.argmin(bic))

    # Backtrack the selected partition.
    breaks, j, m = [], n - 1, m_star
    while m > 0:
        i = int(bptr[m, j])
        breaks.append(i)
        j, m = i, m - 1
    break_idx = sorted(breaks)
    break_dates = [idx[i + 1] for i in break_idx]

    bounds = [0] + [i + 1 for i in break_idx] + [n]
    segments = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        X = np.column_stack([np.ones(b - a), xv[a:b]])
        coef, *_ = np.linalg.lstsq(X, yv[a:b], rcond=None)
        segments.append({'start': idx[a], 'end': idx[b - 1],
                         'intercept': float(coef[0]), 'slope': float(coef[1]),
                         'n': int(b - a)})

    return {
        'n_breaks': m_star, 'break_idx': break_idx, 'break_dates': break_dates,
        'bic': bic, 'ssr': ssr_path, 'segments': segments, 'n': n,
    }


# ===== §5c (iii) Harvey-Leybourne-Taylor I(0)/I(1)-robust trend-break test =====

# HLT (2009, Econometric Theory 25(4):995-1029) Table 1, Model A (trend break only),
# unknown break date, 10% trimming. (critical value, m_xi) per significance level.
_HLT_TABLE_A = {'10%': (2.284, 0.835), '5%': (2.563, 0.853), '1%': (3.135, 0.890)}
_HLT_G1, _HLT_G2 = 500.0, 2.0


def _bartlett_lr_var(resid, bandwidth):
    """Bartlett-kernel long-run variance of a residual series (HLT 2009 eq. 6/7).

    omega^2 = gamma_0 + 2 * sum_{j=1}^{l} (1 - j/(l+1)) * gamma_j, with
    gamma_j = m^{-1} sum resid_t resid_{t-j} (the T^{-1} convention, m = len(resid)).
    """
    r = np.asarray(resid, dtype=float)
    m = len(r)
    g0 = float(np.mean(r * r))
    s = g0
    for j in range(1, int(bandwidth) + 1):
        if j >= m:
            break
        s += 2.0 * (1.0 - j / (bandwidth + 1.0)) * float(np.mean(r[j:] * r[:-j]))
    return max(s, 1e-12)


def hlt_trend_break(y, trim=0.10, sig='5%'):
    """Harvey, Leybourne & Taylor (2009) trend-break test, robust to I(0)/I(1) errors.

    Tests H0: no break in the linear trend of `y` against a single break at an
    unknown date, with size asymptotically invariant to whether the shocks are
    I(0) or I(1) — the right tool for near-unit-root price levels, where a naive
    trend-break regression over-detects (see §5c (ii) trend-spec caveat).

    Model A (trend break only, HLT eq. 1):  y_t = a + b*t + g*DT_t(tau) + u_t,
    DT_t(tau) = 1(t > floor(tau*T)) * (t - floor(tau*T)).

    Construction (HLT eqs. 3, 5, 9, 10, 13):
      - t0* = sup_{tau in [trim, 1-trim]} |t-ratio on g| in the levels regression,
        with a Bartlett long-run-variance denominator (I(0)-optimal); tau_hat = argmax.
      - t1* = sup |t-ratio on g| in the differenced regression
        dy_t = b + g*DU_t(tau) + du_t, DU_t = 1(t > floor(tau*T)) (I(1)-optimal).
      - S0, S1 = KPSS stationarity stats on the two residual series at tau_hat.
      - lambda = exp(-(g1 * S0 * S1)^g2), g1=500, g2=2  -> 1 if I(0), 0 if I(1).
      - t_lambda = lambda*t0* + m_xi*(1-lambda)*t1*  (m_xi from Table 1 per `sig`).
    Reject H0 (a trend break exists) if t_lambda > the Table 1 critical value.

    t-ratios are invariant to regressor scaling, so time and DT are scaled by T
    internally for numerical conditioning. Bandwidth ell = floor(4*(T/100)^0.25).

    Args:
        y: pandas Series (DatetimeIndex), the donor's log-level. NaNs dropped.
        trim: end trimming for the break-fraction search (HLT use 0.10).
        sig: significance level for the (m_xi, critical value) pair: '10%','5%','1%'.

    Returns dict: t_lambda, t0_star, t1_star, lam, S0, S1, break_date, break_idx,
        reject (at `sig`), reject_10/reject_5/reject_1, crit_value, m_xi, T, bandwidth.
    """
    s = y.dropna()
    idx = s.index
    yv = np.asarray(s, dtype=float)
    T = len(yv)
    if T < 50:
        return {'error': f'series too short (T={T})', 'T': T}

    ell = int(np.floor(4.0 * (T / 100.0) ** 0.25))
    tn = np.arange(1, T + 1, dtype=float) / T          # scaled time (conditioning only)
    lo = max(int(np.floor(trim * T)), 2)
    hi = min(int(np.ceil((1 - trim) * T)), T - 2)

    dy = np.diff(yv)                                   # length T-1, aligned to t = 2..T
    tt2 = np.arange(2, T + 1)

    # --- t0(tau): levels regression, sup over candidate breaks ---
    t0_star, tau_hat, resid0_hat, omega0_hat = -np.inf, lo, None, None
    one_T = np.ones(T)
    for Tb in range(lo, hi + 1):
        DTn = np.where(np.arange(1, T + 1) > Tb, (np.arange(1, T + 1) - Tb) / T, 0.0)
        X = np.column_stack([one_T, tn, DTn])
        beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
        resid = yv - X @ beta
        omega2 = _bartlett_lr_var(resid, ell)
        XtX_inv = np.linalg.inv(X.T @ X)
        se_g = np.sqrt(omega2 * XtX_inv[2, 2])
        t0 = abs(beta[2]) / se_g if se_g > 0 else 0.0
        if t0 > t0_star:
            t0_star, tau_hat, resid0_hat, omega0_hat = t0, Tb, resid, omega2

    # --- t1(tau): differenced regression, sup over candidate breaks ---
    t1_star = -np.inf
    one_d = np.ones(T - 1)
    for Tb in range(lo, hi + 1):
        DU = (tt2 > Tb).astype(float)
        X = np.column_stack([one_d, DU])
        beta, *_ = np.linalg.lstsq(X, dy, rcond=None)
        resid = dy - X @ beta
        omega2 = _bartlett_lr_var(resid, ell)
        XtX_inv = np.linalg.inv(X.T @ X)
        se_g = np.sqrt(omega2 * XtX_inv[1, 1])
        t1 = abs(beta[1]) / se_g if se_g > 0 else 0.0
        if t1 > t1_star:
            t1_star = t1

    # --- S0, S1 (KPSS) at tau_hat ---
    DU_hat = (tt2 > tau_hat).astype(float)
    Xd = np.column_stack([one_d, DU_hat])
    betad, *_ = np.linalg.lstsq(Xd, dy, rcond=None)
    residd_hat = dy - Xd @ betad
    omega1_hat = _bartlett_lr_var(residd_hat, ell)
    S0 = float(np.sum(np.cumsum(resid0_hat) ** 2) / (T ** 2 * omega0_hat))
    S1 = float(np.sum(np.cumsum(residd_hat) ** 2) / ((T - 1) ** 2 * omega1_hat))
    lam = float(np.exp(-((_HLT_G1 * S0 * S1) ** _HLT_G2)))

    def _tlam(level):
        cv, m = _HLT_TABLE_A[level]
        return lam * t0_star + m * (1.0 - lam) * t1_star, cv

    rej = {}
    for level in ('10%', '5%', '1%'):
        tl, cv = _tlam(level)
        rej[level] = tl > cv
    t_lambda, crit = _tlam(sig)
    cv_sig, m_sig = _HLT_TABLE_A[sig]

    return {
        't_lambda': float(t_lambda), 't0_star': float(t0_star), 't1_star': float(t1_star),
        'lam': lam, 'S0': S0, 'S1': S1,
        'break_idx': int(tau_hat), 'break_date': idx[tau_hat - 1],
        'reject': bool(rej[sig]),
        'reject_10': bool(rej['10%']), 'reject_5': bool(rej['5%']), 'reject_1': bool(rej['1%']),
        'crit_value': float(cv_sig), 'm_xi': float(m_sig), 'T': T, 'bandwidth': ell,
    }


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
