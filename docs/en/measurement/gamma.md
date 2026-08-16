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
| Full panel (~10 years), 50/50 blend | **+0.101 ± 0.004** |
| — mainstream listeners | +0.160 |
| — beyond-mainstream listeners | +0.023 |
| — window: calendar year | +0.068 |
| — window: one month | +0.048 |
| — head of the distribution (A ≥ 200) | +0.232 |
| Last.fm-360K (top-50 per user) | +0.044 |
| BeyMS truncated to top-50 (falsifier) | +0.041 |

**The sign is solid inside this domain.** It does not flip in any cut: two datasets, two estimators, 27 threshold combinations, both accounting windows, both listener groups, every tail slice; the placebo (permuting audiences) gives ≈ 0. It is *not* a universal law — see [Prior art](prior-art.md) for a domain where the sign reverses.

**The level is not one number, and that is the result.** It depends on who you count and over what window.

## Three structural facts

**The slope is retention, not intensity.** Decomposed by timestamps: +0.101 = pair duration +0.254 plus per-day rate **−0.154**. Listeners of big artists stay with them *longer* but play them *less often per day*. Since real user-centric pools settle monthly, the policy-relevant slope is closer to +0.048.

**The 50/50 blend does not identify the level.** The dataset is constructed half mainstream, half beyond-mainstream; those groups give +0.160 and +0.023. A population figure would need reweighting by the real mainstreaminess distribution.

**The slope is convex — steeper at the head.** Locally at A ≥ 200 it is +0.232. For the question "does the top gain from user-centric" the head slope is the relevant one, not the global average. This is not an anomaly of our data: the Dirichlet model predicts exactly this shape, `b/(1−b)` as a function of penetration.

## The falsifier that worked

Truncating the full-history dataset to the top 50 artists per user moves b from +0.101 to +0.041 — almost exactly the value of the truncated dataset (+0.044). The gap between the two datasets is therefore an artefact of truncation, not a difference in the world. Our pre-registered guess about the *direction* of that bias was wrong, and the gate caught it.

## Feeding it back into the model

The estimator was run on the simulation's own data-generating process to measure its attenuation (ceiling discretisation eats ~16%, factor 0.84). Inverted, the panel b = +0.101 corresponds to a model **γ ≈ +0.12**; the head corresponds to ≈ +0.28. Those are the values the [simulation](../simulations/sim4.md) now runs on — the model no longer turns a free dial.

![Slope on both datasets](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig17_gamma_empirical.png)

## Limits

Last.fm is scrobbling, not a cash register; its demography is skewed; the curated dataset is not a random sample; b is a reduced form that absorbs graph selection as well as intensity; the epoch is pre-algorithmic. The precision `± 0.004` is sampling error only — the systematic uncertainty of sample composition and window choice is larger. All of this is an argument for the platform measuring its own value, not against measuring.

## Run it

```bash
python3 emp1/gamma_measure.py    # gates G1–G4, sensitivity grid, fig17
python3 emp1/moreau_check.py     # cross-check against published streaming estimates
```

Both need the external datasets (~4 GB, not in git); sources and checksums are in [emp1/README.md](https://github.com/ProximaCA/tonify-sims/blob/main/emp1/README.md).
