# Donor Catalog

Reference document for the Brent SCM analysis. Records every series **considered** for the donor pool — those *in* the pool (32 selected), those *rejected* with reason, and the per-event SUTVA treatment audit. The machine-readable audit table is in [../data/donor_audit.csv](../data/donor_audit.csv). Companion to [methodology.md](methodology.md) (design decisions) and [validation.md](validation.md) (full validation battery).

## Focal events

The SCM analysis estimates the chokepoint / geopolitical-risk premium on Brent for two events, both selected because **Brent visibly moved** — i.e. there is an actual disruption to attribute and a magnitude to validate against:

| Event | $T_0$ | Pre-window | Methodological role |
|---|---|---|---|
| **Russia invades Ukraine** | 2022-02-24 | 2020-07-01 → 2022-02-23 | *Magnitude validation* — historically large, well-documented Brent disruption ($95 → $130+); cross-validates the SCM design before applying it to Hormuz |
| **Strait of Hormuz crisis** | 2026-02-28 | 2024-06-01 → 2026-02-27 | *Main thesis* — out-of-sample estimate of the chokepoint premium |

**Why Red Sea is not a focal event.** The 2023-11-19 Bab-el-Mandeb / Galaxy Leader hijack diverted container shipping (Cape rerouting) but crude tankers retained Suez access through 2024 — Brent did not visibly disrupt. An earlier iteration of this analysis used Red Sea as a *null* validation case ("does SCM correctly produce no effect when none should exist?"). That is a weaker form of validation than *magnitude* validation, which is what Russia 2022 provides. Red Sea remains in the historical events table for the EDA timeline but does not get its own SCM estimate.

## Summary — conclusions on donor selection

**Pool.** 32 donors selected across metals, agriculturals, equities, FX, rates / credit, volatility, and crypto. **MSCI World (URTH) is dropped as redundant** with the S&P 500 (a near-collinear broad-equity proxy). Categorical exclusions: the energy complex and petro-currencies (CAD, NOK, BRL, COP, MYR — SUTVA violation on any oil-supply shock); unstable / idiosyncratic FX (TRY, ARS, EGP); thin or contract-discontinuous commodities (cocoa, orange juice, lean hogs, lumber); Russia-supplied industrial metals (aluminium, nickel) for the Russia case.

**Preferred specification.** A **18-donor strict-clean intersection** used for both events. Drops the Russia H-tier (Wheat, Corn, Palladium, EUR, DXY, BTC — direct exposure to the focal event) and the Russia M-tier (Copper, Iron Ore, Soybeans, EM_Eq, GBP, US10Y — secondary or terms-of-trade exposure). Hormuz audits all-C except Cotton (M — the oil→polyester substitution channel), but the same 18-donor pool is used to enable the cross-event weight-transfer validation in [validation.md §5f](validation.md). The 26-donor permissive pool and 32-donor full pool are reported as appendix robustness.

**Focal-event audit (SUTVA on $T_0$).** Russia 2022: **13 of 32 donors flagged** (6 H + 7 M) through identifiable causal channels — Russia / Ukraine agricultural exports, palladium supply concentration, EU energy-crisis pass-through to EUR / DXY, sanctions-evasion narrative for BTC. Hormuz 2026: **1 of 32 donors flagged** (Cotton, M — the oil→polyester substitution channel; no donor is *physically* routed through the Strait); the empirical SUTVA tests in [validation.md §5d](validation.md) flag 0 of 32 at the actual strike date $T_0$ = 2026-02-28 (Cotton’s M is an economic causal-channel call that the contemporaneous tests do not independently reproduce, as expected for an indirect/lagged channel) (the earlier $T_0$ = 2026-02-01 produced a single Wilcoxon-only IronOre flag, which was a concurrent commodity-cycle move rather than Hormuz-treatment).

**Pre-window audit (events inside the fitting window).** Russia pre-window (2020-07 → 2022-02) contains one curated event — the **2021-10 energy-cycle reflation** — which is a common oil-cycle factor; every donor-specific channel through which it could contaminate the SCM weights is already absorbed by the M-tier downgrade. Hormuz pre-window (2024-06 → 2026-02) contains **no curated events**. The pre-window is therefore event-clean for the donor pool under both specifications.

**Empirical support.** The qualitative audits above are confirmed (Hormuz: every donor except the audit-M Cotton agrees; no break or event-window flag survives at the strike-date $T_0$) or supplemented (Russia: 1 additional flag on CNY, attributable to a concurrent macro event — China zero-COVID — rather than Russia-treatment) by the model-agnostic SUTVA battery in [validation.md §5d](validation.md) and the regime-stability test in §5c. The qualitative audit remains the primary defence; the tests are secondary empirical confirmation.

**Temporal dimension (open item).** The C / M / H audit is *contemporaneous* — it scores exposure at $T_0$. Several donors marked C for Russia plausibly acquire a Russia component *over* 2022 through second-round channels (fertilizer cost-push into soft commodities, discounted-crude re-routing into INR/CNY, terms-of-trade into commodity FX, the inflation→rates path into TLT/HYG, PGM supply risk into Platinum). This *delayed / cumulative* contamination is not detectable by the at-$T_0$ tests, biases the estimated gap **toward zero** (it enters the post-window projection, not the pre-window fit), and is controlled through the **post-window length**, not the pre-window. It is *not* the same thing as the cross-model weight dispersion, which is non-uniqueness (Abadie & L'Hour 2021), not time-varying treatment. Full treatment, per-donor delayed-channel audit, and the menu of fixes are in [§Temporal dimension of contamination](#temporal-dimension-of-contamination--delayed-and-cumulative-sutva-violations) below.

## Selection criteria

A series enters the pool only if it satisfies all four:

1. **Co-moves with Brent through common global factors** in normal times — global growth (industrial metals, equities), the dollar (FX, gold), real interest rates (Treasuries), risk premium (VIX, credit), China demand (iron ore, soybeans). This is the co-movement SCM exploits.
2. **Not physically routed through the disruption** the SCM is trying to attribute (Persian Gulf trade for Hormuz; Russia/Ukraine trade for Russia 2022). Direct supply/demand exposure to the focal event is SUTVA failure.
3. **Liquid and daily-traded** with a redistributable Yahoo Finance / EIA / Caldara-Iacoviello source.
4. **Sufficient pre-period history** for the events under study (extending at least to 2020-01).

These four criteria — and the C / M / H audit built from them — are **contemporaneous**: they ask whether a donor is exposed to the focal event *at* $T_0$. A large shock like Russia 2022 transmits in waves over the months *after* the invasion, so a donor that is clean at $T_0$ can acquire a focal-event component later. That **temporal dimension** is treated separately in [§Temporal dimension of contamination](#temporal-dimension-of-contamination--delayed-and-cumulative-sutva-violations) below; it is the single most important way the pool's cleanliness can be weaker than the point-in-time audit suggests.

Rejected energy-complex donors (WTI, Henry Hub, refined products, US crude stocks) are recorded below for completeness — every one violates SUTVA on any chokepoint or oil-supply shock.

## Economic narrative — the shared-factor case for the donor pool

The pool is not a grab-bag of "things that correlate with oil." It is a deliberate attempt to **span the macro-financial factor space that drives Brent in normal times while staying off the oil-supply causal path** — which is exactly the condition under which the synthetic control identifies the oil-specific premium. This section is the *positive* economic justification for inclusion (the institutional step); the per-event SUTVA audit, the temporal-contamination audit, and the statistical batteries ([validation.md §5c-§5d](validation.md)) are the checks that defend it.

### The identifying logic, in economic terms

Decompose Brent's (log) price into a part explained by global macro-financial factors common to many assets, and an oil-specific part:

$$p^{\text{Brent}}_t = \underbrace{\lambda' F_t}_{\text{common global factors}} \;+\; \underbrace{o_t}_{\text{oil-specific (supply, chokepoint, geopolitics)}} \;+\; \varepsilon_t$$

The synthetic is a weighted basket of donors chosen to carry the **same loadings $\lambda$ on the common factors $F_t$** as Brent, but **zero loading on $o_t$** (the donors are not physically routed through oil supply). In the pre-window $o_t$ is small and stable, so the basket tracks Brent. When a chokepoint / geopolitical supply shock fires, $o_t$ jumps for Brent but not for the basket — the two decouple, and that decoupling *is* the estimated premium. Donor selection is therefore the economic exercise of finding assets that share Brent's $F_t$ exposure but not its $o_t$.

### The common factors $F_t$ that link donors to Brent

Brent is a globally-traded, dollar-denominated, demand-cyclical, risk-sensitive commodity. Five factors drive it in normal times — and each has a set of non-oil proxies:

| Common factor | Economic channel to Brent | Donor proxies |
|---|---|---|
| **Global growth / industrial cycle** | Oil demand is procyclical — global industrial production and trade move crude consumption | Copper, Iron Ore ("Dr Copper" / China steel), broad equities, commodity-exporter FX |
| **US dollar** | Oil is priced in USD; a stronger dollar lowers the dollar price of all globally-demanded commodities (and vice versa) | the FX block (inverse-dollar beta), Gold, DXY *(excluded for Russia)* |
| **Real interest rates / monetary policy** | The discount rate and carry on a storable commodity; the global liquidity cycle | TLT, US10Y *(M-tier)*, Gold (real-rate beta) |
| **Global risk appetite** | Oil is a risk asset — it sells off in risk-off episodes alongside equities and credit | VIX (inverse), HYG, SP500, safe-haven JPY / CHF |
| **China demand** | China is the marginal buyer of crude and of many commodities | Iron Ore, Copper, Soybeans, CNY, AUD |

The pool is built to cover all five, so the synthetic can reproduce Brent under any mix of these drivers — not just one.

### Why each donor category belongs — and stays off the oil-supply path

- **Industrial & precious metals.** Copper and iron ore are the canonical real-activity barometers: they rise and fall with the same global manufacturing and China-construction cycle that drives oil *demand*, but their *supply* has nothing to do with Persian-Gulf or Russian crude. Gold and silver add the real-rate / safe-haven dimension — gold's price is a monetary phenomenon (real yields, the dollar, crisis hedging), all factors that also move oil, with no oil-supply linkage. *(Palladium is Russia-supply-exposed and excluded for Russia; platinum carries a smaller, delayed version — see [§Temporal dimension](#temporal-dimension-of-contamination--delayed-and-cumulative-sutva-violations).)*
- **Agriculturals.** Soft commodities (coffee, sugar, live cattle) share the global-demand and dollar factors and move together through the financialised commodity complex (index and managed-money flows treat commodities as one asset class). Their production is concentrated in Brazil, Vietnam, India, North America — not the oil chokepoints. *(Cotton is reclassified **M** for both events — an oil-price rise lifts petroleum-derived synthetic-fibre (polyester) costs and shifts substitution demand toward cotton, an indirect oil-price channel, so it is dropped from the clean pool. Wheat and corn are direct Russia/Ukraine export exposures, excluded for Russia; the fertilizer cost-push channel is a delayed concern — see §Temporal dimension.)*
- **Equities.** Broad indices (S&P 500, Nikkei) price global growth expectations and the equity risk premium — the same growth and risk-appetite factors that move oil as a cyclical risk asset. Energy is a small share of these indices, so they are not proxies for oil *supply*. *(MSCI World is dropped as redundant with the S&P 500; country indices with large energy weights — DAX, FTSE, TSX — are excluded for energy exposure; see Rejected candidates §D.)*
- **FX.** Two clean channels. First, the **dollar factor**: because oil is dollar-priced, every non-USD pair carries an inverse-dollar beta that also shows up in Brent. Second, **terms-of-trade and risk**: commodity exporters (AUD, ZAR) co-move with the commodity cycle, safe havens (JPY, CHF) with risk-off, and CNY/INR/KRW with the China / EM-growth factor. Crucially none of the *retained* currencies is oil-*determined*. **Petrocurrencies (CAD, NOK, BRL, COP, MYR) are excluded precisely because their value is partly set by oil through the exporter's terms of trade** — they sit on the oil causal path, the same disqualification as WTI (Rejected candidates §B).
- **Rates & credit.** Long Treasuries (TLT) and high-yield credit (HYG) capture the real-rate / discount-factor and the risk-premium factors — macro-financial channels that move oil's valuation and the broader risk environment, with no oil-supply content. *(US10Y is M-tier for Russia via the European-inflation pass-through.)*
- **Volatility.** VIX is the risk-appetite factor in its purest form — oil falls in risk-off, and the inverse-VIX relationship is the cleanest expression of that shared channel.

### The identifying contrast — pool vs energy complex

The narrative is sharpest set against what is **deliberately excluded**. WTI, Henry Hub, refined products and crude inventories have the *highest* pre-period correlation with Brent and would give the lowest pre-period RMSPE — yet every one is disqualified, because each is driven by the *same oil-specific shock $o_t$ we are trying to measure* (Rejected candidates §A). That is the whole point: a good donor shares Brent's exposure to the **common factors $F_t$** but not to the **oil-specific component $o_t$**. The pool maximises $F_t$-coverage subject to $o_t$-cleanliness; the energy complex maximises raw correlation by loading on $o_t$ — which would mechanically shrink the estimated premium toward zero. **Selecting the pool is choosing identification over fit** — the central economic decision of the whole design.

## Status code legend (per-event audit)

| Code | Meaning | Used as donor for that event? |
|---|---|---|
| **C** (clean) | No direct supply / demand exposure to the event | Yes |
| **M** (mild) | Secondary or terms-of-trade exposure; bias possible but small | Yes (or excluded in *strict-clean* variants) |
| **H** (heavy) | Direct supply / demand exposure; SUTVA violation | **Excluded** for that event |

**Pool variants used in the SCM notebook (see [methodology.md §3](methodology.md) for the design rationale):**

- *Strict clean* (drops H + M): 18 donors for Russia; the same 18 donors are the **preferred specification for both events** (shared pool enables cross-event weight-transfer validation per [validation.md §5f](validation.md)).
- *Permissive* (drops H only): 26 donors — Russia-only appendix robustness check.
- *Full pool* (no exclusions): 32 donors — appendix robustness for both events, also a contamination diagnostic for Russia.

For **Hormuz 2026** the audit gives all clean except Cotton (M, oil→polyester channel), but the preferred specification uses the same 18-donor shared pool (with the full 32 as an appendix robustness check) to preserve cross-event comparability with Russia.

---

## Pool: 32 selected donors

### Metals (6)
| Donor | Ticker | Factor it loads on with Brent | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| Copper     | `HG=F` | Global industrial cycle ("Dr Copper") | M | C |
| Iron Ore   | `TIO=F` | China industrial demand | M | C |
| Silver     | `SI=F` | Precious + industrial dual factor | C | C |
| Platinum   | `PL=F` | Auto catalysts / South Africa (minor Russia/Norilsk PGM supply — *delayed* channel) | C | C |
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
| Cotton       | `CT=F` | US/China/India producers; oil→polyester substitution demand (indirect oil channel) | **M** | **M** |
| Live Cattle  | `LE=F` | North America domestic; livestock cycle | C | C |

### Equities (3)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| S&P 500             | `SPY`   | US growth / equity risk premium | C | C |
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

### Volatility (1 — audited clean but excluded from the pool by the breakpoint rule)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| VIX | `^VIX` | Implied vol on S&P 500 — risk-on/risk-off | C | C |

VIX is **audited clean (C/C)** but is **removed from the shared/clean pools by the Bai-Perron breakpoint rule** (`config.BREAKPOINT_EXCLUDE`): its donor↔Brent relationship breaks on **2022-01-07**, ~7 weeks before the Russia invasion (early-January Fed hawkish pivot + nascent Ukraine-risk repricing), inside the pre-window — see [validation.md §5c (ii)](validation.md). It stays in the raw data and the *full*-pool contamination diagnostic. This is the only donor the rule currently removes, taking the strict-clean / shared pool from 19 to 18.

### Crypto (1)
| Donor | Ticker | Factor | RU 2022 | HZ 2026 |
|---|---|---|---|---|
| Bitcoin | `BTC-USD` | Digital risk-asset / liquidity factor (post-2020) | **H** *(sanctions-evasion narrative Mar2022)* | C |

### Pool size by event

| Pool variant | Russia 2022 | Hormuz 2026 | Used as |
|---|---|---|---|
| **Strict clean / shared 18-donor intersection** | 18 donors | 18 donors | **Preferred specification, both events** |
| Permissive (drops H only) | 26 donors | n/a | Russia appendix robustness |
| Full pool (no exclusions) | 32 donors | 32 donors | Both events appendix robustness |

Russia 2022 excludes for the strict-clean pool: **Wheat, Corn, Palladium, EUR, DXY, BTC** (H) **+ Copper, IronOre, Soybeans, EM_Eq, GBP, US10Y, Cotton** (M); **plus VIX, removed by the breakpoint rule** (audited C but a pre-window relationship break near $T_0$), which takes the strict-clean pool from 19 to **18**. Hormuz 2026 uses the same 18-donor intersection as preferred specification (sacrificing 12 Hormuz-clean donors plus Cotton to enable cross-event weight-transfer validation); see [methodology.md §3](methodology.md) for the rationale and [validation.md §5f](validation.md) for the validation test that requires the shared pool.

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
| Energy-cycle reflation | 2021-10-01 | **Common (oil cycle)** — post-COVID global demand recovery and commodity-supercycle narrative; moved Brent, industrial metals, EM equities, and growth-sensitive currencies together | Donors sharing this channel are already flagged **M** on the Russia audit (Copper, Iron Ore, Soybeans, EM_Eq, GBP, US10Y) and excluded from the *strict-clean* preferred pool. The remaining 18 donors load on the reflation only through generic global-growth co-movement, which the synthetic absorbs by construction (Abadie 2021 §2.2). |

**Donors with pre-window contamination beyond what the focal-event audit captures: none.** The reflation is a common factor on the energy complex and on growth-sensitive donors; every channel through which it could plausibly contaminate a donor (industrial-metals demand, EM growth, commodity-export terms-of-trade) is precisely what the M-tier downgrade already addresses.

### Hormuz pre-window (2024-06-01 → 2026-02-27)

**No curated events fall inside this window.** The two most recent entries on the timeline before $T_0$ — Israel–Hamas war (2023-10-07) and Red Sea diversion (2023-11-19) — both predate the pre-window start, and Red Sea was specifically considered and rejected as a focal event because Brent did not visibly disrupt (see "Why Red Sea is not a focal event" above).

The implication for the donor audit is that, in the curated-event sense, the Hormuz pre-window is event-clean. This is structurally consistent with the near-all-C audit for Hormuz (Cotton is the lone M, on the oil→polyester channel): there is no qualifying pre-window event for the audit to flag against, and the empirical SUTVA tests in §5d return no break or event-window flags at the strike-date $T_0$ ([validation.md §5d](validation.md), "Hormuz 2026: 31 of 32 agree").

### Where this argument can fail

Two boundary conditions the reader should know:

1. **The curated event list is the binding constraint.** The audit above only addresses events on the curated Brent timeline. Any Brent-moving episode not on that list — whether by selection criteria or by oversight — is also not addressed here. The list's construction and inclusion thresholds are documented in [notebooks/01_EDA.ipynb](../notebooks/01_EDA.ipynb).
2. **Regime change in factor loadings is not an event.** The common-factor absorption argument requires donor coefficients to be *stable* across the pre-window. The §5c distance-correlation test (split-thirds within each pre-window) is the empirical check on this; that test is independent of which events appear on the curated list and would flag drift even in an event-clean window.

---

## Temporal dimension of contamination — delayed and cumulative SUTVA violations

The C / M / H audit above is **contemporaneous**: it asks whether a donor is exposed to the focal event *at* $T_0$. But a shock as large as Russia 2022 does not transmit instantaneously — it propagates in waves over the months *after* the invasion. A donor that is genuinely clean on 2022-02-24 can acquire a Russia-driven component by mid-2022 as second-round channels open. The contemporaneous audit, and the model-agnostic tests that evaluate the jump *at* $T_0$ ([validation.md §5d](validation.md)), are both blind to this. This section makes the temporal dimension explicit, because it is the most important way the pool's "cleanliness" can be weaker than the point-in-time audit implies.

### Three temporal profiles

| Profile | Definition | Audit tier | Detected by |
|---|---|---|---|
| **Immediate** | Donor jumps at $T_0$ through a direct channel | H (excluded) | Battery A permutation / event-window at $T_0$ ([validation.md §5d](validation.md)) |
| **Delayed / cumulative** | Donor is clean at $T_0$ but acquires a Russia component over the post-window as second-round channels (fertilizer costs, terms-of-trade, sanctions logistics, discounted-crude re-routing, the inflation→rates path) build | **not captured by the contemporaneous audit** | post-window sensitivity + per-donor post-window divergence (below) |
| **None** | Donor loads on Brent only through the common global factor, before and after | C | — |

### Why this is *not* the same as "weights vary across models"

It is tempting to read the cross-model dispersion in donor weights as evidence that donors "got affected after a while." **It is not.** Cross-model weight dispersion arises even under a perfectly time-invariant factor structure, for two reasons documented in [validation.md §5f](validation.md): (i) convex-SCM weights are **non-unique** when donors are correlated (Abadie & L'Hour 2021) — the pre-period RMSPE surface is flat over a manifold of weight vectors, so the solver picks an arbitrary point that differs across models; (ii) the five models carry different inductive biases and regularizers (simplex, ridge, $L_1$, trees, Gaussian prior), which spread weight differently across a correlated donor set. Neither mechanism involves time. The genuine fingerprints of *delayed contamination* are (a) the **gap's sensitivity to the post-window length** and (b) each donor's **post-window divergence from its pre-window factor loading** — not weight dispersion.

### Direction of the bias — this is what determines the fix

SCM weights are learned on the **pre-window**; the counterfactual is the weighted donor basket projected into the **post-window**. Delayed contamination therefore enters through the *projection*, not the *fit*:

- A donor that acquires a Russia component in the post-window starts tracking Brent's own Russia premium → the synthetic counterfactual is pulled **up** toward the treated path → the estimated gap (Brent − synthetic) is **biased toward zero**.
- The bias **grows with post-window length**: the longer the projection runs, the more cumulative contamination the synthetic absorbs.

Two consequences. First, delayed contamination is **conservative** for this thesis — it *shrinks* the estimated premium, it cannot manufacture one. Second, the lever that controls it is the **post-window**, not the pre-window. (Pre-window contamination is the mirror case: it biases the *weights* and is fixed by moving / shortening the *pre-window*, per [methodology.md §2](methodology.md). Delayed contamination is fixed by shortening the *post-window*.)

### Per-donor delayed-channel audit (Russia 2022, the 18-donor clean pool)

The contemporaneous audit marks these 18 donors C for Russia. Their *delayed* exposure is not zero — ordered by the plausibility of a cumulative Russia channel:

| Donor(s) | Delayed channel that builds over 2022 | Cumulative risk |
|---|---|---|
| **INR, CNY** | India and China became the buyers of discounted Russian crude over H2-2022; the oil-import benefit (esp. for INR) is an oil-linked channel absent at $T_0$ that switches on mid-year | Moderate |
| **Coffee, Sugar** | Russia/Belarus fertilizer (potash, nitrogen) and Russian gas-for-ammonia raised global agricultural input costs through 2022 — a broad cost-push channel touching every crop *(Cotton, previously here, is now reclassified M via the oil→polyester channel and dropped from the clean pool)* | Moderate |
| **AUD, ZAR, MXN** | Commodity-exporter terms-of-trade: the Russia-amplified energy / grain / metals supercycle lifted these currencies via export prices | Low-moderate |
| **Platinum** | Russia (Norilsk) is a meaningful PGM producer — far below its ~40% palladium share, but non-trivial for platinum; a sanctions / logistics risk premium built over 2022. The CSV audit's "no Russia exposure" note understates this | Low-moderate |
| **TLT, HYG** | The 2022 inflation surge (partly Russia-energy-driven) drove the Fed-hike path; US duration and credit moved with an inflation / rate channel Russia contributed to — the same rationale that already makes US10Y an M-tier donor | Low |
| **SP500, Nikkei** | The European energy crisis fed global recession risk over 2022; equities carried a diffuse Russia growth-risk component | Low |
| **Gold, JPY, CHF** *(VIX was here but is now breakpoint-excluded)* | Safe-haven bid. The catalog's position is that risk-off co-movement is the *intended* common factor SCM exploits, not contamination — but a *persistent, Russia-specific* safe-haven premium blurs that line | Interpretive — treated as signal; flagged for transparency |
| **KRW, LiveCattle** | Korea energy-importer cost pressure; North-American livestock largely insulated | Negligible |

Empirical corroboration: the §5c (ii) Bai-Perron relationship test independently dates a within-pre-window break for **VIX** (now **excluded from the pool by the breakpoint rule**, 19→18) and re-flags **Wheat**, and the §5d KS test flags **INR** (Hormuz) and a broad set (~21 of 32 donors) on Russia (the latter a macro-regime shift, not Russia-treatment) as distributionally shifted ([validation.md §5d](validation.md)) — broadly consistent with the channels above, though KS cannot separate them from the macro-regime change.

### What to do about it — options and current position

This is genuinely **partly open**. The defensible menu, in order of preference:

1. **Post-window sensitivity (recommended primary — *implemented*, [06_Ensemble_Final.ipynb](../notebooks/06_Ensemble_Final.ipynb) → `data/validation/final_postwindow_sensitivity.csv`).** Report the gap at several post-window horizons (1, 2, 3, 6 months and the full window). Because delayed contamination attenuates the gap *monotonically* with horizon, the sensitivity profile is at once a **detector** (a declining gap is the signature) and a **bound** (the short-horizon gap is the least-contaminated estimate). A flat profile means delayed contamination is immaterial; a rising profile means the effect is still building in (the opposite of contamination). This is the same logic as the existing OPEC+ post-window truncation ([methodology.md §2](methodology.md)) and the donor-pool monotonicity diagnostic ([methodology.md §7](methodology.md)) — a diagnostic, not an arbitrary choice. It is the direct answer to "should we reduce the period?": yes — *the post-window*, reported as a sensitivity profile, **not** the pre-window.
2. **Per-donor onset dating (the diagnostic that informs option 1).** For each clean donor, estimate its pre-window loading on the common factor, project into the post-window, and test the donor's *own* post-window abnormal-return path (one-sided CUSUM / structural break) for *when* it diverges. Donors whose divergence onset falls inside the chosen post-window are candidates for reclassification to M/H, or set the truncation point for option 1. This is Brent-free (uses a clean common factor, not Brent), so onset is unambiguous. The rigorous version; full automation is a future iteration.
3. **a priori reclassification.** Promote the highest-risk delayed donors (INR, CNY, the softs, Platinum) from C to M and re-run — the same monotonic-shrinkage check as the existing 21 / 27 / 33 Russia pool diagnostic ([methodology.md §7](methodology.md)).
4. **iSCM spillover correction** — considered and rejected in [methodology.md §3](methodology.md) for the small post-window and cross-event-comparability reasons.

**Current position.** The headline keeps the contemporaneous 18-donor pool and the existing OPEC+-truncated post-window; the implemented post-window sensitivity (option 1) quantifies the delayed-contamination exposure, and the direction of any residual bias is *toward zero* — conservative for the thesis claim that the premium is positive and large. Options 2-3 are the route to a sharper answer and are flagged as the next iteration.

**What the sensitivity sweep finds** ([06_Ensemble_Final.ipynb](../notebooks/06_Ensemble_Final.ipynb)):

- **Russia — declining profile (the delayed-contamination signature).** The ensemble-median gap is largest in the first month (~31%) and attenuates as the window lengthens (2m ≈ 24%, 3m ≈ 26%, full ≈ 22%; a ~9 pp drop from 1-month to full). This is exactly the predicted signature: as second-round Russia channels switch on through 2022, the synthetic is pulled up and the gap shrinks. The headline full-window estimate (~22%) is therefore a **conservative** read; the least-contaminated 1-month estimate is ~31%. (The profile is not perfectly monotone — it ticks up at 3–6 months on the summer-2022 price dynamics — so it is read as a band, not a point.)
- **Hormuz — rising-then-plateau profile (no contamination signature).** The gap rises sharply from the first month and plateaus (1m ≈ 46% → 2m ≈ 59% → full ≈ 59%), the opposite of attenuation: the chokepoint premium is large from the strike and holds, rather than donors contaminating the synthetic. Consistent with its short, near-all-C window (Cotton the lone M) having little room for delayed contamination to accumulate.

The asymmetry is itself reassuring: the diagnostic does not mechanically produce "declining" everywhere — it declines for Russia (where the delayed-contamination story is real) and rises for Hormuz (where the effect is genuinely accumulating).

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
| MSCI World | `URTH` | Broad-equity proxy ~0.95+ correlated with the S&P 500 (SPY); redundant — splits equity weight without adding factor coverage. *Previously in the pool; moved here.* |

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
