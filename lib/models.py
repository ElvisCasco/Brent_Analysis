"""Five model fit functions for the SCM ensemble.

Each fit function returns a dict with the SAME signature so downstream code is uniform:

    {
        'model':       str,                # model name
        'weights':     pd.Series,          # donor → weight/importance (indexed by donor name)
        'rmspe_pre':   float,              # pre-period root mean-squared prediction error (in log units)
        'actual':      pd.Series,          # observed log-Brent, full window (pre + post)
        'synth':       pd.Series,          # synthetic log-Brent, full window
        'gap':         pd.Series,          # actual - synth (log)
        't0':          pd.Timestamp,       # treatment date
        't_pre_start': pd.Timestamp,       # pre-period start
        '_extra':      dict,               # model-specific extras (intercept, posterior, etc.)
    }
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize


# ===== 1. Convex SCM (Abadie, Diamond, Hainmueller 2010) — baseline =====

def fit_convex_scm(panel, treated, donors, t0, t_pre_start,
                   n_random_v=120, seed=0, **_):
    rng = np.random.default_rng(seed)
    pre_mask = (panel.index >= t_pre_start) & (panel.index < t0)
    full_mask = panel.index >= t_pre_start

    Y1_pre = panel.loc[pre_mask, treated].values
    Y0_pre = panel.loc[pre_mask, donors].values
    K, J = Y0_pre.shape

    def w_given_V(V_diag):
        V = np.diag(V_diag)

        def loss(w):
            d = Y1_pre - Y0_pre @ w
            return d @ V @ d

        cons = ({'type': 'eq', 'fun': lambda w: w.sum() - 1.0},)
        bnds = [(0.0, 1.0)] * J
        w0 = np.full(J, 1.0 / J)
        res = minimize(loss, w0, method='SLSQP', bounds=bnds, constraints=cons,
                       options={'ftol': 1e-10, 'maxiter': 500})
        return res.x

    best = {'rmspe_pre': np.inf, 'w': None}
    for _ in range(n_random_v):
        V_diag = rng.dirichlet(np.ones(K))
        w = w_given_V(V_diag)
        Y_hat_pre = Y0_pre @ w
        rmspe = float(np.sqrt(np.mean((Y1_pre - Y_hat_pre) ** 2)))
        if rmspe < best['rmspe_pre']:
            best = {'rmspe_pre': rmspe, 'w': w}

    w_star = best['w']
    Y_full_donors = panel.loc[full_mask, donors].values
    Y_full_treated = panel.loc[full_mask, treated].values
    Y_hat_full = Y_full_donors @ w_star
    idx = panel.index[full_mask]

    return {
        'model': 'convex_scm',
        'weights': pd.Series(w_star, index=donors).round(6),
        'rmspe_pre': best['rmspe_pre'],
        'actual': pd.Series(Y_full_treated, index=idx, name='actual'),
        'synth': pd.Series(Y_hat_full, index=idx, name='synth'),
        'gap': pd.Series(Y_full_treated - Y_hat_full, index=idx, name='gap'),
        't0': t0,
        't_pre_start': t_pre_start,
        '_extra': {},
    }


# ===== 2. Augmented SCM (Ben-Michael, Feller, Rothstein 2021) =====

def fit_ascm(panel, treated, donors, t0, t_pre_start,
             n_random_v=120, seed=0, ridge_lambda=1.0, **_):
    rng = np.random.default_rng(seed)
    pre_mask = (panel.index >= t_pre_start) & (panel.index < t0)
    full_mask = panel.index >= t_pre_start

    Y1_pre = panel.loc[pre_mask, treated].values
    Y0_pre = panel.loc[pre_mask, donors].values
    K, J = Y0_pre.shape

    def w_given_V(V_diag):
        V = np.diag(V_diag)

        def loss(w):
            d = Y1_pre - Y0_pre @ w
            return d @ V @ d

        cons = ({'type': 'eq', 'fun': lambda w: w.sum() - 1.0},)
        bnds = [(0.0, 1.0)] * J
        w0 = np.full(J, 1.0 / J)
        res = minimize(loss, w0, method='SLSQP', bounds=bnds, constraints=cons,
                       options={'ftol': 1e-10, 'maxiter': 500})
        return res.x

    best = {'rmspe_pre': np.inf, 'w': None}
    for _ in range(n_random_v):
        V_diag = rng.dirichlet(np.ones(K))
        w = w_given_V(V_diag)
        Y_hat_pre = Y0_pre @ w
        rmspe = float(np.sqrt(np.mean((Y1_pre - Y_hat_pre) ** 2)))
        if rmspe < best['rmspe_pre']:
            best = {'rmspe_pre': rmspe, 'w': w}

    w_star = best['w']

    # Ridge bias correction on pre-period residual
    A = Y0_pre
    b = Y1_pre - Y0_pre @ w_star
    XtX = A.T @ A + ridge_lambda * np.eye(J)
    eta = np.linalg.solve(XtX, A.T @ b)

    Y_full_donors = panel.loc[full_mask, donors].values
    Y_full_treated = panel.loc[full_mask, treated].values
    Y_hat_full = Y_full_donors @ w_star + Y_full_donors @ eta
    idx = panel.index[full_mask]

    # Effective weights = SCM convex + ridge correction (can be negative or >1)
    eff_weights = w_star + eta

    return {
        'model': 'ascm',
        'weights': pd.Series(eff_weights, index=donors).round(6),
        'rmspe_pre': best['rmspe_pre'],   # SCM pre-RMSPE; ASCM corrects bias mainly post-period
        'actual': pd.Series(Y_full_treated, index=idx, name='actual'),
        'synth': pd.Series(Y_hat_full, index=idx, name='synth'),
        'gap': pd.Series(Y_full_treated - Y_hat_full, index=idx, name='gap'),
        't0': t0,
        't_pre_start': t_pre_start,
        '_extra': {
            'scm_weights': pd.Series(w_star, index=donors).round(6),
            'ridge_eta': pd.Series(eta, index=donors).round(6),
        },
    }


# ===== 3. Elastic-net regression (Doudchenko-Imbens 2016) =====

def fit_elastic_net(panel, treated, donors, t0, t_pre_start,
                    alpha=0.01, l1_ratio=0.5, max_iter=10000, **_):
    from sklearn.linear_model import ElasticNet

    pre_mask = (panel.index >= t_pre_start) & (panel.index < t0)
    full_mask = panel.index >= t_pre_start

    Y1_pre = panel.loc[pre_mask, treated].values
    Y0_pre = panel.loc[pre_mask, donors].values

    model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=max_iter,
                       fit_intercept=True)
    model.fit(Y0_pre, Y1_pre)

    Y_hat_pre = model.predict(Y0_pre)
    rmspe = float(np.sqrt(np.mean((Y1_pre - Y_hat_pre) ** 2)))

    Y_full_donors = panel.loc[full_mask, donors].values
    Y_full_treated = panel.loc[full_mask, treated].values
    Y_hat_full = model.predict(Y_full_donors)
    idx = panel.index[full_mask]

    return {
        'model': 'elastic_net',
        'weights': pd.Series(model.coef_, index=donors).round(6),
        'rmspe_pre': rmspe,
        'actual': pd.Series(Y_full_treated, index=idx, name='actual'),
        'synth': pd.Series(Y_hat_full, index=idx, name='synth'),
        'gap': pd.Series(Y_full_treated - Y_hat_full, index=idx, name='gap'),
        't0': t0,
        't_pre_start': t_pre_start,
        '_extra': {
            'intercept': float(model.intercept_),
            'alpha': alpha,
            'l1_ratio': l1_ratio,
        },
    }


# ===== 4. XGBoost (Chen & Guestrin 2016) =====

def fit_xgboost(panel, treated, donors, t0, t_pre_start,
                eval_t0_end=None, early_stopping_rounds=None, **kwargs):
    """XGBoost.

    Optional early stopping:
    - If `eval_t0_end` is provided and there is data in `[t0, eval_t0_end)`, that range
      is used as the eval_set; `early_stopping_rounds` (default None) is passed to XGB.
    - If `eval_t0_end` is None or the eval window is empty (typical for the train+val
      final refit), early stopping is skipped and the full `n_estimators` is used.

    Exposes `_extra['best_iteration']` (after early stopping) so the train+val refit
    can use the early-stop-selected tree count instead of the user-supplied max.
    """
    from xgboost import XGBRegressor

    pre_mask = (panel.index >= t_pre_start) & (panel.index < t0)
    full_mask = panel.index >= t_pre_start

    Y1_train = panel.loc[pre_mask, treated].values
    Y0_train = panel.loc[pre_mask, donors].values

    # Build eval set for early stopping if requested
    eval_set = None
    if eval_t0_end is not None and early_stopping_rounds is not None:
        eval_mask = (panel.index >= t0) & (panel.index < eval_t0_end)
        if eval_mask.sum() >= 5:
            eval_set = [(panel.loc[eval_mask, donors].values,
                         panel.loc[eval_mask, treated].values)]

    if eval_set is not None:
        model = XGBRegressor(early_stopping_rounds=early_stopping_rounds, **kwargs)
        model.fit(Y0_train, Y1_train, eval_set=eval_set, verbose=False)
        best_iter = int(getattr(model, 'best_iteration', kwargs.get('n_estimators', 0)))
    else:
        model = XGBRegressor(**kwargs)
        model.fit(Y0_train, Y1_train)
        best_iter = int(kwargs.get('n_estimators', 100))

    Y_hat_pre = model.predict(Y0_train)
    rmspe = float(np.sqrt(np.mean((Y1_train - Y_hat_pre) ** 2)))

    Y_full_donors = panel.loc[full_mask, donors].values
    Y_full_treated = panel.loc[full_mask, treated].values
    Y_hat_full = model.predict(Y_full_donors)
    idx = panel.index[full_mask]

    return {
        'model': 'xgboost',
        'weights': pd.Series(model.feature_importances_, index=donors).round(6),
        'rmspe_pre': rmspe,
        'actual': pd.Series(Y_full_treated, index=idx, name='actual'),
        'synth': pd.Series(Y_hat_full, index=idx, name='synth'),
        'gap': pd.Series(Y_full_treated - Y_hat_full, index=idx, name='gap'),
        't0': t0,
        't_pre_start': t_pre_start,
        '_extra': {
            'hparams': kwargs,
            'best_iteration': best_iter,
            'early_stopping_used': eval_set is not None,
        },
    }


# ===== 5. BSTS proxy via Bayesian Ridge (placeholder for full BSTS) =====

def fit_bsts(panel, treated, donors, t0, t_pre_start,
             alpha_1=1e-6, alpha_2=1e-6, lambda_1=1e-6, lambda_2=1e-6, **_):
    """BSTS proxy: Bayesian Ridge regression on donor levels.

    TODO: replace with full BSTS (Brodersen et al. 2015) via tfp.sts for explicit
    trend + seasonal decomposition and proper posterior credible intervals. The current
    implementation is a Bayesian linear regression that captures the regression-on-donors
    component of BSTS but lacks the trend/seasonal decomposition.
    """
    from sklearn.linear_model import BayesianRidge

    pre_mask = (panel.index >= t_pre_start) & (panel.index < t0)
    full_mask = panel.index >= t_pre_start

    Y1_pre = panel.loc[pre_mask, treated].values
    Y0_pre = panel.loc[pre_mask, donors].values

    model = BayesianRidge(alpha_1=alpha_1, alpha_2=alpha_2,
                          lambda_1=lambda_1, lambda_2=lambda_2,
                          fit_intercept=True)
    model.fit(Y0_pre, Y1_pre)

    Y_hat_pre = model.predict(Y0_pre)
    rmspe = float(np.sqrt(np.mean((Y1_pre - Y_hat_pre) ** 2)))

    Y_full_donors = panel.loc[full_mask, donors].values
    Y_full_treated = panel.loc[full_mask, treated].values
    Y_hat_full, Y_hat_std = model.predict(Y_full_donors, return_std=True)
    idx = panel.index[full_mask]

    # Posterior inclusion probability proxy: |coef| / sd_coef
    coef_sd = np.sqrt(np.diag(model.sigma_))
    pip_proxy = np.abs(model.coef_) / (coef_sd + 1e-12)

    return {
        'model': 'bsts',
        'weights': pd.Series(model.coef_, index=donors).round(6),
        'rmspe_pre': rmspe,
        'actual': pd.Series(Y_full_treated, index=idx, name='actual'),
        'synth': pd.Series(Y_hat_full, index=idx, name='synth'),
        'gap': pd.Series(Y_full_treated - Y_hat_full, index=idx, name='gap'),
        't0': t0,
        't_pre_start': t_pre_start,
        '_extra': {
            'intercept': float(model.intercept_),
            'posterior_sd': pd.Series(Y_hat_std, index=idx, name='posterior_sd'),
            'pip_proxy': pd.Series(pip_proxy, index=donors).round(4),
            'note': 'Bayesian Ridge proxy; replace with tfp.sts for full BSTS',
        },
    }


# ===== Dispatcher =====

MODEL_REGISTRY = {
    'convex_scm':  fit_convex_scm,
    'ascm':        fit_ascm,
    'elastic_net': fit_elastic_net,
    'xgboost':     fit_xgboost,
    'bsts':        fit_bsts,
}


def fit_model(model_name, panel, treated, donors, t0, t_pre_start, **kwargs):
    """Dispatch to the named model. Returns the common result dict."""
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f'unknown model: {model_name!r}; available: {list(MODEL_REGISTRY)}')
    return MODEL_REGISTRY[model_name](panel, treated, donors,
                                      t0=t0, t_pre_start=t_pre_start, **kwargs)
