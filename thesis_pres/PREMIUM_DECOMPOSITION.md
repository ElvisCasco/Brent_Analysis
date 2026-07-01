# Understanding "Brent's own move" — a note for the presenters

You raised the right objection:

> *In SCM the whole synthetic Brent is built only from donors. So where does
> "Brent's own move" come from? It feels like we smuggled in an extra term.*

Short answer: **you are right — the counterfactual is 100% donors.** "Brent's own
move" is **not** part of the model. It only shows up when we take an *optional
second step* and break the premium apart. Below is the clean way to think about
it, in two levels.

---

## Level 1 — the actual method (this is all SCM does)

Two lines, nothing else:

1. **Synthetic Brent** = a fixed weighted blend of donors:
   `synthetic_t = intercept + Σ_j β_j · donor_{j,t}`
   → entirely donor-determined. ✅ *This is exactly your intuition.*

2. **Premium** = how far the *real* price sits above that blend:
   `premium_t = observed_t − synthetic_t`

That's the whole answer. **There is no "Brent's own move" here.** The premium is
just the gap between the real Brent and the donor-built Brent.

```
      observed Brent  ─────────────●   ← real price (the data)
                                   │
                                   │  ← premium  = observed − synthetic
                                   │
   synthetic Brent  ──────────────●   ← 100% donors (the counterfactual)
```

If you only ever say this, you are completely correct and you never mention
"Brent's own move." **The headline 53% / 22% comes straight from this gap.**

---

## Level 2 — the waterfall (optional: *why* is there a gap?)

The "What builds the premium" slide does something extra. It asks:

> Over the event window, **how far did each side travel** from the shared
> pre-event starting line?

Because the synthetic tracks Brent *before* the event (good pre-fit), both lines
start from the same place. Then the gun fires (the event), and:

- **Observed Brent travels some distance** → we call this *Brent's own move*.
  This is just the raw before/after change in the real price. **It is the data,
  not a model ingredient.**
- **The synthetic travels some distance** → and because the synthetic is a blend
  of donors, *its* distance is the sum of the donor pieces (`β_j × how far donor
  j moved`).

The premium is simply the **difference in how far the two sides travelled**:

```
premium  =  (how far observed Brent moved)  −  (how far the donor-synthetic moved)
         =        Brent's own move           −        Σ  donor pieces
```

So "Brent's own move" is not a *third thing* competing with the donors. It is the
**observed side** of the gap. The donors are the **model side**. The premium is
the space between them. The waterfall just draws both sides on one axis — which
is why it can look like Brent's move is "another contribution." It isn't; it's
the thing the donors are being compared *against*.

---

## The runner analogy (use this out loud)

Picture a race.

- **Your runner = observed Brent.**
- **The pack = the donor-synthetic** (a fixed weighted team of gold, coffee,
  bonds, …).
- Before the gun they run **side by side** — that's the pre-event fit. This is
  what earns our trust: the pack can shadow Brent when nothing special is
  happening.
- **The gun = the event** (invasion / Strait closure).
- After the gun, your runner sprints. The pack runs too — as fast as normal
  market forces (growth, dollar, risk) would carry it.
- **The premium = how far your runner finishes *ahead of the pack*.**

"Brent's own move" = how far **your runner** went.
"Donor contributions" = how far **the pack** went.
Premium = your runner − the pack. You need both finish lines to measure a lead,
and both are measured from the same start. That's *all* Brent's own move is.

---

## The two events, in runner terms (with the real numbers, log points)

| | Your runner (Brent) | The pack (donors) | Lead = **premium** |
|---|---|---|---|
| **Russia 2022** | +55 | **+36** (pack ran hard) | +20 → **22%** |
| **Hormuz 2026** | +37 | **−5** (pack barely moved) | +43 → **53%** |

- **Russia:** 2022 was a global inflation surge, so the pack (coffee, bonds…)
  *also* sprinted +36. Brent's +55 lead over them is only ~22%. Most of Brent's
  jump was "the whole market ran," not Russia.
- **Hormuz:** the non-oil pack basically stood still (even drifted back as gold
  rose). Brent ran +37 essentially alone → the ~53% is almost all chokepoint.

Same-looking price jumps, opposite verdicts — and the *only* reason we can tell
them apart is that the pack (the donor counterfactual) ran differently.

---

## Why the numbers are in "log points"

We measure each distance as `100 × (log P_after − log P_before)`. Logs are used
for one reason: **they add up**. In log space,
`premium = Brent's move − pack's move` is exact, so the waterfall bars stack
cleanly. Only the final **Premium** bar is converted back to a plain "%"
(e.g. +20 log points → `exp(0.20) − 1 ≈ 22%`). That is why a bar can read
"+55" while the premium reads "22%".

---

## The one algebra line (only if an examiner pushes)

Start from the definition, average over the post window, and use the fact that
the pre-window gap is ≈ 0 (good fit), which pins the intercept:

```
premium ≈ mean_post(gap)
        = [mean_post(logP) − mean_pre(logP)]  −  Σ_j β_j [mean_post(donor_j) − mean_pre(donor_j)]
          └────────── Brent's own move ──────┘     └────────── the pack's move (donors) ─────────┘
```

The intercept and the pre-event levels cancel — which is *why* a term that looks
like "Brent by itself" falls out. It was always just the observed side of
`observed − synthetic`, re-centred on the pre-event baseline.

---

## How to present it — pick your comfort level

- **Safest (Level 1 only):** show the paths figure, say *"premium = real Brent −
  donor-built Brent = 53%."* Never mention Brent's own move. Fully correct.
- **Richer (Level 2, the waterfall):** *"Both start together; after the event
  Brent ran +37 while the donor pack barely moved, so 53% is the lead."* Use the
  runner words, not "contributions," to avoid the confusion you just felt.

If the waterfall still feels like a liability on stage, we can swap that slide
back to the simpler "observed vs synthetic, gap = premium" view and keep the
waterfall as a backup for the Q&A. Your call.
