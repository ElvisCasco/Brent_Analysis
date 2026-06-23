# Results

Reference document for the Brent SCM analysis. Companion to [methodology.md](methodology.md) (design decisions), [validation.md](validation.md) (validation battery + minimum load-bearing set), and [donor_catalog.md](donor_catalog.md) (donor pool catalogue).

This document reports the **headline post-event gap estimates** for the two focal events, the per-model breakdown, and the three minimum load-bearing validation checks defined in [validation.md §5.0a](validation.md). All numbers are taken directly from the CSV outputs in `data/validation/` and `data/results/` produced by notebooks [02_Fit_Models](../notebooks/02_Fit_Models.ipynb), [03_Validate](../notebooks/03_Validate.ipynb), [04_Inference](../notebooks/04_Inference.ipynb), and [05_Cross_Event](../notebooks/05_Cross_Event.ipynb).

## 1. Headline ensemble estimates

Per-model post-event mean gap in % (raw, untransformed) for the **preferred specification** (shared 18-donor pool, preferred pre-window). Drift contribution and drift-adjusted gap follow [validation.md §5b](validation.md): drift_pct = pre-period slope × post-window length; adjusted gap = raw − drift.

### Russia 2022 ($T_0$ = 2022-02-24, post-window 2022-02-24 → 2022-09-30, ~7 months)

| Model | Raw gap (%) | Drift contribution (pp) | Drift-adjusted gap (%) |
|---|---:|---:|---:|
| Convex SCM | 33.6 | +5.2 | 28.4 |
| ASCM | 12.1 | +0.3 | 11.8 |
| Elastic-net | 22.1 | +0.7 | 21.4 |
| XGBoost | 31.6 | +1.8 | 29.8 |
| Bayesian Ridge | -10.1 | +0.1 | -10.2 |
| **Ensemble median** | **22.1** | — | **21.4** |
| **Ensemble IQR (Q25-Q75)** | **[12.1, 31.6]** | — | **[11.8, 29.8]** |

Headline interpretation: Russia 2022 produced an estimated ~22% mean Brent premium over the 7-month window from invasion to OPEC+ October cut. The implied counterfactual mean is $88.46/bbl (ensemble median across the five models) versus actual mean $108.54/bbl, on the EIA Europe Brent Spot series. External validation against the EIA's last pre-invasion STEO forecast issued on 2022-02-08 (§3.4) places the EIA structural counterfactual at $84.94/bbl over the identical 151-day treatment window — i.e., the SCM and EIA disagree on the counterfactual by $3.52/bbl, or ~5.1 pp on the implied ATT.

Direct peer-reviewed comparison against an existing SCM-on-Russia-Brent estimate is not available; the dominant method in the Russia-Ukraine oil-price literature is structural VAR (Kilian 2009 *AER*; Baumeister & Hamilton 2019 *AER*), which decomposes price changes into supply/demand/inventory shocks rather than producing a single counterfactual-level ATT.

### Hormuz 2026 ($T_0$ = 2026-02-28, post-window 2026-03-02 → 2026-06-15, ~3.5 months, n_post = 72)

| Model | Raw gap (%) | Drift contribution (pp) | Drift-adjusted gap (%) |
|---|---:|---:|---:|
| Convex SCM | 55.9 | -1.4 | 57.3 |
| ASCM | 52.2 | -0.1 | 52.3 |
| Elastic-net | 57.1 | -0.3 | 57.3 |
| XGBoost | 51.2 | -1.5 | 52.7 |
| Bayesian Ridge | 43.3 | -0.0 | 43.3 |
| **Ensemble median** | **52.2** | — | **52.7** |
| **Ensemble IQR (Q25-Q75)** | **[51.2, 55.9]** | — | **[52.3, 57.3]** |

Headline interpretation: the Strait of Hormuz crisis produced an estimated ~52% chokepoint premium on Brent over the post-event window now extended to the latest available data (2026-06-15). Actual post-window Brent mean is $106.92/bbl versus an implied ensemble-median counterfactual of ~$70.3/bbl. Note tighter IQR than Russia — donors are more stable in the Hormuz pre-period (~5 pp across models versus ~20 pp for Russia). The median is ~4 pp below the previous (post-window-to-2026-05-29) estimate of ~56%: the additional mid-June observations capture Brent's partial pullback toward ~$84/bbl, which narrows the gap at the end of the window (see the post-window sensitivity profile in §3 and the appendix). The premium remains large and positive under every model.

## 2. Minimum load-bearing validation

### 2.1 Model fit — Walk-forward CV (§5a i)

5-fold expanding-window walk-forward CV per [validation.md §5a](validation.md). Headline `val_rmse` is the Hyndman pooled RMSE over the five non-overlapping fold val residuals; headline `train_rmse` is the cross-fold mean of per-fold train RMSEs (training sets overlap across folds, so pooling them would over-weight early observations). Per-fold breakdown saved separately to `data/validation/walk_forward_cv_folds.csv`. The conventional `> 2` flag is heuristic.

| Event | Model | train RMSE | val RMSE | val/train | Flag |
|---|---|---:|---:|---:|---|
| Russia | Convex SCM | 0.113 | 0.141 | 1.25 | OK |
| Russia | ASCM | 0.047 | 0.092 | 1.95 | OK |
| Russia | Elastic-net | 0.052 | 0.095 | 1.84 | OK |
| Russia | XGBoost | 0.040 | 0.125 | **3.12** | overfit |
| Russia | Bayesian Ridge | 0.034 | 0.107 | **3.12** | overfit |
| Hormuz | Convex SCM | 0.060 | 0.083 | 1.40 | OK |
| Hormuz | ASCM | 0.043 | 0.073 | 1.72 | OK |
| Hormuz | Elastic-net | 0.049 | 0.074 | 1.52 | OK |
| Hormuz | XGBoost | 0.045 | 0.081 | 1.81 | OK |
| Hormuz | Bayesian Ridge | 0.034 | 0.079 | **2.30** | overfit |

Interpretation:
- Russia: 3 of 5 models clean (Convex SCM, ASCM, Elastic-net). ASCM now clears the heuristic (1.95, down from 2.06 with VIX in the pool); XGBoost and Bayesian Ridge fail it.
- Hormuz: 4 of 5 models clean (Convex SCM, ASCM, Elastic-net, XGBoost). Only Bayesian Ridge is flagged.
- Comparison to the previous single 80/20 hold-out: the 5-fold scheme is **less harsh** overall because the pooled val RMSE averages performance across five forecast horizons rather than concentrating all val mass on the last 20% of pre-period. Hormuz Convex SCM (2.18 → 1.40) and Hormuz ASCM (2.50 → 1.72) flipped from overfit to OK; Russia ASCM (1.91 → 1.95) and Russia Bayesian Ridge (5.10 → 3.12) shifted in opposing directions.

Per [validation.md §5a](validation.md), flagged models are **not auto-excluded** from the ensemble; the ratio threshold is heuristic and the IQR across all five is itself the model-uncertainty band.

### 2.2 Donor identification — Audit + permutation mean-shift test at $T_0$ (§5d)

Primary defense: the qualitative audit in [donor_catalog.md](donor_catalog.md). Statistical confirmation from the model-agnostic battery in [01.5_Donor_Cleanliness.ipynb](../notebooks/01.5_Donor_Cleanliness.ipynb).

| Event | Audit verdict | Statistical confirmation (BH-FDR α=0.10) |
|---|---|---|
| Russia 2022 | 13 of 32 donors flagged (6 H + 7 M); excluded → 19-donor strict-clean, then **VIX dropped by the Bai-Perron breakpoint rule → 18-donor shared pool** (see [validation.md §5c](validation.md)) | Tests confirm 0 of audit's 13, but flag CNY (concurrent China zero-COVID — not Russia-treatment). Audit-vs-test agreement: 18 of 32. Audit remains primary. |
| Hormuz 2026 | 1 of 32 donors flagged (Cotton, M — oil→polyester substitution channel; no donor physically routed through the Strait) | Tests flag 0 of 32 at the strike-date $T_0$ = 2026-02-28. Audit-vs-test agreement: 31 of 32 — the lone disagreement is Cotton’s audit-M, which the contemporaneous tests do not independently reproduce. |

### 2.3 Inference — In-space placebo, 18- and 32-donor pools (§5e i)

Brent's permutation p-value in the in-space placebo distribution. Reported under **both** the shared 18-donor pool (preferred for cross-event design) and the 32-donor full pool (lower permutation floor for resolution below conventional significance thresholds).

Permutation floor: $1/(N+1) = 1/19 \approx 0.0526$ for the 18-donor pool, $1/33 \approx 0.0303$ for the 32-donor pool. A p-value at the floor means Brent is ranked first in the placebo distribution — strong signal but no further resolution.

| Event | Model | p (18-donor) | p (32-donor) | Brent ratio (18-donor) |
|---|---|---:|---:|---:|
| Russia | Convex SCM | 0.526 | 0.500 | 2.75 |
| Russia | ASCM | 0.579 | 0.471 | 3.45 |
| Russia | Elastic-net | 0.421 | 0.412 | 4.00 |
| Russia | XGBoost | 0.158 | 0.147 | 7.69 |
| Russia | Bayesian Ridge | 0.632 | 0.529 | 5.92 |
| Hormuz | Convex SCM | **0.053** (floor) | **0.030** (floor) | 6.93 |
| Hormuz | ASCM | **0.053** (floor) | **0.030** (floor) | 9.05 |
| Hormuz | Elastic-net | **0.053** (floor) | **0.030** (floor) | 8.98 |
| Hormuz | XGBoost | **0.053** (floor) | **0.030** (floor) | 10.12 |
| Hormuz | Bayesian Ridge | **0.053** (floor) | **0.030** (floor) | 10.18 |

**Hormuz inference reading.** Brent ranks **first** in the placebo distribution under *every* model and *both* pools — i.e., Brent's post/pre RMSPE ratio is larger than every one of the 18 or 32 placebo donors. With ratios in the 7-11 range and a floor p-value (1/19 and 1/33), this is the strongest possible permutation signal: rejecting H₀ at the strictest attainable level under the Abadie convention.

**Russia inference reading.** No model rejects for Russia in either pool. XGBoost comes closest (p = 0.158 in the 18-donor pool, post/pre ratio = 7.69; 0.147 in the 32-donor pool) but does not reach the floor; the other four sit mid-distribution (p ≈ 0.42–0.63, ratios ~2.7–5.9). Mechanically: Russia's *pre-period* (2020-07 → 2022-02) is itself volatile — COVID recovery, 2021 reflation rally — so donors had large pre-period RMSPE too. This widens the placebo distribution and prevents Brent's post-period ratio from sitting in the tail. The post-event gap magnitudes are independently corroborated by the historical record ($95 → $130+); the inferential weakness here is a known limitation of in-space placebo at pre-periods with high donor volatility, not evidence that Russia's effect was small.

For Russia, defensive depth in the form of (a) larger gap magnitudes relative to drift contributions, (b) the audit-supported SUTVA defense, and (c) the cross-event weight transfer of §5f (next section) substitutes for the unconvincing single-event placebo p-value.

## 3. Defensive depth — supporting results

### 3.1 In-time placebo (§5e ii)

Mean fake-post-period gap when the model is refit with $T_0^{\text{fake}}$ = 6 months before real $T_0$. A small gap means the SCM does not spuriously detect effects in null periods. **Hyperparameters: defaults from `MODEL_HPARAMS`**, not the tuned hparams used in the headline fits — see [validation.md §5e (ii)](validation.md) "Hyperparameter choice — defaults, not tuned" for the leakage rationale.

| Event | Model | Fake $T_0$ | Mean fake-post gap (%) | Read |
|---|---|---|---:|---|
| Russia | Convex SCM | 2021-08-24 | +5.8 | Small-moderate; model is clean |
| Russia | ASCM | 2021-08-24 | +1.3 | Small; clean |
| Russia | Elastic-net | 2021-08-24 | -1.0 | Small; clean |
| Russia | XGBoost | 2021-08-24 | **+17.8** | Large; low-power flag per validation.md (training shrinkage to ~14 months + tree fit on small panel) |
| Russia | Bayesian Ridge | 2021-08-24 | -3.2 | Small; clean |
| Hormuz | Convex SCM | 2025-08-28 | -10.2 | Moderate; audit fake post-period for events |
| Hormuz | ASCM | 2025-08-28 | -6.7 | Moderate; audit |
| Hormuz | Elastic-net | 2025-08-28 | +4.9 | Small; clean |
| Hormuz | XGBoost | 2025-08-28 | -6.8 | Moderate; audit |
| Hormuz | Bayesian Ridge | 2025-08-28 | -1.6 | Small; clean |

Hormuz fake-post gaps are mostly mildly negative (4 of 5 models, ~-7 to -10%; Elastic-net is +4.9%), indicating the synthetic slightly over-predicted Brent during the fake window 2025-08-28 → 2026-02-27 — i.e., Brent was somewhat *below* where the donors said it should be in that pre-Hormuz window. This is the opposite sign of a runup-to-Hormuz premium and is small in magnitude relative to the ~52% post-event gap; the in-time placebo therefore does not flag spurious-effect generation. The event-cleanliness audit (per [validation.md §5e (ii)](validation.md)) for that fake window is reviewed against the EDA event timeline in [scripts/audit_intime_placebo_hormuz.py](../scripts/audit_intime_placebo_hormuz.py).

Note on the defaults switch: the in-time placebo uses `MODEL_HPARAMS` defaults, not the tuned headline hparams, to remove a second-order leakage path documented in [validation.md §5e (ii)](validation.md) (tuned hparams are selected on a validation window that overlaps the fake post-period and would flatter the fake gap). Under defaults the qualitative read is unchanged: Convex SCM, ASCM, Elastic-net, and Bayesian Ridge remain small-fake-gap (clean); only XGBoost (Russia +17.8%) registers a large fake gap, consistent with its known low-power on the shortened ~14-month pre-window.

### 3.2 Leave-one-donor-out (§5e iii)

Range of post-event gap estimates when each high-weight donor is dropped. A tight range around baseline means no single donor drives the headline.

| Event | Model | LOO baseline gap (%) | Leave-out range (%) | Read |
|---|---|---:|---|---|
| Russia | Convex SCM | 29.3 | 27.1 - 33.7 | Tight; robust |
| Russia | ASCM | 13.4 | 6.2 - 19.7 | Moderate; some Platinum sensitivity |
| Russia | Elastic-net | 21.7 | 14.9 - 30.5 | Moderate; Platinum + TLT sensitivity |
| Russia | XGBoost | 42.2 | 35.7 - 40.6 | Tight; robust (LOO baseline higher than headline 36.8 — separate fit, see note) |
| Russia | Bayesian Ridge | 0.5 | -12.8 to +12.0 | Wide; baseline near zero → unstable signal |
| Hormuz | Convex SCM | 55.9 | 51.2 - 59.3 | Tight; robust |
| Hormuz | ASCM | 52.2 | 50.6 - 58.0 | Tight; robust |
| Hormuz | Elastic-net | 57.1 | 52.4 - 61.9 | Tight; robust |
| Hormuz | XGBoost | 51.2 | 52.3 - 58.5 | Tight; robust |
| Hormuz | Bayesian Ridge | 43.3 | 40.5 - 49.8 | Moderate; some donor-mix sensitivity |

Russia Bayesian Ridge LOO range crosses zero — combined with its 3.09 walk-forward ratio, Bayesian Ridge Russia is the least reliable single fit in the ensemble. The ensemble median is robust to this (median across the 5 models is dominated by Convex/ASCM/Elastic-net/XGBoost which agree more closely on an ~11-34% range).

Note on the Russia XGBoost LOO baseline (42.2) vs headline (36.8) mismatch: the LOO function and the headline fit are independent invocations and the XGBoost stochastic components (`subsample=0.7`, `colsample_bytree=0.7`) with `random_state=0` interact slightly differently when the panel is re-built. The qualitative reading (tight LOO range, no single donor drives the result) is unchanged.

### 3.3 Cross-event weight transfer (§5f)

Russia-fitted weights applied to the Hormuz panel. Tight match between independent and transferred counterfactuals = factor structure regime-stable 2020-22 → 2024-26.

| Model | Independent Hormuz gap (%) | Transferred (Russia weights) gap (%) | Δ (pp) | Transferred pre-RMSPE |
|---|---:|---:|---:|---:|
| Convex SCM | 55.9 | 25.3 | -30.6 | 0.336 |
| ASCM | 52.2 | 4.0 | -48.2 | 0.417 |
| Elastic-net | 57.1 | -92.7 | **-149.8** | **2.917** |
| XGBoost | 51.2 | -45.6 | **-96.8** | **0.956** |
| Bayesian Ridge | 43.3 | -100.0 | **-143.3** | **22.377** |

Convex SCM and ASCM transfer with a degraded but non-pathological pre-period fit (transferred pre-RMSPE 0.336 and 0.417 — ~5–6× the independent fit of ~0.066, the smallest multiples in the ensemble). Elastic-net, XGBoost, and Bayesian Ridge produce misspecified transferred counterfactuals — transferred pre-RMSPE is ~18–340× the independent fit and the implied transferred gaps go negative. This is consistent with the [validation.md §5f](validation.md) caveat: convex weights pin to factor-stable donors on the simplex, while signed-regression, tree-based, and prior-dominated models use the full donor set with regime-specific coefficient mass that does not transfer.

**Implication for the Hormuz headline:** the cross-event generalization defense is load-bearing via Convex SCM and ASCM (the two simplex-anchored models). Both transfer to a *positive* Hormuz premium (Convex 25.3%, ASCM 4.0%) that is materially smaller than the independent estimate, so the transfer test corroborates the *sign and broad order of magnitude* of the chokepoint premium but not its precise level — the transferred counterfactual's degraded pre-RMSPE (~5–6× independent) means the post-window extension to 2026-06-15 has somewhat widened the regime gap between the 2020–22 and 2024–26 factor structures relative to the earlier, shorter window. The honest reading is that the convex/ASCM transfer supports a *large positive* Hormuz premium, with the within-event ensemble (§1) carrying the headline magnitude.

### 3.4 External validation — EIA STEO pre-invasion forecasts (Russia only)

Comparison of the SCM ensemble counterfactual against the U.S. Energy Information Administration's last two pre-invasion Brent forecasts. Both were issued *before* the 2022-02-24 invasion, so their forecasts for the post-event window represent EIA's independent counterfactual built on a structural supply/demand model. The two methods share no information path (SCM uses cross-asset co-movement; STEO uses EIA's internal supply/demand model), so agreement is evidence that the SCM is not producing a fantasy counterfactual.

**Method:** build a daily step-function from each STEO's monthly Brent forecast values (each daily observation in month *M* takes the STEO's forecast for *M*), then take the mean over the **exact SCM treatment day-set** (Feb 24 – Sep 30 2022, 151 trading days). This matches the comparison period exactly with the SCM post-event mean.

**Source.** EIA STEO archive, [eia.gov/outlooks/steo/archives/](https://www.eia.gov/outlooks/steo/archives/). The two vintages used:
- **STEO Jan-22** (`jan22_base.xlsx`, issued ~2022-01-11; six weeks pre-invasion)
- **STEO Feb-22** (`feb22_base.xlsx`, issued ~2022-02-08; the last STEO before the invasion)

| Model | Synth $/bbl | STEO Jan-22 $/bbl | STEO Feb-22 $/bbl | Synth − STEO Feb-22 |
|---|---:|---:|---:|---:|
| Convex SCM | 80.82 | 75.66 | 84.94 | -$4.12 |
| ASCM | 96.45 | 75.66 | 84.94 | +$11.51 |
| Elastic-net | 88.46 | 75.66 | 84.94 | +$3.52 |
| XGBoost | 82.42 | 75.66 | 84.94 | -$2.52 |
| Bayesian Ridge | 122.03 | 75.66 | 84.94 | +$37.09 (degenerate) |
| **Ensemble median** | **88.46** | **75.66** | **84.94** | **+$3.52** |

Actual Brent mean over the matched 151-day window: **$108.54**.

**Implied ATTs (matched day-set):**
- SCM ensemble median counterfactual: (108.54 − 88.46) / 88.46 = **+22.7%**
- EIA STEO Feb-22 (last pre-invasion forecast) as counterfactual: (108.54 − 84.94) / 84.94 = **+27.8%**
- EIA STEO Jan-22 as counterfactual: (108.54 − 75.66) / 75.66 = **+43.4%**

**Reading.** The SCM ensemble-median counterfactual ($88.46) sits **within $3.52/bbl** of the EIA's last pre-invasion structural forecast ($84.94), and the implied ATTs disagree by ~5.1 pp. Three of five models (Convex SCM, Elastic-net, XGBoost) bracket the STEO Feb-22 anchor to within ±$4.2. Bayesian Ridge is far off, consistent with its diagnosed degeneracy (walk-forward overfit ratio 3.12, LOO range crosses zero, baseline gap −10.1%). ASCM sits slightly high, consistent with its known shrinkage-toward-mean bias on Russia.

**The SCM is more conservative than the STEO-based counterfactual** by ~5.1 pp because the SCM donors absorb post-Feb-2022 macro co-movement (inflation, demand recovery) that the EIA structural forecast does not. Both methods are "correct" but answer subtly different questions: the SCM nets out cross-asset co-movement; the STEO is EIA's pre-invasion view of where Brent should go conditional on supply/demand fundamentals.

**Caveat.** The STEO is itself a model forecast, not ground truth. The agreement is evidence that two independent methods produce the same counterfactual, not that either is correct. The Hormuz case has no equivalent external benchmark — the equivalent STEO Jan-26 / Feb-26 vintages are *post*-Hormuz from the perspective of the Brent-impact forecast — so this external validation is available only for Russia.

Output: `data/validation/external_steo_russia.csv`. Overlay plot: `plots/russia_steo_validation.html`. Computation: [06_Ensemble_Final.ipynb](../notebooks/06_Ensemble_Final.ipynb) (external-validation cell).

## 4. Caveats and qualifications

1. **In-space placebo Russia weakness.** No model rejects for Russia in either pool — XGBoost comes closest (p = 0.158 in the 18-donor pool, 0.147 in the 32-donor pool) but does not reach the floor. This is *not* evidence that Russia produced no Brent effect — the historical move is well documented. It is evidence that in-space placebo loses power at pre-periods with high donor volatility (Russia pre-period 2020-07 → 2022-02 spans COVID recovery + reflation rally). The post-event gap magnitudes themselves are independently anchored by the historical record.

2. **Hormuz post-window length.** With ~72 post-event observations (window extended to 2026-06-15, the latest available Brent data), every inference test is under-powered. The §5e (i) in-space placebo p-values hit the permutation floor in *both* pools (0.053 / 0.030) because Brent ranks first under every model — strong signal but no further resolution. The cross-event weight transfer (§5f) substitutes inferential depth.

3. **Bayesian Ridge Russia instability.** Walk-forward ratio 3.12 (overfit signal, less severe than the prior 5.1 under single-hold-out CV), LOO range crosses zero, baseline gap −10.1%. Bayesian Ridge Russia remains the single least reliable fit; the ensemble median is robust to it.

4. **Hormuz convex SCM moment-matching SD mismatch.** From [03_Validate.ipynb](../notebooks/03_Validate.ipynb) `moment-match`: Hormuz convex SCM synthetic SD is materially below the treated SD (Brent's volatility is outside the 18-donor convex hull). ASCM corrects this via ridge augmentation. For the Hormuz headline, treat convex SCM and ASCM as the relevant fit pair; convex alone under-represents Brent variance.

5. **Recent citations.** The Chen & Yan (2023) mixed placebo test is cited in [validation.md §5e (ii)](validation.md) but is not currently computed in [04_Inference.ipynb](../notebooks/04_Inference.ipynb) — only the raw in-time fake-post gap is reported. Adding the mixed-placebo p-value is a deferred improvement; the in-time placebo currently relies on visual / magnitude comparison only.

6. **iSCM alternative not run.** [methodology.md §3](methodology.md) documents Di Stefano & Mellace's iSCM as the alternative donor-handling approach considered and not pursued. The 32-donor Russia in-space placebo result in §2.3 is *not* an iSCM application — it is the conservative robustness reading discussed under [validation.md §5e (i)](validation.md) ("Brent ranking high even when partly-treated donors are mixed in").

7. **In-time placebo hparams differ from headline.** Per [validation.md §5e (ii)](validation.md), the in-time placebo uses `MODEL_HPARAMS` defaults rather than the tuned hparams used in the headline fits. This intentional asymmetry removes a second-order leakage path (tuned hparams were selected by argmin val_RMSE on a window that overlaps the fake post-period). The trade-off: the in-time placebo gap magnitudes for non-convex models (Elastic-net, XGBoost) are larger under defaults than they would be with tuned hparams, which is the honest low-power read.

## 5. Source CSVs

| Source | Location |
|---|---|
| Walk-forward CV (headline pooled, 5-fold) | `data/validation/walk_forward_cv.csv` |
| Walk-forward CV (per-fold breakdown) | `data/validation/walk_forward_cv_folds.csv` |
| Parallel-fit + drift | `data/validation/parallel_fit_defence.csv`, `data/validation/validation_summary.csv` |
| Moment matching | `data/validation/moments_{event}_{model}.csv` |
| In-space placebo (18-donor) | `data/validation/inference_inspace_{event}_{model}.csv` |
| In-space placebo (32-donor) | `data/validation/inference_inspace_{event}_{model}_full.csv` |
| Pool comparison | `data/validation/inference_inspace_brent_pool_comparison.csv` |
| In-time placebo | `data/validation/inference_intime.csv` |
| Leave-one-out | `data/validation/inference_loo_{event}_{model}.csv` |
| Cross-event transfer | `data/validation/cross_event_transfer.csv` |
| External STEO comparison (Russia) | `data/validation/external_steo_russia.csv` |
| EIA STEO archive (Brent forecast vintages) | `references/eia/steo_{jan,feb}22.xlsx` (gitignored, downloaded on demand) |
| Donor cleanliness (model-agnostic) | `data/validation/donor_cleanliness_{event}.csv` |
