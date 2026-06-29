# Replication package

This branch is the replication package for the thesis *Pricing a Chokepoint: A
Synthetic-Control Estimate of the Brent Crude Premium from the 2026 Strait of Hormuz
Disruption* (Cherryl Chico, Elvis Casco, Nikoloz Darsalia, June 2026). It holds the code,
input data, and pinned environment needed to reproduce the synthetic-control analysis of
the Brent crude premium around the 2022 Russia invasion and the 2026 Strait of Hormuz
crisis. 

## Contents

- `lib/` — analysis library: data loading (`data.py`), the five SCM estimators
  (`models.py`), the validation battery (`validation.py`), configuration (`config.py`),
  and plotting.
- `notebooks/` — the pipeline, run in numeric order.
- `scripts/` — auxiliary robustness analyses (period robustness, donor contribution, VIX
  sensitivity, 19-donor refit).
- `data/` — the input series needed to run offline: Brent, the donor panel, the GPR
  index, the donor audit, the event timeline, and the EIA STEO files (see below).
- `pyproject.toml`, `uv.lock`, `.python-version` — the pinned Python environment.

## Environment

Python 3.12, managed with [uv](https://docs.astral.sh/uv/):

```
uv sync
```

This installs the exact dependency versions recorded in `uv.lock`.

## Running

Launch Jupyter from the synced environment and run the notebooks in numeric order:

```
uv run jupyter lab
```

Pipeline order:

1. `00_Data_Fetching` — pulls the donors from Yahoo Finance and Brent from the EIA.
2. `01_EDA` and `01.5_Donor_Cleanliness` — exploratory analysis and the donor SUTVA audit.
3. `02_Fit_Models` — fits the five-estimator ensemble per event and writes `data/results/`.
4. `02.5_Donor_Importance`, `03_Validate`, `04_Inference`, `05_Cross_Event`,
   `06_Ensemble_Final` — donor contribution, the validation battery, placebo inference,
   the cross-event weight transfer, and the headline ensemble.

## Data and reproducibility

The bundled `data/` includes the Brent and donor series used in the thesis, so the
analysis runs from `01` onward without re-fetching. Generated data is not tracked on this
branch and is rebuilt when you run the notebooks: `data/results/` and `data/validation/`,
the per-donor `data/donors/` files, and `data/daily_panel.csv`.

Re-running `00_Data_Fetching` pulls current data from Yahoo Finance and the EIA, which will
extend past the thesis sample (Brent through 22 June 2026, donors through 26 June 2026) and
so will not reproduce the thesis numbers exactly. For a faithful replication, skip
`00_Data_Fetching` and use the bundled data.
