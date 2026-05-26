# Donor Catalog

Reference document for the Brent SCM analysis. Records every series **considered** for the donor pool — those *in* the pool (33 selected), those *rejected* with reason, and the per-event SUTVA treatment audit. The machine-readable audit table is in [../data/donor_audit.csv](../data/donor_audit.csv). Companion to [methodology.md](methodology.md) (design decisions) and [validation.md](validation.md) (full validation battery).

## Focal events

The SCM analysis estimates the chokepoint / geopolitical-risk premium on Brent for two events, both selected because **Brent visibly moved** — i.e. there is an actual disruption to attribute and a magnitude to validate against:

| Event | $T_0$ | Pre-window | Methodological role |
|---|---|---|---|
| **Russia invades Ukraine** | 2022-02-24 | 2020-07-01 → 2022-02-23 | *Magnitude validation* — historically large, well-documented Brent disruption ($95 → $130+); cross-validates the SCM design before applying it to Hormuz |
| **Strait of Hormuz crisis** | 2026-02-01 | 2024-06-01 → 2026-01-31 | *Main thesis* — out-of-sample estimate of the chokepoint premium |

**Why Red Sea is not a focal event.** The 2023-11-19 Bab-el-Mandeb / Galaxy Leader hijack diverted container shipping (Cape rerouting) but crude tankers retained Suez access through 2024 — Brent did not visibly disrupt. An earlier iteration of this analysis used Red Sea as a *null* validation case ("does SCM correctly produce no effect when none should exist?"). That is a weaker form of validation than *magnitude* validation, which is what Russia 2022 provides. Red Sea remains in the historical events table for the EDA timeline but does not get its own SCM estimate.

## Summary — conclusions on donor selection

**Pool.** 33 donors selected across metals, agriculturals, equities, FX, rates / credit, volatility, and crypto. Categorical exclusions: the energy complex and petro-currencies (CAD, NOK, BRL, COP, MYR — SUTVA violation on any oil-supply shock); unstable / idiosyncratic FX (TRY, ARS, EGP); thin or contract-discontinuous commodities (cocoa, orange juice, lean hogs, lumber); Russia-supplied industrial metals (aluminium, nickel) for the Russia case.

**Preferred specification.** A **21-donor strict-clean intersection** used for both events. Drops the Russia H-tier (Wheat, Corn, Palladium, EUR, DXY, BTC — direct exposure to the focal event) and the Russia M-tier (Copper, Iron Ore, Soybeans, EM_Eq, GBP, US10Y — secondary or terms-of-trade exposure). Hormuz audits to all-C on the full 33, but the same 21-donor pool is used to enable the cross-event weight-transfer validation in [validation.md §5f](validation.md). The 27-donor permissive pool and 33-donor full pool are reported as appendix robustness.

**Focal-event audit (SUTVA on $T_0$).** Russia 2022: **12 of 33 donors flagged** (6 H + 6 M) through identifiable causal channels — Russia / Ukraine agricultural exports, palladium supply concentration, EU energy-crisis pass-through to EUR / DXY, sanctions-evasion narrative for BTC. Hormuz 2026: **0 of 33 donors flagged** — the no-Persian-Gulf-routing criterion makes the audit empty by construction, and the empirical SUTVA tests in [validation.md §5d](validation.md) confirm it.

**Pre-window audit (events inside the fitting window).** Russia pre-window (2020-07 → 2022-02) contains one curated event — the **2021-10 energy-cycle reflation** — which is a common oil-cycle factor; every donor-specific channel through which it could contaminate the SCM weights is already absorbed by the M-tier downgrade. Hormuz pre-window (2024-06 → 2026-01) contains **no curated events**. The pre-window is therefore event-clean for the donor pool under both specifications.

**Empirical support.** The qualitative audits above are confirmed (Hormuz) or supplemented (Russia: 2 additional flags on JPY / CNY, attributable to concurrent macro events rather than Russia-treatment) by the model-agnostic SUTVA battery in [validation.md §5d](validation.md) and the regime-stability test in §5c. The qualitative audit remains the primary defence; the tests are secondary empirical confirmation.

## Selection criteria

A series enters the pool only if it satisfies all four:

1. **Co-moves with Brent through common global factors** in normal times — global growth (industrial metals, equities), the dollar (FX, gold), real interest rates (Treasuries), risk premium (VIX, credit), China demand (iron ore, soybeans). This is the co-movement SCM exploits.
2. **Not physically routed through the disruption** the SCM is trying to attribute (Persian Gulf trade for Hormuz; Russia/Ukraine trade for Russia 2022). Direct supply/demand exposure to the focal event is SUTVA failure.
3. **Liquid and daily-traded** with a redistributable Yahoo Finance / EIA / Caldara-Iacoviello source.
4. **Sufficient pre-period history** for the events under study (extending at least to 2020-01).

Rejected energy-complex donors (WTI, Henry Hub, refined products, US crude stocks) are recorded below for completeness — every one violates SUTVA on any chokepoint or oil-supply shock.

## Status code legend (per-event audit)

| Code | Meaning | Used as donor for that event? |
|---|---|---|
| **C** (clean) | No direct supply / demand exposure to the event | Yes |
| **M** (mild) | Secondary or terms-of-trade exposure; bias possible but small | Yes (or excluded in *strict-clean* variants) |
| **H** (heavy) | Direct supply / demand exposure; SUTVA violation | **Excluded** for that event |

**Pool variants used in the SCM notebook (see [methodology.md §3](methodology.md) for the design rationale):**

- *Strict clean* (drops H + M): 21 donors for Russia; the same 21 donors are the **preferred specification for both events** (shared pool enables cross-event weight-transfer validation per [validation.md §5f](validation.md)).
- *Permissive* (drops H only): 27 donors — Russia-only appendix robustness check.
- *Full pool* (no exclusions): 33 donors — appendix robustness for both events, also a contamination diagnostic for Russia.

For **Hormuz 2026** the audit gives all 33 clean, but the preferred specification uses the same 21-donor shared pool (with the full 33 as an appendix robustness check) to preserve cross-event comparability with Russia.

---

## Pool: 33 selected donors

### Metals (6)
| Donor | Ticker | Factor it loads on with Brent | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| Copper     | `HG=F` | Global industrial cycle ("Dr Copper") | M | C |
| Iron Ore   | `TIO=F` | China industrial demand | M | C |
| Silver     | `SI=F` | Precious + industrial dual factor | C | C |
| Platinum   | `PL=F` | Auto industry / South Africa | C | C |
| Palladium  | `PA=F` | Auto catalysts (Russia ~40% supply) | **H** | C |
| Gold       | `GC=F` | Real rates / safe-haven premium | C | C |

### Agricultural (7)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| Soybeans     | `ZS=F` | Global trade activity, China demand | M | C |
| Wheat        | `ZW=F` | Russia+Ukraine ~30% world exports — *contaminated* by Russia | **H** | C |
| Corn         | `ZC=F` | Ukraine ~13% world corn exports — *contaminated* by Russia | **H** | C |
| Coffee       | `KC=F` | Brazil/Vietnam concentrated; climate factor | C | C |
| Sugar        | `SB=F` | Brazil/India concentrated | C | C |
| Cotton       | `CT=F` | US/China/India producers | C | C |
| Live Cattle  | `LE=F` | North America domestic; livestock cycle | C | C |

### Equities (4)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| S&P 500             | `SPY`   | US growth / equity risk premium | C | C |
| MSCI World          | `URTH`  | Global growth / risk premium | C | C |
| Nikkei 225          | `^N225` | Japan growth / safe-haven equity | C | C |
| EM equities         | `EEM`   | Broad emerging markets (held some Russia weight pre-exclusion) | M | C |

### FX (11)

Direction conventions are mixed because that is how Yahoo publishes them — the SCM optimizer is direction-agnostic; the documentation matters for reading the EDA plots.

| Donor | Ticker | Direction | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|---|
| EUR | `EURUSD=X` | USD per 1 EUR  *(up = EUR strong)* | Eurozone growth / EUR sovereign | **H** *(EU energy crisis)* | C |
| GBP | `GBPUSD=X` | USD per 1 GBP                       | UK growth | M *(UK gas exposure)* | C |
| AUD | `AUDUSD=X` | USD per 1 AUD                       | Australia / China-demand commodity | C | C |
| JPY | `JPY=X`    | JPY per 1 USD *(up = USD strong)*   | Safe-haven FX | C | C |
| CHF | `CHF=X`    | CHF per 1 USD                       | Safe-haven FX (alternative to JPY) | C | C |
| CNY | `CNY=X`    | CNY per 1 USD                       | China managed currency (stayed out of sanctions) | C | C |
| INR | `INR=X`    | INR per 1 USD                       | India growth / EM | C | C |
| KRW | `KRW=X`    | KRW per 1 USD                       | Korea manufacturing | C | C |
| ZAR | `ZAR=X`    | ZAR per 1 USD                       | EM commodities (PGMs, gold) | C | C |
| MXN | `MXN=X`    | MXN per 1 USD                       | EM, Mexico (net oil exporter — ambiguous direction) | C | C |
| DXY | `DX-Y.NYB` | basket: EUR/JPY/GBP/CAD/SEK/CHF     | Trade-weighted dollar | **H** *(EUR dominant)* | C |

### Rates & credit (3)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| US 10Y yield | `^TNX` | Real risk-free rate / growth expectations | M *(inflation channel via Europe)* | C |
| TLT          | `TLT`  | Long-duration US Treasuries (inverse to yields) | C | C |
| HYG          | `HYG`  | US high-yield credit / risk premium | C | C |

### Volatility (1)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| VIX | `^VIX` | Implied vol on S&P 500 — risk-on/risk-off | C | C |

### Crypto (1)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| Bitcoin | `BTC-USD` | Digital risk-asset / liquidity factor (post-2020) | **H** *(sanctions-evasion narrative Mar2022)* | C |

### Pool size by event

| Pool variant | Russia 2022 | Hormuz 2026 | Used as |
|---|---|---|---|
| **Strict clean / shared 21-donor intersection** | 21 donors | 21 donors | **Preferred specification, both events** |
| Permissive (drops H only) | 27 donors | n/a | Russia appendix robustness |
| Full pool (no exclusions) | 33 donors | 33 donors | Both events appendix robustness |

Russia 2022 excludes for the strict-clean pool: **Wheat, Corn, Palladium, EUR, DXY, BTC** (H) **+ Copper, IronOre, Soybeans, EM_Eq, GBP, US10Y** (M). Hormuz 2026 uses the same 21-donor intersection as preferred specification (sacrificing 12 Hormuz-clean donors to enable cross-event weight-transfer validation); see [methodology.md §3](methodology.md) for the rationale and [validation.md §5f](validation.md) for the validation test that requires the shared pool.

---

## Pre-treatment event audit

The C / M / H columns above audit donors against the **focal event** (the disruption SCM is attributing). A separate identification concern is whether **other events inside the pre-window** contaminate donors. The two checks are conceptually distinct:

- *Focal-event contamination* biases the treatment-effect **estimate** (the donor's post-event move includes the very thing we are trying to measure).
- *Pre-window contamination* biases the synthetic-control **fit**, which then propagates into the estimate (the donor's pre-period co-movement with Brent reflects a transient shock rather than the stable factor structure SCM relies on).

### What counts as pre-window contamination

A pre-window event contaminates the SCM only if it acts as a **donor-specific** shock — i.e., moves a donor through a channel *not shared* with Brent or with the rest of the pool. **Common shocks** (global demand, global liquidity, global risk-off, common oil-cycle moves) are *absorbed* by the donor weights via the factor structure of SCM (Abadie, Diamond & Hainmueller 2010 §2.3; Abadie 2021 §2.2). They are not contamination; they are exactly what the donor pool is for. A pre-window event is a problem only when it (i) hits a donor through a non-shared channel and (ii) is large enough that the convex-weight or regression fit absorbs it into the donor's coefficient. The §5c regime-stability test and the §5d permutation mean-shift test at $T_0$ ([validation.md](validation.md)) are the *empirical* counterparts to the narrative below.

### Scope of this audit

The audit covers only events listed in the curated Brent event timeline ([data/historical_events.csv](../data/historical_events.csv)) that fall **inside** each pre-window. The pre-window start dates are chosen precisely to exclude prior shocks from the fit — the Russia pre-window deliberately starts **after** the COVID-19 demand collapse, the Saudi–Russia price war, and the WTI-negative episode (all Q1–Q2 2020), so none of these contaminate the SCM weights. Macro events not on the curated list (Fed cycles, election repricing) are not enumerated here: the curated list is the set of episodes already validated as having moved Brent meaningfully, and anything below that threshold is by construction either too small to contaminate or too broad to do so non-uniformly across the donor pool.

### Russia pre-window (2020-07-01 → 2022-02-23)

One curated event falls inside this window:

| Event | Date | Common factor or donor-specific? | Implication for donor pool |
|---|---|---|---|
| Energy-cycle reflation | 2021-10-01 | **Common (oil cycle)** — post-COVID global demand recovery and commodity-supercycle narrative; moved Brent, industrial metals, EM equities, and growth-sensitive currencies together | Donors sharing this channel are already flagged **M** on the Russia audit (Copper, Iron Ore, Soybeans, EM_Eq, GBP, US10Y) and excluded from the *strict-clean* preferred pool. The remaining 21 donors load on the reflation only through generic global-growth co-movement, which the synthetic absorbs by construction (Abadie 2021 §2.2). |

**Donors with pre-window contamination beyond what the focal-event audit captures: none.** The reflation is a common factor on the energy complex and on growth-sensitive donors; every channel through which it could plausibly contaminate a donor (industrial-metals demand, EM growth, commodity-export terms-of-trade) is precisely what the M-tier downgrade already addresses.

### Hormuz pre-window (2024-06-01 → 2026-01-31)

**No curated events fall inside this window.** The two most recent entries on the timeline before $T_0$ — Israel–Hamas war (2023-10-07) and Red Sea diversion (2023-11-19) — both predate the pre-window start, and Red Sea was specifically considered and rejected as a focal event because Brent did not visibly disrupt (see "Why Red Sea is not a focal event" above).

The implication for the donor audit is that, in the curated-event sense, the Hormuz pre-window is event-clean. This is structurally consistent with the all-C audit for Hormuz: there is no qualifying pre-window event for the audit to flag against, and the empirical SUTVA tests in §5d return no significant donor flags either ([validation.md §5d](validation.md), "Hormuz 2026: perfect agreement").

### Where this argument can fail

Two boundary conditions the reader should know:

1. **The curated event list is the binding constraint.** The audit above only addresses events on the curated Brent timeline. Any Brent-moving episode not on that list — whether by selection criteria or by oversight — is also not addressed here. The list's construction and inclusion thresholds are documented in [notebooks/01_EDA.ipynb](../notebooks/01_EDA.ipynb).
2. **Regime change in factor loadings is not an event.** The common-factor absorption argument requires donor coefficients to be *stable* across the pre-window. The §5c distance-correlation test (split-thirds within each pre-window) is the empirical check on this; that test is independent of which events appear on the curated list and would flag drift even in an event-clean window.

---

## Rejected candidates — with reason

### A. Energy complex

These have the highest pre-period correlation with Brent and would yield the lowest pre-period RMSPE — but every one violates SUTVA on any chokepoint or oil-supply shock.

| Candidate | Why excluded |
|---|---|
| WTI Crude (`CL=F`, `WTI_Spot`) | Daily arbitrage with Brent via futures-market and cargo-allocation decisions; treated by every oil shock within 24-48 hours |
| Natural Gas (`NG=F`, Henry Hub spot) | Demand substitution from oil into gas in industrial/utility burner-tip markets |
| Refined products (RBOB, heating oil, jet fuel, propane) | Crack-spread is a near-mechanical accounting identity: refined price = crude price + refining margin |
| Cushing stocks / EIA ex-SPR inventories | Drawdown response within the weekly EIA reporting cycle on supply shocks |

### B. FX — petrocurrencies (SUTVA failure)

These currencies have their value partly determined by oil prices through the exporting country's terms of trade — the same mechanism that disqualifies WTI.

| Candidate | Ticker | Why excluded |
|---|---|---|
| CAD | `CAD=X` | Canadian dollar is a textbook petrocurrency; Canada exports ~4 mb/d crude. Including CAD imports the oil signal directly into the synthetic. |
| NOK | `NOK=X` | Norwegian krone; Norway is a major North Sea oil exporter |
| BRL | `BRL=X` | Brazilian real co-moves with iron ore *and* oil via Petrobras exports |
| RUB | (suspended) | Russia 2022 treatment + sanctioned + suspended on most platforms post-2022 |
| COP | `COP=X` | Colombian peso; Colombia oil exporter |
| MYR | `MYR=X` | Malaysian ringgit; Malaysia oil/LNG exporter |

### C. FX — unstable / dominated by domestic factors

Even if not petrocurrency, some FX are poor donors because their volatility is driven by idiosyncratic non-global factors that add noise rather than signal.

| Candidate | Why excluded |
|---|---|
| TRY (Turkish lira) | Dominated by domestic crisis dynamics (unorthodox monetary policy, repeated currency crises) — noise, not signal |
| ARS (Argentine peso) | Multiple exchange-rate regimes, hyper-volatility, capital controls |
| EGP (Egyptian pound) | Same — repeated devaluations, currency controls |

### D. Equity indices considered but rejected

| Candidate | Ticker | Reason |
|---|---|---|
| DAX (Germany) | `^GDAXI` | Russia-2022 *treated* via European energy crisis; high overlap with EUR signal |
| FTSE 100 (UK) | `^FTSE` | UK index ~15% energy-sector weight (Shell, BP); partially oil-treated |
| TSX 60 (Canada) | `^GSPTSE` | ~17% energy-sector weight (oil sands); partial petrocurrency-equivalent |
| KOSPI (Korea) | `^KS11` | Redundant with KRW factor exposure |
| Hang Seng | `^HSI` | Heavy China weight; redundant with CNY + EM_Eq factor exposure |

### E. Other commodities considered but rejected

| Candidate | Ticker | Reason |
|---|---|---|
| Cocoa | `CC=F` | Thin futures market; 2023-24 price spikes driven by Ivory Coast/Ghana climate/disease — idiosyncratic, not macro |
| Orange juice | `OJ=F` | Thin market, hurricane/citrus-greening driven volatility |
| Lean hogs | `HE=F` | Low correlation with global cycle; US livestock-cycle idiosyncratic |
| Lumber | `LBR=F` / `LBS=F` | Contract change 2023-08 (LBS → LBR) breaks pre-period continuity |
| Aluminium (LME 3M) | `ALI=F` | Russia ~6% of world primary aluminium (Rusal) — Russia-treated. Could add for Hormuz-only variant. |
| Nickel (LME 3M) | `^LME-NI` | Russia ~10% world supply (Norilsk) — Russia-treated |
| Zinc, Lead | various | Smaller Russia exposure but limited factor distinction from Copper |

### F. Macro time-series considered but rejected

| Candidate | Reason |
|---|---|
| Caldara-Iacoviello GPR index | Used as a **descriptive overlay** (gap plots, EDA Plot 4) but **not** a donor — GPR spikes endogenously to the very events we are estimating, so it is treated by definition |
| EIA STEO / IEA Oil Market Report forecasts | Forecasts are not observed values, only realized prices are admissible inputs |
| Bloomberg / Reuters consensus oil-price forecasts | Same reason |
| Model-implied counterfactual scenarios | Would import external structural identification |

---

## Updating this catalog

When adding a new donor:
1. Append the ticker to `TICKERS` in [notebooks/00_Data_Fetching.ipynb](../notebooks/00_Data_Fetching.ipynb).
2. Append a row to the `DONOR_AUDIT_RAW` list in the same notebook so [data/donor_audit.csv](../data/donor_audit.csv) is regenerated.
3. Append a row here in `donor_catalog.md` with category, factor, and per-event status.
4. Re-run `00_Data_Fetching.ipynb` — only the new ticker is fetched thanks to per-ticker caching in `data/donors/`.

When removing a donor: simply delete its row from `TICKERS`, the audit list, and this catalog. The cached `data/donors/{name}.parquet` is harmless to leave behind; manual deletion is optional.

When you suspect a cached series is stale and want a clean re-download: delete `data/donors/{name}.parquet` for that ticker (or the whole `data/donors/` directory) and re-run the notebook.
