---
description: The intensity–size coupling measured on public Last.fm logs, with its gates and its limits.
---

# Measurement: the coupling

## The question

The lemmas hold for any play matrix. But one quantity decides *which side of the crossover* real artists fall on: how strongly the intensity of an artist's audience scales with the artist's size. In the simulation this is a dial, `γ`. On real data it is a slope: how `log(plays per pair)` moves with `log(audience)`. Call the measured version **b** — it is a proxy for `γ`, not the same object, because it also absorbs graph selection and retention.

## What was measured

Panel of Last.fm listening logs, 2005–2014. All gates passed before any number was read.

| Cut | b (user fixed effects, two-way clustered SE) |
|---|---|
| Full panel (~10 years), 50/50 blend | **+{{emp1.panel}} ± {{emp1.panel_se}}** |
| — mainstream listeners | +{{emp1.main}} |
| — beyond-mainstream listeners | +{{emp1.beyond}} |
| — window: calendar year | +{{emp1.year}} |
| — window: one month | +{{emp1.month}} |
| — head of the distribution (A ≥ 200) | +{{emp1.head}} |
| Last.fm-360K (top-50 per user) | +{{emp1.k360}} |
| BeyMS truncated to top-50 (falsifier) | +{{emp1.trunc}} |

**The sign is solid inside this domain.** It does not flip in any cut: two datasets, two estimators, 27 threshold combinations, both accounting windows, both listener groups, every tail slice; the placebo (permuting audiences) gives ≈ 0. It is *not* a universal law — see [Prior art](prior-art.md) for a domain where the sign reverses.

**The level is not one number, and that is the result.** It depends on who you count and over what window.

## Three structural facts

**The slope is retention, not intensity.** Decomposed by timestamps: +{{emp1.panel}} = pair duration +{{emp1.retention}} plus per-day rate **−{{emp1.rate}}**. Listeners of big artists stay with them *longer* but play them *less often per day*. Since real user-centric pools settle monthly, the policy-relevant slope is closer to +{{emp1.month}}.

**The 50/50 blend does not identify the level.** The dataset is constructed half mainstream, half beyond-mainstream; those groups give +{{emp1.main}} and +{{emp1.beyond}}. A population figure would need reweighting by the real mainstreaminess distribution.

**The slope is convex — steeper at the head.** Locally at A ≥ 200 it is +{{emp1.head}}. For the question "does the top gain from user-centric" the head slope is the relevant one, not the global average. This is not an anomaly of our data: the Dirichlet model predicts exactly this shape, `b/(1−b)` as a function of penetration.

## The falsifier that worked

Truncating the full-history dataset to the top 50 artists per user moves b from +{{emp1.panel}} to +{{emp1.trunc}} — almost exactly the value of the truncated dataset (+{{emp1.k360}}). The gap between the two datasets is therefore an artefact of truncation, not a difference in the world. Our pre-registered guess about the *direction* of that bias was wrong, and the gate caught it.

## Feeding it back into the model

The estimator was run on the simulation's own data-generating process to measure its attenuation (ceiling discretisation eats ~{{emp1.atten}}%, factor {{emp1.atten_factor}}). Inverted, the panel b = +{{emp1.panel}} corresponds to a model **γ ≈ +{{emp1.gamma_model}}**; the head corresponds to ≈ +0.28. Those are the values the [simulation](../simulations/sim4.md) now runs on — the model no longer turns a free dial.

![Slope on both datasets]({{RAW}}/figures/fig17_gamma_empirical.png)

## Limits

Last.fm is scrobbling, not a cash register; its demography is skewed; the curated dataset is not a random sample; b is a reduced form that absorbs graph selection as well as intensity; the epoch is pre-algorithmic. The precision `± {{emp1.panel_se}}` is sampling error only — the systematic uncertainty of sample composition and window choice is larger. All of this is an argument for the platform measuring its own value, not against measuring.

## Run it

```bash
python3 emp1/gamma_measure.py    # gates G1–G4, sensitivity grid, fig17
python3 emp1/moreau_check.py     # cross-check against published streaming estimates
```

Both need the external datasets (~4 GB, not in git); sources and checksums are in [emp1/README.md]({{REPO}}/blob/main/emp1/README.md).
