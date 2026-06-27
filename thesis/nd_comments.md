# Paper revision notes — changes from the original draft

These notes summarise the substantive changes made to each section. Purely cosmetic
rewording is not listed. A few open items that still need attention are collected at the
end.

A global style rule was applied to every rewritten section: no semicolons and no "---"
(em-dashes). En-dashes inside names, date ranges, and number ranges (e.g. 2020--22,
Benjamini--Hochberg) were kept, since those are correct typography. Sentences that
relied on semicolons or em-dashes were restructured.

The main changes I made were related to methodological inconsistencies, unclear or confusing wording, comments that sounded too AI-generated, places where there wasn't enough context (I added more where I thought it was needed), paragraphs with very dry openings, and weak transitions between sections. I also tried to rewrite some parts so that the whole text reads more like one continuous story. In a few places, I removed information that I felt wasn't really necessary, just to make the paragraphs easier to read and digest.

I didn't add any new figures or tables, and I haven't worked on the appendix section. I also didn't verify any of the numbers in the draft—I assumed they were correct and left them as they were. They're probably fine, but it might still be worth giving them one more check.

Since I didn't work on the appendix, one thing that's still left is to decide what information from our core text we can move to the appendix, and what additional material it would make sense to include there.


**Biggest open question (read this first):**

The main thing still open is whether we mention all five models we trained or not. Our
methodology really does need us to name them at some point, since the whole approach is
running five quite different modelling approaches, taking the median, discussing the
IQRs, and putting each model through several validation checks. So at some point we have
to say which models we trained and what results they gave. I have thought a lot about the
cleanest way to make the text easier to read, and so far I have shortened some tables and
paragraphs by dropping some models, but a few of them are still really dense. I do not
agree with cutting model names entirely, but to lighten the main text we could push the
model-specific details into the appendix, like which features each model used and what
results it had, and in the main text just talk about the median and the IQR without
giving model-level numbers. That probably will not work everywhere, since there are still
paragraphs where we genuinely need to say something about the individual models, but it
would help. This is the open direction. I have thought about it a lot and have not landed
on a solution, so if you work on it, this is the main thing left.

---

## Abstract

1. Changed the beginning — added more context (the ~1/5 of seaborne oil framing) in a
   smoother way, less dry.
2. Fixed the Russia framing. We did **not** apply the Russia-fitted model to Hormuz as
   out-of-sample validation. That was only exploratory and is not our estimation
   methodology, so the original wording was wrong. Now framed as Russia being a
   **benchmark/calibration** event, with each event estimated separately.
3. Removed the "$95 \to $130" Russia numbers (pre-event vs peak price). Potentially
   confusing and not needed in an abstract.
4. Cut the detailed validation list down to one short sentence that the estimate is
   validated and robust. The full battery belongs in the body, not the abstract.

---

## Introduction

1. Rewrote the first paragraph so the sentences connect logically: ~1/5 of consumption,
   which exporters use the Strait, no maritime bypass, hence the strongest bottleneck,
   then the near-misses and the first actual closure.
2. Added **why Brent** (it is the global benchmark most crude is settled against; spot,
   not futures) and **why oil** (input to nearly every industry).
3. Removed the bold paragraph headers ("Why the magnitude matters", etc.). Each
   paragraph now opens with a normal topic sentence instead.
4. Reordered the methods discussion: first **why SCM** (DiD / RDD / IV not feasible),
   then **how it positions** against event studies, SVARs, and scenario models, framed
   as complements rather than competitors.
5. Moved the Becker (2021) novelty point into its own short paragraph (closest neighbour,
   but retail fuel + cross-country donors, so our cross-asset crude application is new).
6. Fixed the same Russia framing as in the abstract: benchmark, not transfer. Added that
   the shared 19-donor pool lets us compare weights across regimes, not transfer a fit.
7. Added the two-part contribution statement (the Hormuz estimate + the validation
   template) and a short roadmap.

---

## Related Literature

1. Cut the references substantially, mainly the ML/time-series subsection, which read
   like a methods-textbook bibliography. Foundational-method citations (boosting,
   elastic net, CV, break tests, etc.) were moved to where the tools are actually used
   (Methods / appendices) rather than listed here.
2. Re-anchored tool citations: where a technique matters, we cite the paper that uses it
   in synthetic control, not the paper that invented it in the abstract.
3. Merged six subsections into four, following the funnel: building counterfactuals for
   one unit → where SCM has/has not been applied (incl. the institutional comparison
   set) → incumbent oil-shock methods → inference.
4. Each subsection now opens with a clear topic sentence.
5. Moved the GPR index (Caldara & Iacoviello) point into the oil-shock-methods paragraph
   as a short "why we don't use it as a regressor or donor" note, since the GPR overlay
   is not on our figures.

---

## Conceptual Framework

1. Replaced the soft opening ("a good data-science analysis needs...") with a direct
   statement of what the section does and why the factor model comes first.
2. Added topic sentences to every subsection.
3. **Important substantive fix:** the contamination-bias subsection no longer claims the
   bias is signed "exactly". The identity is exact, but $\delta_{jt}$ is unobserved, so
   the measured sign is a deliberately naïve directional estimate. This now matches what
   we actually do in Results (otherwise Theory promised something Results walks back).
   Retitled to "The direction of contamination bias".
4. Added the testable vs untestable distinction at the end of the assumptions subsection:
   assumptions 1 and 3 are data-testable, assumption 2 (cleanliness) is the untestable
   one. This motivates the bias subsection.
5. Changed "cross-event weight transfer" to "comparing donor weights between regimes" in
   the regime-stability assumption, consistent with the rest of the paper.
6. Trimmed duplicate foundational citations from the model table.

---

## Data

1. Added a short intro paragraph before the subsections.
2. Added the window-length argument: for daily-traded benchmarks a longer pre-history is
   not automatically better, because spanning multiple regimes re-enters as post-event
   interference (a SUTVA issue), so the goal was the longest **shock-free** window, not
   the longest available.
3. Added a sentence stating how the 19-donor pool is formed operationally (Clean-rated
   for Russia only → 32 reduced to 19) and that Cotton is **excluded** on the strength of
   the Russia audit, so its flag and its absence from the pool are now linked.
4. Removed "to enable the cross-event weight transfer" as a justification for the shared
   pool. The shared pool is justified by comparability instead.

---

## Empirical Strategy and Validation

1. Removed the cross-event weight transfer from the validation battery. Added a sentence
   stating that the two events share donors and pipeline but are trained **separately**,
   and that the transfer is reported in Results only as an **exploratory** regime probe,
   not a validation test.
2. Reconciled the VIX break with the Data section: the VIX relationship-break is ~7 weeks
   **before** the Russia $T_0$, not at it, and does not recur on the analysis window.
3. Restructured the validation around the three named levels (fit / identification /
   inference), so the structure follows the framework we state. The cleanliness battery
   now sits under "identification".
4. Stated the purpose of walk-forward CV in a causal design (evidence against
   overfitting, not model selection).
5. Made the ensemble-median computation explicit (operates on the gap series, since the
   models' weights are incommensurable).
6. Labelled the ARIMA baseline correctly (AIC-selected, reduces to a driftless random
   walk in both events) instead of "frozen ARIMA".
7. Dropped the software/packages sentence.

---

## Results

1. Reduced model-by-model detail. The prose now reports at the ensemble level and names
   individual models only where the model identity is the point (mainly the
   "economic reading of the spread" paragraph). Per-model numbers stay in the tables.
2. Shrunk the tables: dropped raw train/val RMSE columns from the WFCV table (kept ratio
   + flag), and collapsed the Russia rows in the placebo table to a single "best of five".
3. Leave-one-out: report all models for Hormuz (the focal event) and the ensemble-median
   range for Russia, with a sentence explaining the asymmetry (Russia's wider spread is
   the soft-commodity concentration, i.e. the same donor-quality issue as the
   contamination finding).
4. Cross-event transfer: reframed as an exploratory regime-stability probe and added the
   explanation for **why** it is weak (the two pre-periods are different factor regimes:
   COVID-recovery + Fed tightening vs a calmer disinflation regime; the FX-heavy models
   fail hardest; extending the window widens the gap). Framed the weakness as evidence
   that fitting separately is correct.
5. Naïve baseline: added the three findings explicitly — (a) SCM adds value over the
   random-walk null, (b) the naïve bias flips sign across events because the pre-window
   trend sign differs (the key finding), (c) for Russia the SCM and the trend
   extrapolation bracket the truth.
6. Contamination-bias subsection: added the "naïve, directional" framing up front (it
   asks which way a bias would go, not a structural correction). Hormuz: any residual
   bias is negative, so the estimate is conservative (true effect at least as large).
   Russia: bias is positive, with a short economic explanation (risk-off depressed the
   demand-cyclical donors relative to FX), concentrated in low-reliability donors.
7. De-named throughout: replaced "model X did Y" with ranges wherever the model identity
   is not needed to make sentences easier to digest.
8. Interpretation: lead with the headline and its robustness, then caveats. Stopped
   re-listing every passed check. Kept the "complement not competitor" framing.
9. Added a **Limitations** subsection: single treated unit + short post-window
   (under-powered inference, placebo only reaches its floor); reduced-form total
   estimand (no supply/risk/expectations split); Hormuz recency (no external ground
   truth, leans on Russia by analogy); regime-bound factor structure. Noted that donor
   cleanliness is only partly testable.

---

## Conclusion

1. Fixed the Russia framing (benchmark, not "validate first then apply").
2. Aligned the limitations with the Results limitations subsection (dropped the
   Bayesian-ridge-vs-BSTS and convex-volatility points, which we had deliberately left
   out of the Results list).
3. Softened "statistically distinguishable" to "large and robust", consistent with the
   honest reading of the placebo floor.
4. Added the explicit two-part contribution and a short policy-use paragraph.
5. Rewrote into four short, easy-to-read paragraphs.

---

## Extra comments & open items still needing attention

These items are still open and need to be done:

1. **Float placement.** The tables and figures are drifting to the wrong spots in the
   PDF. We need to fix this so they appear where they belong.
2. **Number consistency.** I have not checked the numbers themselves. I assume Elvis'
   Claude got them right, but since there were a few inconsistencies in the
   introduction, it is safer to double-check that every number in the paper comes from
   the latest results.
3. **AI-ish words.** I went through and changed most of the sentences that sounded
   AI-generated, but a few odd or overly fancy words are probably still in there and we
   could swap them for something more natural. There are not many left, though, so even
   if we skip this I do not think a reader would really notice.
4. **`hammiratrix2024` citation.** Claude flagged this one: it could not verify the
   citation and thinks it may be garbled. It currently supports the donor-reliability
   ($R^2$ split) argument. We should either confirm it actually exists and get the exact
   reference, or just leave that sentence without a citation (it reads fine either way).
   We should not submit with an unverifiable citation on a point we lean on.

My thoughts on each section after my edits:

1. **Abstract.** Easier to read now, the opening is much better, and I do not think there
   are any inconsistencies left. The length is about the same as before. **I think this
   part is ready.**
2. **Introduction.** **This part is really good as far as I am concerned.** The one thing
   we could still do is shorten some paragraphs, because **right now we explain a lot of
   things that also get explained later**, especially the literature. We could mention
   those points more briefly here than we currently do, since the lit review covers them
   in full.
3. **Literature.** This part seems done. The only open question is **Caldara and
   Iacoviello**, since we do not really refer to them anywhere else in the paper. We
   could drop them, or, if you think it is worth keeping as an example of a method that
   is widely used in this field but was not a good fit for us, we can leave it in.
4. **Conceptual Framework.** This part seems ready. The only thing is the last paragraph,
   where we point to an appendix about Bayesian ridge. I do not think we need that
   appendix. Explaining each machine-learning method in depth is not necessary and just
   makes the section harder to digest, so we can delete the closing sentences that are
   specifically about Bayesian ridge.
5. **Data.** Here I think we should do more to justify why we picked those 33 variables as
   our donors in the first place, rather than others. We can then add an appendix section
   that explains it properly, covering which variables we excluded and why, the way Elvis
   walked through it in the presentation. Some were dropped for economic reasons and some
   because of our statistical tests. It was a bit boring for the audience, but for an
   appendix it is fine, and anyone with questions will find the answers there.
6. **Empirical Strategy and Validation.** If we want to cut down on how much we explain
   each model, we can move the explanations from the "Estimators" subsection into the
   appendix, and keep only a brief description of the estimators here with a pointer to
   the appendix for the details. "5.2 Validation battery and its logic" seems fine to me
   as it is.
7. **Results.**
   - In some places I removed individual model results where we did not need them to get
     the point across, but in other places we still report all of them. I could not find
     a clean way to cut those, because our whole methodology is five modelling approaches
     and the median across them. We have the charts, we have the IQR, and we need to
     explain that this is the method, and once we do, I do not see how we avoid naming
     some of the models. Maybe we can still thin them out by pushing some results to the
     appendix, but this one is still up for consideration.
   - The **"Economic reading of the model spread"** paragraph is quite dense. Even if we
     keep all five models in the results discussion, I think we should move some of the
     detail into the appendix. Also, where we talk about individual donors like coffee,
     sugar, and the currencies, it would help to have an appendix section with plots
     showing how those variables behaved, including their pre- and post-event trends.
   - I also think it would be good to have an appendix section showing the feature
     importances for each model.
   - We can add more plots or tables in the appendix for our validation checks too, since
     we already have them in the notebooks. For example, in the "Leave one donor out"
     paragraph we report the numbers straight in the text, where a small table or chart
     would work better. The same goes for "cross-event weight stability" and "sign of
     contamination". Some of these can go in the appendix and some in the main text,
     since right now we have a few paragraphs that are just numbers with no chart or table
     to support them.
   - For the post-event horizons plot, it would be better to put the numbers directly on
     the lines.
   - I added the limitations subsection here. If you want to mention something different
     in it, feel free to change it. I think it is better to have a dedicated subsection
     for it rather than only touching on it in the conclusion.
8. **Conclusion.** This one seems good and ready.
9. **Appendix.**
   - "Robustness Grid" — we should keep this, but explain things in more detail, like I
     said above: why we chose those 33 variables, and the criteria we used to remove each
     of the ones that did not make the final pool.
   - "Bayesian ridge and full BSTS" — I do not think we need this appendix. It is a true
     story, but I do not think it is something our supervisor cares about.
   - "Structural-break tests" — we can keep this one.
   - On top of those, we can add the extra sections I mentioned above.