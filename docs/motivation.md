# Motivation

This document states the empirical question, situates it in the policy context, justifies the methodological choices, and explains the two-event design. It is the basis for the thesis introduction. Detailed methodology lives in [methodology.md](methodology.md); donor selection in [donor_catalog.md](donor_catalog.md); validation in [validation.md](validation.md).

## Problem statement

What is the causal effect of the 2026-02-01 Strait of Hormuz disruption on the price of Brent crude over a defined post-event window? Answering this requires constructing the counterfactual price path — what Brent would have done in the absence of the disruption — and comparing it to the observed path. The construction of that counterfactual, not the comparison itself, is the central methodological problem of the thesis.

## Context: the Strait of Hormuz as a chokepoint

The Strait of Hormuz is the narrow shipping lane between Iran and Oman through which a large share of seaborne crude and condensate transits daily — approximately one-fifth of global petroleum-liquids consumption, per US EIA estimates (the precise figure varies year to year and should be re-verified for the year of analysis). No fully redundant bypass exists: the Saudi East-West pipeline and the UAE Habshan-Fujairah line together carry a fraction of the volume that transits the strait, leaving the remainder dependent on the maritime route. A disruption to this chokepoint — whether by physical blockade, mining, military exchange, or insurance-driven shipping withdrawal — is the single largest unhedged supply-side risk in the global oil market.

Periodic near-miss episodes — the 1980s tanker war, the 2019 Abqaiq drone strike, repeated tensions through the mid-2020s — have produced transient risk-premium spikes without an actual closure. The 2026-02-01 event ([data/historical_events.csv](../data/historical_events.csv)) is the realisation of the long-anticipated tail risk. Its magnitude in terms of Brent price drives the policy implications below.

## Why this matters for policy

A credible Brent-price treatment-effect estimate is an input to several policy decisions that are typically actioned under acute uncertainty:

- **Strategic petroleum reserve releases.** IEA-coordinated emergency stockdraws (most recently the 2022 post-invasion release) are sized against the estimated supply shortfall and the implied price displacement. A treatment-effect estimate gives planners a magnitude to calibrate the release size against, rather than relying on contemporaneous market commentary.
- **Central bank reaction function.** Oil-price shocks pass through to headline inflation directly and to core inflation via input costs and inflation expectations. Whether the appropriate response is to look through the shock or to tighten depends on the size of the Brent move and its expected persistence. The treatment-effect estimate is the input to this calculation.
- **Fiscal stabilization in oil-importing economies.** Countries with fuel subsidies, oil-indexed transfers, or import-bill exposure face quantifiable fiscal costs proportional to the price shock. Ex-ante magnitude estimates allow contingency budgeting.
- **Sovereign hedging programs.** Mexico's annual oil-export hedge (priced through OTC put options on Brent or WTI) and analogous programs are sized against scenario-based price paths; a treatment-effect estimate is a defensible input to the disruption scenario.
- **Long-term supply-diversification policy.** The marginal value of strategic infrastructure (additional bypass pipeline capacity, LNG import terminals, refined-product storage) depends on the price avoided per barrel of chokepoint-routed import displaced. The treatment-effect estimate provides the per-barrel benefit term.

None of these applications are hypothetical. Each is documented in standard IEA, IMF, and national-government practice. The binding constraint in each case is the quality of the price-impact estimate, which is what this thesis produces.

## Methodological approach: why synthetic control, and why the ATE

Brent is a single global benchmark with no plausible direct counterpart. This rules out the standard observational causal-inference toolkits that rely on multiple treated and control units (difference-in-differences), on a continuous running variable around a known cutoff (regression discontinuity), or on a credible instrument. The remaining options are:

1. **Event study with abnormal returns.** Gives a magnitude over a short window but no counterfactual path beyond a few days; assumes the pre-window expected return generalises forward, which is brittle over a multi-month post-window relevant to policy.
2. **Structural VAR with identified oil-supply shocks** (Kilian 2009 *AER*; Kilian & Murphy 2014 *JAE*; Baumeister & Hamilton 2019 *AER*). Identifies a decomposition of price moves into demand, supply, and inventory shocks but requires identification restrictions that are themselves contested — and the restrictions appropriate for a chokepoint event have no standard precedent.
3. **Synthetic control method.** Constructs a weighted combination of donor series (other commodities, FX, equities, rates) whose pre-event co-movement with Brent is high, then projects that combination forward through the post-event window as the counterfactual.

The thesis uses synthetic control. The justifications:

- It produces a **full counterfactual path**, not a point estimate. Policy levers (SPR sizing, central-bank pass-through, fiscal buffers) operate on the integrated price displacement over a window, not on the peak spike.
- The identification argument is **auditable**: every assumption is encoded in the donor pool and the per-event SUTVA catalogue, which a reviewer can inspect ([donor_catalog.md](donor_catalog.md)).
- The **inferential machinery** (in-space placebos, in-time placebos, leave-one-out, cross-event transfer) is well-developed at this sample size and traces directly to Abadie, Diamond & Hainmueller (2010 *JASA*, 2015 *AJPS*) and Abadie (2021 *JEL*).
- The method does **not require a structural identification stance** on whether the Brent move reflects supply, risk premium, or expectations. The treatment-effect estimate is reduced-form total-effect, which is precisely what most policy applications need.

The estimand is the **average treatment effect on the treated** (ATT, often called the ATE in informal SCM usage since there is only one treated unit): the average gap between observed and counterfactual Brent over $[T_0, T_0 + W]$, where $W$ is the post-event horizon. The ATT is preferred over the peak gap or the terminal gap because (i) it integrates over the full path including any reversion, which is what the policy levers above care about, and (ii) it is less sensitive to single-day price jumps that may reflect liquidity or futures-roll mechanics rather than persistent dislocation.

## Why two events: Hormuz and Russia 2022

The substantive question is Hormuz. But applying SCM to Hormuz alone has a hard limitation: there is no way to verify the method without first applying it to a comparable, already-known disruption. A reviewer presented with a single SCM number for Hormuz cannot distinguish a sound estimate from an artefact of model choice — the donor pool, the pre-window length, the model class, and the regularisation all interact in ways that the headline number obscures.

The **2022-02-24 Russian invasion of Ukraine** provides the calibration case. Brent rose from approximately \$95 to \$130+ within two weeks of the invasion, and the path over the following months is well-documented in central bank and IEA commentary. Running the same SCM machinery on this known disruption and recovering the documented magnitude is a **magnitude validation** — it verifies that the design produces credible numbers before the design is applied out-of-sample to the focal event.

A second purpose, distinct from magnitude validation: the shared 21-donor pool used for both events ([donor_catalog.md](donor_catalog.md)) enables the **cross-event weight-transfer test** ([validation.md §5f](validation.md)). Russia-fitted donor weights are applied to the Hormuz pre-window; if the implied Hormuz counterfactual agrees with the independently-fitted Hormuz counterfactual, the factor structure underlying SCM is regime-stable across 2020-22 and 2024-26. This is the single strongest test of methodology generalisation available with two events, and it is not available if only one event is estimated.

Excluding Russia would therefore (i) leave the Hormuz estimate without method-validation against a known case, (ii) remove the strongest robustness test in the validation battery, and (iii) make a reviewer's first natural question — *"how do you know SCM works on this kind of shock?"* — unanswerable.

The choice of Russia 2022 specifically (rather than 2019 Abqaiq, 2020 Saudi–Russia price war, or earlier supply disruptions) is justified separately in [donor_catalog.md](donor_catalog.md): Russia 2022 is the most recent large, well-measured, broadly agreed-on Brent disruption, and its pre-window does not overlap with the Hormuz pre-window, preserving independence.

## Scope and boundaries

What this analysis does *not* do, deliberately:

- It does not estimate physical supply shortfalls in barrels per day. The estimand is Brent price; the volume question is upstream and out of scope.
- It does not model downstream pass-through to retail fuel, headline inflation, GDP, or any other macro outcome. Those are *applications* of the Brent-price estimate, sketched in the policy section above but not estimated here.
- It does not produce a structural decomposition of the Brent move into demand, supply, and risk-premium components. The ATT is a reduced-form total-effect estimate; structural decomposition is a separate exercise that requires identification restrictions outside the SCM framework.
- It does not produce ex-ante predictions for future Hormuz disruptions of different severities. The estimate is conditional on the realised 2026-02-01 disruption and its observed donor-pool counterfactual; severity-dependent extrapolation would require a structural model.

The boundaries are deliberate. They keep the analysis on a single well-identified estimand for which SCM is the appropriate tool, and they leave downstream policy applications to users with their own models of the rest of the macro economy.
