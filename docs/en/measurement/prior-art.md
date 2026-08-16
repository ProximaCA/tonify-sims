---
description: Who measured this before us — all 16 sources, and the novelty claim we withdrew.
---

# Prior art

## The claim we withdrew

We initially framed the measurement as the first of its kind. It is not. The coupling between audience size and consumption intensity is the **double jeopardy** law, described in 1969, given a closed form in 1972, and measured since in groceries, on the web, in games, in weighted networks — and described on the very dataset we used.

The check that established this followed the same protocol as the theoretical prior-art pass: scouts by area, academic APIs before web search, and every "this is already known" claim verified against a *retrieved* primary source, defaulting to refuted when the source could not be obtained. 16 sources, all closed — 11 from the primary text, the rest through predecessors, abstracts, or citing works, each flagged as such.

## Where our number sits

| Source | Domain | Slope |
|---|---|---|
| Goodhardt, Ehrenberg & Chatfield 1984 (analytic) | theory | `b/(1−b)` — a function of penetration, not a constant |
| Sharp 2010, washing powders | groceries | +0.1028 |
| Habel & Rungie 2005, Dirichlet line | theory | +0.1032 |
| Stocchi et al. 2025, 32 apps (category FE) | mobile apps | +0.110 |
| **This study, Last.fm panel** | **music** | **+0.101** |
| Šulik 2026, films | cinema | +0.188 |
| Taneja 2020 / Baumann 2015, 24,000 domain-months | web | +0.191 … +0.262 |
| This study, head of the distribution | music | +0.232 |

Four independent sources from four unrelated markets land on the same value to the third decimal. The 1984 analytic result explains why the corridor is a corridor and not a point: the slope equals `b/(1−b)`, so low-penetration tails must be flat and high-penetration heads must be steep — which is exactly the head/tail spread we measured.

## The strongest external check

Moreau, Wikström, Haampland & Johannessen (2024) analysed 890 million streams of a real subscription service with a song fixed effect (52 045 144 observations). Their key coefficient — the elasticity of a song's user-centric revenue with respect to its audience's listening intensity — is **−0.754**. Their own conclusion restates our corollaries (c) and (d) almost word for word: the artist who benefits most from user-centric is the one whose audience listens *lightly* and *concentratedly*.

Running their quantities on our data (`emp1/moreau_check.py`): the Theorem 1 identity holds on real logs to 5.8e-15 across 31 040 artists; the audience-intensity slope is +0.053 arithmetic and +0.038 harmonic, matching their sign. Where the two studies differ — the rank profile of who loses — the specifications are not comparable: theirs identifies from variation within a song over months, ours is a cross-section across artists.

## Where the sign reverses

Pourazad, Stocchi & Narsey (2023) measured the same shape for social-media influencers: on mature platforms (Facebook, YouTube, Twitter) engagement per follower *falls* with audience size — reverse double jeopardy; on TikTok it rises; on Instagram there is no relation. So the sign we call solid is solid **within music streaming and within this epoch**, not as a law of nature.

## What remains ours

A log-log slope on user×artist pairs with within-user fixed effects in music; the decomposition into retention and per-day rate; and — the part with no precedent in the double-jeopardy literature, because that literature never built payout operators — the calibration of the effect into a model parameter, with the estimator's attenuation measured and inverted.

Full ledger, source by source, with the secondary-source flags: [emp1/PRIOR_ART.md](https://github.com/ProximaCA/tonify-sims/blob/main/emp1/PRIOR_ART.md).
