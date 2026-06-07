# Validation methodology

Reference document for the Brent SCM analysis. Catalogues every test used to validate the synthetic control estimates — model fit, donor cleanliness (SUTVA), and inference on the treated unit. Companion to [methodology.md](methodology.md) (design decisions for period selection, donor pool, and model ensemble) and [donor_catalog.md](donor_catalog.md) (donor pool catalogue and per-event SUTVA audit).

A defensible SCM analysis must validate at three conceptual levels:

- **Model fit** — is the synthetic a credible pre-event approximator of the treated unit?
- **Donor identification** — are the donors statistically clean of the event (SUTVA)?
- **Inference** — is the estimated post-event gap larger than what the procedure would produce under the null of no treatment?

The six sub-sections below cover each level. Every test is run **per model in the ensemble** (5 models × 2 events).

## 5.0 Overview of validation tests

| § | Test | Validates | Reference | Applicability notes for this analysis |
|---|---|---|---|---|
| 5a (i) | Walk-forward CV | Model fit / generalization | Hyndman & Athanasopoulos 2018; Bergmeir & Benítez 2012 | Heuristic `val/train > 2` flag; winner's-curse bias noted (§5a). |
| 5a (ii) | Moment matching (mean, SD, min, max, AR(1)) | Pre-period distributional coverage | Abadie 2010 | Hard threshold on mean ($\|\Delta\| < 0.01$ log); softer on SD / extrema / AR(1). |
| 5b | Pre-period parallel-fit (gap-series mean / SD / AR(1) / OLS slope) | Parallel-trends analog | Abadie 2010, 2015, 2021; Roth 2022 | No formal threshold (SCM-literature convention); drift-correction recipe in text. |
| 5c (i) | Pre-period regime-stability (distance correlation across thirds) | Donor-Brent factor stability | Székely & Rizzo 2007; Stock & Watson 1996, 2002 | Model-agnostic; no canonical SCM precedent; `max_shift > 0.30` is a narrative flag, not exclusion. |
| 5c (ii) | Bai-Perron multiple structural-break dating (donor-Brent return relationship, full history) | Donor-Brent loading stability over time ("treated over time") | Bai & Perron 1998, 2003 | Model-agnostic; dates breaks (vs assuming them); `break_in_prewindow` is a narrative flag, not exclusion. Russia: 2/33 in-pre-window (Wheat, VIX); Hormuz: 3/33 (Silver, Platinum, EM_Eq). |
| 5c (iii) | Harvey-Leybourne-Taylor trend-break test (donor's own log-level, full history) | Own-trend stability, I(0)/I(1)-robust ("change in trend") | Harvey, Leybourne & Taylor 2009 | Model-agnostic; Brent-free, so a break at $T_0$ is unambiguous donor-treatment. `break_near_T0` is the focal flag. Result: 33/33 I(1)-classified, 1/33 reject (Gold, 2018), 0 breaks near either $T_0$. |
| 5d | Permutation mean-shift test at known $T_0$ | Donor SUTVA (model-agnostic) | Chow 1960 (hypothesis); Lehmann & Romano 2005 (permutation reference dist.) | Enters BH-FDR ($\alpha = 0.10$) combined flag. |
| 5d | Wilcoxon event-window | Donor SUTVA (model-agnostic) | Brown & Warner 1985 | Enters BH-FDR combined flag. |
| 5d | KS distribution shift | Regime-shift diagnostic | Two-sample KS | Reported only; **excluded** from flag rule (over-rejects under regime shift). |
| 5e (i) | In-space placebo, inferential | Treated-unit inference | Abadie 2010 §3.3 | Min permutation $p \approx 1/N$: 0.048 (21-donor) vs 0.030 (33-donor) — **reported under both pools**. |
| 5e (ii) | In-time placebo (with mixed-placebo p-value) | Spurious-effect check on the treated unit | Abadie, Diamond & Hainmueller 2015; Chen & Yan 2023 | Mixed-placebo p-value computed per model. Formal inferential validity rests on the Hahn & Shi (2017) normality / symmetry assumption — strongest for convex SCM/ASCM, informative-rank only for nonlinear models. Pre-window shrinks under refit (XGBoost low-power); fake post-period audited for event-cleanliness. |
| 5e (iii) | Leave-one-donor-out | Donor-fragility robustness | Abadie, Diamond & Hainmueller 2015 | Importance metric is model-specific: convex weight (SCM, ASCM), regression coefficient (Elastic-net), SHAP (XGBoost), standardised-coefficient magnitude $|\hat\beta_j|/\sigma_{\hat\beta_j}$ (Bayesian Ridge — PIP proxy, not true PIP). |
| 5f | Cross-event weight transfer | Cross-event methodology generalization | No canonical reference (designed for this analysis) | Requires the shared 21-donor pool ([methodology.md §3](methodology.md)); strongest single test of methodology generalization. |

### 5.0a Minimum load-bearing tests

The twelve tests above span model fit, donor identification, and inference. The SCM literature does not formally validate any of them at this sample size (Roth 2022 on pretests; Chen & Yan 2023 §4 and Hahn & Shi 2017 on the symmetry assumption needed for the placebo test). What it *does* anchor on — the irreducible minimum — is much smaller:

| Level | Irreducible test | Where it lives in this pipeline | Why it's the minimum |
|---|---|---|---|
| **Model fit** | §5a (i) Walk-forward CV | [03_Validate.ipynb](../notebooks/03_Validate.ipynb) `wf-cv` cell | Only out-of-sample signal in §5; works for all 5 models; reveals XGBoost/Bayesian Ridge overfitting (val/train > 3 on Russia) |
| **Donor identification** | Qualitative audit in [donor_catalog.md](donor_catalog.md), confirmed by §5d permutation mean-shift test at $T_0$ | [01.5_Donor_Cleanliness.ipynb](../notebooks/01.5_Donor_Cleanliness.ipynb) | Per Abadie 2021 §3.1, donor exclusion is a-priori on substantive grounds; the permutation mean-shift test asks the literal SUTVA question (mean shift at $T_0$) |
| **Inference** | §5e (i) in-space placebo run under **both** the 21-donor and the 33-donor pool | [04_Inference.ipynb](../notebooks/04_Inference.ipynb) `iso` cells | Canonical Abadie 2010 §3.3 test. The 21-donor permutation floor is $1/22 \approx 0.045$; without the 33-donor rerun (floor $1/34 \approx 0.029$) Hormuz p-values cannot be distinguished from the saturation value. |

Everything else in §5 — moment matching (§5a ii), parallel-fit (§5b), regime-stability (§5c), Wilcoxon and KS (§5d), in-time placebo and LOO (§5e ii/iii), cross-event transfer (§5f) — is **defensive depth**. Each strengthens the headline when it agrees, or forces qualification when it disagrees, but none of them replace any of the three minimum tests.

**Caveat for Hormuz only:** with ~60 post-event observations, §5e (i) is structurally underpowered even at the 33-donor floor. The cross-event weight transfer (§5f) substitutes inferential depth there — so the Hormuz minimum set is `{audit, walk-forward CV, in-space placebo 21+33, cross-event transfer §5f (convex SCM and ASCM only)}` rather than the simpler triple sufficient for Russia.

## 5a. Pre-event model fit

Two sub-tests of the synthetic's quality as a pre-event approximator of log-Brent.

**(i) Walk-forward cross-validation (expanding-window, multi-fold)**:

1. Split the pre-event window into `N_FOLDS = 5` expanding-window forecast periods. Fold $i$ fits on $[t_\text{pre\_start}, \tau_i)$ and projects on $[\tau_i, \tau_i + h)$, where $h = $ `WALK_FORWARD_HORIZON = 20` business days and $\tau_i$ steps through cut points starting from `WALK_FORWARD_MIN_TRAIN_FRAC = 0.5` of the pre-period.
2. For each fold, compute train RMSE on the residuals before $\tau_i$ and val RMSE on the 20-day post-$\tau_i$ projection window. Val windows are **non-overlapping** by construction.
3. **Headline val RMSE** is the Hyndman pooled RMSE: $\sqrt{\frac{1}{N}\sum_i \sum_{t \in V_i} r_{i,t}^2}$ over the concatenation of all fold val residuals — unbiased because val windows do not overlap.
4. **Headline train RMSE** is the cross-fold mean $\bar{r}^\text{tr} = \frac{1}{N_\text{folds}} \sum_i r_i^\text{tr}$. Training sets *do* overlap across folds (fold $k$'s train is a superset of fold $k-1$'s), so pooling train residuals would over-weight early observations; the cross-fold mean is the unbiased summary.
5. Per-fold breakdown is also saved (`data/validation/walk_forward_cv_folds.csv`) so fold-to-fold variability is visible. `val_rmse_std_of_folds` is a multi-fold-only signal of regime stability — a large std relative to the mean indicates the model's accuracy depends strongly on which window is held out.

The CV settings live in [`lib/config.py`](../lib/config.py) as `WALK_FORWARD_N_FOLDS`, `WALK_FORWARD_HORIZON`, `WALK_FORWARD_MIN_TRAIN_FRAC`.

**Literature anchoring.** Expanding-window walk-forward CV (also called rolling-origin evaluation) is the canonical out-of-sample evaluation scheme for time-series — random $k$-fold CV cannot be used because of autocorrelation. See **Hyndman & Athanasopoulos (2018, *Forecasting: Principles and Practice* §5.10)** for the textbook treatment of the expanding-window scheme and the pooled-RMSE convention, and **Bergmeir & Benítez (2012, *Information Sciences* 191:192–213)** for the formal proof that walk-forward CV gives unbiased estimates of out-of-sample error for stationary time series. The bias-variance interpretation of the train-vs-val gap follows the classical framework in **Hastie, Tibshirani & Friedman (2009, *Elements of Statistical Learning* §7.2-7.3)**: overfitting manifests as the variance term dominating, with the practical signature of train RMSE ≪ val RMSE.

**Why multi-fold rather than single 80/20 hold-out.** A single 80/20 hold-out is *not* walk-forward CV — it's a single time-series train-test split, and it concentrates all val-rmse mass on the last 20% of the pre-period. If that specific window happens to be a regime change or anomalous segment, the single-fold val/train ratio is misleading. The multi-fold expanding-window scheme averages performance across five forecast horizons, exposing forecast stability rather than the accident of a single late-period sample.

**Flagging vs exclusion (honest statement).** We flag models with `val/train ratio > 2` as overfit candidates. The threshold is a **practitioner heuristic** rather than from a specific statistical test — Andrew Ng's CS229 notes and Goodfellow, Bengio, Courville (2016, *Deep Learning* §5.4) use "much larger" without a number; Kohavi (1995, *IJCAI*) focuses on choosing the minimum CV error model, not the train/val ratio. We report the absolute val_rmse alongside the ratio so a reader can apply their own judgment.

**Flagged models are not automatically excluded** from the ensemble. The headline ensemble ([methodology.md §6](methodology.md)) takes the median across all five models regardless of CV-flag status. Three reasons:

1. The ratio threshold is heuristic; auto-exclusion based on it would over-impose a hard cutoff that the literature does not validate.
2. The second-order validation — in-space placebo (§5e) and cross-event weight transfer (§5f) — provides the formal mechanism for ensemble inclusion/exclusion decisions.
3. The IQR across all five models is *itself* informative as a model-uncertainty band. Excluding flagged models would falsely tighten the IQR.

**For future consideration — bootstrap-CI alternative.** The bare ratio threshold could be replaced with a **probabilistic generalization statement** by bootstrapping val_rmse: compute a 95% CI on val_rmse via block-bootstrap over residuals (accounting for autocorrelation; see Politis & Romano 1994), and flag models where the lower bound of val_rmse exceeds train_rmse × some factor. This converts the heuristic threshold into a hypothesis-test style flag with controlled false-positive rate. Not implemented in the current pipeline; noted here for a more rigorous future iteration.

**Honest limitation — winner's curse on the val set.** The val set is used *twice* in our pipeline: (a) during hyperparameter selection in [02_Fit_Models.ipynb](../notebooks/02_Fit_Models.ipynb) (each grid candidate is scored by pooled val RMSE across folds; the candidate with lowest val RMSE is chosen), and (b) in the walk-forward CV reported here (the chosen hyperparameter's train/val ratio is reported as a generalization metric). Because the chosen hyperparameter is selected to *minimize* val RMSE, the reported val RMSE is **biased downward** vis-à-vis its true generalization performance — i.e., **overfitting is under-detected**, not over-detected.

A formal fix would require a 3-way split (train / val / test_inner) with test_inner held out from hyperparameter selection. We choose not to implement this because the pre-event window is sample-size-constrained (~420 obs / ~100-130 effective independent obs after AR(1) correction): splitting off a third partition shrinks each fold's training set materially, which would degrade hyperparameter selection quality more than the bias correction is worth. Standard SCM papers (Abadie 2010, Born et al. 2019) similarly do not do nested CV.

**The qualitative classifications are robust to this bias:** Russia XGBoost and Bayesian Ridge show val/train ratios above 3× even under the biased measurement, so under a clean measurement they would only look *more* overfit, not less. The borderline pass/fail status of Russia ASCM (2.04) and Hormuz Bayesian Ridge (2.10) should be read with the bias in mind. The in-time placebo (§5e ii) provides a partial second generalization signal on a different held-out window (last 6 months of pre-event), though it shares some overlap with the val set.

**(ii) Moment matching of treated vs synthetic.** Pre-period summary statistics of log-Brent vs log-synthetic.

| Statistic | Acceptable range | What a failure indicates |
|---|---|---|
| Mean | $\|\Delta\| < 0.01$ in log units | SCM doesn't constrain the mean directly — non-zero gap indicates implementation bug |
| SD | $\|\Delta \text{SD}\| / \text{SD}_{\text{treated}} < 0.25$ | Donor pool cannot span Brent's volatility → convex SCM is biased, ASCM required |
| Min, Max | Treated's pre-period min/max within donor envelope | Brent lies outside the donor convex hull → convex SCM cannot reach extrema, ASCM ridge correction necessary |
| AR(1) | Synthetic AR(1) within 0.05 of treated | Synthetic is over- or under-smoothing Brent's persistence |

A model passing both (i) and (ii) is included in the ensemble.

## 5b. Pre-period parallel-fit defence

The SCM analog of the **parallel-trends assumption** in difference-in-differences. Define the pre-period gap series:

$$
\text{gap}_t = 100 \cdot [\exp(y_t - \hat y_t) - 1] \quad \text{for } t < T_0
$$

The statistics on this series **characterise** how the synthetic behaves before the event — they are reported and interpreted, not used as pass/fail tests.

| Statistic | What it characterises | How a reader should use it |
|---|---|---|
| Mean (%) | Synthetic level offset from treated | Non-zero mean indicates a small constant bias; can be re-centred when reporting post-event magnitudes |
| SD (%) | Pre-period noise floor | Calibrates the post-event gap's signal-to-noise — the post-event gap should clear roughly 2× SD to be informative |
| $t$-statistic / $p$-value (mean = 0) | Formal test of zero mean | Reported; SCM does not constrain the mean by construction so a non-zero mean is normal |
| AR(1) autocorrelation | Residual persistence | High AR(1) (> 0.9) signals an unmodelled slow-moving factor — flag for narrative discussion |
| OLS trend slope (% per year) | Drift in the gap over the pre-period | Large slopes warrant explicit drift correction: subtract `slope × (post-window in years)` from the raw post-event gap before reporting |
| Trend $p$-value, $R^2$ | Statistical strength of the drift | Large $R^2$ means time alone explains substantial gap variance — drift correction is most warranted in these cases |

**Why no formal pass/fail threshold.** Applied SCM papers — **Abadie, Diamond & Hainmueller (2010, 2015)**, **Born et al. (2019)**, **Acemoglu et al. (2016)**, and the **Abadie (2021) *JEL* review** — do *not* impose formal numeric thresholds on pre-period diagnostics. They report pre-period RMSPE and the gap-series plot, then rely on the **in-space placebo distribution** (§5e (i)) as the formal inferential anchor. The reason is power: pre-trend tests at applied sample sizes (~400 obs in our case) **have low power**, in the sense of **Roth (2022, *AER: Insights*) — "Pretest with caution"** — they fail to reject parallel-trends nulls even when economically meaningful violations exist. A strict threshold rule therefore generates *false confidence* in the cases it appears to pass, while flagging marginal violations as "failures." Either failure mode is worse than honest reporting.

**Why we report the diagnostics anyway, even when several models look bad on slope or $R^2$.** Under the report-and-interpret framing, no model is "failing" — each is *characterised*. The statistics drive three concrete tasks:

1. **Drift correction in the headline.** A model with pre-period slope $\hat\beta$ % per year contributes $\hat\beta \times L$ percentage points to the raw post-event gap over a post-window of length $L$ years, *independent of the treatment*. Drift-adjusted gap = raw gap − $\hat\beta \times L$. For our windows: Russia $L \approx 0.58$ yr (7 months), Hormuz $L \approx 0.25$ yr (3 months). Example: convex SCM Russia with slope = 10 %/yr contributes ~5.8 pp of drift; ASCM Russia with slope = 0.3 %/yr contributes ~0.2 pp. The 29.6% vs 13.3% raw gap difference partly resolves once drift is acknowledged.
2. **Model comparison.** A model with slope = 0.3 %/yr is structurally more reliable than one with slope = 10 %/yr — independent of any threshold. The diagnostics give a *cross-model ranking* even when no single model is "clean."
3. **Honest framing for review.** A reviewer asking "did you check pre-period fit?" gets a transparent answer with actual numbers and a method for adjusting the headline if drift is material.

The strict thresholds previously imposed here were imported from a DiD-style parallel-trends instinct, which Roth (2022) shows is poorly calibrated at typical applied sample sizes. The SCM literature does not impose them, and adopting the SCM-native report-and-interpret standard is more defensible.

**Future consideration — Rambachan-Roth (2023) drift bounds.** Rather than point-estimating drift and subtracting it, formally bound the *maximum drift* consistent with the pre-period gap series; the post-event gap then carries a corresponding bound on the share attributable to drift versus treatment. **Rambachan & Roth (2023, *Review of Economic Studies*) — "A more credible approach to parallel trends"** is the canonical reference; their `HonestDiD` package is the practical implementation. Not implemented here; noted for a more rigorous future iteration.

## 5c. Pre-period regime-stability tests

Distinct from the parallel-fit defence: parallel-fit tests whether the *synthetic tracks the treated*; regime-stability tests whether the *donor-Brent factor structure itself* is stable. Two complementary tests: **(i)** distance correlation across pre-period thirds (does the dependence vary *within* the fitting window?) and **(ii)** Bai-Perron break dating over the full history (does the loading break, and *when*?).

Both are **model-agnostic** (they use only donor and Brent return series, no SCM model) and are implemented in [01.5_Donor_Cleanliness.ipynb](../notebooks/01.5_Donor_Cleanliness.ipynb) — **(i)** under Battery B, **(ii)** under Battery C — alongside the model-agnostic SUTVA cleanliness tests, so that all pre-modeling data diagnostics live in one place.

### 5c (i) — Distance-correlation regime stability

**Procedure:** split pre-period into three sub-periods (early, middle, late thirds). For each Brent-donor pair, compute **distance correlation** (Székely & Rizzo 2007 *Annals of Statistics*) in each sub-period; report `max_shift = max − min` across the three sub-periods.

**No literature-mandated threshold.** Following the SCM-literature convention of *report and interpret* (cf. §5b above), we report the raw distance correlations + max shifts and discuss the largest shifts narratively. This test is **borrowed from the time-varying-parameter and structural-break literatures** (Stock & Watson 1996, 2002; Bai 2003; Bai & Perron 2003) and applied here in an ad-hoc fashion — distance correlation is a well-established dependence measure, but using sub-period thirds with a pass/fail interpretation has **no canonical SCM precedent**.

**Honest framing.** Large within-pre-period shifts in donor-Brent distance correlation signal either factor-structure drift or sampling noise at the ~140-obs sub-period scale (the two are confounded). Small shifts (e.g., max_shift < 0.15) are uninformative given estimator variance. Large shifts (max_shift > 0.30) are *narrative flags* warranting discussion, not automatic donor exclusion.

### 5c (ii) — Bai-Perron structural-break dating

The formal upgrade to the distance-correlation test. Where (i) asks whether the dependence *varies* across three fixed sub-periods, **Bai & Perron (1998, 2003)** *search for the break dates*: for each donor the regression SSR is globally minimised over all admissible partitions by dynamic programming, and the number of breaks is selected by BIC. This converts the ad-hoc thirds into a dated test that answers the two criticisms the distance-correlation test and the qualitative audit cannot:

- **"Treated over time."** Run over the **full available history** (weekly, Brent back to 2000 intersected with each donor's series), it dates *every* regime change in a donor, not just one at $T_0$ — so a donor whose loading is unstable *inside a pre-window* is caught regardless of the focal event.
- **"Change in trend."** Each break partitions the relationship regression $r^{donor}_t = \alpha_s + \beta_s\,r^{Brent}_t + \varepsilon_t$ into segments with their own co-movement slope $\beta_s$ and relative-drift intercept $\alpha_s$; a break in either is a change in the donor's trend relative to the market.

**Headline spec — relationship (returns).** $y =$ donor weekly log-returns, $x =$ Brent weekly log-returns. Stationary by construction, so the break dating is statistically sound. The implementation is `bai_perron_breaks` in [lib/validation.py](../lib/validation.py) — a dependency-free prefix-sum / dynamic-program solver for the simple-regression (intercept + one regressor) case; settings (`BP_MIN_FRAC=0.10`, `BP_MAX_BREAKS=5`) are in the notebook.

**Per-event flags.** Breaks are dated once per donor (event-independent); two event-specific flags are derived:
- `break_in_prewindow` — a break **strictly inside** that event's preferred pre-window → the donor-Brent loading is not stable across the fitting window. A narrative flag (caution / down-weighting), **not** an automatic exclusion.
- `break_near_T0` — a break within ±8 weeks of $T_0$. **Reported but not used to flag:** the relationship spec regresses on Brent, which is itself treated at $T_0$, so a break there is ambiguous (it may reflect Brent's move, not the donor's).

**Empirical findings.**
- **Most donor breaks predate both pre-windows** — clustering at 2011-2013 (post-GFC normalization) and the 2020-03 COVID crash. The COVID break sits *before* the Russia pre-window start (2020-07-01) and is therefore correctly not flagged, empirically vindicating that start date ([methodology.md §2](methodology.md)).
- **Russia: 2 of 33 break inside the pre-window** — **Wheat** (audit-H; the break test *independently corroborates* the qualitative audit) and **VIX** (2022-01-07, the pre-invasion risk-off run-up).
- **Hormuz: 3 of 33 break inside the pre-window** — Silver, Platinum, EM_Eq, all on a 2024-09-13 precious-metals / Fed-pivot shift; flagged for regime-aware reading of their Hormuz weights.

**Honest limitations.** BIC selection of the break count is the simplest defensible rule; Bai & Perron's sequential supF($\ell+1\mid\ell$) test with bootstrap critical values is the more rigorous alternative, noted for a future iteration. The relationship spec is also intentionally Brent-based, so a break *at* $T_0$ is ambiguous (Brent is itself treated) — the §5c (iii) own-trend test below resolves that.

### 5c (iii) — Harvey-Leybourne-Taylor trend-break test

The Bai-Perron relationship spec answers "did the donor-Brent *co-movement* break, and when." The complementary **"change in trend"** question is whether the donor's **own** price trend breaks. This matters for two reasons the relationship spec cannot address: it is **Brent-free**, so a break at $T_0$ is *unambiguous* evidence the donor itself was treated (not a reflection of Brent's own move); and it targets the trend (level path), not the return co-movement.

The obstacle is that donor price *levels* are near-unit-root (I(1)), and a naive trend-break regression over-detects on integrated series (a random walk has no trend to break, yet OLS finds many spurious ones — empirically a levels Bai-Perron returns ~5 breaks/donor, hitting the search cap). **Harvey, Leybourne & Taylor (2009, *Econometric Theory* 25(4):995-1029)** solve this with a statistic whose asymptotic size is the *same* whether the shocks are I(0) or I(1):

$$t_\lambda = \lambda\,t_0^* + m_\xi\,(1-\lambda)\,t_1^*, \qquad \lambda = \exp\!\big(-(g_1 S_0 S_1)^{g_2}\big)$$

where (Model A, trend break only): $t_0^* = \sup_{\tau}|t\text{-ratio on }\gamma|$ in the levels regression $y_t = \alpha + \beta t + \gamma\,DT_t(\tau) + u_t$ (I(0)-optimal), $t_1^*$ the same in the differenced regression $\Delta y_t = \beta + \gamma\,DU_t(\tau) + \Delta u_t$ (I(1)-optimal), both with a Bartlett long-run-variance denominator and a sup over 10%-trimmed break fractions; $S_0, S_1$ are KPSS stationarity statistics on the two residual series at the estimated break, so the weight $\lambda \to 1$ under I(0) and $\to 0$ under I(1). Constants are HLT's recommended $g_1=500$, $g_2=2$, bandwidth $\ell = \lfloor 4(T/100)^{1/4}\rfloor$, with the $(m_\xi, \text{critical value})$ pairs from HLT Table 1, Model A: (0.835, 2.284) at 10%, (0.853, 2.563) at 5%, (0.890, 3.135) at 1%. Implemented as `hlt_trend_break` in [lib/validation.py](../lib/validation.py); validated on synthetic I(0)+break, I(1)+break, and I(1)-null DGPs.

**Empirical findings (weekly own log-levels, full history).**
- **33 of 33 donors are classified I(1)-like** ($\lambda \approx 0$), so HLT switches to the unit-root branch and does **not** spuriously flag trend breaks. Only **Gold** rejects at 5% ($t_\lambda = 2.66$), with a 2018 break far from both events. This is the over-detection problem *correctly* avoided — a naive levels trend-regression would have flagged a break in essentially every donor.
- **No donor's own trend breaks within ±8 weeks of either $T_0$** — the cleanest possible "change in trend" result: no evidence that any retained donor was itself trend-treated by Russia 2022 or Hormuz 2026.

**Honest limitation.** HLT is mildly **over-sized for I(1) shocks in finite samples** (HLT Table 2 reports empirical sizes ~0.10-0.16 at $T=150$-$300$ for a nominal 5% test; our weekly $T \approx 600$-$1370$ is larger, so the distortion is smaller but non-zero). Borderline rejections should be read with that in mind; the test is used here as a *narrative* trend-stability flag, not a hard exclusion rule.

## 5d. Donor SUTVA / cleanliness battery

The donor catalog ([donor_catalog.md](donor_catalog.md)) gives a *qualitative* SUTVA argument — physical routing, supply-chain reasoning, factor exposure. This section gives the **statistical counterpart**: a model-agnostic battery run in [01.5_Donor_Cleanliness.ipynb](../notebooks/01.5_Donor_Cleanliness.ipynb) *before* any model is fit.

Three tests on each donor's own time-series — none depend on any SCM model:

| Test | Null hypothesis | Used in combined flag? | Source |
|---|---|---|---|
| **Permutation mean-shift test** at known $T_0$ | Donor's log-returns have no mean shift at $T_0$ (pre/post labels are exchangeable) | **Yes** | Chow 1960 (known break point hypothesis); Lehmann & Romano 2005 ch. 15 (permutation methodology) |
| **Wilcoxon event-window** | Mean return in $[-5d, +20d]$ equals mean in a 60-day pre-window control | **Yes** | Brown & Warner 1985; Wilcoxon |
| **Kolmogorov-Smirnov distribution shift** | Pre-event and post-event return distributions are equal | **No — informational only** | Two-sample KS |

**Why this is not the Andrews 1993 test.** The Andrews (1993, *Econometrica*) and Andrews & Ploberger (1994, *Econometrica*) tests target an *unknown* break point — they maximise the Wald or Wald-style statistic over all candidate break dates and use a non-standard reference distribution. Here the break point is fixed at the focal event date $T_0$ (a known calendar date), so the Chow (1960, *Econometrica*) hypothesis "equality of pre/post means at a known break" applies directly. We replace the parametric F-statistic with a permutation reference distribution (Lehmann & Romano 2005, ch. 15) to avoid normality and equal-variance assumptions on daily log-returns. The implementation function is `permutation_mean_shift_test` in [lib/validation.py](../lib/validation.py); the older name `chow_break_test_bootstrap` is deprecated.

**Combined flag rule:** donor flagged as *potentially treated* if **either** of the two SUTVA-specific tests (break OR event-window) rejects after **Benjamini-Hochberg FDR correction at $\alpha = 0.10$**.

**Why KS is reported but excluded from the flag rule.** At large pre-period sample sizes (Russia: ~420 pre obs + ~150 post), KS has very high power to detect *any* distributional difference — including differences driven by **concurrent macroeconomic regime shifts** unrelated to the focal event. For Russia 2022, the pre-period (COVID recovery + low rates) and the post-period (Fed +75bp × 3 + inflation acceleration + dollar surge) are two structurally different macro regimes regardless of the invasion. KS therefore flags ~21 of 33 donors for Russia — far more than the audit's 12 — but the over-rejection is driven by the broad regime shift, not by Russia-treatment of individual donors. We retain KS as a *regime-shift diagnostic* but exclude it from the per-donor SUTVA flag.

**Empirical findings from 01.5:**

- **Hormuz 2026: 32 of 33 agree.** The audit's qualitative "no Persian-Gulf routing for any donor" call is empirically confirmed except for IronOre, which the Wilcoxon event-window test flags on a concurrent commodity-cycle move (not Hormuz-treatment).
- **Russia 2022: partial disagreement** (20 of 33 agree, 13 disagree):
  - *Audit flags, tests miss* (12 cases): the audit's H/M tier (Wheat, Corn, Palladium, EUR, DXY, BTC + the 6 M-tier donors) captures *causal channels* the model-agnostic tests cannot reproduce. The tests see "wheat moved" but the move isn't extreme enough to register after FDR with $N = 33$.
  - *Tests flag, audit clean* (1 case — CNY): the permutation mean-shift test detects China zero-COVID dynamics — **a concurrent macro event, not Russia-treatment**.

**Interpretation.** The hand-curated audit remains the primary SUTVA defense; the model-agnostic tests **largely confirm** the audit on Hormuz (32/33 agreement; the lone test flag is IronOre on a concurrent commodity-cycle move) and **supplement** it on Russia (highlighting CNY as flagged-but-not-audit-relevant — informative for the discussion section but not a reason to revise the audit). Tests and audit are *complementary*, not substitutes: audit captures causal-channel reasoning; tests capture event-localized empirical shifts (excluding KS, which captures the broader regime change).

### Honest power limitations

~415 obs per pre-period is low for detecting small contamination — tests can produce false negatives (failing to detect real contamination, as we see for the Russia H/M tier). Hormuz's post-event window is especially short (~60 obs) → very low power; the near-agreement there (32/33, with the lone IronOre flag attributable to a concurrent commodity-cycle move) is partly because both audit and tests are too conservative at that sample size to call anything treated. The qualitative SUTVA defense in [donor_catalog.md](donor_catalog.md) is the **primary** defense; the statistical tests are **secondary** empirical confirmation.

## 5e. Inferential validation on the treated unit

Three tests of whether the estimated post-event gap for Brent is statistically larger than what the procedure produces under the null.

**(i) In-space placebo for Brent (Abadie 2010 §3.3) — the inferential placebo.**

Note: this is the *same procedure* as §5d's donor-cleanliness placebo, but used for a different purpose. The donor-cleanliness placebo asks "is donor $j$ in the *tail* of the distribution?" (a tail position means treated → exclude). The inferential placebo asks "is *Brent* in the tail of the distribution?" (a tail position means the estimated effect is unusual).

1. For each donor in the (shared 21-donor) pool, refit the SCM treating *that donor* as the placebo treated unit, using the remaining 20 donors as its synthetic.
2. Compute the post/pre RMSPE ratio for each placebo unit and for Brent.
3. Rank Brent's ratio against the placebo distribution. Permutation p-value = share of placebo ratios ≥ Brent's.

A small p-value (< 0.10 is the conventional Abadie threshold) means Brent's gap is unusually large relative to what the SCM produces on units that were not treated. This is the standard non-parametric SCM inference.

**Permutation-distribution resolution — report under both pools.** With the shared 21-donor pool, the permutation distribution has 21 placebo units plus Brent (22 units total), so the minimum attainable p-value is $1/22 \approx 0.045$. This sits right at Abadie's conventional 0.10 threshold but leaves very little headroom below 0.05. To increase resolution, the in-space placebo is **re-run under the 33-donor full pool** (Russia: 33 donors; Hormuz: 33 donors), where the minimum attainable p-value is $1/34 \approx 0.029$. Both permutation p-values are reported in the appendix robustness table ([methodology.md §7](methodology.md)) alongside the headline 21-donor result. Reading: if the 21-donor p-value is at or near the floor of $0.048$, the 33-donor p-value is the cleaner signal of statistical significance; if both are well above the floor, the 21-donor result stands on its own and the 33-donor reading is supplementary.

For reference, Abadie 2010 (California tobacco) has 38 placebo states; Abadie, Diamond & Hainmueller 2015 (German reunification) has 16 countries. 21 donors is comparable to the latter — defensible, but not generous on resolution.

**(ii) In-time placebo (Abadie, Diamond & Hainmueller 2015).**

**Hyperparameter choice — defaults, not tuned.** The in-time placebo refit uses the literature-defensible defaults in `lib/config.py:MODEL_HPARAMS`, *not* the val-tuned hyperparameters stored by [02_Fit_Models.ipynb](../notebooks/02_Fit_Models.ipynb). This is an intentional asymmetry between the headline fit (tuned hparams) and the placebo (defaults).

The reason is the second-order leakage path: tuned hparams were selected by $\arg\min$ val_RMSE on the last 20% of the pre-event window, and the in-time fake post-period $[T_0^{\text{fake}}, T_0]$ overlaps with that val window (~85 of the ~127-129 fake-post observations sit inside the original val window for both events). If the placebo refit inherited the tuned hparams, the model would be using hyperparameters deliberately optimized to fit Brent well in a window that overlaps the placebo's evaluation region — a deck-stacking that biases the fake-period gap toward zero. Using defaults breaks this path: the placebo evaluates the model class without selection bias, not a tuned instance whose selection set leaks into the test set.

This is the standard preference in held-out evaluation (Cawley & Talbot 2010 *JMLR* §3): never evaluate a tuned model on data the tuning saw, even partially. The cost is that the placebo isn't literally testing the same instance as the headline — it's testing the model class as configured by its prior beliefs about hyperparameters (i.e., the `MODEL_HPARAMS` defaults). The benefit is no leakage. For Convex SCM, which has no tunable hyperparameters, headline and placebo configurations are identical, so the asymmetry is moot. For ASCM, Elastic-net, XGBoost, and Bayesian Ridge, defaults differ from tuned (see [methodology.md §4 Hyperparameter choices](methodology.md)) and the placebo is consequently a more honest — and somewhat more pessimistic — test of model-class behaviour.

Set a fake treatment date $T^{\text{fake}}_0$ several months *before* the real $T_0$. We use:
- Russia in-time placebo: $T^{\text{fake}}_0$ = 2021-08-24 (6 months before real $T_0$)
- Hormuz in-time placebo: $T^{\text{fake}}_0$ = 2025-08-01 (6 months before real $T_0$)

1. Restrict the pre-period to $t < T^{\text{fake}}_0$ (Russia: 2020-07-01 → 2021-08-23; Hormuz: 2024-06-01 → 2025-07-31).
2. Re-fit the SCM with this shorter pre-period.
3. Project the counterfactual forward into the *fake post-period* ($T^{\text{fake}}_0$ to real $T_0$ — a stretch of pre-event data we're now pretending is post-event).
4. Compute the gap in the fake post-period.

A *small* fake-period gap (in the same ballpark as the pre-period absolute gap) means the SCM does not produce spurious effects when nothing happened. A *large* fake-period gap reveals the model finds illusory effects in unrelated regimes — interpreting the real post-period gap then becomes much more cautious.

**Formal p-value via the mixed placebo test (Chen & Yan 2023).** Abadie's original in-time placebo produces only a graph; significance is judged by visual inspection. **Chen & Yan (2023, *Economics Letters*) "A mixed placebo test for synthetic control method"** formalize this by running the *in-space* placebo at the fake $T_0^{\text{fake}}$ — for each donor, treat that donor as the placebo unit, refit, and compute the post/pre MSPE ratio over $[T_0^{\text{fake}}, T_0]$. Brent's rank in the resulting distribution gives a permutation p-value (Chen & Yan Eqs. 2-5). Pointwise p-values (two-sided / right / left per period) and an MSPE-based p-value over the fake post-period are both computable. We report the MSPE-based version per model.

**Cross-model validity caveat.** Chen & Yan (Section 4) anchor the inferential validity of the mixed placebo test in the same symmetry assumption (Canay et al. 2017; Lehmann & Romano 2005 Theorem 15.2.1) that underlies Abadie's in-space placebo: the placebo and treated-unit effects must be identically distributed. **Hahn & Shi (2017)** show this requires Gaussian errors *for convex SCM*. For nonlinear estimators in our ensemble the assumption is weaker still. The table below maps Chen & Yan's caveat onto our 5-model ensemble:

| Model | Symmetry-assumption status | How to read the mixed-placebo p-value |
|---|---|---|
| Convex SCM | Chen & Yan-justified under Gaussian errors | Formal-but-restrictive p-value |
| ASCM | Same justification, plus ridge correction | Formal-but-restrictive p-value |
| Elastic-net | Weaker (unconstrained coefficients) | Informative rank statistic |
| XGBoost | Materially violated (tree-structured residuals) | Rank statistic; do not over-interpret |
| Bayesian Ridge | Weaker (linear but unconstrained Gaussian posterior over coefficients) | Rank statistic; the Bayesian Ridge posterior CI is Gaussian and ignores autocorrelation, so report alongside but do not over-interpret |

Chen & Yan themselves caveat (Section 4): *"applied researchers are advised to exercise care when interpreting 'p-values' from the in-space or mixed placebo tests, as they may not be p-values in a formal statistical sense despite carrying useful information."* This caveat applies more strongly to the nonlinear models. We therefore treat the convex SCM and ASCM mixed-placebo p-values as the formal inferential anchor for the in-time placebo, and the Elastic-net / XGBoost / Bayesian Ridge p-values as supporting rank evidence.

**Event-cleanliness audit of the fake post-period.** The in-time placebo only has interpretive force if the fake post-period is free of Brent-specific shocks. A non-zero fake-period gap should not be read as "the SCM produces spurious effects" if a real (smaller, unrelated) shock occurred inside the fake window. Each fake post-period is therefore audited against the EDA event timeline before the test is interpreted:

- **Russia fake post-period (2021-08-24 → 2022-02-23).** Not automatically null. The window contains (i) the late-2021 oil rally driven by demand recovery and OPEC+ underproduction discipline (Brent rose from ~$70 to ~$95), (ii) the Omicron emergence in late November 2021 (a brief risk-off episode that hit Brent), and (iii) the runup-to-invasion premium starting roughly mid-January 2022 as intelligence and diplomacy signals priced in. The third point is the trickiest: if real Russia-invasion risk premium was already accruing in Jan-Feb 2022, the fake post-period *contains* real treatment effect, and a non-zero fake gap is **partially expected** rather than evidence of model fragility. Interpretation: read the Russia in-time placebo qualitatively, not as a hard pass/fail.
- **Hormuz fake post-period (2025-08-01 → 2026-01-31).** Audited against the EDA event timeline notebook; any shock that materially moved Brent inside this window is flagged in the reporting of this test.

**Model-specific power limitation — XGBoost in particular.** Refitting on $t < T_0^{\text{fake}}$ shrinks the pre-window from ~20 months to ~14 months (~290 trading days), which is below the ~400-obs lower bound [methodology.md §4](methodology.md) sets for stable XGBoost training. A "large" in-time placebo gap from XGBoost can therefore reflect training-instability under the shortened window rather than genuine spurious-effect generation by the model. Convex SCM, ASCM, and Elastic-net are linear and degrade gracefully; Bayesian Ridge handles small samples by design via Bayesian priors. The XGBoost in-time placebo result is reported but **flagged as low-power** and not treated as load-bearing for the model's inclusion in the ensemble.

**(iii) Leave-one-donor-out (Abadie, Diamond & Hainmueller 2015).**

For each donor $j$ that receives a non-trivial weight in the SCM fit (e.g., $w_j > 0.05$):

1. Drop donor $j$ from the pool.
2. Re-fit the SCM with the remaining 20 donors.
3. Recompute the post-event gap.

Report the distribution of post-event gaps across all leave-out runs (typically 5-10 runs depending on how many donors carry weight). Stability — small range around the headline gap, similar central tendency — means no single donor is driving the estimate. Large range or distinct outliers identifies fragile dependencies that need to be flagged.

For the nonlinear and regression-based models in the ensemble, "non-trivial weight" is replaced by the model's native donor-importance metric (consistent with the per-model column in [methodology.md §4](methodology.md)):

- **Convex SCM, Augmented SCM:** convex weight $w_j > 0.05$.
- **Elastic-net:** $|\hat\beta_j| > $ a small threshold on the standardised coefficient (the $L_1$ component already zeros out unimportant donors, so the leave-out set is naturally compact).
- **XGBoost:** top-$K$ donors by mean absolute **SHAP value** over the pre-period ($K = 5$). SHAP is preferred over gain-based importance because it is more stable across random seeds at this sample size.
- **Bayesian Ridge:** top-$K$ donors by **standardised-coefficient magnitude** $|\hat\beta_j|/\sigma_{\hat\beta_j}$, with $K=5$. This is the PIP *proxy* used in [lib/models.py](../lib/models.py); it is not a true posterior inclusion probability, which would require spike-and-slab donor selection (see [methodology.md §4](methodology.md) "Bayesian Ridge vs full BSTS").

Reporting one importance metric per model — consistent between [methodology.md §4](methodology.md) (donor-importance column), §5e (iii), and [methodology.md §6](methodology.md) (per-model donor weights table) — preserves auditability across the pipeline.

## 5f. Cross-event weight-transfer validation

The strongest single test of methodology generalization across events. Enabled by the shared 21-donor pool ([methodology.md §3](methodology.md)) — both events have the same input vector, so weights are directly transferable without ad-hoc reweighting.

1. Fit weights $w^{RU}$ on Russia pre-period (2020-07 → 2022-02) using the 21-donor preferred pool.
2. Apply $w^{RU}$ to the Hormuz pre-period (2024-06 → 2026-01): compute $\hat Y^{HZ}_t = \sum_j w^{RU}_j \cdot Y_{jt}$ for $t$ in the Hormuz pre-period using the same 21 donors.
3. Project the implied Hormuz counterfactual using $w^{RU}$ across the post-event window.
4. Compare to the independently-fit Hormuz counterfactual.

If the two Hormuz counterfactuals agree closely → factor structure is regime-stable across 2020-22 and 2024-26 → strong evidence the methodology generalizes from the validation event to the main thesis event. If they disagree → regime drift is real and the Hormuz estimate carries additional uncertainty beyond the within-event model spread.

This is a single test that can be run per model in the ensemble (5 transfers total).

### What the test does and does not establish about donor weights

The test compares *projected synthetics*, not *individual donor weights*. Donor weight rankings often shift substantially between events even for models that pass the transfer test. For instance, convex SCM puts its Russia mass on soft commodities (Cotton 0.45, Sugar 0.29, Coffee 0.26) and its Hormuz mass on a mixed basket (JPY 0.40, Sugar 0.35, Cotton 0.07, KRW 0.06) — JPY moves from rank 12 (zero weight) on Russia to rank 1 on Hormuz, and Coffee from rank 3 to rank 13.

This is consistent with the test passing for two reasons:

1. **Convex SCM weights are not unique when donors are correlated.** With 21 donors clustered into highly-correlated groups (soft commodities, precious metals, Asian FX, safe-haven FX), the pre-period RMSPE surface is flat over a low-dimensional manifold of weight vectors. Two materially different `w` vectors can produce nearly identical synthetic paths. Abadie & L'Hour (2021, *Journal of Business & Economic Statistics*) document this non-uniqueness problem and propose a penalty term to break ties; we do not apply that penalty, so the solver picks an arbitrary point on the flat region. The arbitrary point can shift substantially between events without the underlying factor structure changing.

2. **What is stable is the projection onto donor space, not the per-donor coefficient.** Soft commodities and Asian FX both proxy for the same latent factor that co-moves with Brent (global demand × inflation expectations × risk appetite). The 2020-22 Russia pre-period happened to have soft commodities as the cleanest available proxy (the 2021 inflation rally); the 2024-26 Hormuz pre-period has Asian FX as the cleanest proxy (post-2024 yen carry dynamics). The latent factor is the same; the best in-pool proxy differs.

**Interpretive consequence.** The test supports *aggregate prediction transfer* (the synthetic path is similar across events), not *interpretive narrative transfer* (no donor can be called "the" Brent proxy across events). A statement like "JPY is the most important Brent proxy because it's the safe-haven asset" is not supportable from the cross-event comparison; the model's claim is only that some combination of soft commodities and Asian FX consistently proxies for the latent factor, with the exact mix regime-dependent. The honest framing of §5f is therefore "the projection onto donor space is regime-stable enough to support cross-event prediction," not "donor weights are stable."

The progression Convex SCM < ASCM < Elastic-net in transfer fidelity (transferred pre-RMSPE ratios 1.65, 2.18, 3.85 vs. independent) matches the progression in solution-space dimensionality: convex SCM lives on the simplex (sparsest); ASCM's ridge augmentation uses the full donor space; Elastic-net uses signed dense regression. The more degrees of freedom the model has in fitting donor coefficients, the less stable the projection across events, even though all three pass the heuristic threshold of "transferred RMSPE within 4× independent."


## 5g. Sign and bound of contamination bias (directional signed-divergence test)

§5c–§5d establish *whether* a donor is contaminated; the horizon sweep
([donor_catalog.md §Temporal](donor_catalog.md), [06_Ensemble_Final.ipynb](../notebooks/06_Ensemble_Final.ipynb))
establishes whether the gap *attenuates*. Neither signs the **direction** of the resulting bias
in the ATT. This section does. It is the formal answer to the supervisor critique that the donor
pool is "influenced by the war" (immediate channel) and that high prices "crowd out demand" so
demand-sensitive donors are "negatively affected" (the opposing channel) — i.e. that contamination
could bias the estimate in *either* direction, not only toward zero.

### The bias identity

Let $Y_t^N$ be the true no-event counterfactual and $\hat Y_t^N=\sum_j w_j X_{jt}$ the synthetic.
The ATT bias is exactly

$$\hat\tau_t-\tau_t \;=\; Y_t^N-\hat Y_t^N \;=\; -\sum_j w_j\,\delta_{jt},\qquad
\delta_{jt}\equiv X_{jt}-X_{jt}^{N},$$

where $\delta_{jt}$ is the **event-induced component** of donor $j$'s post-window value (the part
that would be absent without the focal event). The sign of the bias is therefore *minus the
weight-averaged donor contamination* — an empirical quantity, not a sign that can be assumed.

| Donor contamination | $\delta_j$ | Effect on synthetic | Bias $-\sum w_j\delta_j$ | ATT estimate |
|---|---|---|---|---|
| Abnormally **high** (oil-linked terms-of-trade, inflation→rates) | $>0$ | pulled up | $<0$ | **underestimate** (conservative) |
| Abnormally **low** (demand crowd-out, risk-off recession fear) | $<0$ | pulled down | $>0$ | **overestimate** |

### Estimating $\delta_j$ — Brent-free, with a reliability split

For each donor we form a **leave-one-out common factor** (equal-weighted mean of the *other*
donors' pre-standardised returns — never Brent, never the donor itself), fit the donor's
pre-window loading on it, project into the post-window, and accumulate the abnormal divergence.
Its post-window mean is $\delta_j$ in log units, comparable to the synthetic's log-level
contribution. Implemented as Battery D in [01.5_Donor_Cleanliness.ipynb](../notebooks/01.5_Donor_Cleanliness.ipynb);
the weight-aggregation $B=-\sum_j w_j\delta_j$ per model × horizon in [06_Ensemble_Final.ipynb](../notebooks/06_Ensemble_Final.ipynb).

The pre-window factor $R^2$ separates two sources of divergence, and we report the bias split
additively, $B_{\text{full}} = B_{\text{high-}R^2} + B_{\text{low-}R^2}$:

- **High-$R^2$ ($\geq 0.08$)** — the factor explains the donor, so a post-window divergence is
  plausibly *event contamination* (SUTVA-relevant).
- **Low-$R^2$** — the donor is a noisy proxy decoupled from the macro factor, so its divergence is
  mostly *idiosyncratic* (e.g. Coffee's 2022 Brazil supply cycle, not Russia) — a donor-fragility /
  over-reliance problem rather than contamination.

The bias is exact only for the four **linear** models (synthetic $=\sum_j w_j X_{jt}$); XGBoost is
nonlinear and its importances are unsigned, so it is reported elsewhere but excluded from $B$.

### Empirical findings

**Reliable donors agree on direction.** Restricting to $R^2\geq 0.08$ (the top 8 donors per event):

- **Russia: 8 / 8 reliable donors diverge *down*** ($\delta_j<0$): VIX (−0.18), Silver (−0.20),
  Platinum (−0.21), WorldEq (−0.12), SP500 (−0.10), HYG (−0.07), Gold (−0.06), AUD (−0.03). The
  cyclical / risk basket was uniformly depressed post-invasion — the demand-crowd-out / risk-off
  signature. The direction does **not** depend on the low-$R^2$ soft commodities.
- **Hormuz: 6 down / 2 up**, all small ($|\delta_j|\leq 0.08$ except VIX +0.21), i.e. roughly
  balanced and an order of magnitude weaker than Russia.

**Per-model, full-window decomposition** (positive = overestimate; share = bias / that model's gap):

| Event | Model | Gap % | $B_{\text{full}}$ % | high-$R^2$ % | low-$R^2$ % | reliable-wt coverage | bias / gap |
|---|---|---|---|---|---|---|---|
| Russia | Convex SCM | 29.6 | +16.4 | 0.0 | +16.4 | 0.00 | 0.59 |
| Russia | ASCM | 13.3 | +11.0 | +2.7 | +8.1 | 0.27 | 0.83 |
| Russia | Elastic-net | 21.7 | +16.7 | +3.5 | +12.7 | 0.33 | 0.79 |
| Russia | Bayesian Ridge | 0.5 | −0.1 | +4.7 | −4.6 | 0.37 | — (gap ≈ 0) |
| Hormuz | Convex SCM | 38.6 | −2.7 | −1.2 | −1.6 | 0.40 | −0.09 |
| Hormuz | ASCM | 43.7 | −3.7 | −0.9 | −2.9 | 0.42 | −0.11 |
| Hormuz | Elastic-net | 49.8 | −0.6 | +0.5 | −1.0 | 0.83 | −0.01 |
| Hormuz | Bayesian Ridge | 43.6 | +1.3 | +2.3 | −0.9 | 0.51 | +0.04 |

### Interpretation

1. **The Hormuz focal estimate is robust to contamination bias.** Across all four linear models the
   bias is at most ~11% of the gap, and conservative (negative) for three of four. The fits also lean
   on reliable donors (coverage 0.40–0.83), so what little bias exists is well-identified. The large
   positive Hormuz premium is not a contamination artefact.

2. **The Russia *full-window* gap is heavily contamination-biased — upward.** Three of four models
   overestimate by most of their reported gap (share 0.59–0.83), and Bayesian Ridge collapses the gap
   to ≈ 0 entirely. This is **not** the "toward zero, conservative" direction the temporal-contamination
   audit anticipated; for Russia the demand-crowd-out channel dominates. The bias also *grows with
   horizon* (e.g. Convex SCM +4.2% at 1 month → +16.4% at full), and the 1-month gap (~32%) is far less
   contaminated — consistent with the magnitude-validation claim resting on the early/peak window, where
   the well-documented \$95→\$130 move is recovered, while the small *true* full-window average premium
   reflects Brent's round-trip back to ~pre-invasion levels by September 2022. Russia therefore still
   validates the method on the window that matters; the full-window number is where contamination bites.

3. **This dates and explains the cross-model dispersion** the supervisor asked us to resolve rather than
   shrug at. Models split by *which donors they lean on*: Convex SCM and Elastic-net concentrate on
   low-$R^2$ soft commodities (Coffee, Cotton, Sugar) that drifted down idiosyncratically — hence Convex
   SCM's bias is **100% low-$R^2$** (zero reliable coverage); ASCM's ridge spreads weight, diluting it;
   Bayesian Ridge's near-zero gap is two large opposing unconstrained coefficients (JPY +1.29, KRW +1.77
   vs SP500 −1.28) cancelling. The dispersion is a donor-reliance fingerprint, not noise.

4. **Refined claim.** "Contamination is conservative" holds for the **focal Hormuz estimate** but **not**
   for the Russia full-window gap. We state this asymmetry explicitly rather than claiming a universal sign.

### Honest limitations

- The leave-one-out factor **differences out contamination common to the whole pool**, so $\delta_j$
  captures *relative* (cross-donor) contamination; a uniform pool-wide level shift is invisible here and
  is instead addressed by the horizon sweep ([donor_catalog.md §Temporal](donor_catalog.md)).
- $\delta_j$ on **low-$R^2$ donors conflates** event contamination with idiosyncratic drift, which is
  precisely why the bias is reported split by reliability rather than as a single number.
- $\delta_j$ is a cumulative-divergence mean, so magnitudes **scale with horizon**; signs and the
  reliable/idiosyncratic split are the load-bearing outputs, not the absolute percentages.
- XGBoost is excluded from $B$ (nonlinear); the equal-weighted factor is a deliberately simple,
  sign-unambiguous choice over PCA.

  
## References (full citations)

- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control methods for comparative case studies: Estimating the effect of California's Tobacco Control Program. *Journal of the American Statistical Association*, 105(490), 493-505.
- Abadie, A., Diamond, A., & Hainmueller, J. (2015). Comparative politics and the synthetic control method. *American Journal of Political Science*, 59(2), 495-510.
- Abadie, A. (2021). Using synthetic controls: feasibility, data requirements, and methodological aspects. *Journal of Economic Literature*, 59(2), 391-425.
- Abadie, A., & L'Hour, J. (2021). A penalized synthetic control estimator for disaggregated data. *Journal of Business & Economic Statistics*. (Cited for the non-uniqueness of convex SCM weights under correlated donors; verify exact volume/issue against the publication record.)
- Andrews, D. W. K. (1993). Tests for parameter instability and structural change with unknown change point. *Econometrica*, 61(4), 821-856.
- Andrews, D. W. K., & Ploberger, W. (1994). Optimal tests when a nuisance parameter is present only under the alternative. *Econometrica*, 62(6), 1383-1414.
- Bai, J., & Perron, P. (1998). Estimating and testing linear models with multiple structural changes. *Econometrica*, 66(1), 47-78.
- Bai, J., & Perron, P. (2003). Computation and analysis of multiple structural change models. *Journal of Applied Econometrics*, 18(1), 1-22.
- Bergmeir, C., & Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation. *Information Sciences*, 191, 192-213.
- Brown, S. J., & Warner, J. B. (1985). Using daily stock returns: The case of event studies. *Journal of Financial Economics*, 14(1), 3-31.
- Canay, I. A., Romano, J. P., & Shaikh, A. M. (2017). Randomization tests under an approximate symmetry assumption. *Econometrica*, 85(3), 1013-1030.
- Chen, Q., & Yan, G. (2023). A mixed placebo test for synthetic control method. *Economics Letters*, 224, 111004. https://doi.org/10.1016/j.econlet.2023.111004
- Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.
- Hahn, J., & Shi, R. (2017). Synthetic control and inference. *Econometrics*, 5(4), 52.
- Harvey, D. I., Leybourne, S. J., & Taylor, A. M. R. (2009). Simple, robust, and powerful tests of the breaking trend hypothesis. *Econometric Theory*, 25(4), 995-1029. (The I(0)/I(1)-robust trend-break test implemented in §5c (iii); constants $g_1=500$, $g_2=2$ and the Model A critical values / $m_\xi$ scaling constants are from the paper's Table 1.)
- Chow, G. C. (1960). Tests of equality between sets of coefficients in two linear regressions. *Econometrica*, 28(3), 591-605.
- Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2nd ed.). Springer.
- Hyndman, R. J., & Athanasopoulos, G. (2018). *Forecasting: Principles and Practice* (2nd ed.). OTexts.
- Kohavi, R. (1995). A study of cross-validation and bootstrap for accuracy estimation and model selection. *Proceedings of IJCAI* 1995, 1137-1143.
- Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. *Journal of Econometrics*, 54(1-3), 159-178. (The KPSS stationarity statistic used in the HLT weight function, §5c (iii).)
- Lehmann, E. L., & Romano, J. P. (2005). *Testing Statistical Hypotheses* (3rd ed.). Springer.
- Phipson, B., & Smyth, G. K. (2010). Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology*, 9(1), Article 39.
- Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303-1313.
- Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. *Review of Economic Studies*, 90(5), 2555-2591.
- Roth, J. (2022). Pretest with caution: Event-study estimates after testing for parallel trends. *American Economic Review: Insights*, 4(3), 305-322.
- Székely, G. J., & Rizzo, M. L. (2007). Measuring and testing dependence by correlation of distances. *Annals of Statistics*, 35(6), 2769-2794.
