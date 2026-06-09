"""Configuration for the SCM analysis. Edit values here to change parameters globally.

After editing, re-run the affected notebooks (see docs/methodology.md and docs/validation.md).
"""
from pathlib import Path
import pandas as pd

# ===== Project paths =====
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
RESULTS = DATA / 'results'           # 02 writes here; 03-06 read
VALIDATION = DATA / 'validation'      # 03-05 write here; 06 reads


# ===== Focal events =====
T0 = {
    'russia': pd.Timestamp('2022-02-24'),
    'hormuz': pd.Timestamp('2026-02-28'),   # strike date (Sat); Brent reprices Mon 2026-03-02
}

# Fake T_0 for in-time placebo (docs/validation.md §5e (ii) — 6 months before real T_0)
T0_FAKE = {
    'russia': pd.Timestamp('2021-08-24'),
    'hormuz': pd.Timestamp('2025-08-28'),
}


# ===== Pre-event windows (preferred, extended, narrow) =====
PRE_WINDOWS = {
    'russia': {
        'preferred': (pd.Timestamp('2020-07-01'), pd.Timestamp('2022-02-23')),
        'extended':  (pd.Timestamp('2020-01-01'), pd.Timestamp('2022-02-23')),
        'narrow':    (pd.Timestamp('2021-01-01'), pd.Timestamp('2022-02-23')),
    },
    'hormuz': {
        'preferred': (pd.Timestamp('2024-06-01'), pd.Timestamp('2026-02-27')),
        'extended':  (pd.Timestamp('2023-12-01'), pd.Timestamp('2026-02-27')),
        'narrow':    (pd.Timestamp('2025-01-01'), pd.Timestamp('2026-02-27')),
    },
}

# Post-event projection end date (when to stop the counterfactual).
#
# Russia: truncated to 2022-09-30 — last business day before OPEC+'s 2022-10-05
# announcement of a 2 mb/d production cut (effective November 2022). The cut was
# a Brent-specific supply-policy response that confounds the post-invasion premium
# estimate. The earlier symbolic 100kbd cut on 2022-09-05 had minimal market impact
# and is inside the kept window. See docs/methodology.md §2.
#
# Hormuz: extends to latest data available (~3 months post-event).
POST_END = {
    'russia': pd.Timestamp('2022-09-30'),   # before OPEC+ October 2022 cut
    'hormuz': pd.Timestamp('2026-05-31'),   # end May (panel caps at Brent's last obs, currently 2026-04-27)
}


# ===== Donor pool variants =====
# 'shared'        = 21-donor Russia strict-clean ∩ Hormuz clean (PREFERRED for both events; see docs/methodology.md §3)
# 'strict_clean'  = Russia: 21 / Hormuz: 33 (per-event strict)
# 'permissive'    = Russia: 27 / Hormuz: 33  (drops H only)
# 'full'          = Russia: 33 / Hormuz: 33  (no exclusions — contamination diagnostic)
DONOR_POOL_VARIANT = 'shared'

# ===== Breakpoint-rule exclusions (SEPARATE from the SUTVA audit) =====
# Donors removed from the clean pools (strict_clean / permissive / shared) because they
# FAIL the Bai-Perron relationship breakpoint test (Battery C, notebooks/01.5): a structural
# break in the donor<->Brent weekly-return relationship inside the pre-window, near T_0.
# These donors remain audited 'C' and stay in the data and diagnostics; this is an
# additional statistical exclusion layer on top of the hand audit (see docs/validation.md).
#   VIX: relationship break 2022-01-07 (~7 weeks before the Russia invasion -- Fed hawkish
#        pivot + early Ukraine-risk repricing). Applied to BOTH events (shared pool).
# The 'full' variant is the no-exclusions contamination diagnostic and ignores this list.
BREAKPOINT_EXCLUDE = ['VIX']


# ===== Model ensemble (Option B from docs/methodology.md §4) =====
MODELS = ['convex_scm', 'ascm', 'elastic_net', 'xgboost', 'bayesian_ridge']

MODEL_HPARAMS = {
    'convex_scm': {
        'n_random_v': 120,
        'seed': 0,
    },
    'ascm': {
        'n_random_v': 120,
        'seed': 0,
        'ridge_lambda': 1.0,
    },
    'elastic_net': {
        'alpha': 0.01,
        'l1_ratio': 0.5,
        'max_iter': 10000,
    },
    'xgboost': {
        # Tightened for N~420 small-data regime. See docs/methodology.md §4
        # "Hyperparameter choices". Most knobs fixed at small-data-defensible
        # defaults; only `max_depth` and `reg_lambda` are tuned via a 3x3 grid
        # in 02_Fit_Models to control winner's-curse bias on val_RMSE.
        'max_depth': 2,
        'n_estimators': 200,
        'learning_rate': 0.02,
        'gamma': 1.0,
        'reg_lambda': 5.0,
        'subsample': 0.7,
        'colsample_bytree': 0.7,
        'min_child_weight': 5,
        'random_state': 0,
        'verbosity': 0,
    },
    'bayesian_ridge': {
        # sklearn.linear_model.BayesianRidge — Bayesian linear regression on donor levels.
        # Stands in for the regression-on-donors component of Brodersen et al. (2015) BSTS;
        # the trend / seasonal / spike-and-slab components of full BSTS are NOT modelled here.
        # See docs/methodology.md §4 for the relationship to full BSTS.
        # lambda_1=lambda_2 raised from sklearn's 1e-6 default (near-flat prior)
        # to 1e-2 to impose meaningful weight-precision shrinkage. The 1e-6
        # default produced walk-forward val/train ratios of 3-5x on Russia.
        'alpha_1': 1e-6,
        'alpha_2': 1e-6,
        'lambda_1': 1e-2,
        'lambda_2': 1e-2,
    },
}


# ===== Validation settings =====
# Walk-forward CV (expanding window): fold i fits on [t_pre_start, tau_i),
# projects on [tau_i, tau_i + WALK_FORWARD_HORIZON). The smallest fold's training set is
# WALK_FORWARD_MIN_TRAIN_FRAC of the pre-event window; subsequent folds expand it.
WALK_FORWARD_N_FOLDS = 5                  # number of expanding-window folds
WALK_FORWARD_HORIZON = 20                 # business days per fold's val window (~1 month)
WALK_FORWARD_MIN_TRAIN_FRAC = 0.5         # smallest fold's training fraction
FDR_ALPHA = 0.10                 # Benjamini-Hochberg FDR threshold (docs/validation.md §5d)
EVENT_WINDOW_PRE_DAYS = 5        # Event-window return test pre-window (docs/validation.md §5d)
EVENT_WINDOW_POST_DAYS = 20      # Event-window return test post-window (docs/validation.md §5d)
LOO_MIN_WEIGHT = 0.05            # Leave-one-out threshold (docs/validation.md §5e (iii))
