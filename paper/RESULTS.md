*🇬🇧 English | [🇷🇺 Русский](RESULTS.ru.md)*

*English translation of [RESULTS.ru.md](RESULTS.ru.md); the Russian original is the source of truth, numbers are identical.*

# Results v0.2

## World validation (target → obtained)
87% <1000 streams → 87.0% ✓ · 2.6% of rightsholders >$1000/yr → 2.6% ✓ · top 0.28% ~50% of streams → 44.5% ✓
the bottom 90% hold 0.9% of the market (Jensen: "bottom tiers ~2%" — same order of magnitude) · Gini 0.97

## Two numbers that were not in the research
**1. Status quo = 0.42 donations per superfan per year.** Inverse problem: the measured SoundCloud
29% superfan share of revenue is reproduced in this world at 0.42 donations/superfan/yr.
Today's "direct economy" is one donation every 2.4 years.

**2. The direct till breaks even at ≈ 1 donation per year.** Tonify's direct till («касса» in the
Russian original — the direct-payment economy) overtakes the independent pool («котёл» — the streaming
royalty pool; $4.43/1K) once a devoted fan donates more often than ~once a year. Everything the product
must do economically comes down to one dial: push 0.42 → above 1.0. Each further step
(2 → 4 → 8) halves the minimum audience.

## Minimum viable audience (MVA, $100/mo)
Pool, signed: 188,590 listeners · Pool, independent: 12,771
Direct till at the status-quo 0.42/yr: 30,782 (honestly: worse than the independent pool!)
Direct till at 2/yr: 6,407 · at 4/yr: 3,204 · at 8/yr: 1,602

## Fraud
Injecting F% of bot streams siphons F/(1+F) of everyone's money out of the pool; in the direct economy
the honest players' loss = 0: a bot cannot donate with other people's money. At a 30% injection the pool
loses 23% — the direct rail 0%.

## Payout threshold logistics ($13 minimum)
Signed pocket: 94.3% of artists wait longer than a year for their first payout, 89.9% — longer than 10 years.
Matches the manifesto's example (an artist at $0.10/mo → 130 months) — now as a distribution.

## Honest limitations (for the reviewer)
1) No full bipartite user×artist graph — user-centric is not modeled separately (spec for v0.3).
2) The donation shape lognormal($5, σ=0.8) is an assumption; the shape is from Bandcamp/Twitch, not measured for music.
3) The superfan share is fixed at 1.7% — no sensitivity sweep over it (v0.3).
4) "Donations/superfan/yr" is the axis of the still-open "Object 3": the simulation names the parameter, the MVP measures it.

---
# v0.3 — after the red team (see CRITIC.md)

## §1. Breakeven became an honest range
0.38 … **1.25** … 6.31 donations/superfan/yr (18 combinations: plays 8–21 × ticket $3.1–6.9 × superfans 0.6–1.7%).
The 0.42 figure from v0.2 is RETRACTED (category error, CRITIC §1).

## §2. Rate-k benchmarks for the paying fan (answering the Twitch question)
Here k is the rate of payments per superfan per year («кеф» in the Russian original).
- **Twitch: k = 12+/yr structurally** — the subscription is recurring, a paying fan pays monthly
  on autopilot, plus bits/donations on top. Streamer income = donations + subscriptions + bits;
  Gini 0.57 across the top 10k (α=−2.13), ~0.93 extrapolated to the platform [vault: vol0123456789-2].
- **Tencent social: k >> 12** — gifter ARPPU of ¥175/mo at the peak vs ¥8.5 for the subscription
  (a 20.6× multiplier; 6.4× after the regulatory crackdown) [vault: TME 4Q21/4Q24]. The ceiling is the
  state, not demand.
- **Patreon: k = 12** (monthly patronage), ~25M paid vs ~100M free subscriptions.
- **Our breakeven: median 1.25.** Against the Twitch rate that is **~10:1 of headroom**:
  for the direct till to beat the pool, a devoted fan only has to pay ten times less often than a
  Twitch subscriber pays. A recurring artist subscription closes the breakeven structurally (12 > 6.31
  even in the worst corner of the range).

## §3. Cash layer: where the dollar goes (fig4_rails.png), Tonify fee 5%
TON: 94.9¢ to the artist · 5.0¢ Tonify · 0.1¢ rail
Stars desktop: 91.7¢ · 4.8¢ · 3.5¢
Stars mobile: 64.1¢ · 3.4¢ · 32.5¢ (Apple+spread)
Takeaway: the TON rail is not only cheaper for the fan — it earns Tonify 1.5× more on a mobile
donation than Stars does (5.0¢ vs 3.4¢ per dollar).

## §4. Milestone truth: $300K MRR on the 5% fee alone does NOT add up
1M MAU × 1.7% superfans × 4 donations × $6.9 × 5% = **$1,955 MRR**. The gap is 150×.
Configurations where $300K does add up (solver):
- 5M MAU × 5% paying × k = 12 (artist subscriptions) × $6 × blended take 20% = $300K ✓
- 10M MAU × 4% × k = 12 × $5 × take 15% = $300K ✓
Implication for the deck: the milestone is reachable only with (a) recurring artist subscriptions,
(b) a blended take of 15–20% (drops/marketplace/premium on top of the 5% on donations), (c) 5–10M MAU,
— or the milestone must be recomputed. A lone 5% fee on donations is $2–12K MRR per 1M MAU.
