*🇬🇧 English | [🇷🇺 Русский](RESULTS.ru.md)*

*English translation of [RESULTS.ru.md](RESULTS.ru.md); the Russian original is the source of truth, numbers are identical.*

# Results v0.3 — current

The v0.2 headlines ("status quo = 0.42 donations/year"; "breakeven ≈ 1") were
retracted as a category error (CRITIC §1) and are not restated as results.
World validation and the numbers that survived:

## World validation (target → obtained)
87% <1000 streams → 87.0% ✓ · 2.6% of rightsholders >$1000/yr → 2.6% ✓ · top 0.28% ~50% of streams → 44.5% ✓
the bottom 90% hold 0.9% of the market (Jensen: "bottom tiers ~2%" — same order of magnitude) · Gini 0.97

## Minimum viable audience (MVA, $100/mo)
Pool, signed: 188,590 listeners · Pool, independent: 12,771
Direct till at 2/yr: 6,407 · at 4/yr: 3,204 · at 8/yr: 1,602
(The retracted 0.42/yr row, MVA 30,782, is not a result.)

## Fraud
Injecting F% of bot streams siphons F/(1+F) of everyone's money out of the pool; in the direct economy
the honest players' loss = 0: a bot cannot donate with other people's money. At a 30% injection the pool
loses 23% — the direct rail 0%.

## Payout threshold logistics ($13 minimum)
Signed pocket: 94.3% of artists wait longer than a year for their first payout, 89.9% — longer than 10 years.
Matches the manifesto's example (an artist at $0.10/mo → 130 months) — now as a distribution.

## Honest limitations (for the reviewer)
1) Full bipartite user×artist — now sim4, not a Monte-Carlo wallet.
2) The donation shape lognormal($5, σ=0.8) is an assumption; the shape is from Bandcamp/Twitch, not measured for music.
3) Superfan share is a range 0.6–1.7% (CRITIC §7), not a point.
4) Cadence k is UNMEASURED in music — emp2 is the slot; Twitch k=12 is not a closer.

## §1. Breakeven became an honest range
0.38 … **1.25** … 6.31 donations/superfan/yr (18 combinations: plays 8–21 × ticket $3.1–6.9 × superfans 0.6–1.7%).
The 0.42 figure from v0.2 is RETRACTED (category error, CRITIC §1).

## §2. Cadence is unmeasured in music (Twitch does not close the range)
k is payments per superfan per year («кеф» in the Russian original). Adjacent-industry
numbers — Twitch k=12 (subscription arithmetic), Patreon k=12, Tencent gifting ARPPU
20.6× at peak / 6.4× after the squeeze [TME 4Q21/4Q24] — are colour, not a closer of
0.38–1.25–6.31. Recurring mechanics *would* close the worst corner if and only if
measured k ≥ 6.31; that inequality is not a music fact. The protocol that would close
it is emp2: ≥200 Telegram payments in `data/pilot_payments.csv`. Status: **UNMEASURED**
([emp2](../emp2/README.md)). The Twitch-mechanics *rung* of fig5 (MVA 2,353 at Twitch's
own $5 and 50/50 split) is a take-rate comparison, not a cadence closer.

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
