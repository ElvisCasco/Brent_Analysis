"""Brent SCM analysis library.

Modules:
    config      configurable parameters (pre-windows, T0, model hparams)
    data        data loading + per-event panel building + fit save/load
    models      5 model fit functions with a common return signature
    validation  walk-forward CV, parallel-fit, SUTVA battery, inference tests
    plotting    shared plotly helpers

Usage from notebooks/:
    import sys; from pathlib import Path
    sys.path.insert(0, str(Path.cwd().parent))   # add project root to path
    from lib.config import PRE_WINDOWS, T0
    from lib.data import build_panel, save_fit, load_fit
    from lib.models import fit_model
"""
