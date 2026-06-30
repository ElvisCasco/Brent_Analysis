# Presentation outline — Pricing the 2026 Strait of Hormuz disruption

15 minutes, sales pitch. Goal is to make the audience believe one number (~53% Brent premium) and the design that earns it. Show only what carries that narrative. Rough budget: ~3.5 min setup, ~2.5 min headline, ~2.5 min method decisions, ~3 min validation, ~2 min close.

---

## 1. Title slide carries the intro (~1.5 min)
*The situation is the title slide. Open cold on the event, not the method. No separate hook slide.*

- Title + name/affiliation/date, then the situation as the body of the same slide:
- Since 28 Feb 2026 the Strait of Hormuz is largely closed in the Iran war. First time it has actually shut.
- Why it binds: ~1/5 of world petroleum-liquids consumption, ~27% of seaborne oil trade, and no redundant route. Gulf crude has nowhere to go. Brent passed $100 for the first time in four years.
- Why care, spoken: reserve releases, the monetary look-through-or-tighten call, fiscal subsidies, and sovereign hedges all scale with the *size and persistence* of the move, not a headline price.

*Keep the title slide to title + 2–3 situation lines. The policy-levers line is spoken, not printed.*

## 1b. Timeline figure (~0.5 min)
*The visual anchor, and the first appearance of the Russia benchmark. Three beats, ~30s. Don't narrate the price wiggles.*

- **Orient and land the parallel.** Brent roughly doubled after both focal events from a similar base near $75, but reached each differently, a steep 2020–22 recovery before Russia and a mild decline through 2024–25 before Hormuz. Same magnitude, different paths.
- **Why these two, not the rest.** Everything grey is the surrounding cluster of lesser shocks (COVID, price war, Red Sea, Israel–Hamas). The two bold lines are what we isolate, the honesty signal that we step around the noise rather than cherry-pick.
- **Plant the benchmark.** Russia 2022 is documented ($95→$130). It sits next to Hormuz because if the same machinery recovers Russia's known move, the Hormuz number earns trust. The one forward reference that makes the later validation land.
- Skip here: the shaded estimation-window bands and the lettered shock list, both saved for the window bullet on slide 7. (`brent_timeline.png`)

## 2. The question (~1 min)
*Sharpen from "prices rose" to a causal object.*

- The raw jump conflates the disruption with everything else moving markets, and says nothing about the path.
- Research question, stated plainly: **the causal effect of the Hormuz disruption on Brent over a policy-relevant post-event window — as a path, not a single number.**
- The hard part: that counterfactual (Brent absent the disruption) is never observed.

## 3. Why standard tools fail, and what we do instead (~1.5 min)
*Still intro + a thin slice of related literature. Motivate SCM in one breath.*

- One global benchmark, so no DiD control sharing its trend, no credible IV for a one-off geopolitical event.
- **Synthetic control:** a weighted basket of donor assets that co-moves with Brent before the event, projected forward as the counterfactual. Gives a full path and an auditable identifying assumption.
- The gap from the literature (the contribution): SCM has gone to GDP, trade, employment — almost never a daily traded price, and never a crude benchmark with **cross-asset** donors under a geopolitical shock. Institutional analyses (Kiel, OIES, World Bank, IEA) go the opposite way, assuming a barrel shortfall and propagating it. We read the effect off the market instead. Complementary, not competing.
- **The credibility move, stated up front:** we validate the whole design on the documented 2022 Russia invasion before trusting it on Hormuz.

*Cut for time: the full three-literature taxonomy, weight non-uniqueness discussion, inference-theory citations. Mention only if asked.*

---

## 4. Headline result (~3 min)
*Pay off the setup immediately. This is the slide they remember.*

- **Hormuz: ~53% premium** over Brent's no-event level across the first ~4 months (IQR 48–53%). Actual mean ~$105 vs implied counterfactual ~$69.
- **Russia (the benchmark): ~22%**, implied counterfactual ~$89 vs actual ~$108 — consistent with the documented $95→$130 move.
- **Lead figure:** observed vs synthetic paths, both events (`counterfactual_paths.png`), with the two magnitudes on the figure.
- Two support beats underneath, on the same slide, just enough to make 53% feel earned:
  - **It's tight.** Hormuz band is ~5 points across five very different models vs ~20 for Russia — the calm pre-period.
  - **It's conservative.** If the donors are contaminated at all, the bias on Hormuz points *down*, so the true premium is likely larger, not smaller.

## 5. Method — only the decision points (~2.5 min)
*Short. Not a methods lecture. Frame each as a choice with a tradeoff.*

- **Decision 1 — donor pool is identification, not fit.** We span the global factors that move Brent in normal times (industrial cycle, dollar, real rates, risk appetite, China) with non-oil assets, and we *exclude the energy complex by design* — WTI, refined products, petrocurrencies — despite their high correlation, because they load on the very oil-specific shock we are trying to measure. Choosing identification over fit.
- **Decision 2 — an ensemble, not one model.** The counterfactual's functional form is unknown, and SCM weights are non-unique. So five estimators whose biases bracket the cases: convex SCM, augmented SCM, elastic net, XGBoost, Bayesian ridge. Headline is the cross-model **median**; IQR is the model-uncertainty band. A premium that survives biases this different is unlikely to be a single-model artifact. Close this slide with the window point in one breath: the pre-window is the longest stretch with no Brent-specific shock, ~20 months each so the two events are comparable, and each event is fit fully separately so no parameter crosses over (a SUTVA choice, not a sample-size one).

**Two slides:** donor pool, then the five-estimator table (`tab:models`) with the window bullet underneath.

*Cut for time: window-selection detail, hyperparameter grids, walk-forward CV mechanics, the factor-model equations. Appendix / backup slides.*

---

## 6. Why you should believe it (~3 min)
*One continuous arc, mechanism before proof. What's under the hood, then the design holds up internally, then independent methods agree. Don't bounce back to results.*

**Slide A — what drives the number, and why the dispersion is benign**
- The premium is the gap between Brent and the basket, and it's clean only while loaded donors hold their pre-event relationship. So it matters which donors carry the result.
- **Hormuz** rests on **Gold** as the single weighted late-diverger (post-strike safe-haven bid). **Russia** rests on the diverging Asian currencies the Fed cycle pulled away — which is also *why* the Bayesian ridge is the Russia outlier.
- The point: cross-model disagreement traces to a handful of heavy donors, not noise, and for Russia that contamination runs conservative. The dispersion is economic and it works in our favour. (`donor_roles.png`)

**Slide B — independent methods with no shared donors agree**
- **Beats the naive floor:** ~7 points above a donor-free random walk for Hormuz; the donor machinery extracts something Brent's own past cannot, and unlike a trend extrapolation it isn't regime-fragile. (`naive_baselines.png`)
- **External calibration on Russia:** the same machinery lands within **$3.6** of the EIA's pre-invasion structural forecast — two methods that share no information path, nearly the same counterfactual. This is also why Russia's weaker placebo (next slide) doesn't worry us: its magnitude is pinned down independently here.

**Slide C — the design holds up internally, closing on the placebo**
- **No single donor drives it.** Leave-one-out: drop each weighted donor in turn and Hormuz stays tight, ~48–56% across models.
- **The gap isn't a mechanical artifact.** Horizon sensitivity: Hormuz builds in and holds (~46 → 59 → 53%) while Russia attenuates with horizon. The same diagnostic running opposite directions on the two events is the tell that it's real, not a window effect. (`postwindow_sensitivity.png`)
- **In-space placebo, the closer:** Brent ranks **first** of all units, p at the attainable floor (0.050). The strongest result the test allows at this sample size. (`placebo_hormuz.png`)
- Honest caveat, already defused on the previous slide: Russia's placebo never reaches the floor, a known low-power property under a volatile pre-period, which is why Russia leans on the external calibration instead.

*Backup slides ready: walk-forward fit ratios, cross-event transfer, contamination-bias detail, donor-weight heatmap.*

## 7. Close (~2 min)
*Restate the sale and the contribution.*

- **The number:** the 2026 Hormuz disruption added a large, robust premium to Brent — on the order of **half its no-event price** — large, stable across estimators, conservative if anything, driven by no single donor or model.
- **The two-part contribution:** (1) a data-driven ATT for Hormuz that complements the institutional scenario estimates; (2) a transparent, auditable template for cross-asset synthetic control under a single-unit geopolitical shock.
- **Honest limits, briefly:** reduced-form total effect (not decomposed into supply/risk/expectations); validation is internal, calibrated by analogy to Russia; the factor structure is regime-bound.
- Land on: the market's own co-movement says Hormuz added roughly half of Brent's price, and the design that recovers it is itself the deliverable.

---

## Slide budget (target ~11 slides)
1. Title + intro — title, name/affiliation/date, and 2–3 situation lines (strait shut since 28 Feb 2026, why it binds, Brent over $100). Open cold on the live situation, not "this thesis examines." Policy levers spoken.
2. Timeline figure — Brent 2020–2026 with both focal events, plants Russia as the benchmark
3. The causal question
4. Why standard tools fail → SCM + the contribution gap
5. **Headline: paths figure + 53% / 22%, with tight + conservative as support bullets**
6. Method decision 1 — donor pool / exclude energy complex
7. Method decision 2 — the ensemble (five-estimator table), windows as a closing bullet
8. What drives it — donor contributions (Gold for Hormuz, currencies for Russia), dispersion is economic and conservative
9. Validation, external — beats naive floor + EIA calibration on Russia (independent methods agree)
10. Validation, internal — leave-one-out + horizon sensitivity + placebo at the floor (the closer)
11. Conclusion — number + contribution + limits
12. (Backup) window selection, walk-forward fit, transfer, hyperparameters, contamination-bias detail

## Figures available to pull from `thesis/figures/`
- `brent_timeline.png` — slide 2
- `counterfactual_paths.png` — slide 5 (the money slide)
- `donor_roles.png` — slide 8 (what drives it); `donor_importance_heatmap.png` — backup
- `naive_baselines.png` — slide 9 (external)
- `postwindow_sensitivity.png` and `placebo_hormuz.png` — slide 10 (internal)
