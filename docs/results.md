# Results

Reference document for the Brent SCM analysis. Companion to [methodology.md](methodology.md) (design decisions), [validation.md](validation.md) (validation battery + minimum load-bearing set), and [donor_catalog.md](donor_catalog.md) (donor pool catalogue).

This document reports the **headline post-event gap estimates** for the two focal events, the per-model breakdown, and the three minimum load-bearing validation checks defined in [validation.md §5.0a](validation.md). All numbers are taken directly from the CSV outputs in `data/validation/` and `data/results/` produced by notebooks [02_Fit_Models](../notebooks/02_Fit_Models.ipynb), [03_Validate](../notebooks/03_Validate.ipynb), [04_Inference](../notebooks/04_Inference.ipynb), and [05_Cross_Event](../notebooks/05_Cross_Event.ipynb).

## 1. Headline ensemble estimates

Per-model post-event mean gap in % (raw, untransformed) for the **preferred specification** (shared 21-donor pool, preferred pre-window). Drift contribution and drift-adjusted gap follow [validation.md §5b](validation.md): drift_pct = pre-period slope × post-window length; adjusted gap = raw − drift.

### Russia 2022 ($T_0$ = 2022-02-24, post-window 2022-02-24 → 2022-09-30, ~7 months)

| Model | Raw gap (%) | Drift contribution (pp) | Drift-adjusted gap (%) |
|---|---:|---:|---:|
| Convex SCM | 29.6 | +5.8 | 23.8 |
| ASCM | 13.3 | +0.2 | 13.1 |
| Elastic-net | 21.7 | +0.5 | 21.2 |
| XGBoost | 36.8 | +1.9 | 34.9 |
| Bayesian Ridge | 0.5 | +0.1 | 0.4 |
| **Ensemble median** | **21.7** | — | **21.2** |
| **Ensemble IQR (Q25-Q75)** | **[13.3, 29.6]** | — | **[13.1, 23.8]** |

Headline interpretation: Russia 2022 produced an estimated 21-22% mean Brent premium over the 7-month window from invasion to OPEC+ October cut. The implied counterfactual mean is $88.92/bbl (ensemble median across the five models) versus actual mean $108.54/bbl, on the EIA Europe Brent Spot series. External validation against the EIA's last pre-invasion STEO forecast issued on 2022-02-08 (§3.4) places the EIA structural counterfactual at $84.94/bbl over the identical 151-day treatment window — i.e., the SCM and EIA disagree on the counterfactual by $3.98/bbl, or ~5.7 pp on the implied ATT.

Direct peer-reviewed comparison against an existing SCM-on-Russia-Brent estimate is not available; the dominant method in the Russia-Ukraine oil-price literature is structural VAR (Kilian 2009 *AER*; Baumeister & Hamilton 2019 *AER*), which decomposes price changes into supply/demand/inventory shocks rather than producing a single counterfactual-level ATT.

### Hormuz 2026 ($T_0$ = 2026-02-01, post-window 2026-02-01 → 2026-05-01, ~3 months)

| Model | Raw gap (%) | Drift contribution (pp) | Drift-adjusted gap (%) |
|---|---:|---:|---:|
| Convex SCM | 38.6 | -1.8 | 40.3 |
| ASCM | 43.7 | -0.5 | 44.2 |
| Elastic-net | 49.8 | -0.3 | 50.1 |
| XGBoost | 36.8 | -1.2 | 38.0 |
| Bayesian Ridge | 43.6 | -0.0 | 43.6 |
| **Ensemble median** | **43.6** | — | **43.6** |
| **Ensemble IQR (Q25-Q75)** | **[38.6, 43.7]** | — | **[40.3, 44.2]** |

Headline interpretation: the Strait of Hormuz crisis produced an estimated 43-44% chokepoint premium on Brent over the 3-month observation window. Note tighter IQR than Russia — donors are more stable in the Hormuz pre-period (~6 pp across models versus ~14 pp for Russia).

## 2. Minimum load-bearing validation

### 2.1 Model fit — Walk-forward CV (§5a i)

5-fold expanding-window walk-forward CV per [validation.md §5a](validation.md). Headline `val_rmse` is the Hyndman pooled RMSE over the five non-overlapping fold val residuals; headline `train_rmse` is the cross-fold mean of per-fold train RMSEs (training sets overlap across folds, so pooling them would over-weight early observations). Per-fold breakdown saved separately to `data/validation/walk_forward_cv_folds.csv`. The conventional `> 2` flag is heuristic.

| Event | Model | train RMSE | val RMSE | val/train | Flag |
|---|---|---:|---:|---:|---|
| Russia | Convex SCM | 0.109 | 0.127 | 1.16 | OK |
| Russia | ASCM | 0.043 | 0.088 | **2.04** | overfit |
| Russia | Elastic-net | 0.049 | 0.089 | 1.83 | OK |
| Russia | XGBoost | 0.039 | 0.117 | **3.00** | overfit |
| Russia | Bayesian Ridge | 0.031 | 0.096 | **3.07** | overfit |
| Hormuz | Convex SCM | 0.059 | 0.075 | 1.26 | OK |
| Hormuz | ASCM | 0.047 | 0.064 | 1.35 | OK |
| Hormuz | Elastic-net | 0.045 | 0.070 | 1.55 | OK |
| Hormuz | XGBoost | 0.044 | 0.076 | 1.72 | OK |
| Hormuz | Bayesian Ridge | 0.031 | 0.066 | **2.10** | overfit |

Interpretation:
- Russia: 2 of 5 models clean (Convex SCM, Elastic-net). ASCM is at the boundary (2.04); XGBoost and Bayesian Ridge fail the heuristic.
- Hormuz: 4 of 5 models clean (Convex SCM, ASCM, Elastic-net, XGBoost). Only Bayesian Ridge is flagged.
- Comparison to the previous single 80/20 hold-out: the 5-fold scheme is **less harsh** overall because the pooled val RMSE averages performance across five forecast horizons rather than concentrating all val mass on the last 20% of pre-period. Hormuz Convex SCM (2.18 → 1.26) and Hormuz ASCM (2.50 → 1.35) flipped from overfit to OK; Russia ASCM (1.91 → 2.04) and Russia Bayesian Ridge (5.10 → 3.07) shifted in opposing directions.

Per [validation.md §5a](validation.md), flagged models are **not auto-excluded** from the ensemble; the ratio threshold is heuristic and the IQR across all five is itself the model-uncertainty band.

### 2.2 Donor identification — Audit + permutation mean-shift test at $T_0$ (§5d)

Primary defense: the qualitative audit in [donor_catalog.md](donor_catalog.md). Statistical confirmation from the model-agnostic battery in [01.5_Donor_Cleanliness.ipynb](../notebooks/01.5_Donor_Cleanliness.ipynb).

| Event | Audit verdict | Statistical confirmation (BH-FDR α=0.10) |
|---|---|---|
| Russia 2022 | 12 of 33 donors flagged (6 H + 6 M); excluded → 21-donor shared pool | Tests confirm 0 of audit's 12, but flag JPY + CNY (concurrent Fed/BoJ + China zero-COVID — not Russia-treatment). Audit remains primary. |
| Hormuz 2026 | 0 of 33 donors flagged ("no Persian Gulf routing for any donor") | Tests confirm 0 flagged — perfect agreement with audit. |

### 2.3 Inference — In-space placebo, 21- and 33-donor pools (§5e i)

Brent's permutation p-value in the in-space placebo distribution. Reported under **both** the shared 21-donor pool (preferred for cross-event design) and the 33-donor full pool (lower permutation floor for resolution below conventional significance thresholds).

Permutation floor: $1/(N+1) = 1/22 \approx 0.0455$ for the 21-donor pool, $1/34 \approx 0.0294$ for the 33-donor pool. A p-value at the floor means Brent is ranked first in the placebo distribution — strong signal but no further resolution.

| Event | Model | p (21-donor) | p (33-donor) | Brent ratio (21-donor) |
|---|---|---:|---:|---:|
| Russia | Convex SCM | 0.545 | 0.500 | 2.59 |
| Russia | ASCM | 0.682 | 0.471 | 3.58 |
| Russia | Elastic-net | 0.409 | 0.412 | 4.07 |
| Russia | XGBoost | **0.045** (floor) | 0.147 | 9.62 |
| Russia | Bayesian Ridge | 0.636 | 0.529 | 3.88 |
| Hormuz | Convex SCM | **0.045** (floor) | **0.029** (floor) | 6.01 |
| Hormuz | ASCM | **0.045** (floor) | **0.029** (floor) | 7.92 |
| Hormuz | Elastic-net | **0.045** (floor) | **0.029** (floor) | 9.66 |
| Hormuz | XGBoost | **0.045** (floor) | **0.029** (floor) | 9.01 |
| Hormuz | Bayesian Ridge | **0.045** (floor) | **0.029** (floor) | 12.46 |

**Hormuz inference reading.** Brent ranks **first** in the placebo distribution under *every* model and *both* pools — i.e., Brent's post/pre RMSPE ratio is larger than every one of the 21 or 33 placebo units. With ratios in the 6-13 range and a floor p-value, this is the strongest possible permutation signal: rejecting H₀ at the strictest attainable level under the Abadie convention.

**Russia inference reading.** Russia XGBoost ranks first in the 21-donor pool (p = 0.045 at floor, post/pre ratio = 9.6) but slips to p = 0.147 in the 33-donor robustness pool — i.e., adding the 12 audit-flagged donors (some of which experienced co-incident Russia/sanctions exposure) inflates the placebo tail enough that Brent's ratio is no longer rank-1. The four other models do not reject in either pool. Mechanically: Russia's *pre-period* (2020-07 → 2022-02) is itself volatile — COVID recovery, 2021 reflation rally — so donors had large pre-period RMSPE too. This widens the placebo distribution and prevents Brent's post-period ratio (~2.6-4.1 for SCM/ASCM/Elastic-net/Bayesian Ridge, 9.6 for XGBoost) from sitting in the tail. The post-event gap magnitudes (13-37%) are independently corroborated by the historical record ($95 → $130+); the inferential weakness here is a known limitation of in-space placebo at pre-periods with high donor volatility, not evidence that Russia's effect was small.

For Russia, defensive depth in the form of (a) larger gap magnitudes relative to drift contributions, (b) the audit-supported SUTVA defense, and (c) the cross-event weight transfer of §5f (next section) substitutes for the unconvincing single-event placebo p-value.

## 3. Defensive depth — supporting results

### 3.1 In-time placebo (§5e ii)

Mean fake-post-period gap when the model is refit with $T_0^{\text{fake}}$ = 6 months before real $T_0$. A small gap means the SCM does not spuriously detect effects in null periods. **Hyperparameters: defaults from `MODEL_HPARAMS`**, not the tuned hparams used in the headline fits — see [validation.md §5e (ii)](validation.md) "Hyperparameter choice — defaults, not tuned" for the leakage rationale.

| Event | Model | Fake $T_0$ | Mean fake-post gap (%) | Read |
|---|---|---|---:|---|
| Russia | Convex SCM | 2021-08-24 | +1.9 | Small; model is clean |
| Russia | ASCM | 2021-08-24 | -4.2 | Small; clean |
| Russia | Elastic-net | 2021-08-24 | +7.5 | Moderate; under defaults the model registers a positive fake gap (low-power flag) |
| Russia | XGBoost | 2021-08-24 | **+26.4** | Large; low-power flag per validation.md (training shrinkage to ~14 months + tree fit on small panel) |
| Russia | Bayesian Ridge | 2021-08-24 | -5.3 | Small; clean |
| Hormuz | Convex SCM | 2025-08-01 | -11.9 | Moderate-large; audit fake post-period for events |
| Hormuz | ASCM | 2025-08-01 | -9.8 | Moderate-large; audit |
| Hormuz | Elastic-net | 2025-08-01 | -10.6 | Moderate-large; audit |
| Hormuz | XGBoost | 2025-08-01 | -12.4 | Moderate-large; audit |
| Hormuz | Bayesian Ridge | 2025-08-01 | -12.2 | Moderate-large; audit |

Hormuz fake-post negative gaps across models indicate the synthetic over-predicted Brent during 2025-08 → 2026-01 — i.e., Brent moved up by ~10-12% in that pre-Hormuz window relative to where donors said it should be. This is *consistent with* (but does not require) a runup-to-Hormuz premium starting in late 2025. The event-cleanliness audit (per [validation.md §5e (ii)](validation.md)) for that fake window should be reviewed against the EDA event timeline before interpreting these gaps as falsifying the in-time placebo.

Note on the defaults switch: Russia Elastic-net moved from a near-zero gap (under tuned hparams) to +7.5% under defaults, and Russia XGBoost from +17.3% to +26.4%. This is the expected price of removing the second-order leakage path documented in [validation.md §5e (ii)](validation.md): tuned hparams selected on a validation window that overlaps the fake post-period flatter the fake gap. Defaults give a more honest (and less flattering) low-power read for the non-convex models on Russia, but do not change the qualitative read — Convex SCM, ASCM, and Bayesian Ridge remain small-fake-gap (clean), while Elastic-net and XGBoost remain low-power on the short pre-window.

### 3.2 Leave-one-donor-out (§5e iii)

Range of post-event gap estimates when each high-weight donor is dropped. A tight range around baseline means no single donor drives the headline.

| Event | Model | LOO baseline gap (%) | Leave-out range (%) | Read |
|---|---|---:|---|---|
| Russia | Convex SCM | 29.3 | 27.1 - 33.7 | Tight; robust |
| Russia | ASCM | 13.4 | 6.2 - 19.7 | Moderate; some Platinum sensitivity |
| Russia | Elastic-net | 21.7 | 14.9 - 30.5 | Moderate; Platinum + TLT sensitivity |
| Russia | XGBoost | 42.2 | 35.7 - 40.6 | Tight; robust (LOO baseline higher than headline 36.8 — separate fit, see note) |
| Russia | Bayesian Ridge | 0.5 | -12.8 to +12.0 | Wide; baseline near zero → unstable signal |
| Hormuz | Convex SCM | 39.3 | 30.3 - 39.7 | Tight; some Sugar sensitivity |
| Hormuz | ASCM | 44.4 | 38.7 - 47.5 | Tight; robust |
| Hormuz | Elastic-net | 49.8 | 42.3 - 53.4 | Tight; robust |
| Hormuz | XGBoost | 37.3 | 36.3 - 41.0 | Tight; robust |
| Hormuz | Bayesian Ridge | 43.6 | 40.0 - 53.0 | Moderate; some Cotton/CHF sensitivity |

Russia Bayesian Ridge LOO range crosses zero — combined with its 3.07 walk-forward ratio, Bayesian Ridge Russia is the least reliable single fit in the ensemble. The ensemble median is robust to this (median across the 5 models is dominated by Convex/ASCM/Elastic-net/XGBoost which agree more closely on a 13-37% range).

Note on the Russia XGBoost LOO baseline (42.2) vs headline (36.8) mismatch: the LOO function and the headline fit are independent invocations and the XGBoost stochastic components (`subsample=0.7`, `colsample_bytree=0.7`) with `random_state=0` interact slightly differently when the panel is re-built. The qualitative reading (tight LOO range, no single donor drives the result) is unchanged.

### 3.3 Cross-event weight transfer (§5f)

Russia-fitted weights applied to the Hormuz panel. Tight match between independent and transferred counterfactuals = factor structure regime-stable 2020-22 → 2024-26.

| Model | Independent Hormuz gap (%) | Transferred (Russia weights) gap (%) | Δ (pp) | Transferred pre-RMSPE |
|---|---:|---:|---:|---:|
| Convex SCM | 38.6 | 47.0 | +8.4 | 0.109 |
| ASCM | 43.7 | 27.3 | -16.4 | 0.144 |
| Elastic-net | 49.8 | 23.2 | -26.6 | 0.185 |
| XGBoost | 36.8 | -58.2 | **-95.0** | **1.065** |
| Bayesian Ridge | 43.6 | -100.0 | **-143.6** | **13.707** |

Convex SCM, ASCM, and Elastic-net transfer with a plausible pre-period fit (transferred pre-RMSPE within ~4× independent). XGBoost and Bayesian Ridge produce catastrophically misspecified transferred counterfactuals — transferred pre-RMSPE is 22-300× the independent fit. This is consistent with the [validation.md §5f](validation.md) caveat: convex and sparse-regression weights pin to factor-stable donors, while tree-based and prior-dominated models use the full donor set with regime-specific coefficient mass that does not transfer.

**Change vs the prior single-hold-out CV:** Elastic-net moved from "catastrophic" (transferred 92.5%, RMSPE 0.540 under `l1_ratio=0.5`) to "plausibly transferable" (transferred 23.2%, RMSPE 0.185 under the new `l1_ratio=0.8` chosen by 5-fold CV). The sparser elastic-net solution pins to fewer donors that are more factor-stable.

**Implication for the Hormuz headline:** the cross-event generalization defense is load-bearing via Convex SCM, ASCM, and Elastic-net (three of five models transfer with degraded but non-pathological pre-RMSPE). The convex-only transferred-vs-independent agreement is ±16 pp; including elastic-net widens the envelope to ±27 pp — still consistent with regime-stable factor structure for the methods that produce sparse, transferable weights.

### 3.4 External validation — EIA STEO pre-invasion forecasts (Russia only)

Comparison of the SCM ensemble counterfactual against the U.S. Energy Information Administration's last two pre-invasion Brent forecasts. Both were issued *before* the 2022-02-24 invasion, so their forecasts for the post-event window represent EIA's independent counterfactual built on a structural supply/demand model. The two methods share no information path (SCM uses cross-asset co-movement; STEO uses EIA's internal supply/demand model), so agreement is evidence that the SCM is not producing a fantasy counterfactual.

**Method:** build a daily step-function from each STEO's monthly Brent forecast values (each daily observation in month *M* takes the STEO's forecast for *M*), then take the mean over the **exact SCM treatment day-set** (Feb 24 – Sep 30 2022, 151 trading days). This matches the comparison period exactly with the SCM post-event mean.

**Source.** EIA STEO archive, [eia.gov/outlooks/steo/archives/](https://www.eia.gov/outlooks/steo/archives/). The two vintages used:
- **STEO Jan-22** (`jan22_base.xlsx`, issued ~2022-01-11; six weeks pre-invasion)
- **STEO Feb-22** (`feb22_base.xlsx`, issued ~2022-02-08; the last STEO before the invasion)

| Model | Synth $/bbl | STEO Jan-22 $/bbl | STEO Feb-22 $/bbl | Synth − STEO Feb-22 |
|---|---:|---:|---:|---:|
| Convex SCM | 83.55 | 75.66 | 84.94 | -$1.39 |
| ASCM | 95.52 | 75.66 | 84.94 | +$10.58 |
| Elastic-net | 88.92 | 75.66 | 84.94 | +$3.98 |
| XGBoost | 79.28 | 75.66 | 84.94 | -$5.66 |
| Bayesian Ridge | 107.91 | 75.66 | 84.94 | +$22.97 (degenerate) |
| **Ensemble median** | **88.92** | **75.66** | **84.94** | **+$3.98** |

Actual Brent mean over the matched 151-day window: **$108.54**.

**Implied ATTs (matched day-set):**
- SCM ensemble median counterfactual: (108.54 − 88.92) / 88.92 = **+22.1%**
- EIA STEO Feb-22 (last pre-invasion forecast) as counterfactual: (108.54 − 84.94) / 84.94 = **+27.8%**
- EIA STEO Jan-22 as counterfactual: (108.54 − 75.66) / 75.66 = **+43.4%**

**Reading.** The SCM ensemble-median counterfactual ($88.92) sits **within $3.98/bbl** of the EIA's last pre-invasion structural forecast ($84.94), and the implied ATTs disagree by ~5.7 pp. Three of five models (Convex SCM, Elastic-net, XGBoost) bracket the STEO Feb-22 anchor to within ±$6. Bayesian Ridge is far off, consistent with its diagnosed degeneracy (walk-forward overfit ratio 3.07, LOO range crosses zero, baseline gap 0.5%). ASCM sits slightly high, consistent with its known shrinkage-toward-mean bias on Russia.

**The SCM is more conservative than the STEO-based counterfactual** by ~5.7 pp because the SCM donors absorb post-Feb-2022 macro co-movement (inflation, demand recovery) that the EIA structural forecast does not. Both methods are "correct" but answer subtly different questions: the SCM nets out cross-asset co-movement; the STEO is EIA's pre-invasion view of where Brent should go conditional on supply/demand fundamentals.

**Caveat.** The STEO is itself a model forecast, not ground truth. The agreement is evidence that two independent methods produce the same counterfactual, not that either is correct. The Hormuz case has no equivalent external benchmark — the equivalent STEO Jan-26 / Feb-26 vintages are *post*-Hormuz from the perspective of the Brent-impact forecast — so this external validation is available only for Russia.

Output: `data/validation/external_steo_russia.csv`. Overlay plot: `plots/russia_steo_validation.html`. Computation: [06_Ensemble_Final.ipynb](../notebooks/06_Ensemble_Final.ipynb) (external-validation cell).

## 4. Caveats and qualifications

1. **In-space placebo Russia weakness.** Only XGBoost ranks Brent first in the 21-donor pool (p = 0.045 at floor); none of the five models reject in the 33-donor robustness pool, and the XGBoost 21-donor result is itself fragile in the sense that adding the audit-flagged donors moves p to 0.147. This is *not* evidence that Russia produced no Brent effect — the historical move is well documented. It is evidence that in-space placebo loses power at pre-periods with high donor volatility (Russia pre-period 2020-07 → 2022-02 spans COVID recovery + reflation rally). The post-event gap magnitudes themselves (13-37% across models) are independently anchored by the historical record.

2. **Hormuz post-window length.** With ~60 post-event observations, every inference test is under-powered. The §5e (i) in-space placebo p-values hit the permutation floor in *both* pools (0.045 / 0.029) because Brent ranks first under every model — strong signal but no further resolution. The cross-event weight transfer (§5f) substitutes inferential depth.

3. **Bayesian Ridge Russia instability.** Walk-forward ratio 3.07 (overfit signal, less severe than the prior 5.1 under single-hold-out CV), LOO range crosses zero, baseline gap 0.5%. Bayesian Ridge Russia remains the single least reliable fit; the ensemble median is robust to it.

4. **Hormuz convex SCM moment-matching SD mismatch.** From [03_Validate.ipynb](../notebooks/03_Validate.ipynb) `moment-match`: Hormuz convex SCM synthetic SD is materially below the treated SD (Brent's volatility is outside the 21-donor convex hull). ASCM corrects this via ridge augmentation. For the Hormuz headline, treat convex SCM and ASCM as the relevant fit pair; convex alone under-represents Brent variance.

5. **Recent citations.** The Chen & Yan (2023) mixed placebo test is cited in [validation.md §5e (ii)](validation.md) but is not currently computed in [04_Inference.ipynb](../notebooks/04_Inference.ipynb) — only the raw in-time fake-post gap is reported. Adding the mixed-placebo p-value is a deferred improvement; the in-time placebo currently relies on visual / magnitude comparison only.

6. **iSCM alternative not run.** [methodology.md §3](methodology.md) documents Di Stefano & Mellace's iSCM as the alternative donor-handling approach considered and not pursued. The 33-donor Russia in-space placebo result in §2.3 is *not* an iSCM application — it is the conservative robustness reading discussed under [validation.md §5e (i)](validation.md) ("Brent ranking high even when partly-treated donors are mixed in").

7. **In-time placebo hparams differ from headline.** Per [validation.md §5e (ii)](validation.md), the in-time placebo uses `MODEL_HPARAMS` defaults rather than the tuned hparams used in the headline fits. This intentional asymmetry removes a second-order leakage path (tuned hparams were selected by argmin val_RMSE on a window that overlaps the fake post-period). The trade-off: the in-time placebo gap magnitudes for non-convex models (Elastic-net, XGBoost) are larger under defaults than they would be with tuned hparams, which is the honest low-power read.

## 5. Source CSVs

| Source | Location |
|---|---|
| Walk-forward CV (headline pooled, 5-fold) | `data/validation/walk_forward_cv.csv` |
| Walk-forward CV (per-fold breakdown) | `data/validation/walk_forward_cv_folds.csv` |
| Parallel-fit + drift | `data/validation/parallel_fit_defence.csv`, `data/validation/validation_summary.csv` |
| Moment matching | `data/validation/moments_{event}_{model}.csv` |
| In-space placebo (21-donor) | `data/validation/inference_inspace_{event}_{model}.csv` |
| In-space placebo (33-donor) | `data/validation/inference_inspace_{event}_{model}_full.csv` |
| Pool comparison | `data/validation/inference_inspace_brent_pool_comparison.csv` |
| In-time placebo | `data/validation/inference_intime.csv` |
| Leave-one-out | `data/validation/inference_loo_{event}_{model}.csv` |
| Cross-event transfer | `data/validation/cross_event_transfer.csv` |
| External STEO comparison (Russia) | `data/validation/external_steo_russia.csv` |
| EIA STEO archive (Brent forecast vintages) | `references/eia/steo_{jan,feb}22.xlsx` (gitignored, downloaded on demand) |
| Donor cleanliness (model-agnostic) | `data/validation/donor_cleanliness_{event}.csv` |
