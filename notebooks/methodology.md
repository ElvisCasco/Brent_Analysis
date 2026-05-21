# Methodology

Reference document for the Brent SCM analysis. Captures the design decisions for **period selection**, **model ensemble**, and **assumption-validation tests**. Companion to [donor_catalog.md](donor_catalog.md) (which covers the donor pool) and [synthetic_control_oil.qmd](../synthetic_control_oil.qmd) (which covers the underlying SCM theory).

## 1. Focal events

The SCM analysis estimates the chokepoint / geopolitical-risk premium on Brent for **two events**, selected because Brent visibly moved (real disruption → real magnitude to estimate and validate):

| Event | $T_0$ | Role |
|---|---|---|
| **Russia invades Ukraine** | 2022-02-24 | *Magnitude validation* — historical event with large, well-documented Brent move ($95 → $130+). Cross-validates the SCM design on closed data before applying it to Hormuz. |
| **Strait of Hormuz crisis** | 2026-02-01 | *Main thesis* — out-of-sample estimate of the chokepoint premium. |

Red Sea 2023 was considered as a third event but rejected: no visible Brent disruption → only a *null* validation case, weaker than the magnitude validation Russia 2022 provides. Red Sea remains on the EDA event timeline as historical context. Full reasoning: [donor_catalog.md](donor_catalog.md) §Focal events.

**Data-availability constraint on event eligibility.** The donor pool is fetched from Yahoo Finance starting **2010-01-01** (see `TICKERS` in [00_Data_Fetching.ipynb](00_Data_Fetching.ipynb)). The bulk of the 33-donor pool — industrial metals, precious metals, agricultural commodities, S&P 500, FX majors, US rates, VIX — has continuous data from January 2010. A few series start later: **WorldEq (URTH) from 2012-01-12**, **Iron Ore (TIO=F) from 2010-10-14**, **Nikkei from 2010-01-04**, **EM equities (EEM) from 2010-01-04**, and **Bitcoin (BTC-USD) from 2014-09-17**. The binding constraint for the 21-donor shared pool (used as preferred specification) is URTH at 2012-01-12, since BTC is excluded from the Russia clean pool by SUTVA. Allowing ~20 months of pre-event history before $T_0$, this means the SCM design is **only applicable to events with $T_0 \geq$ ~2013-09**.

This rules out as candidate events for SCM estimation: the 2003 Iraq War, the 2005 Hurricane Katrina disruption, the 2008 Brent peak / financial-crisis demand collapse, the 2011 Libyan civil war, and the early Arab Spring — all of which would require donor history extending before 2012. The two focal events (Russia 2022, Hormuz 2026) sit comfortably inside the available donor coverage window, with pre-event windows starting 2020-07-01 and 2024-06-01 respectively. The 2014 OPEC price war ($T_0$ ≈ 2014-11-27) would technically be eligible but only with a very short pre-window (~2 years from URTH start) — not used here.

If a future iteration of this analysis required earlier events, the donor-pool definition would need to be revised: dropping URTH (its factor coverage is largely subsumed by SP500 and Nikkei) would push the binding constraint back to 2010-01 and admit events from 2011 onwards. The 21-donor pool is therefore a deliberate choice — broader factor coverage at the cost of an effective 2013 floor on event eligibility.

## 2. Pre-event period selection

### Selection principle (Abadie 2021 §3.4)

A pre-window must satisfy three conditions:
1. **No within-window Brent-specific shocks** — the SCM weights are learned on the donor→Brent relationship; embedded oil-specific shocks contaminate the learned factor loadings.
2. **Long enough for factor identification** — convex SCM needs ~200+ observations; nonlinear models (XGBoost, BSTS) prefer ~400+.
3. **Same factor regime as the projection window** — donor → Brent loadings should be stable between pre-period and post-event projection.

The cost of strict adherence: pre-windows are inherently short for Brent because oil-specific events happen frequently. Both windows below are ~20 months, which is the longest defensible duration that excludes acute Brent-specific contamination.

### Russia 2022 pre-windows

| Specification | Window | Length | Excludes | Includes |
|---|---|---|---|---|
| **Preferred** | 2020-07-01 → 2022-02-23 | ~19 mo / ~415 obs | March-May 2020 cluster (Saudi-Russia OPEC+ collapse, WTI-negative, acute COVID) | Post-trough COVID recovery + 2021 reflation rally |
| Robustness — extended | 2020-01-01 → 2022-02-23 | ~26 mo | – | The March-May 2020 cluster — stress test for the "COVID asymmetry" concern |
| Robustness — narrow | 2021-01-01 → 2022-02-23 | ~14 mo | All of 2020 | Post-recovery only — robustness to "regime simplification" |

Only the **preferred specification** appears in the main results tables. The two alternative specifications (extended and narrow) are reported in an appendix robustness table — they exist to demonstrate that the gap estimate does not depend on the precise pre-window endpoints.

### Russia 2022 post-event window

**Truncated to 2022-02-24 → 2022-09-30 (~7 months / ~155 trading days).**

Reasoning: OPEC+ announced a 2 mb/d production cut on **2022-10-05** (effective November 2022) — a major Brent-specific supply-policy shock that is *not* a pure response to the Russia/Ukraine invasion but reflects OPEC+'s own market-share strategy in the post-spike normalization. Including data after 2022-10-04 conflates the Russia premium with the OPEC+ supply response, inflating modelling ambiguity about which dynamics belong in the counterfactual.

The truncation at 2022-09-30 keeps the symbolic 2022-09-05 cut (100 kbd, minimal market impact) inside the window and excludes the major October cut. The Russia post-event window is therefore ~7 months — longer than the Hormuz post-event window (~3 months, limited by data availability).

**Sensitivity available but not in main results:** running with an extended Russia post-event window (e.g. to 2023-10-31, the original specification) is one config-line change (`POST_END['russia']` in `lib/config.py`). If a reviewer asks for the longer-window estimate, it can be produced trivially.

**Why 2020-07-01 specifically:** the March-May 2020 cluster combined a Brent-specific OPEC+ collapse (2020-03-08), a global demand shock (WHO pandemic declaration 2020-03-11), and a Brent-specific storage failure (WTI front-month negative 2020-04-20). These overlapping shocks created abnormal factor loadings — Brent fell ~75% peak-to-trough while donors fell 30-35%. Including this period would teach the SCM that "when global growth falls, Brent collapses 75%" — *not* Brent's normal factor loading, and the SCM would extrapolate this bias to post-event projections.

**Honest caveat:** the extended-window robustness specification deliberately *includes* the March-May 2020 collapse, as a stress test. If the gap estimate is similar across narrow / preferred / extended windows, the asymmetry concern is less important in practice than in theory.

### Hormuz 2026 pre-windows

| Specification | Window | Length | Excludes | Includes |
|---|---|---|---|---|
| **Preferred** | 2024-06-01 → 2026-01-31 | ~20 mo / ~415 obs | Russia 2022 + early Israel-Hamas + early Red Sea diversion | Mature Red Sea-rerouted regime + Iran-Israel exchange Apr 2024 |
| Robustness — extended | 2023-12-01 → 2026-01-31 | ~26 mo | Russia 2022 | Israel-Hamas (Oct 2023), Red Sea diversion (Nov 2023) — within-window noise |
| Robustness — narrow | 2025-01-01 → 2026-01-31 | ~13 mo | All of 2024 | Most-recent regime only — minimal contamination but few obs |

Same convention as Russia: only the **preferred specification** appears in the main results; the extended and narrow specifications go in the appendix robustness table.

**Why 2024-06-01 specifically:**
- Red Sea diversion (2023-11-19) had ~6 months to fully transmit through tanker rates and oil flow patterns
- Israel-Hamas initial risk-off (Oct-Dec 2023) had dissipated
- US enforcement of Iran sanctions had stabilized
- Most cleanly post-recent-shocks regime before Hormuz

### Why pre-windows of equal length (~20 months)

Cross-event comparison is cleaner when pre-windows have comparable duration. The XGBoost and BSTS models will have similar training data; the gap-size comparison won't be confounded by "Russia had more training data than Hormuz."

### Why not pool the two pre-periods into one model

Three reasons:

1. **Factor loadings drift between 2020-22 and 2024-26.** Donor → Brent loadings are not time-invariant: Fed regime (QE → QT), crypto reclassification (digital gold → risk asset), Russia oil flows re-routed to India/China, MENA risk premium permanence post-Israel-Hamas, US shale + OPEC+ market-share strategy. A pooled model fits the *average* loading across both regimes and matches neither.

2. **Different treatments, different counterfactuals.** Russia 2022 estimates "Brent without geopolitical-risk premium from the invasion"; Hormuz 2026 estimates "Brent without chokepoint supply premium." These are distinct causal estimands. One SCM model produces one counterfactual line — you need two.

3. **Donor pool differs across events.** Russia uses 21 clean donors after SUTVA exclusions; Hormuz uses 33. Pooling forces either the 21-donor intersection (losing factor coverage for Hormuz) or violates SUTVA for Russia.

The right cross-event design is **same methodology, separate training, validated via cross-event weight transfer** (see §5 below).

## 3. Donor pool

Full details: [donor_catalog.md](donor_catalog.md). Three pool variants per event:

| Pool variant | Russia 2022 size | Hormuz 2026 size | Where reported |
|---|---|---|---|
| **Preferred (shared 21-donor intersection)** | 21 donors | 21 donors | Main results, both events |
| Permissive | 27 donors | n/a | Russia appendix only |
| Full | 33 donors | 33 donors | Both events appendix |

**Why a shared 21-donor pool for both events.** The cross-event weight-transfer validation (§5d) is the single strongest test of methodology generalization, and it requires both events to use the *same input vector* — i.e., the same donors. The 21-donor intersection (Russia strict-clean ∩ Hormuz strict-clean = Russia strict-clean, since every Russia-clean donor is also Hormuz-clean by construction) is the natural shared pool. It also yields the cleanest like-for-like comparison: same model, same donors, same number of features → any difference in the post-event gap is attributable to the *event itself*, not to changes in inputs.

**Cost of sharing.** Hormuz loses 12 donors that are Hormuz-clean but Russia-contaminated: Wheat, Corn, Palladium, EUR, DXY, BTC *(heavily treated by Russia)* + Copper, IronOre, Soybeans, EM_Eq, GBP, US10Y *(mildly treated by Russia)*. Factor coverage thins slightly but all six categories (metals, agri, equities, FX, rates, vol/crypto) remain represented in the 21. The full-pool Hormuz fit is reported in the appendix to quantify what is lost — typically modest because convex-SCM weights are sparse (~5–10 donors get non-trivial weight regardless of pool size).

**Russia pool sensitivity is itself a diagnostic.** Re-running Russia with the permissive (27) and full (33) pools should produce *progressively smaller* gap estimates — the contaminated donors get inflated by the same Russia shock, pull the synthetic upward, and shrink the implied gap. If this monotonic pattern holds empirically, the SUTVA-driven exclusion logic is empirically supported.

**Selection methodology.** Hand-curated based on SUTVA reasoning + factor coverage (see [donor_catalog.md](donor_catalog.md)); the same 21 donors are fed to *all five models* in the ensemble (model-agnostic candidate pool). Each model assigns its own internal donor importance via convex weights, regression coefficients, permutation importance, or posterior inclusion probability — but the candidate pool is shared, preserving cross-model and cross-event comparability of gap estimates.

## 4. Model ensemble

Five models, each with a distinct inductive bias. The bias diversity is the point: if the gap estimate survives across models with different biases, it is more likely to reflect a real effect than a single-model artefact.

| # | Model | Inductive bias | Donor-importance metric | Reference |
|---|---|---|---|---|
| 1 | **Convex SCM** (baseline) | Linear, convex-hull constrained — synthetic must be a non-negative weighted average of donors summing to 1 | Convex weight $w_j$ | Abadie, Diamond & Hainmueller 2010 *JASA* |
| 2 | **Augmented SCM** | Convex SCM + ridge-regression bias correction; allows mild extrapolation outside donor hull | Convex weight + ridge coefficient | Ben-Michael, Feller & Rothstein 2021 *JASA* |
| 3 | **Elastic-net regression** | Linear, sparse + ridge-regularized; can extrapolate freely; lasso component drops donors entirely | Regression coefficient (with $L_1$-induced sparsity) | Doudchenko & Imbens 2016 *NBER WP 22791* |
| 4 | **Gradient Boosting (XGBoost / LightGBM)** | Nonlinear, tree-based; captures interactions; cannot extrapolate beyond training range | SHAP values / permutation importance | Friedman 2001 *Annals of Statistics*; Chen & Guestrin 2016 *KDD* |
| 5 | **Bayesian Structural Time Series (CausalImpact)** | Explicit additive decomposition: trend + seasonal + regression-on-donors + noise; Bayesian — produces posterior credible intervals natively | Posterior inclusion probability + coefficient | Brodersen, Gallusser, Koehler, Remy, Scott 2015 *Annals of Applied Statistics*; Google `CausalImpact` |

**Why these five and not others:**
- **GRU / LSTM neural sequence models** were considered and excluded for this sample size (~400-500 pre-event obs is well below the ~10,000+ typical training size for stable RNN training; required hyperparameter and regularization choices would dominate methodology defense).
- **Matrix Completion (Athey et al. 2021)** is theoretically interesting but lacks a clean per-donor importance metric, so it doesn't add to the cross-model donor ranking exercise.
- **OLS** is dominated by Elastic-net (which includes OLS as a special case with $\alpha = 0$).

**Sample-size compromise for nonlinear models:** with ~415 pre-event observations and 33 input series, XGBoost is at the lower bound of "enough data." Mitigations:
- Small/shallow trees (max_depth ≤ 4)
- Aggressive regularization (`gamma`, `lambda`)
- Early stopping on walk-forward validation set
- Average across multiple random seeds for stability

BSTS handles small samples better by design (Bayesian priors regularize naturally).

## 5. Validation methodology

A defensible SCM analysis must validate at three conceptual levels:

- **Model fit** — is the synthetic a credible pre-event approximator of the treated unit?
- **Donor identification** — are the donors statistically clean of the event (SUTVA)?
- **Inference** — is the estimated post-event gap larger than what the procedure would produce under the null of no treatment?

The six sub-sections below cover each level. Every test is run **per model in the ensemble** (5 models × 2 events).

### 5a. Pre-event model fit

Two sub-tests of the synthetic's quality as a pre-event approximator of log-Brent.

**(i) Walk-forward hold-out cross-validation**:

1. Split pre-event window into train (first 80%) and validation (last 20%, immediately before $T_0$).
2. Fit on train, predict on validation, compute validation RMSE.
3. Report the validation RMSE and the val/train ratio per model.

**Literature anchoring.** Walk-forward CV (also called rolling-origin evaluation) is the canonical out-of-sample evaluation scheme for time-series — random $k$-fold CV cannot be used because of autocorrelation. See **Hyndman & Athanasopoulos (2018, *Forecasting: Principles and Practice* §5.10)** and **Bergmeir & Benítez (2012, *Information Sciences*)**, which formally show that walk-forward CV gives unbiased estimates of out-of-sample error for stationary time series. The bias-variance interpretation of the train-vs-val gap follows the classical framework in **Hastie, Tibshirani & Friedman (2009, *Elements of Statistical Learning* §7.2-7.3)**: overfitting manifests as the variance term dominating, with the practical signature of train RMSE ≪ val RMSE.

**Flagging vs exclusion (honest statement).** We flag models with `val/train ratio > 2` as overfit candidates. The threshold is a **practitioner heuristic** rather than from a specific statistical test — Andrew Ng's CS229 notes and Goodfellow, Bengio, Courville (2016, *Deep Learning* §5.4) use "much larger" without a number; Kohavi (1995, *IJCAI*) focuses on choosing the minimum CV error model, not the train/val ratio. We report the absolute val_rmse alongside the ratio so a reader can apply their own judgment.

**Flagged models are not automatically excluded** from the ensemble. The headline ensemble (§6) takes the median across all five models regardless of CV-flag status. Three reasons:

1. The ratio threshold is heuristic; auto-exclusion based on it would over-impose a hard cutoff that the literature does not validate.
2. The second-order validation — in-space placebo (§5e) and cross-event weight transfer (§5f) — provides the formal mechanism for ensemble inclusion/exclusion decisions.
3. The IQR across all five models is *itself* informative as a model-uncertainty band. Excluding flagged models would falsely tighten the IQR.

**For future consideration — bootstrap-CI alternative.** The bare ratio threshold could be replaced with a **probabilistic generalization statement** by bootstrapping val_rmse: compute a 95% CI on val_rmse via block-bootstrap over residuals (accounting for autocorrelation; see Politis & Romano 1994), and flag models where the lower bound of val_rmse exceeds train_rmse × some factor. This converts the heuristic threshold into a hypothesis-test style flag with controlled false-positive rate. Not implemented in the current pipeline; noted here for a more rigorous future iteration.

**Honest limitation — winner's curse on the val set.** The val set is used *twice* in our pipeline: (a) during hyperparameter selection in `02_Fit_Models` (each grid candidate is scored by val RMSE; the candidate with lowest val RMSE is chosen), and (b) in the walk-forward CV reported here (the chosen hyperparameter's train/val ratio is reported as a generalization metric). Because the chosen hyperparameter is selected to *minimize* val RMSE, the reported val RMSE is **biased downward** vis-à-vis its true generalization performance — i.e., **overfitting is under-detected**, not over-detected.

A formal fix would require a 3-way split (train / val / test_inner) with test_inner held out from hyperparameter selection. We choose not to implement this because the pre-event window is sample-size-constrained (~420 obs / ~100-130 effective independent obs after AR(1) correction): splitting off a third partition shrinks the training set from ~336 to ~252 obs (25% reduction), which would degrade hyperparameter selection quality more than the bias correction is worth. Standard SCM papers (Abadie 2010, Born et al. 2019) similarly do not do nested CV.

**The qualitative classifications are robust to this bias:** XGBoost and BSTS-proxy show val/train ratios of 3-5× on Russia even under the biased measurement, so under a clean measurement they would only look *more* overfit, not less. The borderline pass/fail status of ASCM and Elastic-net should be read with the bias in mind. The in-time placebo (§5e ii) provides a partial second generalization signal on a different held-out window (last 6 months of pre-event), though it shares some overlap with the val set.

**(ii) Moment matching of treated vs synthetic.** Pre-period summary statistics of log-Brent vs log-synthetic.

| Statistic | Acceptable range | What a failure indicates |
|---|---|---|
| Mean | $\|\Delta\| < 0.01$ in log units | SCM doesn't constrain the mean directly — non-zero gap indicates implementation bug |
| SD | $\|\Delta \text{SD}\| / \text{SD}_{\text{treated}} < 0.25$ | Donor pool cannot span Brent's volatility → convex SCM is biased, ASCM required |
| Min, Max | Treated's pre-period min/max within donor envelope | Brent lies outside the donor convex hull → convex SCM cannot reach extrema, ASCM ridge correction necessary |
| AR(1) | Synthetic AR(1) within 0.05 of treated | Synthetic is over- or under-smoothing Brent's persistence |

A model passing both (i) and (ii) is included in the ensemble.

### 5b. Pre-period parallel-fit defence

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

### 5c. Pre-period regime-stability test

Distinct from the parallel-fit defence: parallel-fit tests whether the *synthetic tracks the treated*; regime-stability tests whether the *donor-treated factor structure itself* is stable within the pre-period.

Procedure: split pre-period into three sub-periods (early, middle, late thirds). For each Brent-donor pair, compute **distance correlation** (Székely & Rizzo 2007 *Annals of Statistics*) in each sub-period.

Pass criterion: no donor's distance correlation with Brent shifts by more than 0.20 between sub-periods. If shifts exceed that threshold for multiple donors, the factor structure is unstable and the SCM projection is regime-dependent (flag in results).

### 5d. Donor SUTVA / cleanliness battery (per donor × event)

The donor catalog ([donor_catalog.md](donor_catalog.md)) gives a *qualitative* SUTVA argument — physical routing, supply-chain reasoning, factor exposure. This section gives the **statistical counterpart**. For each donor in the candidate pool and each event:

| Test | Null hypothesis | Variant for nonlinear models | Source |
|---|---|---|---|
| **In-space placebo (RMSPE ratio)** | Donor $j$'s post/pre RMSPE ratio is in the bulk of the placebo distribution | Use the *same model* used for estimation (XGBoost placebos for XGBoost estimation, etc.) | Abadie 2010 §3.3 |
| **Structural break test** | No structural break in donor $j$'s log-return process at $T_0$ | Bootstrap variant — model-free, no DGP assumption | Andrews 1993; Hansen 2000 |
| **Event-window return test** | Donor $j$'s mean return in $[-5d, +20d]$ window equals its mean in a clean control window | Wilcoxon two-sample test — nonparametric | Brown & Warner 1985; Wilcoxon |
| **Correlation-structure invariance** | Joint distribution of donors is the same pre-$T_0$ vs post-$T_0$ | **Distance correlation** instead of Pearson — captures nonlinear dependence | Székely & Rizzo 2007 |

**Rule for exclusion:** a donor failing **≥ 2 of 4** tests for a given event is flagged for exclusion from that event's SCM pool. Failing 0-1 tests means the donor is "statistically clean" against that event.

**Multiple-testing correction:** with 21 donors × 4 tests × 2 events = 168 hypotheses, false discoveries are inevitable without correction. Apply **Benjamini-Hochberg FDR control at $\alpha = 0.10$** within each event. Bonferroni would be over-conservative; B-H is the standard for high-dimensional multiple testing.

**Honest power limitations.** ~415 obs per pre-period is low for detecting small contamination — tests can produce false negatives (failing to detect real contamination). Hormuz's post-event window is especially short (~3 months) → very low power. The qualitative SUTVA defense in [donor_catalog.md](donor_catalog.md) is the primary defense for Hormuz, with Russia 2022 providing the bulk of the statistical evidence.

### 5e. Inferential validation on the treated unit

Three tests of whether the estimated post-event gap for Brent is statistically larger than what the procedure produces under the null.

**(i) In-space placebo for Brent (Abadie 2010 §3.3) — the inferential placebo.**

Note: this is the *same procedure* as §5d's donor-cleanliness placebo, but used for a different purpose. The donor-cleanliness placebo asks "is donor $j$ in the *tail* of the distribution?" (a tail position means treated → exclude). The inferential placebo asks "is *Brent* in the tail of the distribution?" (a tail position means the estimated effect is unusual).

1. For each donor in the (shared 21-donor) pool, refit the SCM treating *that donor* as the placebo treated unit, using the remaining 20 donors as its synthetic.
2. Compute the post/pre RMSPE ratio for each placebo unit and for Brent.
3. Rank Brent's ratio against the placebo distribution. Permutation p-value = share of placebo ratios ≥ Brent's.

A small p-value (< 0.10 is the conventional Abadie threshold) means Brent's gap is unusually large relative to what the SCM produces on units that were not treated. This is the standard non-parametric SCM inference.

**(ii) In-time placebo (Abadie, Diamond & Hainmueller 2015).**

Set a fake treatment date $T^{\text{fake}}_0$ several months *before* the real $T_0$. We use:
- Russia in-time placebo: $T^{\text{fake}}_0$ = 2021-08-24 (6 months before real $T_0$)
- Hormuz in-time placebo: $T^{\text{fake}}_0$ = 2025-08-01 (6 months before real $T_0$)

1. Restrict the pre-period to $t < T^{\text{fake}}_0$ (Russia: 2020-07-01 → 2021-08-23; Hormuz: 2024-06-01 → 2025-07-31).
2. Re-fit the SCM with this shorter pre-period.
3. Project the counterfactual forward into the *fake post-period* ($T^{\text{fake}}_0$ to real $T_0$ — a stretch of pre-event data we're now pretending is post-event).
4. Compute the gap in the fake post-period.

A *small* fake-period gap (in the same ballpark as the pre-period absolute gap) means the SCM does not produce spurious effects when nothing happened. A *large* fake-period gap reveals the model finds illusory effects in unrelated regimes — interpreting the real post-period gap then becomes much more cautious.

**(iii) Leave-one-donor-out (Abadie, Diamond & Hainmueller 2015).**

For each donor $j$ that receives a non-trivial weight in the SCM fit (e.g., $w_j > 0.05$):

1. Drop donor $j$ from the pool.
2. Re-fit the SCM with the remaining 20 donors.
3. Recompute the post-event gap.

Report the distribution of post-event gaps across all leave-out runs (typically 5-10 runs depending on how many donors carry weight). Stability — small range around the headline gap, similar central tendency — means no single donor is driving the estimate. Large range or distinct outliers identifies fragile dependencies that need to be flagged.

For the nonlinear models in the ensemble (XGBoost, BSTS), "non-trivial weight" is replaced by "top-K feature importance" (typically K = 5).

### 5f. Cross-event weight-transfer validation

The strongest single test of methodology generalization across events. Enabled by the shared 21-donor pool (§3) — both events have the same input vector, so weights are directly transferable without ad-hoc reweighting.

1. Fit weights $w^{RU}$ on Russia pre-period (2020-07 → 2022-02) using the 21-donor preferred pool.
2. Apply $w^{RU}$ to the Hormuz pre-period (2024-06 → 2026-01): compute $\hat Y^{HZ}_t = \sum_j w^{RU}_j \cdot Y_{jt}$ for $t$ in the Hormuz pre-period using the same 21 donors.
3. Project the implied Hormuz counterfactual using $w^{RU}$ across the post-event window.
4. Compare to the independently-fit Hormuz counterfactual.

If the two Hormuz counterfactuals agree closely → factor structure is regime-stable across 2020-22 and 2024-26 → strong evidence the methodology generalizes from the validation event to the main thesis event. If they disagree → regime drift is real and the Hormuz estimate carries additional uncertainty beyond the within-event model spread.

This is a single test that can be run per model in the ensemble (5 transfers total).

## 6. Ensemble aggregation

For each event:

1. **Train all 5 models** on the headline pre-window. Save donor weights/importance per model.
2. **Validate** each model (§5a, §5b). Drop models that fail walk-forward validation.
3. **Compute post-event gap** from each surviving model.
4. **Headline estimate** = **median** of post-event gaps across surviving models. The median is robust to a single model producing an outlier (e.g., XGBoost overfitting in an unusual way).
5. **Uncertainty band** = inter-quartile range (Q25-Q75) across surviving models. This is the model-uncertainty, complementary to within-model uncertainty (which is given by each model's own confidence interval, e.g., BSTS posterior).

Reporting structure:

```
                  Russia 2022          Hormuz 2026
Convex SCM       <gap>%  [low, high]   <gap>%  [low, high]
ASCM             <gap>%  [low, high]   <gap>%  [low, high]
Elastic-net      <gap>%  [low, high]   <gap>%  [low, high]
XGBoost          <gap>%  [low, high]   <gap>%  [low, high]
BSTS             <gap>%  [low, high]   <gap>%  [low, high]
─────────────────────────────────────────────────────────────
Ensemble median  <gap>%  [Q25, Q75]    <gap>%  [Q25, Q75]
```

## 7. Robustness / sensitivity grid

The main results table reports only the **preferred specification** for each dimension (preferred pre-window, shared 21-donor pool, ensemble-median gap). The full grid below is reported as an **appendix robustness table** to demonstrate that the headline estimate does not depend on any single methodology choice.

| Dimension | Variants reported in appendix |
|---|---|
| Pre-window | Preferred, extended, narrow (§2 above) |
| Donor pool | Russia: 21 / 27 / 33 (preferred / permissive / full). Hormuz: 21 / 33 (preferred / full). |
| Model | Each of the 5 individual estimates + ensemble median |

For Russia, this is 3 × 3 × 6 = **54 cells**. For Hormuz, 3 × 2 × 6 = **36 cells**. Each cell is a one-line summary (gap estimate + confidence/credible interval); the full appendix table is manageable.

**Russia donor-pool sensitivity is especially diagnostic** (cross-reference §3). The gap estimate is expected to be *largest* with the 21-donor preferred pool (cleanest), *smaller* with the 27-donor permissive pool (mild contamination from M-tier donors pulls the synthetic up), and *smallest* with the 33-donor full pool (heavy contamination from H-tier donors). If this monotonic pattern holds empirically, the SUTVA-driven exclusion logic is empirically confirmed — a free-standing validation of the donor-audit methodology in [donor_catalog.md](donor_catalog.md).

A robust estimate is one where the central tendency does not shift materially across most cells. The qmd's existing battery (§9 in [synthetic_control_oil.qmd](../synthetic_control_oil.qmd)) is a subset of this grid focused on convex SCM only.

## 8. What this methodology does *not* do

Honest framing of what is **out of scope** for this pipeline:

1. **Identification of *mechanism*** — these tests estimate the *magnitude* of the chokepoint / geopolitical-risk premium but do not decompose it into supply, demand, risk-premium, or speculative components. Mechanism decomposition would require a structural model on top of the reduced-form counterfactual.
2. **Forecasting** — the post-event projection is a *counterfactual*, not a forecast. The gap is "what would Brent have been without the event," not "what will Brent be next month." Out-of-sample forecasting accuracy is not a quality metric for SCM and is not reported.
3. **Welfare analysis** — gap × volume gives a rough revenue-impact estimate but proper welfare analysis requires equilibrium modeling (demand elasticity, fiscal incidence, etc.) beyond the SCM framework.
4. **Heterogeneous effects** — Brent is treated as a single aggregate price; cross-regional differentials (WTI, Dubai, Urals discount, Russia ESPO) and quality differentials are not modelled separately.
5. **Statistical inference for very short post-event windows** — for Hormuz specifically, post-event samples are too short (~3 months) for the placebo $p$-values to have high power. The qualitative SUTVA defense + cross-event weight transfer (§5f) substitute for formal inferential weight.

## 9. References (full citations)

- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control methods for comparative case studies: Estimating the effect of California's Tobacco Control Program. *Journal of the American Statistical Association*, 105(490), 493-505.
- Abadie, A., Diamond, A., & Hainmueller, J. (2015). Comparative politics and the synthetic control method. *American Journal of Political Science*, 59(2), 495-510.
- Abadie, A. (2021). Using synthetic controls: feasibility, data requirements, and methodological aspects. *Journal of Economic Literature*, 59(2), 391-425.
- Bergmeir, C., & Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation. *Information Sciences*, 191, 192-213.
- Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.
- Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction* (2nd ed.). Springer.
- Hyndman, R. J., & Athanasopoulos, G. (2018). *Forecasting: Principles and Practice* (2nd ed.). OTexts.
- Kohavi, R. (1995). A study of cross-validation and bootstrap for accuracy estimation and model selection. *Proceedings of IJCAI* 1995, 1137-1143.
- Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303-1313.
- Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. *Review of Economic Studies*, 90(5), 2555-2591.
- Roth, J. (2022). Pretest with caution: Event-study estimates after testing for parallel trends. *American Economic Review: Insights*, 4(3), 305-322.
- Andrews, D. W. K. (1993). Tests for parameter instability and structural change with unknown change point. *Econometrica*, 61(4), 821-856.
- Andrews, D. W. K., & Ploberger, W. (1994). Optimal tests when a nuisance parameter is present only under the alternative. *Econometrica*, 62(6), 1383-1414.
- Ben-Michael, E., Feller, A., & Rothstein, J. (2021). The augmented synthetic control method. *Journal of the American Statistical Association*, 116(536), 1789-1803.
- Brodersen, K. H., Gallusser, F., Koehler, J., Remy, N., & Scott, S. L. (2015). Inferring causal impact using Bayesian structural time-series models. *Annals of Applied Statistics*, 9(1), 247-274.
- Brown, S. J., & Warner, J. B. (1985). Using daily stock returns: The case of event studies. *Journal of Financial Economics*, 14(1), 3-31.
- Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD*, 785-794.
- Doudchenko, N., & Imbens, G. W. (2016). Balancing, regression, difference-in-differences and synthetic control methods: A synthesis. *NBER Working Paper* No. 22791.
- Friedman, J. H. (2001). Greedy function approximation: a gradient boosting machine. *Annals of Statistics*, 29(5), 1189-1232.
- Hansen, B. E. (2000). Testing for structural change in conditional models. *Journal of Econometrics*, 97(1), 93-115.
- Székely, G. J., & Rizzo, M. L. (2007). Measuring and testing dependence by correlation of distances. *Annals of Statistics*, 35(6), 2769-2794.
