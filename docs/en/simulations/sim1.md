---
description: What a listener is worth — pricing the payout mechanisms against the label contract.
---

# sim1 — what a listener is worth

**The question.** How much does a listener deliver to an artist under each payout mechanism, and how does that compare with what the label contract takes?

**The gates.** The synthetic world must reproduce three independently measured anchors before any conclusion is printed: the share of artists below 1000 streams a year, the share above the top threshold, and the share of all streams held by the top fraction. A run that misses them exits non-zero.

**The headline.** The rule axis moves artist viability ×1.34 at the baseline wallet. The contract axis moves it ×14.8. The industry argues about the first number.

**Run it.** `python3 sim1/tonify_cash_sim.py` — then `v04_full.py`, `v05_matrix.py`, `v06_uc_crossover.py`, `v07_passthrough.py` for the world ladder, the rule×contract matrix, the crossover, and the pass-through grid.

***

### sim1 — what a listener is worth: pricing the payout mechanisms

A synthetic market of 200,000 artists, calibrated to three independently
measured anchors (87% of tracks under 1,000 streams/year — Luminate, stylized onto the artist world; 2.6% of
rightsholders above $1,000/year — Spotify Loud & Clear; top-0.28% holding ≈50%
of streams — CMA/Last.fm; obtained: 87.0% / 2.6% / 44.5%, Gini 0.97). Full
model: [PAPER](https://github.com/ProximaCA/tonify-sims/blob/main/paper/PAPER.md); numbers:
[RESULTS](https://github.com/ProximaCA/tonify-sims/blob/main/paper/RESULTS.md); retractions:
[CRITIC](https://github.com/ProximaCA/tonify-sims/blob/main/paper/CRITIC.md); every parameter's source:
[SOURCES](https://github.com/ProximaCA/tonify-sims/blob/main/SOURCES.md).

![fig2_income_dist](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig2_income_dist.png)

*fig2 — annual income distribution over the 200,000 synthetic artists
(simulation, N=200,000 artists, binomial superfan sampling; log x-axis: each
step right is ×10 income). The signed-pool curve sits leftmost — a 30-listener
artist has an honest ~60% chance of zero direct income.*

**Finding 1 — the contract outweighs the rule, and the two multipliers have
different natures.** The contract axis of the {rule × contract} matrix is a
single empirical scalar — the pass-through 0.0003/0.00443 = 6.772% applied to
both rows — so its ×14.8 is arithmetic by construction, not an emergent
result; only the rule axis (×1.34 at the baseline wallet) has a Monte-Carlo
origin. What the matrix contributes is commensurability: the two axes had
never been placed on one MVA grid. The best World-A formula still does not
survive the label pass-through: user-centric signed needs 140,463 listeners
against 12,771 for pro-rata independent. The $100/month ladder: 188,590
(pro-rata signed) → 12,771 (pro-rata independent) → 3,204 (direct, at k=4,
best corner); a signed-360 contract scales the artist take ×0.70 (direct MVA
3,204 → 4,577). And the rule effect itself is not a scalar — see fig14: it
depends on listener intensity u and **flips sign at u\* ≈ 14,146 plays/yr**
(8,731 at PAID_SHARE 0.25; 21,371 at 0.60): above u\*, user-centric is *worse*
than pro-rata for that artist's audience — the rule moves money toward
artists of light listeners and away from artists of heavy ones (at u=20k, UC
needs 18,341 vs pro-rata's 12,771). External empirics (SoundCloud: +34% into
the bottom bucket; Deezer: 2.4% of the pool shifted) independently confirm
the rule effect is small against the contract effect — the qualitative
conclusion survives, the point estimate does not
([PAPER](https://github.com/ProximaCA/tonify-sims/blob/main/paper/PAPER.md) Addendum v0.5; [sim1 SPEC](https://github.com/ProximaCA/tonify-sims/blob/main/sim1/SPEC.md) §3.1–3.2).

![fig5_worlds_ladder](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig5_worlds_ladder.png)

*fig5 — the full World A → World B ladder (analytic; user-centric rows from
the Monte-Carlo wallet model, 200,000 listeners, seed 42). X-axis is log MVA:
each gridline is ×10 fewer listeners needed. Artist take per rung: pool rows —
the per-stream rate itself; Twitch mechanics — 50% split; direct · 360 — 0.80
× 0.70 = 0.56; direct breakeven/k=4 — 0.80; direct recurring TON — 0.949.
Changing the division rule moves MVA ~×1.3; changing the mechanism moves it
1–2 orders of magnitude (188,590 → 900 at recurring k=12 — decomposed:
k 4→12 gives ×3.0 to 1,068 at the same 0.80 take, the TON rail 0.80→0.949
gives the last ×1.19 to 900).*

![fig14_uc_crossover](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig14_uc_crossover.png)

*fig14 — user-centric is not a scalar (Monte-Carlo wallet model, 200,000
listeners/point, seed 42; log-log). MVA under user-centric as a function of
the listener's other listening u, for three PAID_SHARE values; the yellow
dashed line is pro-rata independent (12,771). Each curve crosses it at its
indifference point u\* (14,146 at the baseline PAID_SHARE 0.40): above u\*,
the rule reform makes this artist's audience worse off.*

**Finding 2 — breakeven is a range, not a point.** Direct donations beat the
independent streaming pool when a devoted fan pays more often than
0.38–1.25–6.31 times/year (min/median/max over 18 axis combinations; the
earlier point estimate was retracted — see *Retracted & bounded*). Adjacent-industry
cadence (Twitch/Patreon k=12) does **not** close that range — k is UNMEASURED
in music ([emp2](https://github.com/ProximaCA/tonify-sims/blob/main/emp2/README.md)). Recurring k=12 on the TON rail would drop
direct MVA to 900 *if* that k were measured. The Twitch-mechanics rung (2,353)
uses Twitch's own fixed $5 subscription; on the same $6.89 mean ticket as the
direct rows it would be 1,709 — the direct economy's edge over the Twitch
mechanics is the take rate (5% vs a 50% split), not the rail
([CRITIC](https://github.com/ProximaCA/tonify-sims/blob/main/paper/CRITIC.md) §1; [RESULTS](https://github.com/ProximaCA/tonify-sims/blob/main/paper/RESULTS.md) v0.3 §1–§2;
[PAPER](https://github.com/ProximaCA/tonify-sims/blob/main/paper/PAPER.md) §4; [sim1 SPEC](https://github.com/ProximaCA/tonify-sims/blob/main/sim1/SPEC.md) §3.4).

![fig1_mva](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig1_mva.png)

*fig1 — MVA versus payment rate k (analytic curves; the user-centric
reference lines carry the Monte-Carlo wallet estimate). MVA = minimum viable
audience for $100/month; k = payments per superfan per year; y-axis is log.
The purple direct curve crossing below the green independent-pool line near
k≈1 is the breakeven of Finding 2; each further doubling of k halves the
required audience.*

![fig6_mrr_solver](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig6_mrr_solver.png)

*fig6 — the $300K MRR solver (analytic curves; log-log axes). MRR = the
platform's monthly recurring revenue; MAU = monthly active users. A lone 5%
donation fee yields $1,955 MRR at 1M MAU — a 150× gap to the milestone; the
milestone closes only with recurring patronage and blended take 15–20% at
5–10M MAU.*

**Finding 3 — fraud dilutes pools, not direct rails.** Injecting F% bot
streams drains F/(1+F) of the pool from every artist — at 30% injection the
pool loses 23% — while honest-artist losses in the direct economy are ~0: a
bot cannot donate other people's money. This is an analytic dilution curve
with zero detection assumed, not a simulation; the direct economy has its own
loss classes (chargebacks), but they do not spread onto the innocent
([RESULTS](https://github.com/ProximaCA/tonify-sims/blob/main/paper/RESULTS.md) "Fraud"; [PAPER](https://github.com/ProximaCA/tonify-sims/blob/main/paper/PAPER.md) §4; caveat
[CRITIC](https://github.com/ProximaCA/tonify-sims/blob/main/paper/CRITIC.md) §4).

![fig3_fraud](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig3_fraud.png)

*fig3 — pool dilution under bot-stream injection (analytic curve F/(1+F), no
simulation, zero detection assumed): the pool's loss grows toward 23% at 30%
injection; the direct rail's honest-loss curve is flat zero.*

**Finding 4 — the $13 payout threshold is a decade for signed artists.** At
Telegram's $13 minimum withdrawal, 94.3% of signed-pool artists wait longer
than a year for their first payout, 89.9% longer than ten years; on the
direct rail the mean donation is $6.9 against the same $13 threshold. Of $1
on the TON rail, 94.9¢ reaches the artist (5.0¢ platform, 0.1¢ rail) versus
64.1¢ on Stars mobile ([RESULTS](https://github.com/ProximaCA/tonify-sims/blob/main/paper/RESULTS.md) "Payout threshold
logistics" + §3; [PAPER](https://github.com/ProximaCA/tonify-sims/blob/main/paper/PAPER.md) §4).

![fig4_rails](https://raw.githubusercontent.com/ProximaCA/tonify-sims/main/figures/fig4_rails.png)

*fig4 — where $1 of a donation goes (arithmetic fee breakdown, no
simulation): TON rail 94.9¢ to the artist / 5.0¢ platform / 0.1¢ rail,
against Stars desktop 91.7¢ and Stars mobile 64.1¢ (32.5¢ to app stores and
spread).*
