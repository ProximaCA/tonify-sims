*English translation of [PAPER.md](PAPER.md). The Russian original is the source of truth; numbers are identical.*

# Payout Mechanisms Across Two Worlds: Pro-Rata, User-Centric, and the Attention Economy
### A calibrated simulation of the music market's "cash register" (payout) regimes · v0.4 · MIT License
*Tonify Research · August 2026 · reproducible: `sim1/tonify_cash_sim.py` + `sim1/v04_full.py`, seed=42*

---

## Abstract
We construct a synthetic market of 200,000 artists, calibrated to three independently measured
anchors (Luminate, Spotify Loud & Clear, CMA), and compare four payout mechanisms:
**pro-rata** (Spotify), **user-centric** (SoundCloud FPR), recurring patronage (Twitch),
and the direct **attention economy** (Tonify, World B). Main result: changing the split rule
within World A shifts an artist's minimum viable audience by at most ~1.3×,
whereas moving to the direct mechanisms of World B shifts it by **1–2 orders of magnitude** — provided
that a devoted fan's payment frequency exceeds the breakeven range of 0.38–6.31 payments/year
(median 1.25). Recurring mechanics (per-superfan rate 12 — throughout, the "rate" is payments
per superfan per year, "kef" in the Russian original) close that range structurally.
The red team retracted one v0.2 number and replaced three point assumptions with ranges.

---

## 1. Introduction: two worlds
**World A** — a fixed pool of subscription money divided by a formula: pro-rata (Spotify),
user-centric (SoundCloud), artist-centric (Deezer/UMG). The core theorem (Bergantiños &
Moreno-Ternero, 2023): any stable rule divides a listener's contribution only among the artists
that listener actually played — an artist's ceiling is set by their own audience under any formula.
**World B** — money arrives on top of the subscription, directly: donations, recurring patronage,
drops (Tonify — an attention economy on Telegram/TON rails; Unify — a global
music layer, see §7). The question of this paper: by how many orders of magnitude the worlds differ,
and under which measurable conditions World B outperforms World A.

## 2. Model and calibration
The world: N=200,000 artists; the annual-stream distribution is a piecewise construction
(lognormal body / log-bridge / Pareto tail α=1.4) fitted to the anchors:
T1 87% of artists <1000 streams/year (Luminate) → obtained 87.0% ✓
T2 2.6% of artists >$1000/year in royalties (Spotify) → 2.6% ✓
T3 top 0.28% of artists ≈50% of streams (CMA/Last.fm) → 44.5% ✓; Gini 0.97
A listener's plays for a given artist: lognormal(median 5.16; mean 21.21) [LFM-1b].
All parameters → sources: README.md; red team: CRITIC.md.

## 3. World A: results
Minimum viable audience (MVA) for $100/mo:
- **pro-rata · signed** (a signed artist's per-stream take, $0.0003/stream): **188,590** listeners
- **pro-rata · independent** ($4.43/1000, US 2026): **12,771**
- **user-centric** (Monte Carlo wallet share; 40% paying, pool = 70% of revenue):
  **9,512** at a wallet of 10,000 plays/year (5,000 → 4,800; 20,000 → 18,500)
- **Twitch mechanics** (recurring subscription, 50/50 split, rate 12): **2,353**
Conclusion A: user-centric improves on pro-rata independent by ~1.3× — consistent with
the empirics (SoundCloud: +34% money into the bottom bucket, −7% of artists out of it; Deezer:
2.4% of the pool redistributed). The rule changes — the order of magnitude does not.

## 4. World B: Tonify attention economy
Parameters: superfans at 0.6–1.7% of the audience; ticket size $3.1–6.9; artist share 0.80–0.95.
- **Breakeven against pro-rata independent: 0.38 … 1.25 … 6.31 payments/superfan/year.**
- MVA at rate 4: **3,204**; at a recurring rate of 12 on the TON rail: **900**.
- Paying-fan rate benchmarks: Twitch **12+** (subscription+bits), Patreon **12**,
  Tencent social — ARPPU multiplier of 20.6× (peak) / 6.4× (after the regulatory squeeze).
  The worst breakeven corner (6.31) sits below the structural rate of all three benchmarks.
- Rails, out of $1: TON → 94.9¢ to the artist / 5.0¢ to Tonify; Stars desktop 91.7/4.8;
  Stars mobile 64.1/3.4 (32.5¢ — app stores and spread). On a mobile payment, TON is 1.5×
  more profitable for Tonify than Stars.
- Fraud: injecting F% bot streams siphons F/(1+F) of the pool from everyone (analytical
  dilution curve, no detection); in the direct economy the losses of the innocent ≈ 0
  (its own loss classes — chargebacks — do not smear across artists).
- Logistics of the $13 threshold: 89.9% of signed artists wait >10 years for their first payout.

## 5. Milestone-solver (Tonify's cash, 5% commission)
$300K MRR is **not reached** on donation commission alone: 1M MAU × 1.7% × rate 4 × $6.9
× 5% = $1,955 MRR (a 150× gap). It is reached at: 5M MAU × 5% paying × rate 12 × $6 ×
blended take 20%; or 10M × 4% × 12 × $5 × 15%. Corollary: the milestone requires
recurring patronage and blended lines (drops/premium) — or a recalculation of the figure.

## 6. Review (red team, summary from CRITIC.md)
Retracted: "a status quo of 0.42 donations/year" (verbatim from the simulation output,
translated) — a category error on SoundCloud's 29%.
Replaced with ranges: plays/listener 8–21 (the LFM-1b window ≠ a year), ticket size $3.1–6.9
(PWYW experiment: mean €3.10, refusal rises 24.4% vs 17.3%), superfans 0.6–1.7%
(the 97-2-1 rule). Fixed: binomial superfans (fig2). Honest negative: at today's
payment frequency, direct loses to pro-rata independent.

## 7. Unify: global music layer — [to be filled in by the founder]
Thesis: —
Mechanics on top of Tonify: —
What we measure first: —

## 8. Delegated to Claude Code (spec: CLAUDE_CODE_HANDOFF.md)
- SIM 2 — Telegram social graph: BA+cliques, complex contagion, phase diagram over K, hub seeding. [ ]
- SIM 3 — anti-graveyard: the "payouts ≤ inflow" law (verbatim, translated) versus emission, calibrated on Hamster 300M→12M. [ ]
- Full bipartite user-centric (instead of Monte Carlo wallet share). [ ]
- Artist-centric on Deezer/UMG parameters (×2 boost for 1000 plays/500 listeners). [ ]
- Fraud with detection and the cost of detection; a chargeback model for the direct economy. [ ]
- The Stars spread line and premium subscriptions in the cash layer. [ ]
- — (to be added by the founder)
- — (to be added by the founder)

## 9. Limitations
A synthetic world: the tail shape between the anchors is a construction; UC is a wallet approximation;
the rate, ticket size, and superfan share are unmeasured axes ("Object 3", translated), to be measured by the MVP;
the Tencent benchmark is a blend with advertising; the regulatory risk to gifting (−66% of TME segment
revenue over 3 years) is not in the model. No conclusion is stated more strongly than its falsifier.

## Figures
fig1 MVA curve · fig2 income distribution (binomial) · fig3 fraud dilution ·
fig4 the $1 rails · **fig5 the World A→B ladder** · **fig6 MRR-solver**

*MIT License. Reproduction: python3 sim1/tonify_cash_sim.py && python3 sim1/v04_full.py*

---
## Addendum v0.5 — the full {rule × contract} matrix (caught by the founder)
The split rule and the contract are orthogonal axes; previous versions conflated them.
The full per-listener-year → MVA matrix (fig7): pro-rata signed $0.006/listener-year → 188,590;
pro-rata independent $0.094 → 12,771; user-centric signed $0.0086 → 140,095;
user-centric independent $0.126 → 9,512; direct·360 (rate 4) → 4,577; direct independent
(rate 4) → 3,204; recurring rate 12 TON → 900.
**The matrix's headline conclusion: the contract outweighs the rule.** The pro-rata→user-centric
move yields ×1.34; the signed→independent move yields ×14.7. World A's best formula does not
compensate for the 6.8% label pass-through: user-centric signed (140,095) is worse than pro-rata independent (12,771).
Reforming the rule without reforming the contract is a reshuffle one order of magnitude short of what is needed.
