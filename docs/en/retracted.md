---
description: Claims we published and then withdrew, each with what replaced it.
---

# Retracted & bounded

This page is the point of the whole project, not an appendix to it. Every claim below was ours, was stated with confidence, and was then killed — by an adversarial red team, by a falsifier we built ourselves, or by a literature check we ran on our own novelty claim. Each is listed with what replaced it.

## Public retractions

### 1. "The status quo is 0.42 donations per year"

**What we claimed.** An inversion built on a platform's published 29% figure, used to argue how far the direct economy already was from breakeven.

**Why it died.** A category error: their 29% was superfans' share of *royalties* under a user-centric split, not a share of donations. The red team caught the mismatch.

**What replaced it.** The number was removed from the results entirely. In its place: the breakeven expressed as a range across 18 parameter combinations — 0.38 … 1.25 … 6.31 payments per superfan per year. Adjacent-industry cadence (Twitch k=12) was later itself retracted as a closer of that range — see below.

### 1b. "Twitch k=12 closes the range"

**What we claimed.** Recurring patronage closes 0.38–6.31 structurally, because Twitch and Patreon pay monthly.

**Why it died.** Adjacent-industry billing arithmetic is not a music measurement. The worst corner (6.31) sitting below Twitch's 12 is an analogy, not a fact.

**What replaced it.** [emp2](measurement/cadence.md): a fail-closed Telegram pilot of ≥200 payments. Until that CSV exists the range stays open. The Twitch-mechanics *rung* of fig5 (50/50 split at $5) is a take-rate comparison and was not retracted.

### 2. "γ = +0.10 ± 0.003"

**What we claimed.** A single measured value for the coupling parameter, quoted to three decimals.

**Why it died.** An 18-finding red team pass on the measurement, all 18 confirmed by independent reproduction. The point estimate hid three things: the slope is retention rather than intensity (+0.254 duration against −0.154 per-day rate); the dataset's 50/50 construction does not identify a population level (mainstream +0.160 against beyond +0.023); and the relation is convex, so the head slope (+0.232) is nearly ten times the tail's (+0.023).

**What replaced it.** A structured result instead of a point: the sign is solid, the level is a function of who you count and over what window, and the [full table of cuts](measurement/gamma.md) is published rather than averaged away.

### 3. "The first measurement of the intensity–size coupling"

**What we claimed.** Novelty for the empirical result.

**Why it died.** Our own prior-art check. The effect is the double jeopardy law, described in 1969 and given the closed form `w(1−b) = const` in 1972; it has been measured on the web, in games, in weighted networks, and described on the same Last.fm dataset we used. Our +0.101 lands on the Dirichlet prediction of +0.1032.

**What replaced it.** A narrower and more defensible claim — see [Prior art](measurement/prior-art.md). Landing on a fifty-year-old prediction is a stronger result than an unprecedented one: it means the measurement is right.

## Bounded, not retracted

Statements that survived but had their scope cut:

- **The sign of the coupling is "iron".** True within music streaming, 2005–2014. On mature social platforms the same shape has the opposite sign (Pourazad et al. 2023). All statements about the sign are now dated and domain-bounded.
- **"Only if linear" in the invariance lemma.** The claim that linearity was *necessary* for the minimum-viable-audience ratio was disproved by a log-periodic counterexample; the exact criterion replaced it, and linearity was demoted to sufficient.
- **The Hoeffding bound on lottery risk.** Withdrawn — the event is not a binomial threshold when payments are random; a numerical counterexample violated it by a factor of ~45. Replaced by a Chernoff bound, which preserves the qualitative conclusion.
- **The head-saturation narrative in the simulation.** Withdrawn: the diagnostic selected the top by saturation itself — circular sampling. The real head has Ã/ℓ = 1.08, so there is no over-representation to narrate.
- **An elasticity corridor derived from AM ≥ HM.** Withdrawn during the cross-check against published streaming estimates: the ordering of means does not bound a regression coefficient, and on our data the value falls outside the "corridor" we had asserted.
- **"Direct preserves the upper tail exactly."** Weakened after review. What L3 proves under A1–A8 is preservation of the tail *index* — the regular-variation exponent — not equality of the top share, the tail constant or the Gini. The phrasing also contradicted the sentence beside it, which reported the Gini moving. It now says the mechanism does not make the tail lighter.
- **"Gini barely moves."** Bounded to the world it was computed in. It holds at zero coupling; at the measured coupling `γ = +0.12` the direct economy *lowers* the summary Gini (0.9714 → 0.9651), because it pays for reach while the pool pays for intensity, and intensity concentrates as γ rises. The composition result is what survives unchanged in every world: 73.3% of artists with an audience earn exactly nothing. See [sim4 downside metrics](https://github.com/ProximaCA/tonify-sims/blob/main/sim4/README.md).

## Why publish this

Because the alternative is a document whose confidence is unearned. Every simulation in this project prints its gates *before* its conclusions and exits non-zero when one fails; the same discipline applied to claims means publishing the ones that failed. The ledgers behind this page are in the repository: [paper/THEORY.md §7](https://github.com/ProximaCA/tonify-sims/blob/main/paper/THEORY.md), [paper/CRITIC.md](https://github.com/ProximaCA/tonify-sims/blob/main/paper/CRITIC.md), [sim4/README.md](https://github.com/ProximaCA/tonify-sims/blob/main/sim4/README.md), [emp1/PRIOR_ART.md](https://github.com/ProximaCA/tonify-sims/blob/main/emp1/PRIOR_ART.md).
