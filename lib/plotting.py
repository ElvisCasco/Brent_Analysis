"""Shared plotly helpers for SCM fits."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def save_html(fig, name, dir_=None, include_plotlyjs='cdn'):
    """Save a plotly figure to {dir_}/{name}.html and return the figure (chainable).

    Args:
        fig: plotly figure
        name: filename stem (no .html); the directory is created if missing
        dir_: directory to save into; if None, no save happens (figure is returned as-is)
        include_plotlyjs: 'cdn' (small file, requires internet) | 'inline' (~3MB self-contained)

    Returns:
        The figure unchanged — so you can chain: `save_html(plot_paths(...), name, dir_).show()`
    """
    if dir_ is not None:
        d = Path(dir_)
        d.mkdir(parents=True, exist_ok=True)
        fig.write_html(d / f'{name}.html', include_plotlyjs=include_plotlyjs)
    return fig


PALETTE = {
    'actual': '#111111',
    'synth':  '#d62728',
    'gap':    '#1f77b4',
    'gpr':    '#ff7f0e',
    'val':    '#3a8fb7',   # train/val boundary marker
}


def _add_window_markers(fig, t0, t_val_start=None):
    """Add a grey dotted vline at T_0 and an optional teal-dashed vline at train/val boundary."""
    fig.add_vline(x=t0, line_dash='dot', line_color='grey')
    fig.add_annotation(x=t0, y=1.02, yref='paper', text='T₀ (event)',
                       showarrow=False, font=dict(size=10, color='grey'),
                       xanchor='left')
    if t_val_start is not None:
        fig.add_vline(x=t_val_start, line_dash='dash', line_color=PALETTE['val'])
        fig.add_annotation(x=t_val_start, y=1.02, yref='paper', text='train | val',
                           showarrow=False, font=dict(size=10, color=PALETTE['val']),
                           xanchor='right')

MODEL_COLORS = {
    'convex_scm':     '#d62728',
    'ascm':           '#2ca02c',
    'elastic_net':    '#9467bd',
    'xgboost':        '#ff7f0e',
    'bayesian_ridge': '#1f77b4',
}


def plot_paths(result, title=None, t_val_start=None):
    """Observed vs synthetic Brent (in USD/bbl).

    t_val_start: optional date marking the train/val boundary (drawn as a teal-dashed vline).
    """
    actual = np.exp(result['actual'])
    synth = np.exp(result['synth'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual.index, y=actual.values, mode='lines', name='Observed Brent',
        line=dict(color=PALETTE['actual'], width=2),
    ))
    fig.add_trace(go.Scatter(
        x=synth.index, y=synth.values, mode='lines',
        name=f'Synthetic ({result["model"]})',
        line=dict(color=MODEL_COLORS.get(result['model'], PALETTE['synth']),
                  width=1.5, dash='dash'),
    ))
    _add_window_markers(fig, result['t0'], t_val_start)
    fig.update_layout(
        title=title or f'{result["model"]} — Observed vs synthetic Brent',
        yaxis_title='USD / bbl', xaxis_title='Date',
        template='plotly_white', hovermode='x unified',
        height=460,
        legend=dict(orientation='h', y=-0.18, x=0, xanchor='left', yanchor='top'),
        margin=dict(t=70, b=80, l=70, r=40),
    )
    return fig


def plot_gap(result, title=None, gpr=None, t_val_start=None):
    """Post-event gap (%) over time, optionally with GPR overlay.

    t_val_start: optional date marking the train/val boundary (drawn as a teal-dashed vline).
    """
    gap_pct = 100.0 * (np.exp(result['gap']) - 1.0)
    fig = make_subplots(specs=[[{'secondary_y': gpr is not None}]])
    fig.add_trace(go.Scatter(
        x=gap_pct.index, y=gap_pct.values, mode='lines', name='Gap (%)',
        line=dict(color=PALETTE['gap'], width=1.5), fill='tozeroy',
    ), secondary_y=False)
    if gpr is not None:
        g = gpr['GPRD_30d'].reindex(gap_pct.index).ffill()
        fig.add_trace(go.Scatter(
            x=g.index, y=g.values, mode='lines', name='GPR (30d MA)',
            line=dict(color=PALETTE['gpr'], width=1, dash='dash'),
        ), secondary_y=True)
        fig.update_yaxes(title_text='GPR', secondary_y=True, showgrid=False)
    fig.add_hline(y=0, line_color='black', line_width=0.5)
    _add_window_markers(fig, result['t0'], t_val_start)
    fig.update_yaxes(title_text='Brent − synthetic, %', secondary_y=False)
    fig.update_layout(
        title=title or f'{result["model"]} — Estimated gap (%)',
        template='plotly_white', hovermode='x unified', height=420,
        legend=dict(orientation='h', y=-0.20, x=0, xanchor='left', yanchor='top'),
        margin=dict(t=70, b=80, l=70, r=70),
    )
    return fig


def plot_weights(result, title=None, threshold=0.005):
    """Horizontal bar of donor weights / feature importances above threshold."""
    nz = result['weights'][result['weights'].abs() >= threshold].sort_values()
    if len(nz) == 0:
        return go.Figure().update_layout(title='No donor weight above threshold')
    fig = go.Figure(go.Bar(
        x=nz.values, y=nz.index, orientation='h',
        marker_color='steelblue',
        text=[f'{w:.3f}' for w in nz.values],
        textposition='outside', cliponaxis=False,
    ))
    fig.update_layout(
        title=title or f'{result["model"]} — Donor weights (|w| ≥ {threshold})',
        xaxis_title='weight / importance',
        template='plotly_white',
        height=max(280, 26 * len(nz) + 120),
        margin=dict(t=60, b=60, l=120, r=80),
    )
    return fig


def plot_ensemble_paths(results, title='Ensemble synthetic paths', t_val_start=None):
    """Overlay multiple models' synthetic paths on observed Brent."""
    if not results:
        return go.Figure()
    any_r = next(iter(results.values()))
    actual = np.exp(any_r['actual'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual.index, y=actual.values, mode='lines', name='Observed Brent',
        line=dict(color=PALETTE['actual'], width=2.5),
    ))
    for name, r in results.items():
        synth = np.exp(r['synth'])
        fig.add_trace(go.Scatter(
            x=synth.index, y=synth.values, mode='lines', name=name,
            line=dict(color=MODEL_COLORS.get(name, 'grey'), width=1.4, dash='dash'),
            opacity=0.85,
        ))
    _add_window_markers(fig, any_r['t0'], t_val_start)
    fig.update_layout(
        title=title, yaxis_title='USD / bbl', xaxis_title='Date',
        template='plotly_white', hovermode='x unified', height=500,
        legend=dict(orientation='h', y=-0.18, x=0, xanchor='left', yanchor='top'),
        margin=dict(t=70, b=90, l=70, r=40),
    )
    return fig


def plot_ensemble_gaps(results, title='Ensemble gap series', t_val_start=None):
    """Overlay multiple models' gap series."""
    if not results:
        return go.Figure()
    any_r = next(iter(results.values()))
    fig = go.Figure()
    for name, r in results.items():
        gap_pct = 100.0 * (np.exp(r['gap']) - 1.0)
        fig.add_trace(go.Scatter(
            x=gap_pct.index, y=gap_pct.values, mode='lines', name=name,
            line=dict(color=MODEL_COLORS.get(name, 'grey'), width=1.4),
            opacity=0.85,
        ))
    fig.add_hline(y=0, line_color='black', line_width=0.5)
    _add_window_markers(fig, any_r['t0'], t_val_start)
    fig.update_layout(
        title=title, yaxis_title='Brent − synthetic, %', xaxis_title='Date',
        template='plotly_white', hovermode='x unified', height=440,
        legend=dict(orientation='h', y=-0.20, x=0, xanchor='left', yanchor='top'),
        margin=dict(t=70, b=80, l=70, r=40),
    )
    return fig
