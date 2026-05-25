# Methodology

Reference document for the Brent SCM analysis. Captures the design decisions for **period selection**, **donor pool**, and **model ensemble**. Companion to [validation.md](validation.md) (full validation battery — pre-event fit, donor SUTVA, inference) and [donor_catalog.md](donor_catalog.md) (donor pool catalogue).

## 1. Focal events

The SCM analysis estimates the chokepoint / geopolitical-risk premium on Brent for **two events**, selected because Brent visibly moved (real disruption → real magnitude to estimate and validate):

| Event | $T_0$ | Role |
|---|---|---|
| **Russia invades Ukraine** | 2022-02-24 | *Magnitude validation* — historical event with large, well-documented Brent move ($95 → $130+). Cross-validates the SCM design on closed data before applying it to Hormuz. |
| **Strait of Hormuz crisis** | 2026-02-01 | *Main thesis* — out-of-sample estimate of the chokepoint premium. |

Red Sea 2023 was considered as a third event but rejected: no visible Brent disruption → only a *null* validation case, weaker than the magnitude validation Russia 2022 provides. Red Sea remains on the EDA event timeline as historical context. Full reasoning: [donor_catalog.md](donor_catalog.md) §Focal events.

**Data-availability constraint on event eligibility.** The donor pool is fetched from Yahoo Finance starting **2010-01-01** (see `TICKERS` in [00_Data_Fetching.ipynb](../notebooks/00_Data_Fetching.ipynb)). The bulk of the 33-donor pool — industrial metals, precious metals, agricultural commodities, S&P 500, FX majors, US rates, VIX — has continuous data from January 2010. A few series start later: **WorldEq (URTH) from 2012-01-12**, **Iron Ore (TIO=F) from 2010-10-14**, **Nikkei from 2010-01-04**, **EM equities (EEM) from 2010-01-04**, and **Bitcoin (BTC-USD) from 2014-09-17**. The binding constraint for the 21-donor shared pool (used as preferred specification) is URTH at 2012-01-12, since BTC is excluded from the Russia clean pool by SUTVA. Allowing ~20 months of pre-event history before $T_0$, this means the SCM design is **only applicable to events with $T_0 \geq$ ~2013-09**.

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

The right cross-event design is **same methodology, separate training, validated via cross-event weight transfer** (see [validation.md §5f](validation.md)).

## 3. Donor pool

Full details: [donor_catalog.md](donor_catalog.md). Three pool variants per event:

| Pool variant | Russia 2022 size | Hormuz 2026 size | Where reported |
|---|---|---|---|
| **Preferred (shared 21-donor intersection)** | 21 donors | 21 donors | Main results, both events |
| Permissive | 27 donors | n/a | Russia appendix only |
| Full | 33 donors | 33 donors | Both events appendix |

**Why a shared 21-donor pool for both events.** The cross-event weight-transfer validation ([validation.md §5f](validation.md)) is the single strongest test of methodology generalization, and it requires both events to use the *same input vector* — i.e., the same donors. The 21-donor intersection (Russia strict-clean ∩ Hormuz strict-clean = Russia strict-clean, since every Russia-clean donor is also Hormuz-clean by construction) is the natural shared pool. It also yields the cleanest like-for-like comparison: same model, same donors, same number of features → any difference in the post-event gap is attributable to the *event itself*, not to changes in inputs.

**Cost of sharing.** Hormuz loses 12 donors that are Hormuz-clean but Russia-contaminated: Wheat, Corn, Palladium, EUR, DXY, BTC *(heavily treated by Russia)* + Copper, IronOre, Soybeans, EM_Eq, GBP, US10Y *(mildly treated by Russia)*. Factor coverage thins slightly but all six categories (metals, agri, equities, FX, rates, vol/crypto) remain represented in the 21. The full-pool Hormuz fit is reported in the appendix to quantify what is lost — typically modest because convex-SCM weights are sparse (~5–10 donors get non-trivial weight regardless of pool size).

**Russia pool sensitivity is itself a diagnostic.** Re-running Russia with the permissive (27) and full (33) pools should produce *progressively smaller* gap estimates — the contaminated donors get inflated by the same Russia shock, pull the synthetic upward, and shrink the implied gap. If this monotonic pattern holds empirically, the SUTVA-driven exclusion logic is empirically supported.

**Selection methodology.** Hand-curated based on SUTVA reasoning + factor coverage (see [donor_catalog.md](donor_catalog.md)); the same 21 donors are fed to *all five models* in the ensemble (model-agnostic candidate pool). Each model assigns its own internal donor importance via convex weights, regression coefficients, permutation importance, or posterior inclusion probability — but the candidate pool is shared, preserving cross-model and cross-event comparability of gap estimates.

**Alternative considered but not pursued — Di Stefano & Mellace's inclusive SCM (iSCM).** A recent alternative to a priori donor exclusion is the **inclusive Synthetic Control Method (iSCM)** of Di Stefano & Mellace (2024, *arXiv* 2403.17624). iSCM retains "potentially affected" donors in the pool and algebraically removes their post-intervention spillover contribution: fit one SCM per potentially-affected donor (treating each in turn as if treated), obtain a system of $m$ equations in $m$ unknowns (the main treatment effect plus $m-1$ spillover effects), and solve via Cramer's rule. For Russia 2022 with 12 audit-flagged donors, iSCM would require solving a 12-equation system per post-event observation. We do not pursue iSCM for three reasons: (i) the cross-event weight-transfer design ([validation.md §5f](validation.md)) requires both events to use the same shared donor pool, which iSCM-Russia (33 donors with spillover correction) and standard-Hormuz (33 donors clean) would not preserve in a like-for-like way; (ii) the system inversion adds estimator variance that the small post-event windows (~7 months Russia, ~3 months Hormuz) can ill afford; (iii) iSCM is an arXiv working paper without peer-reviewed validation. The a priori exclusion of the 12 Russia-contaminated donors remains the more defensible choice for this thesis; iSCM could be added as an appendix robustness specification in a future iteration.

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

The full validation battery — pre-event model fit (walk-forward CV, moment matching), parallel-fit defence, pre-period regime stability, donor SUTVA / cleanliness, treated-unit inference (in-space placebo, in-time placebo, leave-one-donor-out), and cross-event weight transfer — is documented in its own reference: **[validation.md](validation.md)**. The `§5`-numbered cross-references elsewhere in this document and in the notebooks (e.g., `§5a`, `§5e (i)`, `§5f`) refer to sections of [validation.md](validation.md).

## 6. Ensemble aggregation

For each event:

1. **Train all 5 models** on the headline pre-window. Save donor weights/importance per model.
2. **Validate** each model ([validation.md §5a, §5b](validation.md)). Drop models that fail walk-forward validation.
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

A robust estimate is one where the central tendency does not shift materially across most cells.

## 8. What this methodology does *not* do

Honest framing of what is **out of scope** for this pipeline:

1. **Identification of *mechanism*** — these tests estimate the *magnitude* of the chokepoint / geopolitical-risk premium but do not decompose it into supply, demand, risk-premium, or speculative components. Mechanism decomposition would require a structural model on top of the reduced-form counterfactual.
2. **Forecasting** — the post-event projection is a *counterfactual*, not a forecast. The gap is "what would Brent have been without the event," not "what will Brent be next month." Out-of-sample forecasting accuracy is not a quality metric for SCM and is not reported.
3. **Welfare analysis** — gap × volume gives a rough revenue-impact estimate but proper welfare analysis requires equilibrium modeling (demand elasticity, fiscal incidence, etc.) beyond the SCM framework.
4. **Heterogeneous effects** — Brent is treated as a single aggregate price; cross-regional differentials (WTI, Dubai, Urals discount, Russia ESPO) and quality differentials are not modelled separately.
5. **Statistical inference for very short post-event windows** — for Hormuz specifically, post-event samples are too short (~3 months) for the placebo $p$-values to have high power. The qualitative SUTVA defense + cross-event weight transfer ([validation.md §5f](validation.md)) substitute for formal inferential weight.

## 9. References (full citations)

- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control methods for comparative case studies: Estimating the effect of California's Tobacco Control Program. *Journal of the American Statistical Association*, 105(490), 493-505.
- Abadie, A., Diamond, A., & Hainmueller, J. (2015). Comparative politics and the synthetic control method. *American Journal of Political Science*, 59(2), 495-510.
- Abadie, A. (2021). Using synthetic controls: feasibility, data requirements, and methodological aspects. *Journal of Economic Literature*, 59(2), 391-425.
- Ben-Michael, E., Feller, A., & Rothstein, J. (2021). The augmented synthetic control method. *Journal of the American Statistical Association*, 116(536), 1789-1803.
- Brodersen, K. H., Gallusser, F., Koehler, J., Remy, N., & Scott, S. L. (2015). Inferring causal impact using Bayesian structural time-series models. *Annals of Applied Statistics*, 9(1), 247-274.
- Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD*, 785-794.
- Di Stefano, R., & Mellace, G. (2024). The inclusive Synthetic Control Method. *arXiv preprint* arXiv:2403.17624. https://arxiv.org/abs/2403.17624
- Doudchenko, N., & Imbens, G. W. (2016). Balancing, regression, difference-in-differences and synthetic control methods: A synthesis. *NBER Working Paper* No. 22791.
- Friedman, J. H. (2001). Greedy function approximation: a gradient boosting machine. *Annals of Statistics*, 29(5), 1189-1232.

For the validation-specific references (placebo tests, walk-forward CV, parallel-trends critique, regime-stability tests, donor SUTVA tests), see [validation.md](validation.md#references-full-citations).
